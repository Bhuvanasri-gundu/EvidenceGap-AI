"""Unified Scientific Validator.

Orchestrates citation checks, NLI predictions, novelty assessment, and rule-based validation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from src.validation.citation_verifier import citation_verifier
from src.validation.nli_validator import nli_validator
from src.validation.novelty_assessor import novelty_assessor
from src.validation.rule_checker import rule_checker

logger = logging.getLogger(__name__)


class UnifiedValidator:
    """Combines all validation stages into a unified scientific assessment."""

    def __init__(self):
        self.citation_verifier = citation_verifier
        self.nli_validator = nli_validator
        self.novelty_assessor = novelty_assessor
        self.rule_checker = rule_checker

    def validate(
        self,
        hypothesis_statement: str,
        citations: Optional[List[str]] = None,
        retrieved_passages: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Validate a hypothesis across all dimensions."""
        # 1. Citations
        cite_res = self.citation_verifier.verify_citations(
            citations=citations or [],
            hypothesis_text=hypothesis_statement,
            retrieved_passages=retrieved_passages,
        )

        # 2. NLI
        top_premise = retrieved_passages[0].get("text", "") if retrieved_passages else hypothesis_statement
        nli_res = self.nli_validator.predict(premise=top_premise, hypothesis=hypothesis_statement)

        # 3. Novelty
        nov_res = self.novelty_assessor.assess_novelty(hypothesis_statement)

        # 4. Rules
        rules = self.rule_checker.check(hypothesis_statement)

        # Composite validity score
        rule_score = sum(r["score"] for r in rules) / len(rules) if rules else 0.8
        nli_score = nli_res.get("score", 0.7)
        nov_score = nov_res.get("novelty_score", 0.7)
        cite_score = 1.0 if cite_res.get("verified") else 0.6

        overall_validity = round((rule_score * 0.3) + (nli_score * 0.3) + (nov_score * 0.2) + (cite_score * 0.2), 3)

        return {
            "citation_valid": cite_res.get("verified", True),
            "citation_check": cite_res,
            "nli_label": nli_res.get("label", "entailment"),
            "nli_score": nli_res.get("score", 0.85),
            "novelty_score": nov_score,
            "novelty": nov_res,
            "rule_checks": rules,
            "overall_validity_score": overall_validity,
            "prior_art": [p["title"] for p in nov_res.get("prior_art", [])],
        }


validator = UnifiedValidator()
