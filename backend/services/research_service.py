"""Research service -- wraps src/ modules for gap discovery, knowledge graph, retrieval."""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.persistence.models import ResearchGap, Topic
from backend.schemas.responses import (
    GapResponse,
    RetrievalPassage,
    RetrievalResponse,
    TopicResponse,
)

logger = logging.getLogger(__name__)


def _safe_json_loads(value: Optional[str], default: Any = None) -> Any:
    """Safely parse a JSON string, returning *default* on failure."""
    if value is None:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default


class ResearchService:
    """Service for research gap, topic, knowledge graph, and retrieval operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------------------------------------------------------
    # Topics
    # ------------------------------------------------------------------

    async def list_topics(self, run_id: Optional[str] = None) -> list[TopicResponse]:
        """List topics, optionally filtered by run."""
        stmt = select(Topic)
        if run_id:
            stmt = stmt.where(Topic.run_id == run_id)
        stmt = stmt.order_by(Topic.topic_id)

        result = await self.session.execute(stmt)
        topics = result.scalars().all()

        if not topics and not run_id:
            from src.topic_modeling.bertopic_modeler import modeler
            fallback_topics = modeler.run()
            return [
                TopicResponse(
                    id=str(td.get("topic_id", idx)),
                    topic_id=td.get("topic_id", idx),
                    label=td.get("label", f"Topic {idx}"),
                    keywords=td.get("keywords", []),
                    document_count=td.get("document_count", 0),
                    count=td.get("document_count", 0),
                    trend=td.get("trend"),
                )
                for idx, td in enumerate(fallback_topics)
            ]

        return [
            TopicResponse(
                id=t.id,
                topic_id=t.topic_id,
                label=f"Topic {t.topic_id}: {', '.join(_safe_json_loads(t.keywords, [])[:3])}",
                keywords=_safe_json_loads(t.keywords, []),
                document_count=t.document_count,
                count=t.document_count,
                trend=None,
            )
            for t in topics
        ]

    async def get_topic(self, topic_id: str) -> Optional[TopicResponse]:
        """Get a single topic by its DB primary key."""
        result = await self.session.execute(
            select(Topic).where(Topic.id == topic_id)
        )
        t = result.scalar_one_or_none()
        if t is None:
            return None

        return TopicResponse(
            id=t.id,
            topic_id=t.topic_id,
            keywords=_safe_json_loads(t.keywords, []),
            document_count=t.document_count,
            trend=None,
        )

    # ------------------------------------------------------------------
    # Gaps
    # ------------------------------------------------------------------

    async def list_gaps(self, run_id: Optional[str] = None, limit: int = 20) -> list[GapResponse]:
        """List research gaps, optionally filtered by run."""
        stmt = select(ResearchGap)
        if run_id:
            stmt = stmt.where(ResearchGap.run_id == run_id)
        stmt = stmt.order_by(ResearchGap.score.desc()).limit(limit)

        result = await self.session.execute(stmt)
        gaps = result.scalars().all()

        if not gaps and not run_id:
            from src.gap_discovery.gap_detector import discoverer
            fallback_gaps = discoverer.discover()
            return [
                GapResponse(
                    id=g.get("id", f"gap_{idx}"),
                    run_id=None,
                    description=g.get("description", ""),
                    score=float(g.get("score", 0.8)),
                    evidence=g.get("evidence", []),
                    related_concepts=g.get("related_concepts", []),
                    related_topics=g.get("related_topics", []),
                    evidence_density=float(g.get("evidence_density", 0.05)),
                )
                for idx, g in enumerate(fallback_gaps[:limit])
            ]

        return [self._gap_to_response(g) for g in gaps]

    async def get_gap(self, gap_id: str) -> Optional[GapResponse]:
        """Get a single gap with evidence."""
        result = await self.session.execute(
            select(ResearchGap).where(ResearchGap.id == gap_id)
        )
        g = result.scalar_one_or_none()
        if g is None:
            return None
        return self._gap_to_response(g)

    # ------------------------------------------------------------------
    # Knowledge Graph
    # ------------------------------------------------------------------

    async def get_knowledge_graph(self, run_id: Optional[str] = None, max_nodes: int = 100) -> dict[str, Any]:
        """Return knowledge graph data suitable for front-end visualization."""
        try:
            from src.knowledge_graph import builder as kg_builder  # type: ignore
            json_path = kg_builder.output_dir / "knowledge_graph.json"
            if json_path.exists():
                with open(json_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return kg_builder.get_visualization_data(max_nodes=max_nodes)
        except Exception as exc:
            logger.debug("Error loading knowledge graph: %s", exc)

        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []

        # Topics as nodes
        topics = await self.list_topics(run_id=run_id)
        for t in topics:
            nodes.append({
                "id": f"topic-{t.id}",
                "label": ", ".join(t.keywords[:3]) if t.keywords else f"Topic {t.topic_id}",
                "type": "topic",
                "size": t.document_count,
            })

        # Gaps as nodes
        gaps = await self.list_gaps(run_id=run_id)
        for g in gaps:
            nodes.append({
                "id": f"gap-{g.id}",
                "label": g.description[:60],
                "type": "gap",
                "score": g.score,
            })
            # Link gap to related concept topics
            if g.related_concepts:
                for concept in g.related_concepts:
                    for t_node in nodes:
                        if t_node["type"] == "topic" and concept.lower() in t_node["label"].lower():
                            edges.append({
                                "source": f"gap-{g.id}",
                                "target": t_node["id"],
                                "relationship": "related_to",
                            })

        return {"nodes": nodes, "edges": edges}

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        use_ontology: bool = True,
        filters: Optional[dict[str, Any]] = None,
    ) -> RetrievalResponse:
        """Run semantic retrieval against the corpus.

        Delegates to src.retrieval if available; returns empty results otherwise.
        """
        try:
            from src.retrieval import retriever as ret_module  # type: ignore

            results = ret_module.search(
                query=query,
                top_k=top_k,
                use_ontology=use_ontology,
                filters=filters,
            )
            passages = [
                RetrievalPassage(
                    passage=r.get("passage", ""),
                    score=r.get("score", 0.0),
                    source_pmid=r.get("pmid"),
                    source_title=r.get("title"),
                    source_journal=r.get("journal"),
                    chunk_index=r.get("chunk_index"),
                )
                for r in results
            ]
            return RetrievalResponse(
                query=query,
                total_results=len(passages),
                passages=passages,
            )
        except (ImportError, AttributeError) as exc:
            logger.warning("src.retrieval not available: %s", exc)
            return RetrievalResponse(query=query, total_results=0, passages=[])

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _gap_to_response(g: ResearchGap) -> GapResponse:
        return GapResponse(
            id=g.id,
            run_id=g.run_id,
            description=g.description,
            score=g.score,
            evidence=_safe_json_loads(g.evidence),
            related_concepts=_safe_json_loads(g.related_concepts),
            created_at=g.created_at,
        )
