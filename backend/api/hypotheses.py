"""API router for hypothesis generation, challenge, refinement, and ranking."""

from __future__ import annotations

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.jobs.task_manager import task_manager
from backend.persistence.database import get_session, get_session_dep
from backend.services.hypothesis_service import HypothesisService
from backend.schemas.requests import GenerateHypothesesRequest, RefineRequest
from backend.schemas.responses import (
    HypothesisResponse,
    RunDetailResponse,
    RunResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hypotheses", tags=["Hypotheses"])


async def _run_pipeline_background(run_id: str) -> None:
    """Background task runner with dedicated session."""
    async with get_session() as session:
        service = HypothesisService(session)
        await service.run_pipeline(run_id)


@router.post("/generate", response_model=RunResponse)
@router.post("/runs", response_model=RunResponse)
async def generate_hypotheses(
    req: GenerateHypothesesRequest,
    session: AsyncSession = Depends(get_session_dep),
) -> RunResponse:
    """Start an asynchronous hypothesis generation run."""
    service = HypothesisService(session)
    theme = req.effective_theme or "mHealth research exploration"
    obj = req.effective_objective
    run = await service.create_run(
        research_theme=theme,
        target_population=req.target_population,
        objective=obj,
        num_hypotheses=req.num_hypotheses,
    )

    # Spawn background pipeline execution
    task_manager.spawn(run.id, _run_pipeline_background, run.id)

    return RunResponse(
        id=run.id,
        run_id=run.id,
        status=run.status.value,
        research_theme=run.research_theme,
        theme=run.research_theme,
        target_population=run.target_population,
        objective=run.objective,
        research_objective=run.objective,
        num_hypotheses=run.num_hypotheses,
        created_at=run.created_at,
        updated_at=run.updated_at,
        hypothesis_count=0,
        error=None,
    )


@router.get("/runs", response_model=list[RunResponse])
async def list_runs(
    session: AsyncSession = Depends(get_session_dep),
) -> list[RunResponse]:
    """List all hypothesis generation runs."""
    service = HypothesisService(session)
    return await service.list_runs()


@router.get("/runs/{run_id}", response_model=RunDetailResponse)
async def get_run_detail(
    run_id: str,
    session: AsyncSession = Depends(get_session_dep),
) -> RunDetailResponse:
    """Get full details of a run including hypotheses, gaps, and topics."""
    service = HypothesisService(session)
    run_detail = await service.get_run_detail(run_id)
    if not run_detail:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return run_detail


@router.get("/runs/{run_id}/status")
async def get_run_status(
    run_id: str,
    session: AsyncSession = Depends(get_session_dep),
) -> dict:
    """Get lightweight status of a run."""
    service = HypothesisService(session)
    status_info = await service.get_run_status(run_id)
    if not status_info:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    status_info["is_background_active"] = task_manager.is_running(run_id)
    return status_info


@router.get("/runs/{run_id}/hypotheses", response_model=list[HypothesisResponse])
async def list_hypotheses(
    run_id: str,
    session: AsyncSession = Depends(get_session_dep),
) -> list[HypothesisResponse]:
    """List all hypotheses for a given run."""
    service = HypothesisService(session)
    return await service.list_hypotheses(run_id)


@router.get("/runs/{run_id}/hypotheses/{hyp_id}", response_model=HypothesisResponse)
async def get_hypothesis(
    run_id: str,
    hyp_id: str,
    session: AsyncSession = Depends(get_session_dep),
) -> HypothesisResponse:
    """Get a specific hypothesis by ID."""
    service = HypothesisService(session)
    hyp = await service.get_hypothesis(run_id, hyp_id)
    if not hyp:
        raise HTTPException(status_code=404, detail=f"Hypothesis {hyp_id} not found in run {run_id}")
    return hyp


@router.post("/runs/{run_id}/hypotheses/{hyp_id}/challenge", response_model=HypothesisResponse)
async def challenge_hypothesis(
    run_id: str,
    hyp_id: str,
    session: AsyncSession = Depends(get_session_dep),
) -> HypothesisResponse:
    """Trigger an evidence challenge against a specific hypothesis."""
    service = HypothesisService(session)
    hyp = await service.challenge_hypothesis(run_id, hyp_id)
    if not hyp:
        raise HTTPException(status_code=404, detail=f"Hypothesis {hyp_id} not found")
    return hyp


@router.post("/runs/{run_id}/hypotheses/{hyp_id}/refine", response_model=HypothesisResponse)
async def refine_hypothesis(
    run_id: str,
    hyp_id: str,
    session: AsyncSession = Depends(get_session_dep),
) -> HypothesisResponse:
    """Trigger refinement for a hypothesis based on challenge results."""
    service = HypothesisService(session)
    hyp = await service.refine_hypothesis(run_id, hyp_id)
    if not hyp:
        raise HTTPException(status_code=404, detail=f"Hypothesis {hyp_id} not found")
    return hyp


@router.get("/runs/{run_id}/ranking", response_model=list[HypothesisResponse])
async def get_ranked_hypotheses(
    run_id: str,
    session: AsyncSession = Depends(get_session_dep),
) -> list[HypothesisResponse]:
    """Get hypotheses sorted by rank score."""
    service = HypothesisService(session)
    return await service.list_hypotheses(run_id)
