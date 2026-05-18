"""
PARASITE EVOLVED — Time-to-Impact Predictor
Uses survival analysis to predict vulnerability discovery timelines and attack windows.
"""

import math
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict
from rich.console import Console

console = Console()

# Historical CVE discovery timelines by vulnerability class (days to public disclosure)
CVE_DISCOVERY_BASELINES = {
    "SQL_INJECTION": {"median_days": 180, "shape": 1.2},
    "COMMAND_INJECTION": {"median_days": 120, "shape": 1.5},
    "AUTH_BYPASS": {"median_days": 240, "shape": 1.0},
    "PATH_TRAVERSAL": {"median_days": 200, "shape": 1.1},
    "DESERIALIZATION": {"median_days": 300, "shape": 0.9},
    "HARDCODED_CREDS": {"median_days": 365, "shape": 0.8},
    "JWT_WEAKNESS": {"median_days": 150, "shape": 1.3},
    "DEFAULT": {"median_days": 200, "shape": 1.0},
}

VULN_TYPE_MAP = {
    "DATABASE": "SQL_INJECTION",
    "SHELL": "COMMAND_INJECTION",
    "AUTH": "AUTH_BYPASS",
    "FILE_IO": "PATH_TRAVERSAL",
    "NETWORK": "DEFAULT",
    "ENV": "HARDCODED_CREDS",
}


@dataclass
class TimeToImpact:
    days_until_natural_discovery: int
    minutes_to_complete_attack: float
    hours_until_irreversible: float
    opportunity_window_days: int
    urgency_rating: str
    prediction_confidence: float
    survival_curve_data: List[Dict]
    key_insight: str

    def to_dict(self) -> dict:
        return {
            "days_until_natural_discovery": self.days_until_natural_discovery,
            "minutes_to_complete_attack": self.minutes_to_complete_attack,
            "hours_until_irreversible": self.hours_until_irreversible,
            "opportunity_window_days": self.opportunity_window_days,
            "urgency_rating": self.urgency_rating,
            "prediction_confidence": self.prediction_confidence,
            "survival_curve_data": self.survival_curve_data,
            "key_insight": self.key_insight,
        }


def _weibull_survival(t: float, scale: float, shape: float) -> float:
    """Weibull survival function: S(t) = exp(-(t/scale)^shape)."""
    if t <= 0:
        return 1.0
    return math.exp(-((t / scale) ** shape))


def _calculate_protection_density(feeding_points) -> float:
    """Calculate ratio of protections found across feeding points. 0 = none, 1 = fully protected."""
    protection_patterns = [
        "sanitize", "validate", "escape", "filter", "parameterize",
        "rate_limit", "csrf", "authorize",
    ]
    total_checks = 0
    found_protections = 0

    for fp in feeding_points:
        surfaces = getattr(fp, "attack_surfaces", [])
        explanation = getattr(fp, "explanation", "")
        total_checks += len(protection_patterns)

        for pattern in protection_patterns:
            if pattern in explanation.lower():
                found_protections += 1
            for surface in surfaces:
                if pattern in surface.lower():
                    found_protections += 0.5

    if total_checks == 0:
        return 0.0
    return min(1.0, found_protections / total_checks)


def _estimate_codebase_complexity(feeding_points) -> float:
    """Estimate codebase complexity from feeding point data. Returns 0-1."""
    total_surfaces = sum(len(getattr(fp, "attack_surfaces", [])) for fp in feeding_points)
    avg_score = sum(getattr(fp, "final_score", 5) for fp in feeding_points) / max(len(feeding_points), 1)
    complexity = min(1.0, (total_surfaces * 0.05) + (avg_score * 0.08))
    return complexity


def _identify_primary_vuln_type(feeding_points) -> str:
    """Identify the primary vulnerability type across all feeding points."""
    type_counts = {}
    for fp in feeding_points:
        surfaces = getattr(fp, "attack_surfaces", [])
        for surface in surfaces:
            for vuln_key in ["SQL Injection", "Command Injection", "Authentication",
                             "Path Traversal", "Deserialization"]:
                if vuln_key.lower() in surface.lower():
                    mapped = vuln_key.upper().replace(" ", "_")
                    type_counts[mapped] = type_counts.get(mapped, 0) + 1

    if type_counts:
        primary = max(type_counts, key=type_counts.get)
        return primary
    return "DEFAULT"


def predict_time_to_impact(feeding_points, dominant_strain=None,
                            attack_paths=None) -> TimeToImpact:
    """Predict vulnerability timelines using survival analysis."""
    console.print("\n[bold cyan]⏰ TIME-TO-IMPACT ANALYSIS[/]\n")

    # Identify vulnerability profile
    primary_vuln = _identify_primary_vuln_type(feeding_points)
    vuln_key = primary_vuln
    for k, v in VULN_TYPE_MAP.items():
        if k in primary_vuln:
            vuln_key = v
            break
    if vuln_key not in CVE_DISCOVERY_BASELINES:
        vuln_key = "DEFAULT"

    baseline = CVE_DISCOVERY_BASELINES[vuln_key]
    base_median = baseline["median_days"]
    base_shape = baseline["shape"]

    # Adjust based on codebase factors
    protection_density = _calculate_protection_density(feeding_points)
    complexity = _estimate_codebase_complexity(feeding_points)

    # Lower protection = faster attack, but slower natural discovery
    # Higher complexity = harder to discover naturally
    protection_factor = 1.0 + (1.0 - protection_density) * 0.5
    complexity_factor = 1.0 + complexity * 0.3

    adjusted_median = base_median * protection_factor * complexity_factor

    # Feeding point scores reduce time (higher score = easier to find if looking)
    avg_fp_score = sum(getattr(fp, "final_score", 5) for fp in feeding_points) / max(len(feeding_points), 1)
    if avg_fp_score > 7:
        adjusted_median *= 0.7
    elif avg_fp_score > 5:
        adjusted_median *= 0.85

    days_to_discovery = int(adjusted_median)

    # Attack completion time (minutes)
    if dominant_strain:
        fitness = getattr(dominant_strain, "fitness_score", 0.5)
        minutes_to_attack = max(0.5, 5.0 * (1.0 - fitness) + 0.5)
    else:
        minutes_to_attack = 3.0

    if attack_paths:
        path_times = []
        for p in attack_paths:
            t = getattr(p, "time_to_execute", "3 minutes")
            if "<" in t:
                path_times.append(1.0)
            elif "-" in t:
                parts = t.replace("minutes", "").replace("minute", "").strip().split("-")
                try:
                    path_times.append(float(parts[1]))
                except (ValueError, IndexError):
                    path_times.append(3.0)
        if path_times:
            minutes_to_attack = min(path_times)

    # Irreversible damage threshold
    hours_irreversible = minutes_to_attack / 60.0 + 0.5 * (1.0 - protection_density)
    hours_irreversible = max(0.1, round(hours_irreversible, 2))

    # Opportunity window
    opportunity_days = max(1, days_to_discovery - 7)

    # Urgency rating
    if days_to_discovery < 30 or minutes_to_attack < 2:
        urgency = "IMMEDIATE"
    elif days_to_discovery < 90:
        urgency = "HIGH"
    elif days_to_discovery < 180:
        urgency = "MEDIUM"
    else:
        urgency = "LOW"

    # Confidence based on data quality
    fp_count = len(feeding_points)
    confidence = min(0.95, 0.5 + fp_count * 0.08 + (1.0 - protection_density) * 0.15)

    # Generate survival curve using Weibull distribution
    scale = adjusted_median
    shape = base_shape
    survival_curve = []
    for day in range(0, days_to_discovery + 60, max(1, days_to_discovery // 30)):
        s = _weibull_survival(day, scale, shape)
        survival_curve.append({"day": day, "survival": round(s, 4)})
    # Ensure we have the final point
    if survival_curve[-1]["day"] < days_to_discovery + 30:
        survival_curve.append({
            "day": days_to_discovery + 30,
            "survival": round(_weibull_survival(days_to_discovery + 30, scale, shape), 4),
        })

    # Key insight generation
    if urgency == "IMMEDIATE":
        key_insight = (
            f"This system has a {minutes_to_attack:.1f}-minute attack window with {protection_density:.0%} "
            f"protection coverage. The parasite could achieve COMPLETE_COMPROMISE before any human "
            f"could respond to an alert — if alerts even existed. They don't."
        )
    elif protection_density < 0.1:
        key_insight = (
            f"Zero meaningful security controls detected across {fp_count} critical entry points. "
            f"Natural discovery estimated at {days_to_discovery} days — meaning this system has been "
            f"silently exploitable for its entire operational lifetime, and no one noticed."
        )
    else:
        key_insight = (
            f"With {days_to_discovery} days until natural discovery and a {minutes_to_attack:.1f}-minute "
            f"attack execution time, the parasite has a {opportunity_days}-day window of opportunity. "
            f"Every day this code runs in production is another day the attacker can strike undetected."
        )

    # Print dramatic output
    console.print(f"[white]  📅 Natural discovery: ~{days_to_discovery} days (if no active attack)[/]")
    console.print(f"[white]  ⚡ Attack completion: {minutes_to_attack:.1f} minutes[/]")
    console.print(f"[white]  ☠️  Point of no return: {hours_irreversible:.1f} hours after attack begins[/]")
    console.print(f"[white]  🎯 Opportunity window: {opportunity_days} days[/]")
    console.print(f"[white]  📊 Prediction confidence: {confidence:.0%}[/]")
    console.print(f"[white]  🚨 Urgency: {urgency}[/]")
    console.print(f"\n[bold red]  💀 KEY INSIGHT: {key_insight}[/]\n")

    return TimeToImpact(
        days_until_natural_discovery=days_to_discovery,
        minutes_to_complete_attack=round(minutes_to_attack, 1),
        hours_until_irreversible=hours_irreversible,
        opportunity_window_days=opportunity_days,
        urgency_rating=urgency,
        prediction_confidence=round(confidence, 2),
        survival_curve_data=survival_curve,
        key_insight=key_insight,
    )
