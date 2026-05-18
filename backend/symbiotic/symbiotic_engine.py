import os
from dataclasses import dataclass
from rich.console import Console

from backend.symbiotic.healer import heal_feeding_point, HealingPlan
from backend.symbiotic.defense_paths import convert_to_defense, DefensePath
from backend.symbiotic.hardening_guide import generate_hardening_guide, HardeningGuide

console = Console()

@dataclass
class SymbioticResult:
    session_id: str
    healing_plans: list
    defense_paths: list
    hardening_guide: HardeningGuide
    mode: str = "SYMBIOTIC"
    complete: bool = True

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "healing_plans": [p.to_dict() for p in self.healing_plans],
            "defense_paths": [p.to_dict() for p in self.defense_paths],
            "hardening_guide": self.hardening_guide.to_dict(),
            "mode": self.mode,
            "complete": self.complete,
        }

def run_symbiotic(session_id: str, revelation_result, feeding_points: list) -> SymbioticResult:
    console.print("\n[bold green]💚 PARASITE ENTERING SYMBIOTIC MODE...[/bold green]")
    
    # 1. Healing Plans
    healing_plans = []
    for i, fp in enumerate(feeding_points):
        fp_name = getattr(fp, "name", "unknown")
        console.print(f"[dim green]🔬 Analyzing wound: {fp_name}[/dim green]")
        plan = heal_feeding_point(fp, priority=i+1)
        healing_plans.append(plan)
        console.print(f"[green]💊 Healing plan generated: {plan.vulnerability_name}[/green]")
        
    # 2. Defense Paths
    defense_paths = []
    for attack_path in revelation_result.attack_paths:
        console.print(f"[dim green]🛡️  Converting attack path to defense: {attack_path.name}[/dim green]")
        d_path = convert_to_defense(attack_path, healing_plans)
        defense_paths.append(d_path)
        
    # 3. Hardening Guide
    console.print("[dim green]📋 Generating hardening guide...[/dim green]")
    guide = generate_hardening_guide(session_id, healing_plans, defense_paths)
    
    console.print("[bold green]💚 SYMBIOTIC SEQUENCE COMPLETE.[/bold green]")
    console.print(f"[green]🌱 {len(feeding_points)} wounds identified. {len(healing_plans)} cures prescribed.[/green]\n")
    
    return SymbioticResult(
        session_id=session_id,
        healing_plans=healing_plans,
        defense_paths=defense_paths,
        hardening_guide=guide
    )
