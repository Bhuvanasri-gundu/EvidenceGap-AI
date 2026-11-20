"""Biomedical Concept Normalization and Canonicalization.

Normalizes free text biomedical entities to canonical identifiers
and maintains concept provenance.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from src.ontology.mesh_mapper import mesh_mapper
from src.ontology.bioportal_client import bioportal_client

logger = logging.getLogger(__name__)


class ConceptNormalizer:
    """Normalizes extracted terms and assigns canonical ontology identifiers."""

    def __init__(self):
        self.mesh_mapper = mesh_mapper
        self.bioportal_client = bioportal_client

    def normalize(self, term: str) -> Dict[str, Any]:
        """Normalize a concept term and return its canonical details."""
        clean_term = re.sub(r"[^\w\s-]", "", term).strip().lower()

        # Check MeSH first
        for name, data in self.mesh_mapper.hierarchy.items():
            if clean_term == name.lower() or clean_term in [s.lower() for s in data["synonyms"]]:
                return {
                    "original": term,
                    "canonical_name": name,
                    "ontology": "MeSH",
                    "identifier": data["tree_number"],
                    "synonyms": data["synonyms"],
                    "provenance": "mesh_hierarchy",
                }

        # Check BioPortal / fallback
        bp_results = self.bioportal_client.search_concept(term)
        if bp_results:
            top = bp_results[0]
            return {
                "original": term,
                "canonical_name": top.get("prefLabel", term),
                "ontology": top.get("ontology", "MeSH"),
                "identifier": top.get("id", ""),
                "synonyms": top.get("synonyms", []),
                "provenance": "bioportal_lookup",
            }

        return {
            "original": term,
            "canonical_name": term.title(),
            "ontology": "FreeText",
            "identifier": None,
            "synonyms": [],
            "provenance": "unmapped",
        }


concept_normalizer = ConceptNormalizer()
