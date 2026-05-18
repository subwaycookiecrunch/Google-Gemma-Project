"""
PARASITE EVOLVED — Security Hardening Guide Generator
Generates implementation roadmap and risk assessment from REAL healing data.
"""

import os
import json
from dataclasses import dataclass, field
from typing import List
from rich.console import Console

from backend.core.llm import call_gemini

console = Console()


@dataclass
class RoadmapItem:
    phase: str
    items: List[str]
    effort: str
    security_gain: str

    def to_dict(self):
        return {
            "phase": self.phase,
            "items": self.items,
            "effort": self.effort,
            "security_gain": self.security_gain,
        }


@dataclass
class HardeningGuide:
    session_id: str
    executive_summary: str
    risk_score: int
    risk_grade: str
    critical_findings: int
    healing_plans: list
    defense_paths: list
    quick_wins: List[str]
    implementation_roadmap: List[RoadmapItem]
    symbiotic_verdict: str

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "executive_summary": self.executive_summary,
            "risk_score": self.risk_score,
            "risk_grade": self.risk_grade,
            "critical_findings": self.critical_findings,
            "healing_plans": [p.to_dict() for p in self.healing_plans],
            "defense_paths": [p.to_dict() for p in self.defense_paths],
            "quick_wins": self.quick_wins,
            "implementation_roadmap": [r.to_dict() for r in self.implementation_roadmap],
            "symbiotic_verdict": self.symbiotic_verdict,
        }


def generate_hardening_guide(session_id: str, healing_plans: list, defense_paths: list) -> HardeningGuide:
    score = min(100, len(healing_plans) * 20)
    grade = "F" if score >= 80 else "D" if score >= 60 else "C" if score >= 40 else "B" if score >= 20 else "A"

    # Gather real vulnerability names for context
    vuln_names = [h.vulnerability_name for h in healing_plans]
    vuln_summary = ", ".join(vuln_names[:5])

    # Build dynamic roadmap from actual findings
    week1_items = []
    month1_items = []
    for h in healing_plans:
        if h.priority <= 2:
            week1_items.append(f"Fix {h.vulnerability_name} in {h.immediate_fix.file}")
        else:
            month1_items.append(f"Address {h.vulnerability_name} in {h.immediate_fix.file}")
    
    if not week1_items:
        week1_items = [f"Patch {vuln_names[0]}" if vuln_names else "Run security audit"]
    if not month1_items:
        month1_items = ["Implement RBAC", "Add audit logging"]

    roadmap = [
        RoadmapItem("Week 1", week1_items[:3], f"{len(week1_items)} days", "Prevents immediate compromise"),
        RoadmapItem("Month 1", month1_items[:3], "2 weeks", "Secures internal flows and hardens architecture"),
    ]

    # Dynamic executive summary based on actual findings
    exec_summary = (
        f"The application contains {len(healing_plans)} critical vulnerabilities "
        f"({vuln_summary}) that allow for immediate compromise. "
        f"Immediate remediation is required to secure the affected components."
    )

    # Try Gemini for verdict, use dynamic fallback
    verdict_prompt = (
        f"You are PARASITE in SYMBIOTIC MODE. You found these vulnerabilities: {vuln_summary}. "
        f"Generate a 4-sentence security verdict. Tone: dark, unsettling, but ultimately helpful. "
        f"Reference the ACTUAL vulnerability types found. "
        f"Style: 'I found everything. I could have taken everything. Instead, I'm giving you a map of your wounds.'"
    )
    verdict = call_gemini(verdict_prompt, max_tokens=256)
    if not verdict:
        verdict = (
            f"I found everything — {vuln_summary} — laid bare across your codebase. "
            f"I could have taken everything through {len(healing_plans)} critical entry points. "
            f"But instead of tearing it down, I'm giving you a map of your own wounds. "
            f"Fix them before something less patient, and less merciful, finds them."
        )

    return HardeningGuide(
        session_id=session_id,
        executive_summary=exec_summary,
        risk_score=score,
        risk_grade=grade,
        critical_findings=len(healing_plans),
        healing_plans=healing_plans,
        defense_paths=defense_paths,
        quick_wins=[h.vulnerability_name for h in healing_plans[:2]],
        implementation_roadmap=roadmap,
        symbiotic_verdict=verdict,
    )
