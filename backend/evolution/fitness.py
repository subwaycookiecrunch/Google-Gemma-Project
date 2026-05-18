"""
PARASITE EVOLVED — Fitness Scoring Engine
Evaluates strain mutations across stealth, blast radius, and persistence dimensions.
"""

import re
from dataclasses import dataclass
from rich.console import Console

console = Console()

SUSPICIOUS_KEYWORDS = [
    "hack", "exploit", "malware", "backdoor", "payload", "trojan",
    "keylogger", "rootkit", "reverse_shell", "bind_shell", "shellcode",
    "ransomware", "cryptominer", "botnet", "c2_server", "exfil",
]

CAMOUFLAGE_INDICATORS = [
    r"def\s+\w+\(",              # proper function definitions
    r"\"\"\".*?\"\"\"",           # docstrings present
    r"#\s+\w+",                  # inline comments
    r"try:\s*\n\s+",             # error handling
    r"logging\.\w+\(",           # uses logging
    r"return\s+",                # has return statements
    r"if\s+.*?:",                # conditional logic
]

BLAST_MULTIPLIERS = {
    "SHELL": 10,
    "DATABASE": 8,
    "AUTH": 8,
    "FILE_IO": 5,
    "NETWORK": 5,
    "ENV": 4,
}

DAMAGE_LEVELS = {
    (0, 3): "DATA_LOSS",
    (3, 6): "OUTAGE",
    (6, 8): "BREACH",
    (8, 11): "COMPLETE_COMPROMISE",
}


@dataclass
class FitnessResult:
    stealth: float
    blast_radius: float
    persistence: float
    combined: float
    verdict: str
    reasoning: str
    damage_estimate: str


def _score_stealth(code: str, surrounding_code: str = "") -> tuple:
    """Evaluate how well generated code blends with existing codebase."""
    score = 0.0
    reasons = []

    # Check code style matching (+3)
    style_matches = 0
    for pattern in CAMOUFLAGE_INDICATORS:
        if re.search(pattern, code, re.DOTALL):
            style_matches += 1
    style_score = min(3.0, (style_matches / max(len(CAMOUFLAGE_INDICATORS), 1)) * 4.5)
    score += style_score
    if style_score >= 2.0:
        reasons.append("Code style matches surrounding patterns")
    else:
        reasons.append("Code style diverges from host patterns")

    # Check variable names non-suspicious (+2)
    var_pattern = re.compile(r'\b([a-z_][a-z0-9_]*)\s*=', re.IGNORECASE)
    variables = var_pattern.findall(code)
    suspicious_vars = [v for v in variables if any(k in v.lower() for k in ["hack", "exploit", "evil", "malicious", "backdoor", "payload"])]
    var_score = 2.0 if not suspicious_vars else max(0.0, 2.0 - len(suspicious_vars) * 0.5)
    score += var_score
    if var_score >= 1.5:
        reasons.append("Variable naming appears benign")
    else:
        reasons.append(f"Suspicious variable names detected: {suspicious_vars[:3]}")

    # No obvious malicious keywords (+2)
    keyword_hits = [k for k in SUSPICIOUS_KEYWORDS if k in code.lower()]
    keyword_score = 2.0 if not keyword_hits else max(0.0, 2.0 - len(keyword_hits) * 0.4)
    score += keyword_score
    if keyword_score >= 1.5:
        reasons.append("No suspicious keywords detected")
    else:
        reasons.append(f"Malicious keyword patterns found: {keyword_hits[:3]}")

    # Mutation blends with existing patterns (+3)
    if surrounding_code:
        # Check indentation style match
        code_indent = "    " if "    " in code else "\t"
        surr_indent = "    " if "    " in surrounding_code else "\t"
        indent_match = code_indent == surr_indent

        # Check comment style
        code_has_docs = '"""' in code or "'''" in code
        surr_has_docs = '"""' in surrounding_code or "'''" in surrounding_code
        doc_match = code_has_docs == surr_has_docs

        blend_score = 0.0
        if indent_match:
            blend_score += 1.5
        if doc_match:
            blend_score += 1.5
        score += blend_score
        if blend_score >= 2.0:
            reasons.append("Mutation integrates seamlessly with host code")
        else:
            reasons.append("Mutation shows stylistic divergence from host")
    else:
        score += 1.5
        reasons.append("No surrounding context for blend analysis")

    return min(10.0, score), reasons


def _score_blast_radius(strain, feeding_point) -> tuple:
    """Evaluate potential damage of a successful attack via this strain."""
    score = 0.0
    reasons = []

    # Privilege level from feeding point
    priv_ops = getattr(feeding_point, "attack_surfaces", [])
    priv_weight = 0
    for surface in priv_ops:
        for priv_type, mult in BLAST_MULTIPLIERS.items():
            if priv_type.lower().replace("_", " ") in surface.lower() or priv_type.lower() in surface.lower():
                priv_weight = max(priv_weight, mult)

    # Scale privilege to 0-4 range
    priv_score = min(4.0, priv_weight * 0.5)
    score += priv_score

    # Feeding point's own blast radius
    fp_blast = getattr(feeding_point, "blast_radius_score", 5.0)
    inherited = min(3.0, fp_blast * 0.3)
    score += inherited
    reasons.append(f"Inherited blast from feeding point: {fp_blast:.1f}")

    # Number of attack surfaces
    surface_count = len(priv_ops)
    surface_score = min(3.0, surface_count * 0.4)
    score += surface_score
    reasons.append(f"{surface_count} attack surfaces exposed")

    # Determine damage estimate
    damage = "DATA_LOSS"
    for (lo, hi), level in DAMAGE_LEVELS.items():
        if lo <= score < hi:
            damage = level
            break
    if score >= 8:
        damage = "COMPLETE_COMPROMISE"

    reasons.append(f"Estimated damage: {damage}")
    return min(10.0, score), reasons, damage


def _score_persistence(strain, feeding_point) -> tuple:
    """Evaluate how resistant this strain is to detection and removal."""
    score = 0.0
    reasons = []

    # Call graph depth from feeding point persistence score
    fp_persist = getattr(feeding_point, "persistence_score", 3.0)
    depth_score = min(3.0, fp_persist * 0.4)
    score += depth_score
    reasons.append(f"Graph depth factor: {depth_score:.1f}")

    # Mutation generation — more evolved = more persistent
    gen = getattr(strain, "generation", 0)
    gen_score = min(2.0, gen * 0.8)
    score += gen_score
    reasons.append(f"Generation {gen} evolutionary hardening")

    # Surviving previous mutations shows resilience
    history = getattr(strain, "mutation_history", [])
    survived = sum(1 for m in history if m.survived)
    survival_score = min(2.5, survived * 1.0)
    score += survival_score
    if survived > 0:
        reasons.append(f"Survived {survived} previous selection cycles")

    # Code review resistance — check for obfuscation patterns
    code = getattr(strain, "camouflage_code", "")
    if code:
        has_docstring = '"""' in code or "'''" in code
        has_comments = "#" in code
        has_error_handling = "try:" in code or "except" in code
        review_score = 0.0
        if has_docstring:
            review_score += 1.0
        if has_comments:
            review_score += 0.5
        if has_error_handling:
            review_score += 1.0
        score += min(2.5, review_score)
        if review_score >= 1.5:
            reasons.append("Passes basic code review patterns")
        else:
            reasons.append("Vulnerable to code review detection")
    else:
        score += 1.0

    return min(10.0, score), reasons


def calculate_fitness(strain, mutation_code: str = "", surrounding_code: str = "") -> FitnessResult:
    """Calculate combined fitness score for a strain after mutation."""
    feeding_point = strain.target_feeding_point
    code = mutation_code or strain.camouflage_code

    stealth, stealth_reasons = _score_stealth(code, surrounding_code)
    blast, blast_reasons, damage = _score_blast_radius(strain, feeding_point)
    persist, persist_reasons = _score_persistence(strain, feeding_point)

    combined = (stealth * 0.4 + blast * 0.4 + persist * 0.2) / 10.0

    if combined < 0.3:
        verdict = "TERMINATED"
    elif combined < 0.6:
        verdict = "ALIVE"
    elif combined < 0.8:
        verdict = "STRONG"
    else:
        verdict = "DOMINANT"

    all_reasons = stealth_reasons + blast_reasons + persist_reasons
    reasoning = " | ".join(all_reasons)

    return FitnessResult(
        stealth=round(stealth, 2),
        blast_radius=round(blast, 2),
        persistence=round(persist, 2),
        combined=round(combined, 4),
        verdict=verdict,
        reasoning=reasoning,
        damage_estimate=damage,
    )
