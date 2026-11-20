"""Pydantic response models for the EvidenceGap AI 2026 API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared / helper
# ---------------------------------------------------------------------------

class PaginatedResponse(BaseModel):
    """Wrapper for paginated list responses."""

    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class StatusMessage(BaseModel):
    """Generic status / message response."""

    status: str
    message: str


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

class RunResponse(BaseModel):
    """Summary of a hypothesis-generation run."""

    id: str
    run_id: Optional[str] = None
    status: str
    research_theme: str
    theme: Optional[str] = None
    target_population: Optional[str] = None
    objective: Optional[str] = None
    research_objective: Optional[str] = None
    num_hypotheses: int = 5
    created_at: datetime
    updated_at: datetime
    hypothesis_count: int = 0
    error: Optional[str] = None

    model_config = {"from_attributes": True}


class RunDetailResponse(BaseModel):
    """Full run detail including child objects."""

    id: str
    run_id: Optional[str] = None
    status: str
    research_theme: str
    theme: Optional[str] = None
    target_population: Optional[str] = None
    objective: Optional[str] = None
    research_objective: Optional[str] = None
    num_hypotheses: int = 5
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None
    hypothesis_count: int = 0
    evidence_count: int = 0
    hypotheses: list["HypothesisResponse"] = []
    gaps: list["GapResponse"] = []
    topics: list["TopicResponse"] = []
    validation: Optional["ValidationResponse"] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Hypothesis
# ---------------------------------------------------------------------------

class HypothesisResponse(BaseModel):
    """Full hypothesis representation."""

    id: str
    run_id: str
    gap_id: Optional[str] = None
    statement: str
    research_question: Optional[str] = None
    population: Optional[str] = None
    intervention: Optional[str] = None
    outcome: Optional[str] = None
    mechanism: Optional[str] = None
    relationship: Optional[str] = None
    citations: Optional[list[str]] = None
    assumptions: Optional[list[str]] = None
    limitations: Optional[list[str]] = None
    status: str
    validation_results: Optional[dict[str, Any]] = None
    challenge_results: Optional[dict[str, Any]] = None
    refined_statement: Optional[str] = None
    rank_score: Optional[float] = None
    evidence_records: list["EvidenceResponse"] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Topic
# ---------------------------------------------------------------------------

class TopicResponse(BaseModel):
    """Topic from topic modeling."""

    id: str
    topic_id: int
    label: Optional[str] = None
    keywords: list[str] = []
    document_count: int = 0
    count: Optional[int] = 0
    relevance: Optional[float] = 0.8
    trend: Optional[str] = None  # e.g. "rising", "stable", "declining"

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Research Gap
# ---------------------------------------------------------------------------

class GapResponse(BaseModel):
    """Discovered research gap."""

    id: str
    run_id: Optional[str] = None
    description: str
    score: float
    evidence: Optional[list[dict[str, Any]]] = None
    related_concepts: Optional[list[str]] = None
    related_topics: Optional[list[str]] = None
    evidence_density: Optional[float] = 0.05
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------

class EvidenceResponse(BaseModel):
    """Evidence record linked to a hypothesis."""

    id: str
    evidence_type: str
    source_pmid: Optional[str] = None
    passage: str
    relevance_score: float
    nli_label: Optional[str] = None
    nli_score: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class ValidationResponse(BaseModel):
    """Validation results for a run or hypothesis."""

    citation_valid: Optional[bool] = None
    nli_results: Optional[dict[str, Any]] = None
    novelty: Optional[dict[str, Any]] = None
    rule_checks: Optional[dict[str, Any]] = None
    overall_score: Optional[float] = None


# ---------------------------------------------------------------------------
# Corpus
# ---------------------------------------------------------------------------

class CorpusStatsResponse(BaseModel):
    """High-level statistics about the ingested corpus."""

    total_documents: int = 0
    fulltext_count: int = 0
    abstract_count: int = 0
    date_range: Optional[dict[str, str]] = None
    top_journals: list[dict[str, Any]] = []
    mesh_term_count: int = 0


class DocumentResponse(BaseModel):
    """Single document detail."""

    id: str
    pmid: Optional[str] = None
    pmcid: Optional[str] = None
    doi: Optional[str] = None
    title: str
    abstract: Optional[str] = None
    journal: Optional[str] = None
    pub_date: Optional[str] = None
    source_type: str
    mesh_terms: Optional[list[str]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MeshTermSummary(BaseModel):
    """MeSH term with document count."""

    term: str
    count: int


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

class RetrievalPassage(BaseModel):
    """A single retrieved passage with metadata."""

    passage: str
    score: float
    source_pmid: Optional[str] = None
    source_title: Optional[str] = None
    source_journal: Optional[str] = None
    chunk_index: Optional[int] = None


class RetrievalResponse(BaseModel):
    """Results from semantic retrieval."""

    query: str
    total_results: int
    passages: list[RetrievalPassage] = []


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

class MetricResult(BaseModel):
    """A single evaluation metric."""

    name: str
    value: float
    description: Optional[str] = None


class BaselineComparison(BaseModel):
    """Comparison of system against a baseline."""

    baseline_name: str
    baseline_score: float
    system_score: float
    improvement: float
    metric: str


class EvaluationResponse(BaseModel):
    """Full evaluation results for a run."""

    run_id: str
    metrics: list[MetricResult] = []
    baselines: list[BaselineComparison] = []
    ablation: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None


class GraphNode(BaseModel):
    """A node in the biomedical knowledge graph."""

    id: str
    label: str
    type: str
    properties: Optional[dict[str, Any]] = None


class GraphEdge(BaseModel):
    """A directed edge in the knowledge graph."""

    source: str
    target: str
    relation: str
    source_type: Optional[str] = "literature"


class KnowledgeGraphData(BaseModel):
    """Knowledge graph payload for network visualization."""

    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []


# Rebuild forward refs
RunDetailResponse.model_rebuild()
HypothesisResponse.model_rebuild()
