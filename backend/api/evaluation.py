"""API router for evaluation, baselines, and ablation studies."""

from __future__ import annotations

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.persistence.database import get_session_dep
from backend.services.evaluation_service import EvaluationService
from backend.schemas.requests import EvaluationRequest
from backend.schemas.responses import EvaluationResponse

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.get("/runs/{run_id}/metrics", response_model=Optional[EvaluationResponse])
async def get_run_metrics(
    run_id: str,
    session: AsyncSession = Depends(get_session_dep),
) -> Optional[EvaluationResponse]:
    """Get evaluation metrics for a specific run."""
    service = EvaluationService(session)
    res = await service.get_metrics(run_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"No metrics available for run {run_id}")
    return res


@router.post("/baseline", response_model=EvaluationResponse)
async def run_baseline_comparison(
    req: EvaluationRequest,
    session: AsyncSession = Depends(get_session_dep),
) -> EvaluationResponse:
    """Run baseline comparisons for a run against standard baselines."""
    service = EvaluationService(session)
    return await service.run_baseline(
        run_id=req.run_id,
        baseline_modes=req.baseline_modes,
    )


@router.get("/runs/{run_id}/ablation")
async def get_ablation_results(
    run_id: str,
    session: AsyncSession = Depends(get_session_dep),
) -> dict[str, Any]:
    """Get component ablation study results for a run."""
    service = EvaluationService(session)
    ablation = await service.get_ablation(run_id)
    if not ablation:
        raise HTTPException(status_code=404, detail=f"Ablation data not found for run {run_id}")
    return ablation
