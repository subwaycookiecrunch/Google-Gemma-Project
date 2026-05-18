"""
PARASITE EVOLVED — Pydantic Data Models for API
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class InfiltrateRequest(BaseModel):
    repo_path: str = Field(..., description="Absolute path to target repository")


class PrivilegeOpModel(BaseModel):
    type: str
    line: int
    code_snippet: str
    risk_level: str


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    layer: str
    file: Optional[str] = None
    language: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    privilege_ops: Optional[List[Dict[str, Any]]] = None
    risk_level: Optional[str] = None
    is_input_source: Optional[bool] = False
    is_dangerous_sink: Optional[bool] = False
    weight: Optional[float] = None


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str
    layer: str
    label: Optional[str] = None
    weight: Optional[float] = None
    risk_level: Optional[str] = None


class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class FeedingPointModel(BaseModel):
    node_id: str
    name: str
    file: str
    line: int
    blast_radius_score: float
    stealth_score: float
    persistence_score: float
    final_score: float
    danger_level: str
    explanation: str
    attack_surfaces: List[str]
    attack_approach: str


class InfiltrationStats(BaseModel):
    files: int
    functions: int
    edges: int
    privilege_ops: int
    dataflow_paths: int
    critical_ops: int


class InfiltrateResponse(BaseModel):
    session_id: str
    stats: InfiltrationStats
    graph: GraphData
    feeding_points: List[FeedingPointModel]
    infiltration_complete: bool


class StatsResponse(BaseModel):
    session_id: str
    stats: InfiltrationStats


class FeedingPointsResponse(BaseModel):
    session_id: str
    feeding_points: List[FeedingPointModel]
    count: int
