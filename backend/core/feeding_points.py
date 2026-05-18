"""
PARASITE EVOLVED — Feeding Point Detection & Scoring
Identifies the most dangerous entry points for a parasite in the infiltration graph.
"""

import networkx as nx
from dataclasses import dataclass, field
from typing import List, Dict
from rich.console import Console
from backend.core.graph_builder import InfiltrationGraph

console = Console()

PROTECTION_PATTERNS = [
    "sanitize", "validate", "escape", "clean", "filter", "whitelist",
    "parameterize", "prepared", "binding", "csrf", "rate_limit",
    "throttle", "captcha", "verify", "check_permission", "authorize",
]

PRIVILEGE_WEIGHTS = {
    "SHELL": 10,
    "DATABASE": 8,
    "AUTH": 8,
    "FILE_IO": 5,
    "NETWORK": 5,
    "ENV": 4,
}


@dataclass
class FeedingPoint:
    node_id: str
    name: str
    file: str
    line: int
    blast_radius_score: float
    stealth_score: float
    persistence_score: float
    final_score: float
    danger_level: str
    explanation: str
    attack_surfaces: List[str]
    attack_approach: str


def _calculate_fan_in(graph: nx.MultiDiGraph, node_id: str) -> int:
    """Count incoming edges (dependencies) for a node."""
    try:
        return graph.in_degree(node_id)
    except nx.NetworkXError:
        return 0


def _calculate_privilege_level(graph: nx.MultiDiGraph, node_id: str) -> float:
    """Calculate weighted privilege level based on connected privilege operations."""
    total = 0.0
    for _, target, data in graph.out_edges(node_id, data=True):
        if data.get("layer") == "privilege":
            priv_type = graph.nodes[target].get("priv_type", "")
            total += PRIVILEGE_WEIGHTS.get(priv_type, 1)
    # Also check the function's own privilege ops
    node_data = graph.nodes.get(node_id, {})
    for op in node_data.get("privilege_ops", []):
        total += PRIVILEGE_WEIGHTS.get(op.get("type", ""), 1) * 0.5
    return total


def _detect_protection_level(graph: nx.MultiDiGraph, node_id: str, raw_code: str = "") -> int:
    """Count protection patterns found in a node's code and connections."""
    count = 0
    code_lower = raw_code.lower() if raw_code else ""

    for pattern in PROTECTION_PATTERNS:
        if pattern in code_lower:
            count += 1

    # Check if any calling functions have protection
    for pred in graph.predecessors(node_id):
        pred_data = graph.nodes.get(pred, {})
        pred_name = pred_data.get("name", "").lower()
        for pattern in PROTECTION_PATTERNS:
            if pattern in pred_name:
                count += 1
    return count


def _get_function_code(graph: nx.MultiDiGraph, node_id: str, parsed_files) -> str:
    """Retrieve raw code for a function node."""
    node_data = graph.nodes.get(node_id, {})
    file_path = node_data.get("file", "")
    func_name = node_data.get("name", "")
    # Search parsed files for the matching function
    if hasattr(parsed_files, '__iter__'):
        for pf in parsed_files:
            if pf.path == file_path:
                for fn in pf.functions:
                    if fn.name == func_name:
                        return fn.raw_code
    return ""


def _generate_explanation(node_id: str, node_data: dict, blast: float,
                          stealth: float, persist: float,
                          graph: nx.MultiDiGraph) -> str:
    """Generate natural language explanation of why a feeding point is dangerous."""
    name = node_data.get("name", node_id)
    file_label = node_data.get("file", "unknown")
    parts = []

    # Privilege analysis
    priv_ops = node_data.get("privilege_ops", [])
    priv_types = list({op.get("type", "") for op in priv_ops})
    if priv_types:
        parts.append(f"Function '{name}' performs {len(priv_ops)} privilege operations "
                     f"({', '.join(priv_types)})")

    # Blast radius analysis
    fan_in = _calculate_fan_in(graph, node_id)
    if fan_in > 0:
        parts.append(f"with {fan_in} incoming dependencies amplifying blast radius")

    # Stealth analysis
    if stealth > 7:
        parts.append("No input validation or sanitization patterns detected — "
                     "attacks pass through unfiltered")
    elif stealth > 4:
        parts.append("Minimal protection patterns present — insufficient for security")

    # Data flow
    is_source = node_data.get("is_input_source", False)
    is_sink = node_data.get("is_dangerous_sink", False)
    if is_source and is_sink:
        parts.append("Acts as BOTH input source and dangerous sink — "
                     "direct injection vector with no intermediate validation")
    elif is_source:
        parts.append("Receives external input that propagates to sensitive operations")
    elif is_sink:
        parts.append("Contains dangerous operations reachable from user-controlled data")

    return ". ".join(parts) + "."


def _generate_attack_surfaces(node_id: str, node_data: dict,
                               graph: nx.MultiDiGraph) -> List[str]:
    """List specific attack surfaces exposed by this feeding point."""
    surfaces = []
    priv_ops = node_data.get("privilege_ops", [])

    for op in priv_ops:
        op_type = op.get("type", "")
        snippet = op.get("snippet", "")
        risk = op.get("risk", "")

        if op_type == "SHELL":
            surfaces.append(f"Command Injection via: {snippet}")
        elif op_type == "DATABASE":
            surfaces.append(f"SQL Injection via: {snippet}")
        elif op_type == "FILE_IO":
            surfaces.append(f"Path Traversal / File Access via: {snippet}")
        elif op_type == "AUTH":
            surfaces.append(f"Authentication Bypass via: {snippet}")
        elif op_type == "NETWORK":
            surfaces.append(f"SSRF / Network Access via: {snippet}")
        elif op_type == "ENV":
            surfaces.append(f"Environment Variable Leak via: {snippet}")

    # Check for sensitive data exposure
    if node_data.get("is_input_source") and node_data.get("is_dangerous_sink"):
        surfaces.append("Direct input-to-sink data flow (no sanitization boundary)")

    # Check successors for additional surfaces
    for _, target, data in graph.out_edges(node_id, data=True):
        target_data = graph.nodes.get(target, {})
        if target_data.get("type") == "privilege":
            pt = target_data.get("priv_type", "")
            if f"{pt}" not in " ".join(surfaces):
                surfaces.append(f"Transitive access to {pt} operations")

    return surfaces if surfaces else ["General code execution surface"]


def _generate_attack_approach(node_data: dict, surfaces: List[str]) -> str:
    """Generate a suggested attack approach description."""
    priv_ops = node_data.get("privilege_ops", [])
    priv_types = {op.get("type", "") for op in priv_ops}
    name = node_data.get("name", "target")

    if "SHELL" in priv_types:
        return (f"Inject malicious payload through '{name}' parameters to achieve "
                f"remote command execution. The function passes user input directly "
                f"to shell execution without sanitization.")
    elif "DATABASE" in priv_types:
        return (f"Craft SQL injection payload targeting '{name}'. Raw string "
                f"formatting in queries allows full database compromise including "
                f"data exfiltration and privilege escalation.")
    elif "AUTH" in priv_types and "DATABASE" in priv_types:
        return (f"Exploit authentication flow in '{name}' using SQL injection "
                f"to bypass login, then escalate via hardcoded credentials "
                f"found in the authentication module.")
    elif "AUTH" in priv_types:
        return (f"Target authentication mechanism in '{name}' — exploit weak "
                f"credential handling, hardcoded secrets, or missing brute force "
                f"protection to gain unauthorized access.")
    elif "FILE_IO" in priv_types:
        return (f"Exploit path traversal in '{name}' to read arbitrary files "
                f"from the server filesystem, potentially accessing credentials, "
                f"configuration, or source code.")
    else:
        return (f"Compromise '{name}' to establish persistent access to "
                f"privileged operations: {', '.join(surfaces[:2])}.")


def detect_feeding_points(infiltration_graph: InfiltrationGraph,
                          parsed_files=None, top_n: int = 5) -> List[FeedingPoint]:
    """Analyze the infiltration graph to find the most dangerous feeding points."""
    console.print("[bold magenta]🎯 Analyzing feeding points...[/]")

    graph = infiltration_graph.graph
    candidates = []

    # Pre-compute betweenness centrality ONCE for the entire graph
    # Use approximate centrality for large graphs (>500 nodes)
    num_nodes = graph.number_of_nodes()
    console.print(f"[dim]  Computing centrality for {num_nodes} nodes...[/]")
    try:
        if num_nodes > 500:
            # Approximate betweenness — sample k nodes instead of all
            centrality = nx.betweenness_centrality(graph, k=min(100, num_nodes))
        else:
            centrality = nx.betweenness_centrality(graph)
    except Exception:
        centrality = {}

    # Pre-compute shortest paths from file nodes (limited to first 10)
    file_nodes_sample = infiltration_graph.file_nodes[:10]
    depth_cache: Dict[str, int] = {}
    console.print(f"[dim]  Computing dependency depths...[/]")
    for source in file_nodes_sample:
        try:
            lengths = nx.single_source_shortest_path_length(graph, source, cutoff=8)
            for node_id, length in lengths.items():
                depth_cache[node_id] = max(depth_cache.get(node_id, 0), length)
        except nx.NetworkXError:
            pass

    # Only analyze function nodes
    for node_id in infiltration_graph.function_nodes:
        node_data = graph.nodes.get(node_id, {})
        if node_data.get("type") != "function":
            continue

        # Get raw code for protection analysis
        raw_code = ""
        if parsed_files:
            raw_code = _get_function_code(graph, node_id, parsed_files)

        # Calculate component scores
        fan_in = _calculate_fan_in(graph, node_id)
        priv_level = _calculate_privilege_level(graph, node_id)
        protection_count = _detect_protection_level(graph, node_id, raw_code)

        # Use pre-computed centrality
        node_centrality = centrality.get(node_id, 0)

        # Use pre-computed depth
        max_depth = depth_cache.get(node_id, 0)

        # === SCORING ===
        # Blast Radius (0-10): fan_in × privilege_level
        blast_raw = (fan_in + 1) * (priv_level + 1)
        blast_score = min(10.0, blast_raw / 5.0)

        # Stealth (0-10): inverse of protection patterns
        stealth_score = min(10.0, max(0.0, 10.0 - (protection_count * 2.5)))

        # Persistence (0-10): centrality × dependency depth
        persist_raw = (node_centrality * 100 + 1) * (max_depth + 1)
        persistence_score = min(10.0, persist_raw / 3.0)

        # Boost scores for nodes that are both sources and sinks
        if node_data.get("is_input_source") and node_data.get("is_dangerous_sink"):
            blast_score = min(10.0, blast_score * 1.5)
            stealth_score = min(10.0, stealth_score * 1.2)

        final_score = (blast_score * 0.4) + (stealth_score * 0.4) + (persistence_score * 0.2)

        if final_score < 1.0 and priv_level == 0:
            continue

        # Determine danger level
        if final_score >= 7.0:
            danger_level = "CRITICAL"
        elif final_score >= 4.5:
            danger_level = "HIGH"
        else:
            danger_level = "MEDIUM"

        # Generate analysis
        explanation = _generate_explanation(node_id, node_data, blast_score,
                                           stealth_score, persistence_score, graph)
        attack_surfaces = _generate_attack_surfaces(node_id, node_data, graph)
        attack_approach = _generate_attack_approach(node_data, attack_surfaces)

        file_path = node_data.get("file", "")
        line = node_data.get("line_start", 0)

        candidates.append(FeedingPoint(
            node_id=node_id,
            name=node_data.get("name", node_id),
            file=file_path,
            line=line,
            blast_radius_score=round(blast_score, 2),
            stealth_score=round(stealth_score, 2),
            persistence_score=round(persistence_score, 2),
            final_score=round(final_score, 2),
            danger_level=danger_level,
            explanation=explanation,
            attack_surfaces=attack_surfaces,
            attack_approach=attack_approach,
        ))

    # Sort by final score descending and take top N
    candidates.sort(key=lambda fp: fp.final_score, reverse=True)
    top_points = candidates[:top_n]

    for fp in top_points:
        color = {"CRITICAL": "bold red", "HIGH": "bold yellow", "MEDIUM": "bold cyan"}.get(fp.danger_level, "white")
        console.print(f"[{color}]☠️  FEEDING POINT DETECTED: {fp.name} — Score: {fp.final_score} — {fp.danger_level}[/]")

    return top_points

