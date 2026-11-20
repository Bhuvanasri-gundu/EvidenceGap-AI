"""Relevance Filtering Module.

Scores articles for mobile health (mHealth) domain relevance using
multi-term keyword heuristics and domain concept density.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

MHEALTH_KEYWORDS = {
    # Core digital health terms
    "mhealth": 3.0,
    "mobile health": 3.0,
    "smartphone": 2.5,
    "mobile application": 2.5,
    "health app": 2.5,
    "wearable": 2.5,
    "biosensor": 2.0,
    "smartwatch": 2.0,
    "telehealth": 2.0,
    "telemedicine": 2.0,
    "remote monitoring": 2.5,
    "digital health": 2.0,
    "digital intervention": 2.5,
    "sensor": 1.5,
    "sms": 1.5,
    "text messaging": 1.5,
    "ecological momentary assessment": 3.0,
    "ema": 1.5,
    "continuous glucose monitoring": 2.5,
    "cgm": 2.0,
    "mobile phone": 1.5,
}


class RelevanceFilter:
    """Filters records for mobile health relevance based on clinical/technical criteria."""

    def __init__(self, threshold: float = 2.0):
        self.threshold = threshold

    def score_record(self, record: Dict[str, Any]) -> float:
        """Compute an mHealth relevance score for a document."""
        title = record.get("title", "").lower()
        abstract = record.get("abstract", "").lower()
        mesh_terms = [m.lower() for m in (record.get("mesh_terms") or [])]
        text = f"{title} {abstract} {' '.join(mesh_terms)}"

        score = 0.0
        for kw, weight in MHEALTH_KEYWORDS.items():
            if kw in title:
                score += weight * 2.0  # Double weight for title matches
            elif kw in text:
                score += weight

        return score

    def filter_corpus(
        self, records: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Split corpus into relevant and non-relevant sets."""
        relevant = []
        excluded = []

        for r in records:
            score = self.score_record(r)
            r["relevance_score"] = round(score, 2)
            if score >= self.threshold:
                relevant.append(r)
            else:
                excluded.append(r)

        logger.info(
            "Relevance filtering (threshold=%.1f): %d retained, %d excluded",
            self.threshold,
            len(relevant),
            len(excluded),
        )
        return relevant, excluded


relevance_filter = RelevanceFilter()
