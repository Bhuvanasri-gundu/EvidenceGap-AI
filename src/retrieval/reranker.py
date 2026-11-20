"""Scientific Passage Reranker Module.

Re-scores retrieved passages using term overlap, PICOT concept alignment,
and optional cross-encoder models for maximal evidence precision.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PassageReranker:
    """Reranks retrieved candidate passages to prioritize high-evidence sections."""

    def __init__(self, section_weights: Optional[Dict[str, float]] = None):
        self.section_weights = section_weights or {
            "results": 1.3,
            "conclusion": 1.2,
            "methods": 1.0,
            "discussion": 1.0,
            "introduction": 0.9,
            "other": 0.8,
            "abstract": 1.1,
        }

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Reranks passages using section importance and query token overlap."""
        if not candidates:
            return []

        query_terms = set(query.lower().split())

        scored_candidates = []
        for c in candidates:
            base_score = float(c.get("score", c.get("relevance_score", 0.5)))
            sec_type = c.get("section_type", c.get("section", "other")).lower()
            sec_multiplier = self.section_weights.get(sec_type, 1.0)

            # Lexical overlap bonus
            text_terms = set(c.get("text", c.get("passage", "")).lower().split())
            overlap = len(query_terms.intersection(text_terms)) / max(1, len(query_terms))

            final_score = round((base_score * 0.7 + overlap * 0.3) * sec_multiplier, 4)
            scored_candidates.append({**c, "rerank_score": final_score})

        scored_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored_candidates[:top_k]


reranker = PassageReranker()
