"""
PARASITE EVOLVED — LangGraph Multi-Agent Orchestration
4 agents: Scout, Mutator, Validator, Overseer — orchestrated in a directed graph.
"""

from typing import TypedDict, List, Optional, Any
from datetime import datetime
from rich.console import Console

from backend.evolution.strains import Strain, StrainStatus, EvolutionSession, APPROACH_SEQUENCE
from backend.evolution.mutation import mutate_strain
from backend.evolution.fitness import calculate_fitness

console = Console()


class ParasiteState(TypedDict):
    session_id: str
    infiltration_graph: Any
    feeding_points: list
    strains: List[Any]
    current_generation: int
    evolution_log: List[str]
    dominant_strain: Any
    complete: bool


def _log(state: ParasiteState, message: str):
    """Append timestamped message to evolution log."""
    ts = datetime.utcnow().strftime("%H:%M:%S")
    entry = f"[{ts}] {message}"
    state["evolution_log"].append(entry)


def agent_scout(state: ParasiteState) -> ParasiteState:
    """SCOUT — Maps unexplored attack surfaces and updates strain targets."""
    gen = state["current_generation"]
    approach = APPROACH_SEQUENCE.get(gen, "LOGIC_BOMB")

    console.print(f"\n[bold magenta]🔍 Scout mapping unexplored territories... Generation {gen}[/]")
    _log(state, f"🔍 Scout activated — Generation {gen}")
    _log(state, f"🔍 Scanning for {approach} attack vectors...")

    alive_strains = [s for s in state["strains"] if s.status in (StrainStatus.ALIVE, StrainStatus.DOMINANT)]

    for strain in alive_strains:
        strain.attack_approach = approach
        strain.status = StrainStatus.MUTATING
        fp = strain.target_feeding_point
        target_name = getattr(fp, "name", "unknown")
        _log(state, f"🔍 {strain.strain_id} locked onto {target_name} — vector: {approach}")

    console.print(f"[magenta]  ↳ {len(alive_strains)} strains targeted for {approach} mutation[/]")
    _log(state, f"🔍 Scout complete. {len(alive_strains)} active targets identified.")

    return state


def agent_mutator(state: ParasiteState) -> ParasiteState:
    """MUTATOR — Runs mutation engine for each alive strain."""
    gen = state["current_generation"]

    console.print(f"\n[bold green]🧬 Mutator initiating genetic cascade... Generation {gen}[/]")
    _log(state, f"🧬 Mutator activated — initiating genetic cascade")

    mutating_strains = [s for s in state["strains"] if s.status == StrainStatus.MUTATING]

    for strain in mutating_strains:
        _log(state, f"🧬 Mutating {strain.strain_id}...")
        records = mutate_strain(strain, gen)
        strain.mutation_history.extend(records)

        # Keep the best surviving variant
        surviving = [r for r in records if r.survived]
        if surviving:
            best = max(surviving, key=lambda r: r.fitness_after)
            strain.camouflage_code = best.code_generated
            strain.fitness_score = best.fitness_after
            strain.last_mutated_at = datetime.utcnow()
            _log(state, f"🧬 {strain.strain_id} best variant: {best.mutation_id} fitness={best.fitness_after:.2f}")
        else:
            _log(state, f"🧬 {strain.strain_id} — all variants failed this generation")

    _log(state, f"🧬 Mutator complete. {len(mutating_strains)} strains processed.")
    return state


def agent_validator(state: ParasiteState) -> ParasiteState:
    """VALIDATOR — Enforces natural selection: kill weak, promote strong."""
    console.print(f"\n[bold yellow]⚖️  Validator enforcing natural selection...[/]")
    _log(state, f"⚖️  Validator activated — enforcing selection pressure")

    for strain in state["strains"]:
        if strain.status == StrainStatus.DEAD:
            continue

        # Re-evaluate fitness with current camouflage code
        if strain.camouflage_code:
            fitness = calculate_fitness(strain, mutation_code=strain.camouflage_code)
            strain.fitness_score = fitness.combined
            strain.stealth_score = fitness.stealth
            strain.blast_radius_score = fitness.blast_radius
            strain.persistence_score = fitness.persistence

        # Apply selection thresholds
        if strain.fitness_score < 0.3:
            strain.status = StrainStatus.DEAD
            console.print(f"[red]  ☠️  {strain.strain_id} TERMINATED — fitness {strain.fitness_score:.2f}[/]")
            _log(state, f"☠️  {strain.strain_id} terminated. Fitness {strain.fitness_score:.2f} — too weak to survive.")
        elif strain.fitness_score >= 0.8:
            strain.status = StrainStatus.DOMINANT
            console.print(f"[bold green]  👑 {strain.strain_id} DOMINANT — fitness {strain.fitness_score:.2f}[/]")
            _log(state, f"👑 {strain.strain_id} achieves DOMINANT status! Fitness: {strain.fitness_score:.2f}")
        elif strain.fitness_score >= 0.6:
            strain.status = StrainStatus.ALIVE
            console.print(f"[yellow]  ⚡ {strain.strain_id} STRONG — fitness {strain.fitness_score:.2f}[/]")
            _log(state, f"⚡ {strain.strain_id} rated STRONG. Fitness: {strain.fitness_score:.2f}")
        else:
            strain.status = StrainStatus.ALIVE
            console.print(f"[cyan]  🧬 {strain.strain_id} ALIVE — fitness {strain.fitness_score:.2f}[/]")
            _log(state, f"🧬 {strain.strain_id} survives. Fitness: {strain.fitness_score:.2f}")

    alive = sum(1 for s in state["strains"] if s.status != StrainStatus.DEAD)
    dead = sum(1 for s in state["strains"] if s.status == StrainStatus.DEAD)
    _log(state, f"⚖️  Validator complete. {alive} alive, {dead} terminated.")

    return state


def agent_overseer(state: ParasiteState) -> ParasiteState:
    """OVERSEER — Decides if evolution is complete or needs to continue."""
    gen = state["current_generation"]

    console.print(f"\n[bold white]👁️  Overseer observing the evolution... Generation {gen}[/]")
    _log(state, f"👁️  Overseer evaluation — Generation {gen}")

    alive_strains = [s for s in state["strains"] if s.status != StrainStatus.DEAD]
    dominant = [s for s in state["strains"] if s.status == StrainStatus.DOMINANT]

    if dominant:
        best = max(dominant, key=lambda s: s.fitness_score)
        state["dominant_strain"] = best
        state["complete"] = True
        _log(state, f"👁️  DOMINANT STRAIN IDENTIFIED: {best.strain_id} — fitness {best.fitness_score:.2f}")
        _log(state, f"👁️  Evolution COMPLETE at Generation {gen}.")
        console.print(f"[bold green]  👁️  Evolution complete! Dominant: {best.strain_id}[/]")
        return state

    if gen >= 2:
        # Force selection after generation 3 (0-indexed)
        if alive_strains:
            best = max(alive_strains, key=lambda s: s.fitness_score)
            best.status = StrainStatus.DOMINANT
            state["dominant_strain"] = best
            state["complete"] = True
            _log(state, f"👁️  Max generations reached. Forcing dominant: {best.strain_id} — fitness {best.fitness_score:.2f}")
            console.print(f"[bold yellow]  👁️  Forced dominant selection: {best.strain_id}[/]")
        else:
            state["complete"] = True
            _log(state, f"👁️  All strains terminated. Evolution failed.")
            console.print(f"[bold red]  👁️  All strains dead. Evolution collapsed.[/]")
        return state

    # Continue evolution
    state["current_generation"] = gen + 1
    _log(state, f"👁️  Evolution continues to Generation {gen + 1}...")
    console.print(f"[white]  👁️  Advancing to Generation {gen + 1}...[/]")
    state["complete"] = False

    return state


def run_agent_loop(state: ParasiteState) -> ParasiteState:
    """Execute the full LangGraph-style agent loop: Scout→Mutator→Validator→Overseer."""
    max_generations = 3

    _log(state, "═══════════════════════════════════════")
    _log(state, "🦠 EVOLUTION ENGINE ACTIVATED")
    _log(state, "═══════════════════════════════════════")

    while not state["complete"] and state["current_generation"] < max_generations:
        gen = state["current_generation"]
        _log(state, f"")
        _log(state, f"━━━ GENERATION {gen} ━━━")

        state = agent_scout(state)
        state = agent_mutator(state)
        state = agent_validator(state)
        state = agent_overseer(state)

    # If not yet complete after loop exits, force it
    if not state["complete"]:
        alive = [s for s in state["strains"] if s.status != StrainStatus.DEAD]
        if alive:
            best = max(alive, key=lambda s: s.fitness_score)
            best.status = StrainStatus.DOMINANT
            state["dominant_strain"] = best
        state["complete"] = True
        _log(state, "👁️  Evolution forcefully concluded.")

    return state
