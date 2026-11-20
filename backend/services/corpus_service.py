"""Corpus service -- wraps src/ modules for corpus and document operations."""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.persistence.models import Document, SourceType
from backend.schemas.responses import (
    CorpusStatsResponse,
    DocumentResponse,
    MeshTermSummary,
    PaginatedResponse,
)

logger = logging.getLogger(__name__)


class CorpusService:
    """Service for corpus-level operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    async def get_stats(self) -> CorpusStatsResponse:
        """Return high-level corpus statistics."""
        total = await self.session.scalar(select(func.count(Document.id)))
        fulltext = await self.session.scalar(
            select(func.count(Document.id)).where(
                Document.source_type == SourceType.fulltext
            )
        )
        abstract = await self.session.scalar(
            select(func.count(Document.id)).where(
                Document.source_type == SourceType.abstract
            )
        )

        # Date range
        min_date = await self.session.scalar(select(func.min(Document.pub_date)))
        max_date = await self.session.scalar(select(func.max(Document.pub_date)))

        date_range = None
        if min_date and max_date:
            date_range = {"earliest": str(min_date), "latest": str(max_date)}

        # Top journals
        stmt = (
            select(Document.journal, func.count(Document.id).label("cnt"))
            .where(Document.journal.isnot(None))
            .group_by(Document.journal)
            .order_by(text("cnt DESC"))
            .limit(20)
        )
        result = await self.session.execute(stmt)
        top_journals = [
            {"journal": row.journal, "count": row.cnt} for row in result
        ]

        # MeSH term count (approximate -- count non-null rows)
        mesh_count = await self.session.scalar(
            select(func.count(Document.id)).where(Document.mesh_terms.isnot(None))
        )

        return CorpusStatsResponse(
            total_documents=total or 0,
            fulltext_count=fulltext or 0,
            abstract_count=abstract or 0,
            date_range=date_range,
            top_journals=top_journals,
            mesh_term_count=mesh_count or 0,
        )

    # ------------------------------------------------------------------
    # Document listing
    # ------------------------------------------------------------------

    async def list_documents(
        self,
        page: int = 1,
        page_size: int = 20,
        journal: Optional[str] = None,
        source_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> PaginatedResponse:
        """Return a paginated list of documents."""
        stmt = select(Document)
        count_stmt = select(func.count(Document.id))

        if journal:
            stmt = stmt.where(Document.journal.ilike(f"%{journal}%"))
            count_stmt = count_stmt.where(Document.journal.ilike(f"%{journal}%"))
        if source_type:
            stmt = stmt.where(Document.source_type == source_type)
            count_stmt = count_stmt.where(Document.source_type == source_type)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                Document.title.ilike(pattern) | Document.abstract.ilike(pattern)
            )
            count_stmt = count_stmt.where(
                Document.title.ilike(pattern) | Document.abstract.ilike(pattern)
            )

        total = await self.session.scalar(count_stmt) or 0

        offset = (page - 1) * page_size
        stmt = stmt.order_by(Document.created_at.desc()).offset(offset).limit(page_size)
        result = await self.session.execute(stmt)
        docs = result.scalars().all()

        total_pages = (total + page_size - 1) // page_size if page_size else 1

        items = [self._doc_to_response(d) for d in docs]

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_document_by_pmid(self, pmid: str) -> Optional[DocumentResponse]:
        """Get a single document by PMID."""
        result = await self.session.execute(
            select(Document).where(Document.pmid == pmid)
        )
        doc = result.scalar_one_or_none()
        if doc is None:
            return None
        return self._doc_to_response(doc)

    # ------------------------------------------------------------------
    # MeSH terms
    # ------------------------------------------------------------------

    async def get_mesh_summary(self, top_n: int = 50) -> list[MeshTermSummary]:
        """Aggregate MeSH terms across the corpus and return top terms."""
        result = await self.session.execute(
            select(Document.mesh_terms).where(Document.mesh_terms.isnot(None))
        )
        rows = result.scalars().all()

        term_counts: dict[str, int] = {}
        for mesh_json in rows:
            try:
                terms = json.loads(mesh_json) if isinstance(mesh_json, str) else mesh_json
                if isinstance(terms, list):
                    for t in terms:
                        term_counts[t] = term_counts.get(t, 0) + 1
            except (json.JSONDecodeError, TypeError):
                continue

        sorted_terms = sorted(term_counts.items(), key=lambda x: -x[1])[:top_n]
        return [MeshTermSummary(term=t, count=c) for t, c in sorted_terms]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _doc_to_response(doc: Document) -> DocumentResponse:
        mesh = None
        if doc.mesh_terms:
            try:
                mesh = json.loads(doc.mesh_terms)
            except (json.JSONDecodeError, TypeError):
                mesh = None

        return DocumentResponse(
            id=doc.id,
            pmid=doc.pmid,
            pmcid=doc.pmcid,
            doi=doc.doi,
            title=doc.title,
            abstract=doc.abstract,
            journal=doc.journal,
            pub_date=doc.pub_date,
            source_type=doc.source_type.value if doc.source_type else "abstract",
            mesh_terms=mesh,
            created_at=doc.created_at,
        )
