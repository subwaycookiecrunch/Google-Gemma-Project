"""
PARASITE EVOLVED — Multi-language AST Parser
Uses Tree-sitter to extract functions, classes, imports, and privilege operations.
"""

import os
import re
from dataclasses import dataclass, field
from typing import List, Optional
from functools import lru_cache
from rich.console import Console
from tree_sitter_languages import get_language, get_parser

console = Console()

SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
}

PRIVILEGE_PATTERNS = {
    "NETWORK": [
        r"requests\.(get|post|put|delete|patch|head)",
        r"urllib\.request",
        r"http\.client",
        r"socket\.",
        r"fetch\(",
        r"axios\.",
        r"HttpClient",
        r"net\.Dial",
        r"http\.Get",
        r"http\.Post",
    ],
    "FILE_IO": [
        r"open\(",
        r"\.read\(",
        r"\.write\(",
        r"\.readlines\(",
        r"os\.path",
        r"os\.makedirs",
        r"os\.remove",
        r"shutil\.",
        r"pathlib\.",
        r"fs\.",
        r"readFile",
        r"writeFile",
        r"os\.Create",
        r"os\.Open",
        r"ioutil\.",
    ],
    "DATABASE": [
        r"\.execute\(",
        r"\.executemany\(",
        r"\.executescript\(",
        r"cursor\.",
        r"\.query\(",
        r"\.fetchone\(",
        r"\.fetchall\(",
        r"sqlite3\.",
        r"psycopg2\.",
        r"mysql\.",
        r"mongoose\.",
        r"sequelize\.",
        r"sql\.Open",
        r"\.Raw\(",
    ],
    "ENV": [
        r"os\.environ",
        r"os\.getenv",
        r"process\.env",
        r"dotenv",
        r"os\.Getenv",
    ],
    "SHELL": [
        r"subprocess\.",
        r"os\.system\(",
        r"os\.popen\(",
        r"exec\(",
        r"eval\(",
        r"child_process",
        r"exec\.Command",
        r"Runtime\.getRuntime\(\)\.exec",
        r"ProcessBuilder",
    ],
    "AUTH": [
        r"login",
        r"authenticate",
        r"jwt\.",
        r"token",
        r"session",
        r"password",
        r"credential",
        r"hashlib\.",
        r"bcrypt\.",
        r"hmac\.",
        r"api_key",
        r"secret",
    ],
}

RISK_LEVELS = {
    "SHELL": "CRITICAL",
    "DATABASE": "HIGH",
    "AUTH": "HIGH",
    "FILE_IO": "MEDIUM",
    "NETWORK": "MEDIUM",
    "ENV": "MEDIUM",
}

SENSITIVE_DATA_PATTERNS = [
    r"password\s*=",
    r"secret\s*=",
    r"api_key\s*=",
    r"token\s*=",
    r"credential",
    r"DB_PASSWORD",
    r"JWT_SECRET",
    r"ADMIN_PASSWORD",
    r"SYSTEM_API_KEY",
    r"private_key",
]


@dataclass
class PrivilegeOp:
    type: str
    line: int
    code_snippet: str
    risk_level: str


@dataclass
class ParsedFunction:
    name: str
    file: str
    line_start: int
    line_end: int
    parameters: List[str]
    calls: List[str]
    privilege_operations: List[PrivilegeOp]
    raw_code: str


@dataclass
class ParsedFile:
    path: str
    language: str
    functions: List[ParsedFunction]
    imports: List[str]
    raw_content: str
    classes: List[str] = field(default_factory=list)
    sensitive_assignments: List[dict] = field(default_factory=list)


def _detect_privilege_ops(code: str, start_line: int) -> List[PrivilegeOp]:
    """Scan code string for privilege operation patterns."""
    ops = []
    lines = code.split("\n")
    for i, line in enumerate(lines):
        for op_type, patterns in PRIVILEGE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    ops.append(PrivilegeOp(
                        type=op_type,
                        line=start_line + i,
                        code_snippet=line.strip(),
                        risk_level=RISK_LEVELS.get(op_type, "LOW"),
                    ))
                    break
    return ops


def _detect_sensitive_assignments(content: str) -> List[dict]:
    """Find variable assignments involving sensitive data."""
    results = []
    for i, line in enumerate(content.split("\n"), 1):
        for pattern in SENSITIVE_DATA_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                results.append({"line": i, "code": line.strip(), "pattern": pattern})
                break
    return results


def _extract_calls_from_code(code: str) -> List[str]:
    """Extract function/method call names from code using regex."""
    call_pattern = re.compile(r'(?:^|[^"\'])([a-zA-Z_][\w.]*)\s*\(', re.MULTILINE)
    matches = call_pattern.findall(code)
    keywords = {"if", "for", "while", "return", "print", "elif", "except", "with", "def", "class", "assert", "raise", "import", "from", "not", "and", "or", "in", "is"}
    return [m for m in matches if m not in keywords and not m.startswith("__")]


def _get_node_text(node, source_bytes: bytes) -> str:
    """Extract text from a tree-sitter node."""
    return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _parse_python(tree, source_bytes: bytes, filepath: str) -> ParsedFile:
    """Parse Python source using tree-sitter AST."""
    root = tree.root_node
    content = source_bytes.decode("utf-8", errors="replace")
    functions = []
    imports = []
    classes = []

    def walk(node):
        if node.type == "import_statement" or node.type == "import_from_statement":
            imports.append(_get_node_text(node, source_bytes))

        elif node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                classes.append(_get_node_text(name_node, source_bytes))
            for child in node.children:
                walk(child)

        elif node.type == "function_definition" or node.type == "decorated_definition":
            func_node = node
            if node.type == "decorated_definition":
                for c in node.children:
                    if c.type == "function_definition":
                        func_node = c
                        break

            name_node = func_node.child_by_field_name("name")
            if not name_node:
                return

            name = _get_node_text(name_node, source_bytes)
            params_node = func_node.child_by_field_name("parameters")
            params = []
            if params_node:
                for p in params_node.children:
                    if p.type in ("identifier", "typed_parameter", "default_parameter", "typed_default_parameter"):
                        param_text = _get_node_text(p, source_bytes)
                        if param_text not in ("(", ")", ",", "self", "cls"):
                            params.append(param_text.split(":")[0].split("=")[0].strip())

            raw_code = _get_node_text(node, source_bytes)
            line_start = node.start_point[0] + 1
            line_end = node.end_point[0] + 1
            calls = _extract_calls_from_code(raw_code)
            priv_ops = _detect_privilege_ops(raw_code, line_start)

            functions.append(ParsedFunction(
                name=name, file=filepath,
                line_start=line_start, line_end=line_end,
                parameters=params, calls=calls,
                privilege_operations=priv_ops, raw_code=raw_code,
            ))
        else:
            for child in node.children:
                walk(child)

    walk(root)
    sensitive = _detect_sensitive_assignments(content)

    return ParsedFile(
        path=filepath, language="python", functions=functions,
        imports=imports, raw_content=content, classes=classes,
        sensitive_assignments=sensitive,
    )


def _parse_javascript(tree, source_bytes: bytes, filepath: str, lang_name: str) -> ParsedFile:
    """Parse JavaScript/TypeScript source using tree-sitter AST."""
    root = tree.root_node
    content = source_bytes.decode("utf-8", errors="replace")
    functions = []
    imports = []
    classes = []

    def walk(node):
        if node.type in ("import_statement", "import_declaration"):
            imports.append(_get_node_text(node, source_bytes))

        elif node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                classes.append(_get_node_text(name_node, source_bytes))
            for child in node.children:
                walk(child)

        elif node.type in ("function_declaration", "method_definition",
                           "arrow_function", "function"):
            name = ""
            if node.type == "function_declaration":
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = _get_node_text(name_node, source_bytes)
            elif node.type == "method_definition":
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = _get_node_text(name_node, source_bytes)
            elif node.type == "arrow_function" and node.parent:
                if node.parent.type == "variable_declarator":
                    name_node = node.parent.child_by_field_name("name")
                    if name_node:
                        name = _get_node_text(name_node, source_bytes)

            if not name:
                name = f"anonymous_{node.start_point[0]}"

            params_node = node.child_by_field_name("parameters")
            params = []
            if params_node:
                for p in params_node.children:
                    if p.type in ("identifier", "required_parameter", "optional_parameter"):
                        pt = _get_node_text(p, source_bytes)
                        if pt not in ("(", ")", ","):
                            params.append(pt.split(":")[0].split("=")[0].strip())

            raw_code = _get_node_text(node, source_bytes)
            calls = _extract_calls_from_code(raw_code)
            line_start = node.start_point[0] + 1
            line_end = node.end_point[0] + 1
            priv_ops = _detect_privilege_ops(raw_code, line_start)

            functions.append(ParsedFunction(
                name=name, file=filepath,
                line_start=line_start, line_end=line_end,
                parameters=params, calls=calls,
                privilege_operations=priv_ops, raw_code=raw_code,
            ))
        else:
            for child in node.children:
                walk(child)

    walk(root)
    sensitive = _detect_sensitive_assignments(content)

    return ParsedFile(
        path=filepath, language=lang_name, functions=functions,
        imports=imports, raw_content=content, classes=classes,
        sensitive_assignments=sensitive,
    )


def _parse_java(tree, source_bytes: bytes, filepath: str) -> ParsedFile:
    """Parse Java source using tree-sitter AST."""
    root = tree.root_node
    content = source_bytes.decode("utf-8", errors="replace")
    functions = []
    imports = []
    classes = []

    def walk(node):
        if node.type == "import_declaration":
            imports.append(_get_node_text(node, source_bytes))
        elif node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                classes.append(_get_node_text(name_node, source_bytes))
            for child in node.children:
                walk(child)
        elif node.type == "method_declaration":
            name_node = node.child_by_field_name("name")
            if not name_node:
                return
            name = _get_node_text(name_node, source_bytes)
            params_node = node.child_by_field_name("parameters")
            params = []
            if params_node:
                for p in params_node.children:
                    if p.type == "formal_parameter":
                        pname = p.child_by_field_name("name")
                        if pname:
                            params.append(_get_node_text(pname, source_bytes))

            raw_code = _get_node_text(node, source_bytes)
            calls = _extract_calls_from_code(raw_code)
            line_start = node.start_point[0] + 1
            line_end = node.end_point[0] + 1
            priv_ops = _detect_privilege_ops(raw_code, line_start)
            functions.append(ParsedFunction(
                name=name, file=filepath,
                line_start=line_start, line_end=line_end,
                parameters=params, calls=calls,
                privilege_operations=priv_ops, raw_code=raw_code,
            ))
        else:
            for child in node.children:
                walk(child)

    walk(root)
    sensitive = _detect_sensitive_assignments(content)
    return ParsedFile(
        path=filepath, language="java", functions=functions,
        imports=imports, raw_content=content, classes=classes,
        sensitive_assignments=sensitive,
    )


def _parse_go(tree, source_bytes: bytes, filepath: str) -> ParsedFile:
    """Parse Go source using tree-sitter AST."""
    root = tree.root_node
    content = source_bytes.decode("utf-8", errors="replace")
    functions = []
    imports = []
    classes = []

    def walk(node):
        if node.type == "import_declaration":
            imports.append(_get_node_text(node, source_bytes))
        elif node.type in ("function_declaration", "method_declaration"):
            name_node = node.child_by_field_name("name")
            if not name_node:
                return
            name = _get_node_text(name_node, source_bytes)
            params_node = node.child_by_field_name("parameters")
            params = []
            if params_node:
                for p in params_node.children:
                    if p.type == "parameter_declaration":
                        for c in p.children:
                            if c.type == "identifier":
                                params.append(_get_node_text(c, source_bytes))
                                break

            raw_code = _get_node_text(node, source_bytes)
            calls = _extract_calls_from_code(raw_code)
            line_start = node.start_point[0] + 1
            line_end = node.end_point[0] + 1
            priv_ops = _detect_privilege_ops(raw_code, line_start)
            functions.append(ParsedFunction(
                name=name, file=filepath,
                line_start=line_start, line_end=line_end,
                parameters=params, calls=calls,
                privilege_operations=priv_ops, raw_code=raw_code,
            ))
        else:
            for child in node.children:
                walk(child)

    walk(root)
    sensitive = _detect_sensitive_assignments(content)
    return ParsedFile(
        path=filepath, language="go", functions=functions,
        imports=imports, raw_content=content, classes=classes,
        sensitive_assignments=sensitive,
    )


def parse_file(filepath: str) -> Optional[ParsedFile]:
    """Parse a single source file and extract all code structures."""
    ext = os.path.splitext(filepath)[1].lower()
    lang_name = SUPPORTED_EXTENSIONS.get(ext)
    if not lang_name:
        return None

    try:
        with open(filepath, "rb") as f:
            source_bytes = f.read()
    except (IOError, OSError):
        return None

    try:
        language = get_language(lang_name)
        parser = get_parser(lang_name)
        tree = parser.parse(source_bytes)
    except Exception:
        return None

    if lang_name == "python":
        return _parse_python(tree, source_bytes, filepath)
    elif lang_name in ("javascript", "typescript"):
        return _parse_javascript(tree, source_bytes, filepath, lang_name)
    elif lang_name == "java":
        return _parse_java(tree, source_bytes, filepath)
    elif lang_name == "go":
        return _parse_go(tree, source_bytes, filepath)

    return None


MAX_FILES = 200  # Smart cap for large repos


def parse_repository(repo_path: str, session_id: str = None) -> List[ParsedFile]:
    """Walk repository directory and parse all supported source files.
    
    For large repos (>MAX_FILES files), performs a two-pass scan:
    1. Quick scan to identify high-value files (with privilege ops)
    2. Deep parse of prioritized files up to MAX_FILES
    """
    from backend.core.progress import progress_store

    parsed_files = []
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv",
                 "env", ".env", "dist", "build", ".tox", ".mypy_cache",
                 ".gradle", ".mvn", "target", ".idea", ".settings",
                 "test", "tests", "vendor", "third_party", "examples"}

    # Discover all source files
    all_files = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                all_files.append(os.path.join(root, fname))

    total_discovered = len(all_files)
    console.print(f"[bold green]🔬 Scanning host repository... {total_discovered} source files detected[/]")

    # Initialize progress
    if session_id:
        progress_store.update(session_id,
                              phase="DISCOVERING",
                              total_files=min(total_discovered, MAX_FILES))

    # Smart file selection for large repos
    if total_discovered > MAX_FILES:
        console.print(f"[bold yellow]⚡ Large repository detected ({total_discovered} files). "
                      f"Prioritizing {MAX_FILES} highest-value files.[/]")
        
        if session_id:
            progress_store.update(session_id, phase="PRIORITIZING")

        # Quick scan: score files by potential interest (size, privilege-keyword density)
        scored_files = []
        privilege_keywords = [
            "exec", "system", "password", "secret", "token", "auth", "admin",
            "query", "execute", "socket", "Runtime", "ProcessBuilder", "credential",
            "session", "cookie", "encrypt", "decrypt", "hash", "key", "cert",
            "inject", "command", "shell", "eval", "deserializ", "serialize",
            "upload", "download", "file", "path", "sql", "database",
        ]

        for fpath in all_files:
            try:
                with open(fpath, "r", errors="replace") as f:
                    content = f.read(8192)  # Read first 8KB only for scoring
                score = sum(1 for kw in privilege_keywords if kw.lower() in content.lower())
                file_size = os.path.getsize(fpath)
                # Penalize very large files (likely generated), boost medium files
                size_factor = 1.0 if file_size < 50000 else 0.5 if file_size < 200000 else 0.2
                scored_files.append((fpath, score * size_factor))
            except Exception:
                scored_files.append((fpath, 0))

        # Sort by score (highest first), take top MAX_FILES
        scored_files.sort(key=lambda x: x[1], reverse=True)
        all_files = [f[0] for f in scored_files[:MAX_FILES]]
        console.print(f"[bold green]🎯 Selected {len(all_files)} priority files for deep analysis[/]")

    total_to_parse = len(all_files)
    if session_id:
        progress_store.update(session_id,
                              phase="PARSING",
                              total_files=total_to_parse)

    for i, fpath in enumerate(sorted(all_files)):
        rel_path = os.path.relpath(fpath, repo_path)
        
        # Update progress
        if session_id:
            progress_store.update(session_id,
                                  files_scanned=i,
                                  current_file=rel_path)

        result = parse_file(fpath)
        if result:
            func_count = len(result.functions)
            priv_count = sum(len(fn.privilege_operations) for fn in result.functions)
            
            if session_id:
                current = progress_store.get(session_id)
                if current:
                    progress_store.update(session_id,
                                          functions_found=current.functions_found + func_count,
                                          privilege_ops_found=current.privilege_ops_found + priv_count)

            # Only log every 10th file for large repos to avoid spam
            if total_to_parse <= 50 or i % 10 == 0 or priv_count > 0:
                console.print(f"[cyan]🧬 [{i+1}/{total_to_parse}] {rel_path} — "
                              f"{func_count} functions, {priv_count} priv ops[/]")

            parsed_files.append(result)

    if session_id:
        progress_store.update(session_id,
                              files_scanned=total_to_parse,
                              phase="BUILDING_GRAPH")

    return parsed_files

