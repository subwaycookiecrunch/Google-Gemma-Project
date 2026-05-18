"""
PARASITE EVOLVED — Evolution API Routes
Endpoints for running and querying the evolution engine.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from rich.console import Console

from backend.api.routes import sessions as infiltration_sessions
from backend.evolution.evolution_loop import run_evolution
from backend.evolution.strains import StrainStatus

console = Console()
evolution_router = APIRouter(prefix="/api")

# Evolution session store
evolution_sessions = {}


class EvolveRequest(BaseModel):
    session_id: str


@evolution_router.post("/evolve")
async def evolve(request: EvolveRequest):
    """Run full evolution loop against existing infiltration results."""
    sid = request.session_id

    if sid not in infiltration_sessions:
        raise HTTPException(status_code=404, detail=f"Infiltration session '{sid}' not found. Run /api/infiltrate first.")

    inf_data = infiltration_sessions[sid]

    # Use raw feeding point dataclasses (not Pydantic models) for evolution
    feeding_points = inf_data.get("feeding_points_raw", [])
    infiltration_graph = inf_data.get("infiltration_graph")

    if not feeding_points:
        raise HTTPException(status_code=400, detail="No feeding points found in session. Re-run infiltration.")

    # Run evolution
    evo_session = run_evolution(
        session_id=sid,
        feeding_points=feeding_points,
        infiltration_graph=infiltration_graph,
    )

    evolution_sessions[sid] = evo_session
    return evo_session.to_dict()


@evolution_router.get("/evolution/{session_id}")
async def get_evolution(session_id: str):
    """Return current evolution session state."""
    if session_id not in evolution_sessions:
        raise HTTPException(status_code=404, detail="Evolution session not found")
    return evolution_sessions[session_id].to_dict()


@evolution_router.get("/strains/{session_id}")
async def get_strains(session_id: str):
    """Return all strains with status and fitness scores."""
    if session_id not in evolution_sessions:
        raise HTTPException(status_code=404, detail="Evolution session not found")

    evo = evolution_sessions[session_id]
    return {
        "session_id": session_id,
        "generation": evo.generation,
        "strain_count": len(evo.strains),
        "alive": sum(1 for s in evo.strains if s.status != StrainStatus.DEAD),
        "dead": sum(1 for s in evo.strains if s.status == StrainStatus.DEAD),
        "strains": [s.to_dict() for s in evo.strains],
    }


@evolution_router.get("/dominant/{session_id}")
async def get_dominant(session_id: str):
    """Return dominant strain full details + mutation history."""
    if session_id not in evolution_sessions:
        raise HTTPException(status_code=404, detail="Evolution session not found")

    evo = evolution_sessions[session_id]
    if not evo.dominant_strain:
        raise HTTPException(status_code=404, detail="No dominant strain found — evolution may have failed")

    return {
        "session_id": session_id,
        "dominant": evo.dominant_strain.to_dict(),
        "generation": evo.generation,
        "total_mutations": len(evo.dominant_strain.mutation_history),
        "survived_mutations": sum(1 for m in evo.dominant_strain.mutation_history if m.survived),
    }


@evolution_router.get("/evolution-log/{session_id}")
async def get_evolution_log(session_id: str):
    """Return dark themed evolution narrative log."""
    if session_id not in evolution_sessions:
        raise HTTPException(status_code=404, detail="Evolution session not found")

    evo = evolution_sessions[session_id]
    return {
        "session_id": session_id,
        "generation": evo.generation,
        "complete": evo.complete,
        "log_entries": evo.evolution_log,
        "entry_count": len(evo.evolution_log),
    }
