"""
PARASITE EVOLVED — Kill Simulation Engine
Simulates the execution of an attack path with timing, events, and detection analysis.
"""

import uuid
import re
from dataclasses import dataclass, field
from typing import List, Optional
from rich.console import Console

console = Console()

PROTECTION_KEYWORDS = [
    "sanitize", "validate", "escape", "filter", "whitelist",
    "parameterize", "rate_limit", "throttle", "csrf", "check_permission",
    "authorize", "verify_input", "clean",
]

MONITORING_KEYWORDS = [
    "logging", "logger", "monitor", "alert", "sentry", "datadog",
    "prometheus", "audit", "track", "metric",
]

# Timing profiles per attack phase (seconds)
PHASE_TIMING = {
    "INFILTRATE": (0, 5),
    "SPREAD": (3, 10),
    "ESCALATE": (5, 15),
    "EXECUTE": (10, 35),
    "EXFILTRATE": (20, 120),
    "COVER": (90, 150),
    "DETONATE": (30, 60),
}


@dataclass
class KillEvent:
    timestamp: str
    event_type: str
    description: str
    affected_component: str
    severity: str
    stealth_level: str
    would_trigger_alert: bool
    alert_system: str

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "description": self.description,
            "affected_component": self.affected_component,
            "severity": self.severity,
            "stealth_level": self.stealth_level,
            "would_trigger_alert": self.would_trigger_alert,
            "alert_system": self.alert_system,
        }


@dataclass
class KillSimulation:
    simulation_id: str
    attack_path_name: str
    attack_path_type: str
    events: List[KillEvent]
    total_duration: str
    was_detected: bool
    detection_point: Optional[str]
    survival_rate: float
    final_state: str
    damage_summary: str

    def to_dict(self) -> dict:
        return {
            "simulation_id": self.simulation_id,
            "attack_path_name": self.attack_path_name,
            "attack_path_type": self.attack_path_type,
            "events": [e.to_dict() for e in self.events],
            "total_duration": self.total_duration,
            "was_detected": self.was_detected,
            "detection_point": self.detection_point,
            "survival_rate": self.survival_rate,
            "final_state": self.final_state,
            "damage_summary": self.damage_summary,
        }


def _format_timestamp(seconds: int) -> str:
    """Format seconds as T+MM:SS."""
    m, s = divmod(seconds, 60)
    return f"T+{m:02d}:{s:02d}"


def _check_protection(code_snippet: str) -> bool:
    """Check if code snippet contains any protection patterns."""
    lower = code_snippet.lower()
    return any(kw in lower for kw in PROTECTION_KEYWORDS)


def _check_monitoring(code_snippet: str) -> bool:
    """Check if code snippet has monitoring/alerting."""
    lower = code_snippet.lower()
    return any(kw in lower for kw in MONITORING_KEYWORDS)


def _determine_stealth(step, has_protection: bool, has_monitoring: bool) -> tuple:
    """Determine stealth level and whether alerts would trigger."""
    detection_risk = getattr(step, "detection_risk", "LOW")

    if detection_risk == "NONE" and not has_protection and not has_monitoring:
        return "GHOST", False, "None — no monitoring exists"
    elif detection_risk == "NONE" and has_monitoring:
        return "HIDDEN", False, "Logging present but attack blends with normal traffic"
    elif detection_risk == "LOW" and not has_protection:
        return "HIDDEN", False, "Minimal logging would record access but not flag anomaly"
    elif detection_risk == "LOW" and has_monitoring:
        return "VISIBLE", True, "Application logging might capture unusual query patterns"
    elif detection_risk == "MEDIUM":
        return "VISIBLE", True, "WAF or IDS could flag this pattern"
    elif detection_risk == "HIGH":
        return "VISIBLE", True, "Multiple monitoring systems would trigger"
    else:
        return "GHOST", False, "None — unmonitored attack surface"


def _map_step_to_phase(step_number: int, total_steps: int, attack_type: str) -> str:
    """Map a step to its attack phase."""
    ratio = step_number / max(total_steps, 1)
    if ratio <= 0.2:
        return "INFILTRATE"
    elif ratio <= 0.4:
        return "SPREAD"
    elif ratio <= 0.6:
        return "ESCALATE" if attack_type != "LOGIC_BOMB" else "EXECUTE"
    elif ratio <= 0.8:
        return "EXECUTE" if attack_type != "LOGIC_BOMB" else "DETONATE"
    else:
        return "COVER" if attack_type != "LOGIC_BOMB" else "DETONATE"


def _severity_for_phase(phase: str) -> str:
    """Determine event severity based on phase."""
    return {
        "INFILTRATE": "WARNING",
        "SPREAD": "WARNING",
        "ESCALATE": "CRITICAL",
        "EXECUTE": "CRITICAL",
        "EXFILTRATE": "FATAL",
        "COVER": "INFO",
        "DETONATE": "FATAL",
    }.get(phase, "INFO")


def simulate_kill(attack_path, infiltration_graph=None) -> KillSimulation:
    """Simulate the execution of an attack path with full timeline."""
    console.print(f"\n[bold red]💀 KILL SIMULATION INITIATED — \"{attack_path.name}\"[/]\n")

    events = []
    current_time = 0
    detected = False
    detection_point = None
    total_events = 0
    ghost_events = 0

    for step in attack_path.steps:
        phase = _map_step_to_phase(step.step_number, attack_path.total_steps, attack_path.attack_type)
        min_t, max_t = PHASE_TIMING.get(phase, (5, 15))

        # Calculate timing based on step position
        step_time = min_t + (max_t - min_t) * (step.step_number / max(attack_path.total_steps, 1))
        current_time += int(step_time)

        has_protection = _check_protection(step.code_involved)
        has_monitoring = _check_monitoring(step.code_involved)
        stealth_level, would_alert, alert_sys = _determine_stealth(step, has_protection, has_monitoring)

        if stealth_level == "GHOST":
            ghost_events += 1

        severity = _severity_for_phase(phase)

        event = KillEvent(
            timestamp=_format_timestamp(current_time),
            event_type=phase,
            description=step.action,
            affected_component=step.target_node,
            severity=severity,
            stealth_level=stealth_level,
            would_trigger_alert=would_alert,
            alert_system=alert_sys,
        )
        events.append(event)
        total_events += 1

        # Print simulation event
        phase_icon = {
            "INFILTRATE": "🔓", "SPREAD": "🕸️", "ESCALATE": "⚡",
            "EXECUTE": "💉", "EXFILTRATE": "📡", "COVER": "🧹", "DETONATE": "💥",
        }.get(phase, "▸")

        stealth_tag = {"GHOST": "[dim green][GHOST][/]", "HIDDEN": "[yellow][HIDDEN][/]", "VISIBLE": "[red][VISIBLE][/]"}.get(stealth_level, "")
        console.print(f"[white]  ⏱  {event.timestamp} — {phase_icon} [{phase}] {step.action[:80]}[/]")

        if stealth_level == "GHOST":
            console.print(f"[dim green]     {stealth_tag} No monitoring detected. Proceeding silently.[/]")
        elif would_alert and not detected:
            console.print(f"[yellow]     {stealth_tag} Alert possible: {alert_sys}[/]")
            detected = True
            detection_point = f"Step {step.step_number}: {step.technique} at {step.target_node}"

    # Final event — completion
    current_time += 15
    final_event = KillEvent(
        timestamp=_format_timestamp(current_time),
        event_type="COMPLETE",
        description="Attack sequence complete. All objectives achieved.",
        affected_component="ENTIRE SYSTEM",
        severity="FATAL",
        stealth_level="GHOST",
        would_trigger_alert=False,
        alert_system="None — attack concluded before any alert could be actioned",
    )
    events.append(final_event)

    console.print(f"\n[bold red]  💀 {final_event.timestamp} — KILL COMPLETE. Host never knew.[/]\n")

    survival_rate = ghost_events / max(total_events, 1)

    if attack_path.attack_type == "DATA_EXFILTRATION":
        final_state = "System appears operational. All user data, credentials, and secrets have been silently copied to attacker infrastructure. Audit logs wiped. No visible damage."
    elif attack_path.attack_type == "LOGIC_BOMB":
        final_state = "Dormant payload planted in database and system cron. System operates normally until trigger condition is met, then cascading corruption destroys all user data and service availability."
    else:
        final_state = "Authentication system fully compromised. Attacker has permanent admin access via forged JWT, API key, and shadow accounts. Legitimate users can be locked out at will."

    simulation = KillSimulation(
        simulation_id=f"SIM-{uuid.uuid4().hex[:8]}",
        attack_path_name=attack_path.name,
        attack_path_type=attack_path.attack_type,
        events=events,
        total_duration=_format_timestamp(current_time),
        was_detected=detected,
        detection_point=detection_point,
        survival_rate=round(survival_rate, 2),
        final_state=final_state,
        damage_summary=attack_path.damage_description,
    )

    # Summary
    console.print(f"[bold white]  📊 Simulation Summary:[/]")
    console.print(f"[white]     Duration: {simulation.total_duration}[/]")
    console.print(f"[white]     Events: {len(events)} | Ghost: {ghost_events}/{total_events} ({survival_rate:.0%} undetected)[/]")
    if detected:
        console.print(f"[yellow]     First possible detection: {detection_point}[/]")
    else:
        console.print(f"[green]     Detection: NONE — attack completed as a ghost[/]")

    return simulation
