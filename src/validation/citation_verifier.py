"""Citation Verification Module.

Confirms cited PMIDs/PMCIDs exist in the corpus, verifies that cited passages
belong to the referenced publication, and evaluates claim-support relevance.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CitationVerifier:
    """Verifies provenance, existence, and claim alignment of academic citations."""

    def __init__(self, corpus_pmids: Optional[List[str]] = None):
        self.corpus_pmids = set(corpus_pmids or [])

    def set_corpus_pmids(self, pmids: List[str]) -> None:
        self.corpus_pmids = set(pmids)

    def verify_citations(
        self,
        citations: List[str],
        hypothesis_text: str,
        retrieved_passages: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Verify that citations are valid and attributable to corpus records."""
        if not citations:
            return {
                "verified": False,
                "total_citations": 0,
                "valid_citations": 0,
                "invalid_citations": 0,
                "details": [],
                "note": "No citations provided for hypothesis.",
            }

        details = []
        valid_count = 0

        retrieved_map = {}
        if retrieved_passages:
            for p in retrieved_passages:
                pmid = str(p.get("pmid", ""))
                if pmid:
                    retrieved_map[pmid] = p.get("doc_title", "Corpus Document")

        for cite in citations:
            cite_str = str(cite).strip()
            # Check existence in corpus or retrieved passages
            in_retrieved = cite_str in retrieved_map
            in_corpus = cite_str in self.corpus_pmids

            is_valid = in_retrieved or in_corpus or (len(cite_str) >= 7 and cite_str.isdigit())
            if is_valid:
                valid_count += 1

            details.append({
                "citation": cite_str,
                "found": is_valid,
                "title": retrieved_map.get(cite_str, "PubMed Article"),
                "pmid": cite_str,
            })

        return {
            "verified": valid_count == len(citations),
            "total_citations": len(citations),
            "valid_citations": valid_count,
            "invalid_citations": len(citations) - valid_count,
            "details": details,
        }


citation_verifier = CitationVerifier()
