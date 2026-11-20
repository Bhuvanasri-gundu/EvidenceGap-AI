"""Ontology-Guided Scientific Retrieval Module.

Enhances dense semantic retrieval using:
1. MeSH hierarchy query expansion (synonyms, broader/narrower terms)
2. Ontological concept boosting
3. Provenance tracking of ontology contributions
4. Ablation comparison against vanilla semantic search
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from src.ontology.mesh_mapper import mesh_mapper
from src.retrieval.faiss_index import vector_index

logger = logging.getLogger(__name__)


class OntologyGuidedRetriever:
    """Combines FAISS vector retrieval with biomedical ontology guidance."""

    def __init__(self):
        self.vector_index = vector_index
        self.mesh_mapper = mesh_mapper

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        use_ontology: bool = True,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant passages with optional ontology expansion."""
        if not use_ontology:
            # Baseline vanilla semantic search
            return self.vector_index.search(query=query, top_k=top_k)

        # Ontology-guided query expansion
        expanded_terms = self.mesh_mapper.expand_query(query)
        expanded_query = f"{query} {' '.join(expanded_terms[:4])}"

        logger.info(
            "Ontology expansion for '%s': added terms %s",
            query,
            expanded_terms[:4],
        )

        passages = self.vector_index.search(query=expanded_query, top_k=top_k)

        # Annotate passages with ontology match details
        for p in passages:
            text = (p.get("text") or "").lower()
            matched_terms = [t for t in expanded_terms if t.lower() in text]
            p["matched_ontology_terms"] = matched_terms
            p["ontology_guided"] = True

        return passages


retriever = OntologyGuidedRetriever()
