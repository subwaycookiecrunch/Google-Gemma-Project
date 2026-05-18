from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rich.console import Console

from backend.api.routes import sessions as infiltration_sessions
from backend.api.revelation_routes import revelation_sessions
from backend.symbiotic.symbiotic_engine import run_symbiotic

console = Console()
symbiotic_router = APIRouter(prefix="/api")

# Symbiotic session store
symbiotic_sessions = {}

class SymbioticRequest(BaseModel):
    session_id: str

@symbiotic_router.post("/symbiotic")
async def symbiotic(request: SymbioticRequest):
    """Run full symbiotic sequence against existing revelation results."""
    sid = request.session_id

    if sid not in revelation_sessions:
        raise HTTPException(status_code=404, detail="Revelation session not found. Run /api/reveal first.")
    
    rev_result = revelation_sessions[sid]
    inf_data = infiltration_sessions.get(sid, {})
    feeding_points = inf_data.get("feeding_points_raw", [])

    result = run_symbiotic(
        session_id=sid,
        revelation_result=rev_result,
        feeding_points=feeding_points
    )

    symbiotic_sessions[sid] = result
    return result.to_dict()

@symbiotic_router.get("/healing-plans/{session_id}")
async def get_healing_plans(session_id: str):
    if session_id not in symbiotic_sessions:
        raise HTTPException(status_code=404, detail="Symbiotic session not found.")
    return {"healing_plans": [p.to_dict() for p in symbiotic_sessions[session_id].healing_plans]}

@symbiotic_router.get("/defense-paths/{session_id}")
async def get_defense_paths(session_id: str):
    if session_id not in symbiotic_sessions:
        raise HTTPException(status_code=404, detail="Symbiotic session not found.")
    return {"defense_paths": [p.to_dict() for p in symbiotic_sessions[session_id].defense_paths]}

@symbiotic_router.get("/hardening-guide/{session_id}")
async def get_hardening_guide(session_id: str):
    if session_id not in symbiotic_sessions:
        raise HTTPException(status_code=404, detail="Symbiotic session not found.")
    return {"hardening_guide": symbiotic_sessions[session_id].hardening_guide.to_dict()}

@symbiotic_router.get("/symbiotic-verdict/{session_id}")
async def get_symbiotic_verdict(session_id: str):
    if session_id not in symbiotic_sessions:
        raise HTTPException(status_code=404, detail="Symbiotic session not found.")
    return {"symbiotic_verdict": symbiotic_sessions[session_id].hardening_guide.symbiotic_verdict}
