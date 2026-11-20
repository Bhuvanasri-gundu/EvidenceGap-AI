"""API router for research gaps, knowledge graph, and retrieval."""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.persistence.database import get_session_dep
from backend.services.research_service import ResearchService
from backend.schemas.requests import RetrievalRequest
from backend.schemas.responses import GapResponse, KnowledgeGraphData, RetrievalResponse

router = APIRouter(prefix="/research", tags=["Research"])


@router.get("/gaps", response_model=list[GapResponse])
async def list_gaps(
    run_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session_dep),
) -> list[GapResponse]:
    """List discovered research gaps, optionally filtered by run."""
    service = ResearchService(session)
    return await service.list_gaps(run_id=run_id, limit=limit)


@router.get("/gaps/{gap_id}", response_model=GapResponse)
async def get_gap(
    gap_id: str,
    session: AsyncSession = Depends(get_session_dep),
) -> GapResponse:
    """Get research gap detail by ID."""
    service = ResearchService(session)
    gap = await service.get_gap(gap_id)
    if not gap:
        raise HTTPException(status_code=404, detail=f"Research gap {gap_id} not found")
    return gap


@router.get("/knowledge-graph", response_model=KnowledgeGraphData)
async def get_knowledge_graph(
    run_id: Optional[str] = Query(None),
    max_nodes: int = Query(100, ge=10, le=500),
    session: AsyncSession = Depends(get_session_dep),
) -> KnowledgeGraphData:
    """Get knowledge graph nodes and edges for visualization."""
    service = ResearchService(session)
    return await service.get_knowledge_graph(run_id=run_id, max_nodes=max_nodes)


@router.post("/retrieve", response_model=RetrievalResponse)
async def retrieve_passages(
    req: RetrievalRequest,
    session: AsyncSession = Depends(get_session_dep),
) -> RetrievalResponse:
    """Perform semantic / ontology-guided retrieval over corpus passages."""
    service = ResearchService(session)
    return await service.retrieve(
        query=req.query,
        top_k=req.top_k,
        use_ontology=req.use_ontology,
        filters=req.filters,
    )
