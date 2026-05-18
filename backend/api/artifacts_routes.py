from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rich.console import Console

from backend.api.routes import sessions as infiltration_sessions
from backend.api.evolution_routes import evolution_sessions
from backend.api.revelation_routes import revelation_sessions
from backend.api.symbiotic_routes import symbiotic_sessions
from backend.artifacts.artifacts_engine import generate_artifacts

console = Console()
artifacts_router = APIRouter(prefix="/api")

artifacts_store = {}

class ArtifactsRequest(BaseModel):
    session_id: str

@artifacts_router.post("/artifacts")
async def create_artifacts(request: ArtifactsRequest):
    """Generate autopsy report and mint certificate."""
    sid = request.session_id

    if sid not in revelation_sessions:
        raise HTTPException(status_code=404, detail="Revelation session not found. Cannot generate artifacts.")
    
    # Convert dataclass session objects to dicts for artifact generation
    inf_data = infiltration_sessions.get(sid, {})
    evo_obj = evolution_sessions.get(sid, None)
    rev_obj = revelation_sessions.get(sid, None)
    sym_obj = symbiotic_sessions.get(sid, None)

    full_results = {
        "infiltration": {
            "repo_path": inf_data.get("repo_path", "unknown"),
            "stats": inf_data.get("stats"),
            "feeding_points_raw": inf_data.get("feeding_points_raw", []),
        },
        "evolution": evo_obj.to_dict() if evo_obj and hasattr(evo_obj, 'to_dict') else (evo_obj or {}),
        "revelation": rev_obj.to_dict() if rev_obj and hasattr(rev_obj, 'to_dict') else (rev_obj or {}),
        "symbiotic": sym_obj.to_dict() if sym_obj and hasattr(sym_obj, 'to_dict') else None,
    }

    result = generate_artifacts(
        session_id=sid,
        full_results=full_results
    )

    artifacts_store[sid] = result
    return result.to_dict()

@artifacts_router.get("/artifacts/{session_id}")
async def get_artifacts(session_id: str):
    if session_id not in artifacts_store:
        raise HTTPException(status_code=404, detail="Artifacts not found.")
    return artifacts_store[session_id].to_dict()
