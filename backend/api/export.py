"""API router for exporting research reports."""

from __future__ import annotations

import json
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.persistence.database import get_session_dep
from backend.services.hypothesis_service import HypothesisService

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/runs/{run_id}/report")
async def export_run_report(
    run_id: str,
    session: AsyncSession = Depends(get_session_dep),
) -> dict[str, Any]:
    """Export complete evidence report for a run as structured JSON."""
    service = HypothesisService(session)
    run_detail = await service.get_run_detail(run_id)
    if not run_detail:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    report = {
        "title": "EvidenceGap AI 2026 — Evidence-Grounded Research Report",
        "academic_title": "Ontology-Guided Hypothesis Generation Using LLMs and Topic Modeling in mHealth Research",
        "run": run_detail.model_dump(),
        "metadata": {
            "version": "1.0.0",
            "export_format": "json",
        },
    }
    return report


@router.get("/runs/{run_id}/report/markdown")
async def export_run_report_markdown(
    run_id: str,
    session: AsyncSession = Depends(get_session_dep),
) -> Response:
    """Export evidence report as a Markdown document."""
    service = HypothesisService(session)
    run_detail = await service.get_run_detail(run_id)
    if not run_detail:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    lines = [
        f"# EvidenceGap AI 2026: Research Report",
        f"**Run ID:** `{run_detail.id}`  ",
        f"**Status:** {run_detail.status}  ",
        f"**Research Theme:** {run_detail.research_theme}  ",
        f"**Target Population:** {run_detail.target_population or 'All'}  ",
        f"**Objective:** {run_detail.objective or 'Broad Exploration'}  \n",
        f"## Identified Research Gaps",
    ]

    for i, gap in enumerate(run_detail.gaps, 1):
        lines.append(f"### Gap {i}: {gap.description}")
        lines.append(f"- **Score:** {gap.score:.3f}")
        if gap.related_concepts:
            lines.append(f"- **Related Concepts:** {', '.join(gap.related_concepts)}")

    lines.append("\n## Generated & Validated Hypotheses")
    for i, h in enumerate(run_detail.hypotheses, 1):
        lines.append(f"### Hypothesis {i}: {h.statement}")
        if h.refined_statement:
            lines.append(f"**Refined Version:** {h.refined_statement}")
        lines.append(f"- **Question:** {h.research_question}")
        lines.append(f"- **Population:** {h.population}")
        lines.append(f"- **Intervention:** {h.intervention}")
        lines.append(f"- **Outcome:** {h.outcome}")
        lines.append(f"- **Mechanism:** {h.mechanism}")
        lines.append(f"- **Rank Score:** {h.rank_score or 'N/A'}")
        if h.citations:
            lines.append(f"- **Citations:** {', '.join(h.citations)}")

    content = "\n".join(lines)
    return Response(
        content=content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=evidencegap_report_{run_id}.md"},
    )
