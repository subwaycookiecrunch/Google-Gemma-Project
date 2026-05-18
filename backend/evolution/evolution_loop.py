"""
PARASITE EVOLVED — Evolution Loop Coordinator
Orchestrates the complete evolution sequence from strain initialization to dominant selection.
"""

import os
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from backend.evolution.strains import (
    Strain, StrainStatus, EvolutionSession, initialize_strains, STRAIN_NAMES,
)
from backend.evolution.agents import ParasiteState, run_agent_loop

console = Console()


def run_evolution(session_id: str, feeding_points: list,
                  infiltration_graph=None) -> EvolutionSession:
    """Run the complete evolution loop from feeding points to dominant strain."""

    console.print(Panel.fit(
        "[bold red]🦠 PARASITE EVOLVED — EVOLUTION ENGINE[/bold red]\n"
        f"[dim]Session: {session_id}[/dim]\n"
        "[yellow]Initiating strain cultivation...[/yellow]",
        border_style="red",
    ))

    # Initialize 5 strains from top feeding points
    strains = initialize_strains(feeding_points)

    console.print(f"\n[bold white]Initialized {len(strains)} strains:[/]")
    for s in strains:
        fp = s.target_feeding_point
        target_name = getattr(fp, "name", "unknown")
        target_file = os.path.basename(getattr(fp, "file", "unknown"))
        console.print(
            f"  [cyan]{s.strain_id}[/] → {target_name}() @ {target_file} "
            f"[dim]| initial fitness: {s.fitness_score:.2f}[/]"
        )

    # Build initial state
    state: ParasiteState = {
        "session_id": session_id,
        "infiltration_graph": infiltration_graph,
        "feeding_points": feeding_points,
        "strains": strains,
        "current_generation": 0,
        "evolution_log": [],
        "dominant_strain": None,
        "complete": False,
    }

    # Run the agent loop
    state = run_agent_loop(state)

    # Collect results
    dead_strains = [s for s in state["strains"] if s.status == StrainStatus.DEAD]
    alive_strains = [s for s in state["strains"] if s.status != StrainStatus.DEAD]
    dominant = state.get("dominant_strain")
    final_gen = state["current_generation"]

    # Print dramatic evolution summary
    _print_evolution_summary(
        generation=final_gen,
        dominant=dominant,
        alive_strains=alive_strains,
        dead_strains=dead_strains,
        strains=state["strains"],
    )

    session = EvolutionSession(
        session_id=session_id,
        strains=state["strains"],
        generation=final_gen,
        dominant_strain=dominant,
        dead_strains=dead_strains,
        evolution_log=state["evolution_log"],
        complete=True,
    )

    return session


def _print_evolution_summary(generation: int, dominant: Optional[Strain],
                              alive_strains: list, dead_strains: list,
                              strains: list):
    """Print the dramatic evolution completion summary."""
    console.print("\n")
    console.print("[bold red]═══════════════════════════════════════[/]")
    console.print(f"[bold red]🦠 EVOLUTION COMPLETE — Generation {generation}[/]")
    console.print("[bold red]═══════════════════════════════════════[/]")

    if dominant:
        fp = dominant.target_feeding_point
        target_name = getattr(fp, "name", "unknown")
        target_file = os.path.basename(getattr(fp, "file", "unknown"))
        target_line = getattr(fp, "line", 0)

        console.print(f"[bold green]👑 DOMINANT STRAIN: {dominant.strain_id}[/]")
        console.print(f"[white]🎯 Target: {target_name}() — {target_file}:{target_line}[/]")
        console.print(
            f"[yellow]⚡ Fitness: {dominant.fitness_score:.2f} | "
            f"Stealth: {dominant.stealth_score:.1f} | "
            f"Blast: {dominant.blast_radius_score:.1f} | "
            f"Persist: {dominant.persistence_score:.1f}[/]"
        )

        # Show attack approach history
        approaches = []
        for m in dominant.mutation_history:
            if m.survived and m.approach not in approaches:
                approaches.append(m.approach)
        if approaches:
            console.print(f"[red]☠️  Attack Approach: {' → '.join(approaches)}[/]")

    # Dead strains
    if dead_strains:
        dead_info = ", ".join(
            f"{s.strain_id.split('-')[-1]} ({s.fitness_score:.2f})"
            for s in dead_strains
        )
        console.print(f"[dim red]💀 Dead Strains: {dead_info}[/]")

    # Surviving strains (non-dominant, non-dead)
    surviving = [s for s in strains
                 if s.status != StrainStatus.DEAD
                 and (dominant is None or s.strain_id != dominant.strain_id)]
    if surviving:
        surv_info = ", ".join(
            f"{s.strain_id.split('-')[-1]} ({s.fitness_score:.2f})"
            for s in surviving
        )
        console.print(f"[cyan]🧬 Surviving Strains: {surv_info}[/]")

    console.print("[bold red]═══════════════════════════════════════[/]")
    console.print()

    # Detailed strain table
    table = Table(title="Strain Status Report", border_style="red")
    table.add_column("Strain", style="cyan", width=16)
    table.add_column("Status", width=12)
    table.add_column("Fitness", justify="right", width=8)
    table.add_column("Stealth", justify="right", width=8)
    table.add_column("Blast", justify="right", width=8)
    table.add_column("Persist", justify="right", width=8)
    table.add_column("Mutations", justify="right", width=10)
    table.add_column("Target", width=24)

    for s in strains:
        status_style = {
            StrainStatus.DOMINANT: "[bold green]DOMINANT[/]",
            StrainStatus.ALIVE: "[yellow]ALIVE[/]",
            StrainStatus.DEAD: "[red]DEAD[/]",
            StrainStatus.MUTATING: "[cyan]MUTATING[/]",
        }.get(s.status, str(s.status.value))

        fp = s.target_feeding_point
        target = getattr(fp, "name", "?")

        table.add_row(
            s.strain_id,
            status_style,
            f"{s.fitness_score:.2f}",
            f"{s.stealth_score:.1f}",
            f"{s.blast_radius_score:.1f}",
            f"{s.persistence_score:.1f}",
            str(len(s.mutation_history)),
            target,
        )

    console.print(table)
    console.print()
