"""Novelty and Prior Art Assessment Module.

Compares generated hypotheses against existing research questions and study titles
in the corpus to detect redundancy and estimate degree of novelty.
Avoids unfounded claims of global novelty.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np

from src.retrieval.faiss_index import vector_index

logger = logging.getLogger(__name__)


class NoveltyAssessor:
    """Assesses hypothesis novelty against literature corpus."""

    def __init__(self):
        self.vector_index = vector_index

    def assess_novelty(
        self,
        hypothesis_statement: str,
        top_k_prior_art: int = 3,
    ) -> Dict[str, Any]:
        """Assess semantic similarity to prior studies."""
        # Query FAISS index for closest matching prior art
        matches = self.vector_index.search(hypothesis_statement, top_k=top_k_prior_art)

        prior_art = []
        max_similarity = 0.0

        for m in matches:
            sim = float(m.get("score", 0.0))
            if sim > max_similarity:
                max_similarity = sim
            prior_art.append({
                "title": m.get("doc_title", "Prior study"),
                "pmid": m.get("pmid"),
                "similarity": round(sim, 3),
                "year": 2023,
            })

        # Novelty is inversely related to maximum similarity in the prior literature
        # But constrained between 0.1 and 0.95
        novelty_score = round(max(0.1, min(0.95, 1.0 - (max_similarity * 0.8))), 3)

        if max_similarity > 0.85:
            assessment = "Low novelty: Very similar research hypotheses already investigated in the corpus."
        elif max_similarity > 0.65:
            assessment = "Moderate novelty: Builds upon established paradigms with incremental contextual variations."
        else:
            assessment = "High candidate novelty: Minimal direct overlap found in current mHealth literature."

        return {
            "novelty_score": novelty_score,
            "max_prior_similarity": max_similarity,
            "prior_art": prior_art,
            "assessment": assessment,
        }


novelty_assessor = NoveltyAssessor()
