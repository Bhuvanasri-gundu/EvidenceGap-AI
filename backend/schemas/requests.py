"""Pydantic request models for the EvidenceGap AI 2026 API."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class GenerateHypothesesRequest(BaseModel):
    """Request to start a hypothesis-generation run."""

    research_theme: Optional[str] = Field(
        default=None,
        max_length=500,
        description="The biomedical research theme or domain to investigate.",
    )
    theme: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Alias for research_theme.",
    )
    target_population: Optional[str] = Field(
        default=None,
        max_length=300,
        description="Target patient or biological population.",
    )
    objective: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Specific research objective or angle.",
    )
    research_objective: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Alias for objective.",
    )
    num_hypotheses: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of hypotheses to generate (1-20).",
    )

    @property
    def effective_theme(self) -> str:
        return (self.research_theme or self.theme or "").strip()

    @property
    def effective_objective(self) -> Optional[str]:
        return self.objective or self.research_objective


class RetrievalRequest(BaseModel):
    """Request for semantic retrieval over the corpus."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Natural-language query for retrieval.",
    )
    top_k: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of top passages to return.",
    )
    use_ontology: bool = Field(
        default=True,
        description="Whether to expand the query using ontology concepts.",
    )
    filters: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional filters (e.g. {'journal': '...', 'date_from': '2020'}).",
    )


class RefineRequest(BaseModel):
    """Request to refine a specific hypothesis."""

    hypothesis_id: str = Field(
        ...,
        description="UUID of the hypothesis to refine.",
    )
    feedback: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional expert feedback to guide refinement.",
    )


class EvaluationRequest(BaseModel):
    """Request to run baseline comparison evaluation."""

    run_id: str = Field(
        ...,
        description="UUID of the run to evaluate.",
    )
    baseline_modes: list[str] = Field(
        default_factory=lambda: ["random", "frequency", "llm_only"],
        description="Baseline methods to compare against.",
    )


class PaginationParams(BaseModel):
    """Common pagination parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
