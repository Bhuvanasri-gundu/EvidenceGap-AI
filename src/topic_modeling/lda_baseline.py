"""Latent Dirichlet Allocation (LDA) Baseline Topic Modeling.

Provides a reproducible statistical baseline for topic discovery,
topic coherence comparison, and diversity metrics against BERTopic.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from config.settings import TOPICS_DIR, get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LDABaseline:
    """Statistical LDA baseline topic model with evaluation utilities."""

    def __init__(self, num_topics: int = 15):
        self.num_topics = num_topics or settings.lda_num_topics
        self.vectorizer = None
        self.lda_model = None
        self.feature_names: List[str] = []
        self.topics_data: List[Dict[str, Any]] = []

    def fit(self, documents: List[str]) -> List[Dict[str, Any]]:
        """Fit LDA model using scikit-learn LatentDirichletAllocation."""
        from sklearn.decomposition import LatentDirichletAllocation
        from sklearn.feature_extraction.text import CountVectorizer

        logger.info("Fitting LDA baseline model with %d topics...", self.num_topics)

        self.vectorizer = CountVectorizer(
            max_df=0.95,
            min_df=2,
            max_features=1000,
            stop_words="english",
        )
        tf_matrix = self.vectorizer.fit_transform(documents)
        self.feature_names = self.vectorizer.get_feature_names_out()

        self.lda_model = LatentDirichletAllocation(
            n_components=self.num_topics,
            max_iter=15,
            learning_method="online",
            random_state=42,
        )
        doc_topic_dist = self.lda_model.fit_transform(tf_matrix)

        # Extract top keywords per topic
        self.topics_data = []
        for topic_idx, topic in enumerate(self.lda_model.components_):
            top_indices = topic.argsort()[::-1][:10]
            top_words = [self.feature_names[i] for i in top_indices]
            assigned_docs = int((doc_topic_dist.argmax(axis=1) == topic_idx).sum())

            self.topics_data.append({
                "topic_id": topic_idx,
                "keywords": top_words,
                "document_count": assigned_docs,
                "label": f"LDA Topic {topic_idx}: {', '.join(top_words[:3])}",
            })

        return self.topics_data

    def evaluate_diversity(self) -> float:
        """Compute Topic Diversity (percentage of unique words in top-k words across all topics)."""
        if not self.topics_data:
            return 0.0

        all_words = []
        for t in self.topics_data:
            all_words.extend(t.get("keywords", [])[:10])

        if not all_words:
            return 0.0

        unique_words = set(all_words)
        diversity = len(unique_words) / len(all_words)
        return round(float(diversity), 3)


lda_baseline = LDABaseline()
