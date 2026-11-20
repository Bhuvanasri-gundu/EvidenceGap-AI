"""Information Retrieval Evaluation Metrics.

Computes standard scientific IR metrics:
- Precision@k
- Recall@k
- Mean Reciprocal Rank (MRR)
- Normalized Discounted Cumulative Gain (nDCG@k)
"""

from __future__ import annotations

import math
from typing import Dict, List, Set


class RetrievalEvaluator:
    """Evaluates passage retrieval quality against relevance judgments."""

    @staticmethod
    def precision_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
        """Calculate Precision@k."""
        if k <= 0 or not retrieved:
            return 0.0
        top_k = retrieved[:k]
        hits = sum(1 for doc in top_k if doc in relevant)
        return round(hits / k, 4)

    @staticmethod
    def recall_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
        """Calculate Recall@k."""
        if not relevant or k <= 0:
            return 0.0
        top_k = retrieved[:k]
        hits = sum(1 for doc in top_k if doc in relevant)
        return round(hits / len(relevant), 4)

    @staticmethod
    def mean_reciprocal_rank(retrieved_lists: List[List[str]], relevant_sets: List[Set[str]]) -> float:
        """Calculate Mean Reciprocal Rank (MRR)."""
        rr_sum = 0.0
        for retrieved, relevant in zip(retrieved_lists, relevant_sets):
            for rank, doc in enumerate(retrieved, start=1):
                if doc in relevant:
                    rr_sum += 1.0 / rank
                    break
        return round(rr_sum / max(1, len(retrieved_lists)), 4)

    @staticmethod
    def ndcg_at_k(retrieved: List[str], relevance_scores: Dict[str, float], k: int) -> float:
        """Calculate nDCG@k."""
        if k <= 0 or not retrieved:
            return 0.0

        top_k = retrieved[:k]
        dcg = 0.0
        for i, doc in enumerate(top_k):
            rel = relevance_scores.get(doc, 0.0)
            dcg += (2**rel - 1) / math.log2(i + 2)

        # Ideal DCG
        ideal_rels = sorted(relevance_scores.values(), reverse=True)[:k]
        idcg = sum((2**rel - 1) / math.log2(i + 2) for i, rel in enumerate(ideal_rels))

        return round(dcg / idcg, 4) if idcg > 0 else 0.0


retrieval_evaluator = RetrievalEvaluator()
