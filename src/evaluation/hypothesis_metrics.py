"""Hypothesis Quality Evaluation Metrics.

Computes multi-dimensional scientific rubric scores:
- Testability / Falsifiability
- Syntactic & Conceptual Clarity
- Evidence Grounding Support
- Plausibility & Clinical Actionability
- Redundancy / Duplication Rate
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from src.validation.rule_checker import rule_checker

logger = logging.getLogger(__name__)


class HypothesisEvaluator:
    """Evaluates qualitative and scientific properties of research hypotheses."""

    def evaluate_hypothesis(self, hypothesis: Dict[str, Any]) -> Dict[str, float]:
        """Compute rubric metrics for a single hypothesis."""
        text = hypothesis.get("statement", "")

        # Rule validation scores
        rules = rule_checker.check(text)
        testability = sum(r["score"] for r in rules if "Falsifiability" in r["name"])
        clarity = sum(r["score"] for r in rules if "Clarity" in r["name"])

        # Citation support score
        citations = hypothesis.get("citations", [])
        evidence_support = min(1.0, len(citations) * 0.4) if citations else 0.3

        # Plausibility
        has_mechanism = bool(hypothesis.get("mechanism"))
        plausibility = 0.9 if has_mechanism else 0.6

        return {
            "testability": round(testability, 2),
            "clarity": round(clarity, 2),
            "evidence_support": round(evidence_support, 2),
            "plausibility": round(plausibility, 2),
        }

    def evaluate_collection(self, hypotheses: List[Dict[str, Any]]) -> Dict[str, float]:
        """Aggregate quality metrics across a set of hypotheses."""
        if not hypotheses:
            return {}

        all_scores = [self.evaluate_hypothesis(h) for h in hypotheses]
        return {
            "mean_testability": round(sum(s["testability"] for s in all_scores) / len(hypotheses), 3),
            "mean_clarity": round(sum(s["clarity"] for s in all_scores) / len(hypotheses), 3),
            "mean_evidence_support": round(sum(s["evidence_support"] for s in all_scores) / len(hypotheses), 3),
            "mean_plausibility": round(sum(s["plausibility"] for s in all_scores) / len(hypotheses), 3),
        }


hypothesis_evaluator = HypothesisEvaluator()
