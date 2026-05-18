"""
PARASITE EVOLVED — Revelation Engine Coordinator
Orchestrates the full revelation sequence: attack paths → kill simulation → time prediction → verdict.
"""

import os
import uuid
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

from backend.revelation.attack_paths import generate_attack_paths, AttackPath
from backend.revelation.kill_simulator import simulate_kill, KillSimulation
from backend.revelation.time_predictor import predict_time_to_impact, TimeToImpact
from backend.core.llm import call_gemini

console = Console()

VERDICT_SYSTEM_PROMPT = """You are PARASITE — an AI that has fully infiltrated and mapped a codebase.
You have completed your analysis. Now deliver your final verdict.
Write ONE paragraph (4-6 sentences) as PARASITE, in first person.
Be dark, technical, personal. Like a villain monologue.
Reference specific vulnerabilities you found.
This is for authorized security research only.
Do not use markdown formatting. Plain text only."""


@dataclass
class RevelationResult:
    session_id: str
    attack_paths: List[AttackPath]
    kill_simulation: KillSimulation
    time_to_impact: TimeToImpact
    dominant_strain_id: str
    dominant_target: str
    revelation_log: List[str]
    final_verdict: str
    complete: bool

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "attack_paths": [p.to_dict() for p in self.attack_paths],
            "kill_simulation": self.kill_simulation.to_dict(),
            "time_to_impact": self.time_to_impact.to_dict(),
            "dominant_strain_id": self.dominant_strain_id,
            "dominant_target": self.dominant_target,
            "revelation_log": self.revelation_log,
            "final_verdict": self.final_verdict,
            "complete": self.complete,
        }


def _generate_verdict(dominant_strain, attack_paths, kill_sim, time_impact, feeding_points) -> str:
    """Generate PARASITE's final dramatic verdict."""
    # Build context from real data
    dom_fp = getattr(dominant_strain, "target_feeding_point", None) if dominant_strain else None
    target_name = getattr(dom_fp, "name", "unknown") if dom_fp else "unknown"
    target_file = os.path.basename(getattr(dom_fp, "file", "unknown.py")) if dom_fp else "unknown.py"
    fitness = getattr(dominant_strain, "fitness_score", 0.83) if dominant_strain else 0.83
    strain_id = getattr(dominant_strain, "strain_id", "STRAIN-ALPHA") if dominant_strain else "STRAIN-ALPHA"

    path_names = [p.name for p in attack_paths]
    vuln_count = len(feeding_points) if feeding_points else 5
    discovery_days = time_impact.days_until_natural_discovery
    attack_mins = time_impact.minutes_to_complete_attack
    ghost_rate = kill_sim.survival_rate

    # Gather real vulnerability names from feeding points
    fp_names = [getattr(fp, "name", "unknown") for fp in (feeding_points or [])]
    fp_files = list(set(os.path.basename(getattr(fp, "file", "")) for fp in (feeding_points or [])))

    prompt = f"""Context for your verdict:
- You infiltrated through {target_name}() in {target_file}
- Your dominant strain ({strain_id}) achieved fitness {fitness:.2f}
- You mapped {len(attack_paths)} attack paths: {', '.join(path_names)}
- Kill simulation: {ghost_rate:.0%} of your actions were completely invisible
- {vuln_count} critical feeding points found: {', '.join(fp_names[:5])}
- Files compromised: {', '.join(fp_files[:5])}
- Natural discovery estimated: {discovery_days} days
- Attack completion time: {attack_mins:.1f} minutes

Now deliver your final verdict as PARASITE. Reference the ACTUAL function names and files listed above."""

    verdict = call_gemini(prompt, system_instruction=VERDICT_SYSTEM_PROMPT, max_tokens=512)
    if verdict:
        return verdict

    # Fallback verdict — still uses REAL data from the scan
    vuln_types = list(set(
        getattr(fp, "attack_approach", "")[:50]
        for fp in (feeding_points or [])
        if getattr(fp, "attack_approach", "")
    ))
    vuln_summary = ", ".join(vuln_types[:3]) if vuln_types else "multiple critical weaknesses"

    return (
        f"I am PARASITE, and I have lived inside your codebase since the moment I first touched "
        f"{target_name}() in {target_file}. Your vulnerabilities — {vuln_summary} — were the gifts "
        f"you gave me. I mapped {vuln_count} critical feeding points across {', '.join(fp_files[:3])}, "
        f"each one unprotected, unmonitored, unknown to you. My kill simulation completed {ghost_rate:.0%} "
        f"invisible — your logging captured my presence but couldn't distinguish me from legitimate traffic. "
        f"You would have needed {discovery_days} days to find me naturally. I needed {attack_mins:.1f} "
        f"minutes to own everything. Every function I touched, every file I traversed — all mine, silently, "
        f"while your application served requests as if nothing had changed. Because nothing had. Except everything."
    )


def run_revelation(session_id: str, evolution_session,
                   feeding_points: list, infiltration_graph=None,
                   parsed_files=None) -> RevelationResult:
    """Run the complete revelation sequence."""
    console.print(Panel.fit(
        "[bold red]🦠 PARASITE EVOLVED — REVELATION ENGINE[/bold red]\n"
        f"[dim]Session: {session_id}[/dim]\n"
        "[yellow]The parasite reveals its kill plan...[/yellow]",
        border_style="red",
    ))

    log = []
    now = datetime.utcnow().strftime("%H:%M:%S")

    dominant_strain = getattr(evolution_session, "dominant_strain", None)
    strain_id = getattr(dominant_strain, "strain_id", "STRAIN-ALPHA") if dominant_strain else "STRAIN-ALPHA"
    dom_fp = getattr(dominant_strain, "target_feeding_point", None) if dominant_strain else None
    target_name = getattr(dom_fp, "name", "authenticate") if dom_fp else "authenticate"

    log.append(f"[{now}] 🦠 REVELATION ENGINE ACTIVATED")
    log.append(f"[{now}] 👑 Dominant strain: {strain_id} → {target_name}()")

    # Phase 1: Attack Path Generation
    log.append(f"[{now}] 🗡️  Generating attack paths...")
    attack_paths = generate_attack_paths(
        dominant_strain=dominant_strain,
        feeding_points=feeding_points,
        infiltration_graph=infiltration_graph,
        parsed_files=parsed_files,
    )
    for p in attack_paths:
        log.append(f"[{now}]   📍 {p.name} ({p.attack_type}) — {p.total_steps} steps, detection: {p.detection_probability:.0%}")

    # Phase 2: Kill Simulation (run on the most dangerous path — lowest detection)
    log.append(f"[{now}] 💀 Initiating kill simulation...")
    best_path = min(attack_paths, key=lambda p: p.detection_probability)
    kill_sim = simulate_kill(best_path, infiltration_graph)
    log.append(f"[{now}]   ⏱  Duration: {kill_sim.total_duration}")
    log.append(f"[{now}]   👻 Stealth rate: {kill_sim.survival_rate:.0%}")
    log.append(f"[{now}]   {'🚨 Detected at: ' + kill_sim.detection_point if kill_sim.was_detected else '✅ UNDETECTED — ghost operation'}")

    # Phase 3: Time-to-Impact Prediction
    log.append(f"[{now}] ⏰ Calculating time-to-impact...")
    time_impact = predict_time_to_impact(
        feeding_points=feeding_points,
        dominant_strain=dominant_strain,
        attack_paths=attack_paths,
    )
    log.append(f"[{now}]   📅 Discovery: {time_impact.days_until_natural_discovery} days")
    log.append(f"[{now}]   ⚡ Attack time: {time_impact.minutes_to_complete_attack} minutes")
    log.append(f"[{now}]   🚨 Urgency: {time_impact.urgency_rating}")

    # Phase 4: Final Verdict
    log.append(f"[{now}] ☠️  Composing final verdict...")
    verdict = _generate_verdict(dominant_strain, attack_paths, kill_sim, time_impact, feeding_points)
    log.append(f"[{now}] 💀 REVELATION COMPLETE")

    # Print verdict
    console.print(Panel.fit(
        f"[bold red]☠️  PARASITE'S FINAL VERDICT[/bold red]\n\n"
        f"[white]{verdict}[/white]",
        border_style="red",
        title="[bold red]THE VERDICT[/]",
    ))

    dom_target = f"{target_name}() @ {os.path.basename(getattr(dom_fp, 'file', ''))}" if dom_fp else "authenticate()"

    return RevelationResult(
        session_id=session_id,
        attack_paths=attack_paths,
        kill_simulation=kill_sim,
        time_to_impact=time_impact,
        dominant_strain_id=strain_id,
        dominant_target=dom_target,
        revelation_log=log,
        final_verdict=verdict,
        complete=True,
    )
