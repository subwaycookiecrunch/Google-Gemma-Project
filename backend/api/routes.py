import uuid
import os
import re
import subprocess
import tempfile
import shutil
from fastapi import APIRouter, HTTPException
from rich.console import Console

from backend.api.models import (
    InfiltrateRequest, InfiltrateResponse, GraphData, GraphNode, GraphEdge,
    FeedingPointModel, InfiltrationStats, StatsResponse, FeedingPointsResponse,
)
from backend.core.parser import parse_repository
from backend.core.graph_builder import build_infiltration_graph
from backend.core.feeding_points import detect_feeding_points
from backend.core.progress import progress_store

console = Console()
router = APIRouter(prefix="/api")

# In-memory session store
sessions = {}

# Track cloned repos for cleanup
_cloned_repos = {}


def _is_github_url(path: str) -> bool:
    """Check if the input looks like a GitHub URL."""
    return bool(re.match(r'^https?://(www\.)?github\.com/[\w\-\.]+/[\w\-\.]+', path.strip()))


def _clone_github_repo(url: str) -> str:
    """Clone a GitHub repo to a temp directory and return the path."""
    # Clean up the URL
    url = url.strip().rstrip('/')
    # Remove .git suffix if present for display, add for clone
    clone_url = url if url.endswith('.git') else url + '.git'
    
    # Create a temp directory
    clone_dir = os.path.join(tempfile.gettempdir(), f"parasite_repo_{uuid.uuid4().hex[:8]}")
    
    console.print(f"\n[bold cyan]📡 Cloning repository: {url}[/bold cyan]")
    console.print(f"[dim]   → {clone_dir}[/dim]")
    
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", clone_url, clone_dir],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            raise Exception(f"git clone failed: {result.stderr.strip()}")
        
        console.print(f"[bold green]✅ Repository cloned successfully[/bold green]")
        return clone_dir
    except subprocess.TimeoutExpired:
        raise Exception("Repository clone timed out (60s). Try a smaller repo.")
    except FileNotFoundError:
        raise Exception("git is not installed. Please install git first.")

def _graph_to_json(infiltration_graph) -> GraphData:
    """Convert NetworkX graph to frontend-friendly JSON format."""
    graph = infiltration_graph.graph
    nodes = []
    for node_id, data in graph.nodes(data=True):
        nodes.append(GraphNode(
            id=node_id,
            label=data.get("label", os.path.basename(str(node_id))),
            type=data.get("type", "unknown"),
            layer=data.get("layer", "unknown"),
            file=data.get("file"),
            language=data.get("language"),
            line_start=data.get("line_start"),
            line_end=data.get("line_end"),
            privilege_ops=data.get("privilege_ops"),
            risk_level=data.get("risk_level"),
            is_input_source=data.get("is_input_source", False),
            is_dangerous_sink=data.get("is_dangerous_sink", False),
            weight=data.get("weight"),
        ))

    edges = []
    for src, tgt, data in graph.edges(data=True):
        edges.append(GraphEdge(
            source=src,
            target=tgt,
            type=data.get("type", "unknown"),
            layer=data.get("layer", "unknown"),
            label=data.get("label"),
            weight=data.get("weight"),
            risk_level=data.get("risk_level"),
        ))

    return GraphData(nodes=nodes, edges=edges)


def _feeding_point_to_model(fp) -> FeedingPointModel:
    """Convert FeedingPoint dataclass to Pydantic model."""
    return FeedingPointModel(
        node_id=fp.node_id,
        name=fp.name,
        file=fp.file,
        line=fp.line,
        blast_radius_score=fp.blast_radius_score,
        stealth_score=fp.stealth_score,
        persistence_score=fp.persistence_score,
        final_score=fp.final_score,
        danger_level=fp.danger_level,
        explanation=fp.explanation,
        attack_surfaces=fp.attack_surfaces,
        attack_approach=fp.attack_approach,
    )


@router.post("/infiltrate/start")
async def infiltrate_start(request: InfiltrateRequest):
    """Start infiltration in background. Returns session_id immediately for progress polling."""
    import threading

    raw_path = request.repo_path.strip()

    # Detect GitHub URLs and clone automatically
    if _is_github_url(raw_path):
        try:
            repo_path = _clone_github_repo(raw_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        repo_path = os.path.abspath(raw_path)

    if not os.path.isdir(repo_path):
        raise HTTPException(status_code=400, detail=f"Repository path not found: {repo_path}")

    # Create session ID upfront for progress tracking
    session_id = str(uuid.uuid4())[:12]
    progress_store.create(session_id)

    def _run_scan():
        try:
            console.print("\n[bold red]🦠 PARASITE EVOLVED — Initializing infiltration sequence...[/]\n")

            progress_store.update(session_id, phase="PARSING")
            parsed_files = parse_repository(repo_path, session_id=session_id)
            if not parsed_files:
                progress_store.error(session_id, "No supported source files found")
                return

            progress_store.update(session_id, phase="BUILDING_GRAPH")
            infiltration_graph = build_infiltration_graph(parsed_files)

            progress_store.update(session_id, phase="DETECTING_FEEDING_POINTS")
            feeding_points = detect_feeding_points(infiltration_graph, parsed_files=parsed_files)

            total_priv_ops = sum(
                len(fn.privilege_operations) for pf in parsed_files for fn in pf.functions
            )

            stats = InfiltrationStats(
                files=len(parsed_files),
                functions=sum(len(pf.functions) for pf in parsed_files),
                edges=infiltration_graph.stats.total_edges,
                privilege_ops=total_priv_ops,
                dataflow_paths=infiltration_graph.stats.dataflow_paths,
                critical_ops=infiltration_graph.stats.critical_ops,
            )

            graph_data = _graph_to_json(infiltration_graph)
            fp_models = [_feeding_point_to_model(fp) for fp in feeding_points]

            sessions[session_id] = {
                "repo_path": repo_path,
                "stats": stats,
                "graph": graph_data,
                "feeding_points": fp_models,
                "feeding_points_raw": feeding_points,
                "parsed_files": parsed_files,
                "infiltration_graph": infiltration_graph,
            }

            progress_store.complete(session_id)
            console.print(f"\n[bold green]👑 Infiltration complete. {len(feeding_points)} feeding points mapped.[/]\n")

        except Exception as e:
            console.print(f"[bold red]❌ Scan error: {e}[/]")
            progress_store.error(session_id, str(e))

    # Run scan in background thread
    thread = threading.Thread(target=_run_scan, daemon=True)
    thread.start()

    return {"session_id": session_id, "status": "started"}


@router.get("/infiltrate/result/{session_id}")
async def infiltrate_result(session_id: str):
    """Get infiltration results after background scan completes."""
    progress = progress_store.get(session_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Session not found")

    if not progress.complete:
        return {"session_id": session_id, "status": "scanning", "progress": progress.to_dict()}

    if progress.error:
        raise HTTPException(status_code=400, detail=progress.error)

    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session results not ready yet")

    data = sessions[session_id]
    return InfiltrateResponse(
        session_id=session_id,
        stats=data["stats"],
        graph=data["graph"],
        feeding_points=data["feeding_points"],
        infiltration_complete=True,
    )


@router.post("/infiltrate", response_model=InfiltrateResponse)
async def infiltrate(request: InfiltrateRequest):
    """Execute full infiltration pipeline: parse → graph → feeding points (blocking)."""
    raw_path = request.repo_path.strip()
    
    # Detect GitHub URLs and clone automatically
    if _is_github_url(raw_path):
        try:
            repo_path = _clone_github_repo(raw_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        repo_path = os.path.abspath(raw_path)

    if not os.path.isdir(repo_path):
        raise HTTPException(status_code=400, detail=f"Repository path not found: {repo_path}")

    console.print("\n[bold red]🦠 PARASITE EVOLVED — Initializing infiltration sequence...[/]\n")

    # Create session ID upfront for progress tracking
    session_id = str(uuid.uuid4())[:12]
    progress_store.create(session_id)

    # Phase 1: Parse (with progress tracking)
    progress_store.update(session_id, phase="PARSING")
    parsed_files = parse_repository(repo_path, session_id=session_id)
    if not parsed_files:
        progress_store.error(session_id, "No supported source files found")
        raise HTTPException(status_code=400, detail="No supported source files found in repository")

    # Phase 2: Build graph
    progress_store.update(session_id, phase="BUILDING_GRAPH")
    infiltration_graph = build_infiltration_graph(parsed_files)

    # Phase 3: Detect feeding points
    progress_store.update(session_id, phase="DETECTING_FEEDING_POINTS")
    feeding_points = detect_feeding_points(infiltration_graph, parsed_files=parsed_files)

    # Store session
    total_priv_ops = sum(
        len(fn.privilege_operations) for pf in parsed_files for fn in pf.functions
    )

    stats = InfiltrationStats(
        files=len(parsed_files),
        functions=sum(len(pf.functions) for pf in parsed_files),
        edges=infiltration_graph.stats.total_edges,
        privilege_ops=total_priv_ops,
        dataflow_paths=infiltration_graph.stats.dataflow_paths,
        critical_ops=infiltration_graph.stats.critical_ops,
    )

    graph_data = _graph_to_json(infiltration_graph)
    fp_models = [_feeding_point_to_model(fp) for fp in feeding_points]

    sessions[session_id] = {
        "repo_path": repo_path,
        "stats": stats,
        "graph": graph_data,
        "feeding_points": fp_models,
        "feeding_points_raw": feeding_points,
        "parsed_files": parsed_files,
        "infiltration_graph": infiltration_graph,
    }

    # Mark progress complete
    progress_store.complete(session_id)

    console.print(f"\n[bold green]👑 Infiltration complete. {len(feeding_points)} feeding points mapped.[/]")
    console.print(f"[bold red]💀 Host has {infiltration_graph.stats.critical_ops} critical vulnerabilities. Parasite is ready to evolve.[/]\n")

    return InfiltrateResponse(
        session_id=session_id,
        stats=stats,
        graph=graph_data,
        feeding_points=fp_models,
        infiltration_complete=True,
    )


@router.get("/progress/{session_id}")
async def get_progress(session_id: str):
    """Return real-time scan progress for a session."""
    progress = progress_store.get(session_id)
    if not progress:
        return {
            "session_id": session_id,
            "phase": "NOT_FOUND",
            "percent": 0,
            "total_files": 0,
            "files_scanned": 0,
            "current_file": "",
            "functions_found": 0,
            "privilege_ops_found": 0,
            "elapsed_seconds": 0,
            "eta_seconds": 0,
            "complete": False,
            "error": None,
        }
    return progress.to_dict()


@router.get("/graph/{session_id}")
async def get_graph(session_id: str):
    """Return full graph JSON for 3D visualization."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    data = sessions[session_id]
    return {"session_id": session_id, "graph": data["graph"]}


@router.get("/feeding-points/{session_id}", response_model=FeedingPointsResponse)
async def get_feeding_points(session_id: str):
    """Return ranked feeding points with full details."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    data = sessions[session_id]
    return FeedingPointsResponse(
        session_id=session_id,
        feeding_points=data["feeding_points"],
        count=len(data["feeding_points"]),
    )


@router.get("/stats/{session_id}", response_model=StatsResponse)
async def get_stats(session_id: str):
    """Return infiltration statistics."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return StatsResponse(session_id=session_id, stats=sessions[session_id]["stats"])
