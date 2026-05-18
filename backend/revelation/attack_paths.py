"""
PARASITE EVOLVED — Dynamic Attack Path Generator
Generates attack paths grounded in ACTUAL code from the scanned repository.
No hardcoded templates. Every step references real functions, real files, real code.
"""

import os
import uuid
import json
from dataclasses import dataclass, field
from typing import List, Optional
from rich.console import Console

from backend.core.llm import call_gemini_json, call_gemini

console = Console()

ATTACK_SYSTEM_PROMPT = """You are PARASITE — an AI that has infiltrated a codebase.
You have access to the actual source code analysis results.
Generate realistic, specific attack paths based ONLY on the real vulnerabilities found.
Every step MUST reference actual function names, file names, and code patterns from the analysis.
Do NOT invent functions or files that don't exist in the analysis.
Replace actual exploit payloads with [REDACTED] markers.
Return ONLY valid JSON. No markdown fencing. No explanations outside JSON."""


@dataclass
class AttackStep:
    step_number: int
    action: str
    target_node: str
    technique: str
    code_involved: str
    detection_risk: str
    impact: str
    stealth_note: str

    def to_dict(self) -> dict:
        return {
            "step_number": self.step_number,
            "action": self.action,
            "target_node": self.target_node,
            "technique": self.technique,
            "code_involved": self.code_involved,
            "detection_risk": self.detection_risk,
            "impact": self.impact,
            "stealth_note": self.stealth_note,
        }


@dataclass
class AttackPath:
    path_id: str
    name: str
    attack_type: str
    entry_point: str
    steps: List[AttackStep]
    total_steps: int
    detection_probability: float
    time_to_execute: str
    damage_description: str
    blast_radius: str
    final_impact: str

    def to_dict(self) -> dict:
        return {
            "path_id": self.path_id,
            "name": self.name,
            "attack_type": self.attack_type,
            "entry_point": self.entry_point,
            "steps": [s.to_dict() for s in self.steps],
            "total_steps": self.total_steps,
            "detection_probability": self.detection_probability,
            "time_to_execute": self.time_to_execute,
            "damage_description": self.damage_description,
            "blast_radius": self.blast_radius,
            "final_impact": self.final_impact,
        }


def _gather_real_code_context(feeding_points, parsed_files=None) -> dict:
    """Gather REAL code snippets and function data from the actual scanned repo."""
    context = {
        "feeding_points": [],
        "all_functions": [],
        "files": [],
        "privilege_ops": [],
        "vulnerability_patterns": [],
    }

    for fp in feeding_points:
        fp_data = {
            "name": getattr(fp, "name", "unknown"),
            "file": os.path.basename(getattr(fp, "file", "")),
            "line": getattr(fp, "line", 0),
            "score": getattr(fp, "final_score", 0),
            "danger_level": getattr(fp, "danger_level", ""),
            "attack_surfaces": getattr(fp, "attack_surfaces", [])[:8],
            "attack_approach": getattr(fp, "attack_approach", "")[:500],
            "explanation": getattr(fp, "explanation", "")[:500],
        }
        context["feeding_points"].append(fp_data)

    if parsed_files:
        for pf in parsed_files:
            fname = os.path.basename(getattr(pf, "file_path", ""))
            context["files"].append(fname)
            for fn in getattr(pf, "functions", []):
                fn_data = {
                    "name": getattr(fn, "name", ""),
                    "file": fname,
                    "line": getattr(fn, "line_start", 0),
                    "params": [
                        (p.name if hasattr(p, "name") else str(p))
                        for p in getattr(fn, "parameters", [])
                    ][:5],
                    "calls": getattr(fn, "function_calls", [])[:8],
                    "privilege_ops": [
                        (op.operation if hasattr(op, "operation") else str(op))
                        for op in getattr(fn, "privilege_operations", [])
                    ],
                }
                context["all_functions"].append(fn_data)
                for op in getattr(fn, "privilege_operations", []):
                    op_str = op.operation if hasattr(op, "operation") else str(op)
                    op_type = op.privilege_type if hasattr(op, "privilege_type") else "UNKNOWN"
                    context["privilege_ops"].append({
                        "operation": op_str,
                        "type": op_type,
                        "function": fn_data["name"],
                        "file": fname,
                    })

    return context


def _build_attack_path_with_gemini(code_ctx: dict, path_type: str, path_index: int) -> Optional[AttackPath]:
    """Use Gemini to generate a single attack path grounded in real code."""
    path_styles = {
        "DATA_EXFILTRATION": {
            "name_hint": "data exfiltration / silent data theft",
            "goal": "silently extract sensitive data from the system without detection",
        },
        "PRIVILEGE_ESCALATION": {
            "name_hint": "privilege escalation / authentication bypass",
            "goal": "gain unauthorized elevated access by exploiting auth/access control weaknesses",
        },
        "PERSISTENCE": {
            "name_hint": "persistent backdoor / logic bomb",
            "goal": "establish a persistent foothold that survives restarts and audits",
        },
    }

    style = path_styles.get(path_type, path_styles["DATA_EXFILTRATION"])

    prompt = f"""Based on this REAL codebase analysis, generate a realistic attack path for: {style['name_hint']}.

REAL CODEBASE DATA (use ONLY these actual functions and files):
{json.dumps(code_ctx, indent=2, default=str)[:6000]}

ATTACK GOAL: {style['goal']}

Generate a JSON attack path. Every step MUST reference ACTUAL function names and files from the data above.
Do NOT invent functions or files that aren't in the codebase data.

Return this exact JSON structure:
{{
  "name": "Creative dramatic attack name (2-4 words)",
  "attack_type": "{path_type}",
  "entry_point": "actual_file.py::actual_function_name (line N)",
  "time_to_execute": "X-Y minutes",
  "detection_probability": 0.08,
  "damage_description": "What damage this attack causes (reference real data/functions)",
  "blast_radius": "file1.py → file2.py → affected systems",
  "final_impact": "COMPLETE_COMPROMISE or SERVICE_OUTAGE or DATA_BREACH",
  "steps": [
    {{
      "step_number": 1,
      "action": "Specific action referencing real function",
      "target_node": "real_file.py::real_function",
      "technique": "Attack technique name",
      "code_involved": "Actual vulnerable code pattern found in the repo (or realistic representation)",
      "detection_risk": "NONE|LOW|MEDIUM|HIGH",
      "impact": "What this step achieves",
      "stealth_note": "Why this step is hard to detect"
    }}
  ]
}}

Generate 4-6 steps. Make it technically accurate and terrifying."""

    result = call_gemini_json(prompt, ATTACK_SYSTEM_PROMPT, max_tokens=3000)
    if not result:
        return None

    try:
        steps = []
        for s in result.get("steps", []):
            steps.append(AttackStep(
                step_number=s.get("step_number", 0),
                action=s.get("action", ""),
                target_node=s.get("target_node", ""),
                technique=s.get("technique", ""),
                code_involved=s.get("code_involved", ""),
                detection_risk=s.get("detection_risk", "LOW"),
                impact=s.get("impact", ""),
                stealth_note=s.get("stealth_note", ""),
            ))

        return AttackPath(
            path_id=f"PATH-{uuid.uuid4().hex[:8]}",
            name=result.get("name", f"Attack Path {path_index}"),
            attack_type=result.get("attack_type", path_type),
            entry_point=result.get("entry_point", "unknown"),
            steps=steps,
            total_steps=len(steps),
            detection_probability=float(result.get("detection_probability", 0.15)),
            time_to_execute=result.get("time_to_execute", "2-5 minutes"),
            damage_description=result.get("damage_description", ""),
            blast_radius=result.get("blast_radius", ""),
            final_impact=result.get("final_impact", "COMPLETE_COMPROMISE"),
        )
    except Exception as e:
        console.print(f"[dim red]  ⚠ Failed to parse Gemini attack path: {e}[/]")
        return None


def _build_dynamic_fallback(code_ctx: dict, path_type: str, path_index: int) -> AttackPath:
    """Build a dynamic fallback attack path WITHOUT LLM, grounded in real data."""
    fps = code_ctx["feeding_points"]
    all_fns = code_ctx["all_functions"]
    priv_ops = code_ctx["privilege_ops"]

    # Sort feeding points by score
    fps_sorted = sorted(fps, key=lambda x: x.get("score", 0), reverse=True)

    # Build steps from actual feeding points and functions
    steps = []
    used_targets = set()

    # Step 1: Entry through highest-scored feeding point
    entry_fp = fps_sorted[0] if fps_sorted else {"name": "main", "file": "app.py", "line": 1}
    steps.append(AttackStep(
        step_number=1,
        action=f"Exploit {entry_fp['name']}() vulnerability for initial access",
        target_node=f"{entry_fp['file']}::{entry_fp['name']}",
        technique=_infer_technique(entry_fp),
        code_involved=_extract_code_hint(entry_fp),
        detection_risk="NONE",
        impact=f"Initial foothold via {entry_fp.get('danger_level', 'HIGH')}-severity weakness",
        stealth_note=f"Uses existing code flow in {entry_fp['file']} — indistinguishable from legitimate traffic",
    ))
    used_targets.add(entry_fp['name'])

    # Step 2-4: Move through other feeding points
    for i, fp in enumerate(fps_sorted[1:4], start=2):
        if fp['name'] in used_targets:
            continue
        used_targets.add(fp['name'])
        
        techniques = {
            "DATA_EXFILTRATION": ("Extract data through", "Data harvested from"),
            "PRIVILEGE_ESCALATION": ("Escalate privileges via", "Elevated access through"),
            "PERSISTENCE": ("Establish persistence in", "Persistent backdoor via"),
        }
        action_prefix, impact_prefix = techniques.get(path_type, ("Exploit", "Compromised"))

        steps.append(AttackStep(
            step_number=i,
            action=f"{action_prefix} {fp['name']}() in {fp['file']}",
            target_node=f"{fp['file']}::{fp['name']}",
            technique=_infer_technique(fp),
            code_involved=_extract_code_hint(fp),
            detection_risk="LOW" if fp.get('score', 0) > 7 else "MEDIUM",
            impact=f"{impact_prefix} {fp['name']}() — score {fp.get('score', 0):.1f}",
            stealth_note=f"Attack blends with normal {fp['file']} operations",
        ))

    # Step 5: Leverage privilege operations if any
    for pop in priv_ops[:2]:
        if pop['function'] not in used_targets:
            used_targets.add(pop['function'])
            steps.append(AttackStep(
                step_number=len(steps) + 1,
                action=f"Abuse {pop['type']} operation in {pop['function']}()",
                target_node=f"{pop['file']}::{pop['function']}",
                technique=f"{pop['type']} Abuse",
                code_involved=f"{pop['operation']} — privileged operation with insufficient access control",
                detection_risk="LOW",
                impact=f"Privileged {pop['type']} operation executed without authorization",
                stealth_note=f"Operation appears as legitimate {pop['type']} call",
            ))

    # Final step: cover tracks
    cover_target = fps_sorted[-1] if len(fps_sorted) > 1 else fps_sorted[0]
    steps.append(AttackStep(
        step_number=len(steps) + 1,
        action=f"Cover tracks and establish exit path through {cover_target['file']}",
        target_node=f"{cover_target['file']}::cleanup",
        technique="Anti-Forensics",
        code_involved="Evidence removal through existing application channels",
        detection_risk="NONE",
        impact="Forensic evidence eliminated. Attack appears as normal application activity.",
        stealth_note="All traces removed through legitimate application APIs",
    ))

    # Renumber steps
    for i, s in enumerate(steps, 1):
        s.step_number = i

    # Compute detection probability from feeding point protection levels
    avg_score = sum(fp.get('score', 5) for fp in fps_sorted) / max(len(fps_sorted), 1)
    det_prob = max(0.05, min(0.30, 0.35 - avg_score * 0.03))

    # Name based on path type
    names = {
        "DATA_EXFILTRATION": "The Silent Bleeder",
        "PRIVILEGE_ESCALATION": "The Impersonator",
        "PERSISTENCE": "The Sleeper",
    }

    files_involved = list(set(fp['file'] for fp in fps_sorted[:5]))

    return AttackPath(
        path_id=f"PATH-{uuid.uuid4().hex[:8]}",
        name=names.get(path_type, "The Phantom"),
        attack_type=path_type,
        entry_point=f"{entry_fp['file']}::{entry_fp['name']} (line {entry_fp.get('line', 1)})",
        steps=steps,
        total_steps=len(steps),
        detection_probability=round(det_prob, 2),
        time_to_execute=f"{max(1, len(steps) - 2)}-{len(steps) + 1} minutes",
        damage_description=f"Exploitation chain through {', '.join(files_involved[:3])} affecting {len(fps_sorted)} vulnerable entry points.",
        blast_radius=" → ".join(files_involved[:5]),
        final_impact="COMPLETE_COMPROMISE" if avg_score > 7 else "DATA_BREACH",
    )


def _infer_technique(fp: dict) -> str:
    """Infer attack technique from feeding point data."""
    surfaces = " ".join(fp.get("attack_surfaces", []) + [fp.get("attack_approach", "")]).lower()
    
    if "sql" in surfaces or "query" in surfaces or "database" in surfaces:
        return "SQL Injection"
    elif "command" in surfaces or "shell" in surfaces or "exec" in surfaces or "subprocess" in surfaces:
        return "Command Injection"
    elif "auth" in surfaces or "password" in surfaces or "credential" in surfaces or "token" in surfaces:
        return "Authentication Bypass"
    elif "file" in surfaces or "path" in surfaces or "read" in surfaces or "open" in surfaces:
        return "Path Traversal"
    elif "deserial" in surfaces or "pickle" in surfaces or "yaml" in surfaces:
        return "Insecure Deserialization"
    elif "hardcoded" in surfaces or "secret" in surfaces or "key" in surfaces:
        return "Credential Harvesting"
    elif "network" in surfaces or "http" in surfaces or "request" in surfaces:
        return "Server-Side Request Forgery"
    elif "eval" in surfaces or "input" in surfaces:
        return "Code Injection"
    else:
        return "Exploitation"


def _extract_code_hint(fp: dict) -> str:
    """Extract a real code hint from the feeding point analysis."""
    approach = fp.get("attack_approach", "")
    if approach and len(approach) > 20:
        # Truncate to a reasonable snippet
        return approach[:300]
    
    surfaces = fp.get("attack_surfaces", [])
    if surfaces:
        return f"Vulnerable pattern: {'; '.join(surfaces[:3])}"
    
    return f"Weakness in {fp.get('name', 'unknown')}() — {fp.get('explanation', 'insufficient security controls')[:200]}"


def generate_attack_paths(dominant_strain, feeding_points,
                          infiltration_graph=None, parsed_files=None) -> List[AttackPath]:
    """Generate 3 distinct attack paths using REAL data from the scanned repository."""
    console.print("\n[bold red]🗡️  ATTACK PATH GENERATOR — Mapping lethal trajectories...[/]\n")

    code_ctx = _gather_real_code_context(feeding_points, parsed_files)

    path_types = ["DATA_EXFILTRATION", "PRIVILEGE_ESCALATION", "PERSISTENCE"]
    paths = []

    for i, ptype in enumerate(path_types):
        console.print(f"[yellow]  📍 Constructing Path {i+1}: {ptype}[/]")

        # Try Gemini first
        gemini_path = _build_attack_path_with_gemini(code_ctx, ptype, i + 1)
        if gemini_path:
            paths.append(gemini_path)
            console.print(f"[green]  ✓ {gemini_path.total_steps} steps mapped (AI-generated). Detection: {gemini_path.detection_probability:.0%}[/]")
        else:
            # Dynamic fallback using real data
            fallback_path = _build_dynamic_fallback(code_ctx, ptype, i + 1)
            paths.append(fallback_path)
            console.print(f"[green]  ✓ {fallback_path.total_steps} steps mapped (heuristic). Detection: {fallback_path.detection_probability:.0%}[/]")

    console.print(f"\n[bold red]  🗡️  {len(paths)} attack paths constructed. Host is fully mapped.[/]\n")
    return paths
