"""API router for corpus statistics, documents, and MeSH terms."""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.persistence.database import get_session_dep
from backend.services.corpus_service import CorpusService
from backend.services.research_service import ResearchService
from backend.schemas.responses import (
    CorpusStatsResponse,
    DocumentResponse,
    MeshTermSummary,
    PaginatedResponse,
    TopicResponse,
)

router = APIRouter(prefix="/corpus", tags=["Corpus"])


@router.get("", response_model=CorpusStatsResponse)
@router.get("/", response_model=CorpusStatsResponse)
@router.get("/stats", response_model=CorpusStatsResponse)
async def get_corpus_stats(
    session: AsyncSession = Depends(get_session_dep),
) -> CorpusStatsResponse:
    """Return high-level corpus statistics."""
    service = CorpusService(session)
    return await service.get_stats()


@router.get("/documents", response_model=PaginatedResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    journal: Optional[str] = Query(None),
    source_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session_dep),
) -> PaginatedResponse:
    """Return paginated list of corpus documents."""
    service = CorpusService(session)
    return await service.list_documents(
        page=page,
        page_size=page_size,
        journal=journal,
        source_type=source_type,
        search=search,
    )


@router.get("/documents/{pmid}", response_model=DocumentResponse)
async def get_document(
    pmid: str,
    session: AsyncSession = Depends(get_session_dep),
) -> DocumentResponse:
    """Get a single document by PMID."""
    service = CorpusService(session)
    doc = await service.get_document_by_pmid(pmid)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document with PMID {pmid} not found")
    return doc


@router.get("/topics", response_model=list[TopicResponse])
async def list_topics(
    run_id: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session_dep),
) -> list[TopicResponse]:
    """List topics discovered by topic modeling."""
    service = ResearchService(session)
    return await service.list_topics(run_id=run_id)


@router.get("/topics/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: int,
    run_id: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session_dep),
) -> TopicResponse:
    """Get topic details by topic ID."""
    service = ResearchService(session)
    topic = await service.get_topic_by_id(topic_id, run_id=run_id)
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found")
    return topic


@router.get("/mesh-terms", response_model=list[MeshTermSummary])
async def get_mesh_terms(
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session_dep),
) -> list[MeshTermSummary]:
    """Get top MeSH terms aggregated across the corpus."""
    service = CorpusService(session)
    return await service.get_mesh_summary(top_n=limit)
