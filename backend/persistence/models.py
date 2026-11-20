"""SQLAlchemy ORM models for EvidenceGap AI 2026."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship as orm_relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RunStatus(str, enum.Enum):
    pending = "pending"
    collecting = "collecting"
    processing = "processing"
    analyzing = "analyzing"
    complete = "complete"
    failed = "failed"


class SourceType(str, enum.Enum):
    fulltext = "fulltext"
    abstract = "abstract"


class EvidenceType(str, enum.Enum):
    supporting = "supporting"
    contradictory = "contradictory"
    neutral = "neutral"


class HypothesisStatus(str, enum.Enum):
    generated = "generated"
    validated = "validated"
    challenged = "challenged"
    refined = "refined"
    ranked = "ranked"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Run(Base):
    """A hypothesis-generation run / research session."""

    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    research_theme: Mapped[str] = mapped_column(Text, nullable=False)
    target_population: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    objective: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    num_hypotheses: Mapped[int] = mapped_column(Integer, default=5)
    status: Mapped[RunStatus] = mapped_column(
        Enum(RunStatus), default=RunStatus.pending, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    results_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    topics: Mapped[list["Topic"]] = orm_relationship(
        "Topic", back_populates="run", cascade="all, delete-orphan"
    )
    gaps: Mapped[list["ResearchGap"]] = orm_relationship(
        "ResearchGap", back_populates="run", cascade="all, delete-orphan"
    )
    hypotheses: Mapped[list["Hypothesis"]] = orm_relationship(
        "Hypothesis", back_populates="run", cascade="all, delete-orphan"
    )


class Document(Base):
    """An ingested biomedical document (PubMed article)."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    pmid: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, index=True)
    pmcid: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    doi: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    journal: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    pub_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType), default=SourceType.abstract
    )
    mesh_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class Topic(Base):
    """A topic discovered via topic modeling for a specific run."""

    __tablename__ = "topics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic_id: Mapped[int] = mapped_column(Integer, nullable=False)
    keywords: Mapped[str] = mapped_column(Text, nullable=False)  # JSON list
    document_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    run: Mapped["Run"] = orm_relationship("Run", back_populates="topics")


class ResearchGap(Base):
    """A discovered research gap."""

    __tablename__ = "research_gaps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    related_concepts: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    run: Mapped["Run"] = orm_relationship("Run", back_populates="gaps")
    hypotheses: Mapped[list["Hypothesis"]] = orm_relationship(
        "Hypothesis", back_populates="gap", cascade="all, delete-orphan"
    )


class Hypothesis(Base):
    """A generated research hypothesis."""

    __tablename__ = "hypotheses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    gap_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("research_gaps.id", ondelete="SET NULL"), nullable=True
    )

    # Core hypothesis fields
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    research_question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    population: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    intervention: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mechanism: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    relationship: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Evidence
    citations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list
    assumptions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list
    limitations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list

    # Status & results
    status: Mapped[HypothesisStatus] = mapped_column(
        Enum(HypothesisStatus), default=HypothesisStatus.generated
    )
    validation_results: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    challenge_results: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    refined_statement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rank_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    run: Mapped["Run"] = orm_relationship("Run", back_populates="hypotheses")
    gap: Mapped[Optional["ResearchGap"]] = orm_relationship(
        "ResearchGap", back_populates="hypotheses"
    )
    evidence_records: Mapped[list["EvidenceRecord"]] = orm_relationship(
        "EvidenceRecord", back_populates="hypothesis", cascade="all, delete-orphan"
    )


class EvidenceRecord(Base):
    """An evidence record linked to a hypothesis."""

    __tablename__ = "evidence_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    hypothesis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("hypotheses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evidence_type: Mapped[EvidenceType] = mapped_column(Enum(EvidenceType), nullable=False)
    source_pmid: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    passage: Mapped[str] = mapped_column(Text, nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    nli_label: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    nli_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    hypothesis: Mapped["Hypothesis"] = orm_relationship(
        "Hypothesis", back_populates="evidence_records"
    )
