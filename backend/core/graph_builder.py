"""
PARASITE EVOLVED — 4-Layer Infiltration Graph Builder
Constructs a unified MultiDiGraph from parsed source files.
Layers: File → Function → Data Flow → Privilege/Trust
"""

import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple
import networkx as nx
from rich.console import Console
from backend.core.parser import ParsedFile, ParsedFunction, PrivilegeOp

console = Console()

INPUT_SOURCES = {
    "request", "request.get_json", "request.args", "request.form",
    "request.files", "request.data", "request.headers", "req.body",
    "req.params", "req.query", "sys.argv", "input", "stdin",
    "os.environ", "os.getenv", "process.env",
}

DANGEROUS_SINKS = {
    "execute", "executemany", "executescript", "cursor.execute",
    "os.system", "subprocess.run", "subprocess.call", "subprocess.Popen",
    "eval", "exec", "pickle.loads", "pickle.load",
    "open", "write", "send_file",
    "requests.get", "requests.post", "urllib.request.urlopen",
}


@dataclass
class GraphStats:
    total_nodes: int = 0
    total_edges: int = 0
    file_nodes: int = 0
    function_nodes: int = 0
    dataflow_paths: int = 0
    privilege_nodes: int = 0
    critical_ops: int = 0


@dataclass
class InfiltrationGraph:
    graph: nx.MultiDiGraph
    file_nodes: List[str]
    function_nodes: List[str]
    dataflow_paths: List[List[str]]
    privilege_nodes: List[str]
    stats: GraphStats


def _resolve_import_target(imp_stmt: str, current_file: str, all_files: Dict[str, ParsedFile]) -> List[str]:
    """Resolve an import statement to actual file paths in the repo."""
    targets = []
    # Handle "from X import Y" and "import X"
    match = re.match(r"from\s+([\w.]+)\s+import", imp_stmt)
    if not match:
        match = re.match(r"import\s+([\w.]+)", imp_stmt)
    if not match:
        return targets

    module = match.group(1)
    module_parts = module.split(".")

    for fpath in all_files:
        fname = os.path.splitext(os.path.basename(fpath))[0]
        if fname == module_parts[-1] or module in fpath.replace(os.sep, "."):
            targets.append(fpath)

    return targets


def _build_file_layer(graph: nx.MultiDiGraph, parsed_files: List[ParsedFile]) -> List[str]:
    """Layer 1: File dependency graph from import relationships."""
    file_map = {pf.path: pf for pf in parsed_files}
    file_nodes = []

    for pf in parsed_files:
        priv_count = sum(len(fn.privilege_operations) for fn in pf.functions)
        graph.add_node(pf.path, **{
            "type": "file",
            "layer": "file",
            "language": pf.language,
            "function_count": len(pf.functions),
            "privilege_op_count": priv_count,
            "label": os.path.basename(pf.path),
            "classes": pf.classes,
        })
        file_nodes.append(pf.path)

    edge_count = 0
    for pf in parsed_files:
        for imp in pf.imports:
            targets = _resolve_import_target(imp, pf.path, file_map)
            for target in targets:
                if target != pf.path:
                    graph.add_edge(pf.path, target,
                                   layer="file", type="imports",
                                   label=imp.strip()[:60])
                    edge_count += 1

    console.print(f"[bold yellow]🕸️  Constructing file dependency graph... {len(file_nodes)} nodes, {edge_count} edges[/]")
    return file_nodes


def _build_function_layer(graph: nx.MultiDiGraph, parsed_files: List[ParsedFile]) -> List[str]:
    """Layer 2: Function call graph with privilege annotations."""
    func_map: Dict[str, ParsedFunction] = {}
    func_nodes = []

    # Register all functions as nodes
    for pf in parsed_files:
        for fn in pf.functions:
            node_id = f"{pf.path}::{fn.name}"
            priv_ops_data = [
                {"type": p.type, "line": p.line, "snippet": p.code_snippet, "risk": p.risk_level}
                for p in fn.privilege_operations
            ]
            graph.add_node(node_id, **{
                "type": "function",
                "layer": "function",
                "file": pf.path,
                "name": fn.name,
                "line_start": fn.line_start,
                "line_end": fn.line_end,
                "parameters": fn.parameters,
                "privilege_ops": priv_ops_data,
                "call_count": len(fn.calls),
                "label": fn.name,
            })
            func_nodes.append(node_id)
            func_map[fn.name] = fn

            # Cross-layer edge: file → function
            graph.add_edge(pf.path, node_id,
                           layer="cross", type="contains",
                           label=f"defines {fn.name}")

    # Build call edges
    all_func_names = {fn.name: f"{pf.path}::{fn.name}"
                      for pf in parsed_files for fn in pf.functions}

    for pf in parsed_files:
        for fn in pf.functions:
            caller_id = f"{pf.path}::{fn.name}"
            for call_name in fn.calls:
                # Strip method-style prefixes: self.method → method
                simple_name = call_name.split(".")[-1]
                if simple_name in all_func_names:
                    callee_id = all_func_names[simple_name]
                    if callee_id != caller_id:
                        graph.add_edge(caller_id, callee_id,
                                       layer="function", type="calls",
                                       label=f"calls {simple_name}")

    return func_nodes


def _build_dataflow_layer(graph: nx.MultiDiGraph, parsed_files: List[ParsedFile]) -> List[List[str]]:
    """Layer 3: Data flow graph tracking taint from sources to sinks."""
    dataflow_paths = []

    # Identify source and sink functions
    source_funcs = []
    sink_funcs = []

    for pf in parsed_files:
        for fn in pf.functions:
            node_id = f"{pf.path}::{fn.name}"

            # Check if function receives external input
            is_source = False
            for param in fn.parameters:
                if param in ("request", "req", "data", "payload", "query", "body"):
                    is_source = True
                    break
            for call in fn.calls:
                for src in INPUT_SOURCES:
                    if src in call:
                        is_source = True
                        break
            if any("request" in line or "args.get" in line or "get_json" in line
                   for line in fn.raw_code.split("\n")):
                is_source = True

            if is_source:
                source_funcs.append(node_id)
                graph.nodes[node_id]["is_input_source"] = True

            # Check if function contains dangerous sinks
            is_sink = False
            for call in fn.calls:
                for sink in DANGEROUS_SINKS:
                    if sink in call or call.endswith(sink.split(".")[-1]):
                        is_sink = True
                        break
            for op in fn.privilege_operations:
                if op.risk_level in ("CRITICAL", "HIGH"):
                    is_sink = True

            if is_sink:
                sink_funcs.append(node_id)
                graph.nodes[node_id]["is_dangerous_sink"] = True

    # Trace paths from sources to sinks through the call graph
    # Limit pairs to prevent O(n²) explosion on large repos
    max_pairs = 50
    pair_count = 0
    for source in source_funcs:
        if pair_count >= max_pairs:
            break
        for sink in sink_funcs:
            if pair_count >= max_pairs:
                break
            if source == sink:
                # Same function is both source and sink — direct taint
                graph.add_edge(source, sink,
                               layer="dataflow", type="direct_taint",
                               label="input→sink (direct)")
                dataflow_paths.append([source])
                pair_count += 1
                continue

            try:
                if nx.has_path(graph, source, sink):
                    paths = list(nx.all_simple_paths(graph, source, sink, cutoff=4))
                    for path in paths[:2]:
                        for i in range(len(path) - 1):
                            graph.add_edge(path[i], path[i + 1],
                                           layer="dataflow", type="taint_flow",
                                           label="tainted data")
                        dataflow_paths.append(path)
                    pair_count += 1
            except nx.NetworkXError:
                pass

    console.print(f"[bold blue]🌊 Tracing data flows... {len(dataflow_paths)} taint paths identified[/]")
    return dataflow_paths


def _build_privilege_layer(graph: nx.MultiDiGraph, parsed_files: List[ParsedFile]) -> List[str]:
    """Layer 4: Privilege/trust graph connecting functions to privilege operations."""
    priv_nodes = []
    priv_type_nodes: Dict[str, str] = {}
    critical_count = 0

    # Create privilege type nodes
    for priv_type in ("NETWORK", "FILE_IO", "DATABASE", "ENV", "SHELL", "AUTH"):
        priv_node_id = f"PRIV::{priv_type}"
        priv_type_nodes[priv_type] = priv_node_id

    # Connect functions to privilege operations
    for pf in parsed_files:
        for fn in pf.functions:
            func_id = f"{pf.path}::{fn.name}"
            seen_types: Set[str] = set()

            for op in fn.privilege_operations:
                if op.type not in seen_types:
                    priv_node_id = priv_type_nodes[op.type]
                    if priv_node_id not in priv_nodes:
                        risk_weight = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
                        graph.add_node(priv_node_id, **{
                            "type": "privilege",
                            "layer": "privilege",
                            "priv_type": op.type,
                            "risk_level": op.risk_level,
                            "label": op.type,
                            "weight": risk_weight.get(op.risk_level, 1),
                        })
                        priv_nodes.append(priv_node_id)

                    hop_count = 1
                    priv_weight = {"CRITICAL": 10, "HIGH": 7, "MEDIUM": 4, "LOW": 1}
                    weight = hop_count + priv_weight.get(op.risk_level, 1)

                    graph.add_edge(func_id, priv_node_id,
                                   layer="privilege", type="accesses",
                                   weight=weight,
                                   risk_level=op.risk_level,
                                   snippet=op.code_snippet[:80],
                                   label=f"{op.type} (L{op.line})")
                    seen_types.add(op.type)

                if op.risk_level == "CRITICAL":
                    critical_count += 1

    console.print(f"[bold red]⚡ Mapping privilege operations... {critical_count} critical ops found[/]")
    return priv_nodes


def build_infiltration_graph(parsed_files: List[ParsedFile]) -> InfiltrationGraph:
    """Construct the unified 4-layer infiltration graph from parsed files."""
    graph = nx.MultiDiGraph()

    # Build each layer
    file_nodes = _build_file_layer(graph, parsed_files)
    func_nodes = _build_function_layer(graph, parsed_files)
    dataflow_paths = _build_dataflow_layer(graph, parsed_files)
    priv_nodes = _build_privilege_layer(graph, parsed_files)

    stats = GraphStats(
        total_nodes=graph.number_of_nodes(),
        total_edges=graph.number_of_edges(),
        file_nodes=len(file_nodes),
        function_nodes=len(func_nodes),
        dataflow_paths=len(dataflow_paths),
        privilege_nodes=len(priv_nodes),
        critical_ops=sum(
            1 for _, d in graph.nodes(data=True)
            if d.get("type") == "privilege" and d.get("risk_level") == "CRITICAL"
        ),
    )

    return InfiltrationGraph(
        graph=graph,
        file_nodes=file_nodes,
        function_nodes=func_nodes,
        dataflow_paths=dataflow_paths,
        privilege_nodes=priv_nodes,
        stats=stats,
    )
