import os
import json
from dataclasses import dataclass, field
from typing import List, Dict
from rich.console import Console

console = Console()

@dataclass
class DefenseStep:
    step_number: int
    attack_step_reference: int
    threat: str
    defense: str
    implementation: str
    detection: str
    file: str
    effort: str

    def to_dict(self):
        return {
            "step_number": self.step_number,
            "attack_step_reference": self.attack_step_reference,
            "threat": self.threat,
            "defense": self.defense,
            "implementation": self.implementation,
            "detection": self.detection,
            "file": self.file,
            "effort": self.effort,
        }

@dataclass
class DefensePath:
    path_id: str
    attack_path_name: str
    defense_name: str
    steps: List[DefenseStep]
    total_effort: str
    security_gain: str
    implementation_order: str

    def to_dict(self):
        return {
            "path_id": self.path_id,
            "attack_path_name": self.attack_path_name,
            "defense_name": self.defense_name,
            "steps": [s.to_dict() for s in self.steps],
            "total_effort": self.total_effort,
            "security_gain": self.security_gain,
            "implementation_order": self.implementation_order,
        }

def convert_to_defense(attack_path, healing_plans) -> DefensePath:
    # Convert attack path to defense path
    ap_name = getattr(attack_path, "name", "Unknown Attack")
    
    defense_name_map = {
        "The Silent Bleeder": "The Tourniquet",
        "The Sleeper": "The Wakeup Call",
        "The Impersonator": "The Identity Shield",
    }
    def_name = defense_name_map.get(ap_name, f"{ap_name} Defense")
    
    steps = []
    ap_steps = getattr(attack_path, "steps", [])
    
    for i, step in enumerate(ap_steps):
        target = getattr(step, "target_node", "unknown")
        file_name = target.split("::")[0] if "::" in target else target
        
        d_step = DefenseStep(
            step_number=i+1,
            attack_step_reference=getattr(step, "step_number", i+1),
            threat=getattr(step, "action", "Unknown action"),
            defense=f"Neutralize threat at {target}",
            implementation=f"Add validation and secure access controls in {file_name}",
            detection="Implement logging for unauthorized access attempts.",
            file=file_name,
            effort="20 minutes"
        )
        steps.append(d_step)
        
    return DefensePath(
        path_id=getattr(attack_path, "path_id", "def-path") + "-def",
        attack_path_name=ap_name,
        defense_name=def_name,
        steps=steps,
        total_effort=f"{len(steps) * 20} minutes",
        security_gain=f"Prevents {getattr(attack_path, 'final_impact', 'system compromise')}.",
        implementation_order="Sequential"
    )
