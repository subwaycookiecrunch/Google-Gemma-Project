"""
PARASITE EVOLVED — Revelation API Routes
Endpoints for running and querying the revelation engine.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rich.console import Console

from backend.api.routes import sessions as infiltration_sessions
from backend.api.evolution_routes import evolution_sessions
from backend.revelation.revelation_engine import run_revelation

console = Console()
revelation_router = APIRouter(prefix="/api")

# Revelation session store
revelation_sessions = {}


class RevealRequest(BaseModel):
    session_id: str


@revelation_router.post("/reveal")
async def reveal(request: RevealRequest):
    """Run full revelation sequence against existing evolution results."""
    sid = request.session_id

    if sid not in evolution_sessions:
        raise HTTPException(status_code=404, detail=f"Evolution session '{sid}' not found. Run /api/evolve first.")
    if sid not in infiltration_sessions:
        raise HTTPException(status_code=404, detail=f"Infiltration session '{sid}' not found.")

    evo_session = evolution_sessions[sid]
    inf_data = infiltration_sessions[sid]

    feeding_points = inf_data.get("feeding_points_raw", [])
    infiltration_graph = inf_data.get("infiltration_graph")
    parsed_files = inf_data.get("parsed_files")

    result = run_revelation(
        session_id=sid,
        evolution_session=evo_session,
        feeding_points=feeding_points,
        infiltration_graph=infiltration_graph,
        parsed_files=parsed_files,
    )

    revelation_sessions[sid] = result
    return result.to_dict()


@revelation_router.get("/attack-paths/{session_id}")
async def get_attack_paths(session_id: str):
    """Return all 3 attack paths with full steps."""
    if session_id not in revelation_sessions:
        raise HTTPException(status_code=404, detail="Revelation session not found. Run /api/reveal first.")
    result = revelation_sessions[session_id]
    return {
        "session_id": session_id,
        "attack_paths": [p.to_dict() for p in result.attack_paths],
        "count": len(result.attack_paths),
    }


@revelation_router.get("/kill-simulation/{session_id}")
async def get_kill_simulation(session_id: str):
    """Return kill simulation timeline and events."""
    if session_id not in revelation_sessions:
        raise HTTPException(status_code=404, detail="Revelation session not found. Run /api/reveal first.")
    result = revelation_sessions[session_id]
    return {
        "session_id": session_id,
        "kill_simulation": result.kill_simulation.to_dict(),
    }


@revelation_router.get("/time-to-impact/{session_id}")
async def get_time_to_impact(session_id: str):
    """Return time prediction and survival curve data."""
    if session_id not in revelation_sessions:
        raise HTTPException(status_code=404, detail="Revelation session not found. Run /api/reveal first.")
    result = revelation_sessions[session_id]
    return {
        "session_id": session_id,
        "time_to_impact": result.time_to_impact.to_dict(),
    }


@revelation_router.get("/final-verdict/{session_id}")
async def get_final_verdict(session_id: str):
    """Return PARASITE's dramatic closing statement."""
    if session_id not in revelation_sessions:
        raise HTTPException(status_code=404, detail="Revelation session not found. Run /api/reveal first.")
    result = revelation_sessions[session_id]
    return {
        "session_id": session_id,
        "dominant_strain": result.dominant_strain_id,
        "dominant_target": result.dominant_target,
        "final_verdict": result.final_verdict,
    }
