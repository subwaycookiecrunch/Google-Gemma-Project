"""
PARASITE EVOLVED — FastAPI Application Entry Point
🦠 Biological-inspired AI parasite for codebase infiltration analysis.
"""

import os
import asyncio
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from backend.api.routes import router
from backend.api.evolution_routes import evolution_router
from backend.api.revelation_routes import revelation_router
from backend.api.symbiotic_routes import symbiotic_router
from backend.api.artifacts_routes import artifacts_router

load_dotenv()
console = Console()

app = FastAPI(
    title="PARASITE EVOLVED",
    description="Biological-inspired AI parasite that infiltrates codebases and reveals lethal attack paths.",
    version="1.0.0",
)

# CORS for frontend
origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(evolution_router)
app.include_router(revelation_router)
app.include_router(symbiotic_router)
app.include_router(artifacts_router)


@app.on_event("startup")
async def startup():
    console.print(Panel.fit(
        "[bold red]🦠 PARASITE EVOLVED[/bold red]\n"
        "[dim]Infiltration + Evolution + Revelation + Symbiotic + Artifacts v6.0.0[/dim]\n"
        "[cyan]Powered by Gemma 4 (27B-IT) | Safety & Trust[/cyan]\n"
        "[yellow]Awaiting host target...[/yellow]",
        border_style="red",
    ))
    
    if not os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY") == "your_key_here":
        console.print("[bold yellow]⚠️ WARNING: GEMINI_API_KEY not set. Gemma 4 will run in offline fallback mode.[/bold yellow]")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    console.print(f"[bold red]Global Exception:[/bold red] {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"An internal server error occurred: {str(exc)}"}
    )

@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    # POST endpoints that call Claude can take 60+ seconds
    timeout = 120.0 if request.method == "POST" else 30.0
    try:
        return await asyncio.wait_for(call_next(request), timeout=timeout)
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=504,
            content={"detail": f"Request timed out after {timeout} seconds"}
        )

@app.get("/api/health")
async def health_check():
    return {"status": "alive", "version": "EVOLVED"}


@app.get("/")
async def root():
    return {
        "name": "PARASITE EVOLVED",
        "version": "5.0.0",
        "status": "alive",
        "endpoints": [
            "POST /api/infiltrate",
            "POST /api/evolve",
            "POST /api/reveal",
            "POST /api/symbiotic",
            "POST /api/artifacts",
            "GET /api/graph/{session_id}",
            "GET /api/feeding-points/{session_id}",
            "GET /api/stats/{session_id}",
            "GET /api/evolution/{session_id}",
            "GET /api/strains/{session_id}",
            "GET /api/dominant/{session_id}",
            "GET /api/evolution-log/{session_id}",
            "GET /api/attack-paths/{session_id}",
            "GET /api/kill-simulation/{session_id}",
            "GET /api/time-to-impact/{session_id}",
            "GET /api/final-verdict/{session_id}",
            "GET /api/healing-plans/{session_id}",
            "GET /api/defense-paths/{session_id}",
            "GET /api/hardening-guide/{session_id}",
            "GET /api/symbiotic-verdict/{session_id}",
            "GET /api/artifacts/{session_id}",
        ],
    }
