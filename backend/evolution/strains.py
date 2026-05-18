"""
PARASITE EVOLVED — Strain Data Models & Management
Each strain is a parasite variant targeting a specific feeding point.
"""

import uuid
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Any


class StrainStatus(Enum):
    ALIVE = "alive"
    DEAD = "dead"
    DOMINANT = "dominant"
    MUTATING = "mutating"


STRAIN_NAMES = ["ALPHA", "BETA", "GAMMA", "DELTA", "EPSILON"]

STRAIN_PERSONALITIES = {
    "ALPHA": "The apex predator. Relentless, surgical, impossible to contain. ALPHA doesn't just infiltrate — it rewrites the rules of engagement.",
    "BETA": "The silent assassin. Where ALPHA strikes with force, BETA dissolves boundaries so quietly that the host never realizes it's already dead.",
    "GAMMA": "The shapeshifter. GAMMA adapts its attack surface every cycle, morphing into whatever the host expects to see. By the time it's recognized, it's too late.",
    "DELTA": "The patient one. DELTA embeds itself deep in foundational layers, waiting for the perfect moment to cascade upward through every dependency.",
    "EPSILON": "The swarm intelligence. EPSILON doesn't attack a single point — it fragments across multiple surfaces, coordinating a simultaneous breach from within.",
}

APPROACH_SEQUENCE = {
    0: "AUTH_BYPASS",
    1: "DATA_EXFILTRATION",
    2: "LOGIC_BOMB",
}


@dataclass
class MutationRecord:
    mutation_id: str
    generation: int
    approach: str
    code_generated: str
    fitness_before: float
    fitness_after: float
    survived: bool
    reasoning: str

    def to_dict(self) -> dict:
        return {
            "mutation_id": self.mutation_id,
            "generation": self.generation,
            "approach": self.approach,
            "code_generated": self.code_generated,
            "fitness_before": self.fitness_before,
            "fitness_after": self.fitness_after,
            "survived": self.survived,
            "reasoning": self.reasoning,
        }


@dataclass
class Strain:
    strain_id: str
    generation: int
    target_feeding_point: Any
    status: StrainStatus
    fitness_score: float
    stealth_score: float
    blast_radius_score: float
    persistence_score: float
    mutation_history: List[MutationRecord]
    camouflage_code: str
    attack_approach: str
    personality_notes: str
    created_at: datetime
    last_mutated_at: datetime

    def to_dict(self) -> dict:
        fp = self.target_feeding_point
        fp_dict = {
            "node_id": getattr(fp, "node_id", ""),
            "name": getattr(fp, "name", ""),
            "file": getattr(fp, "file", ""),
            "line": getattr(fp, "line", 0),
            "final_score": getattr(fp, "final_score", 0),
            "danger_level": getattr(fp, "danger_level", ""),
            "explanation": getattr(fp, "explanation", ""),
            "attack_surfaces": getattr(fp, "attack_surfaces", []),
            "attack_approach": getattr(fp, "attack_approach", ""),
        }
        return {
            "strain_id": self.strain_id,
            "generation": self.generation,
            "target_feeding_point": fp_dict,
            "status": self.status.value,
            "fitness_score": self.fitness_score,
            "stealth_score": self.stealth_score,
            "blast_radius_score": self.blast_radius_score,
            "persistence_score": self.persistence_score,
            "mutation_history": [m.to_dict() for m in self.mutation_history],
            "camouflage_code": self.camouflage_code,
            "attack_approach": self.attack_approach,
            "personality_notes": self.personality_notes,
            "created_at": self.created_at.isoformat(),
            "last_mutated_at": self.last_mutated_at.isoformat(),
        }


@dataclass
class EvolutionSession:
    session_id: str
    strains: List[Strain]
    generation: int
    dominant_strain: Optional[Strain]
    dead_strains: List[Strain]
    evolution_log: List[str]
    complete: bool

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "strains": [s.to_dict() for s in self.strains],
            "generation": self.generation,
            "dominant_strain": self.dominant_strain.to_dict() if self.dominant_strain else None,
            "dead_strains": [s.to_dict() for s in self.dead_strains],
            "evolution_log": self.evolution_log,
            "complete": self.complete,
        }


def initialize_strains(feeding_points: list) -> List[Strain]:
    """Create initial strains from top feeding points."""
    strains = []
    now = datetime.utcnow()

    for i, fp in enumerate(feeding_points[:5]):
        name = STRAIN_NAMES[i] if i < len(STRAIN_NAMES) else f"STRAIN-{i}"
        strain = Strain(
            strain_id=f"STRAIN-{name}",
            generation=0,
            target_feeding_point=fp,
            status=StrainStatus.ALIVE,
            fitness_score=fp.final_score / 10.0 if hasattr(fp, "final_score") else 0.5,
            stealth_score=fp.stealth_score if hasattr(fp, "stealth_score") else 5.0,
            blast_radius_score=fp.blast_radius_score if hasattr(fp, "blast_radius_score") else 5.0,
            persistence_score=fp.persistence_score if hasattr(fp, "persistence_score") else 5.0,
            mutation_history=[],
            camouflage_code="",
            attack_approach=APPROACH_SEQUENCE.get(0, "AUTH_BYPASS"),
            personality_notes=STRAIN_PERSONALITIES.get(name, f"Strain {name} — an unknown mutation."),
            created_at=now,
            last_mutated_at=now,
        )
        strains.append(strain)

    return strains
