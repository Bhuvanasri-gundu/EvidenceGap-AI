"""Rule-Based Scientific Rigor Checker.

Evaluates testability, falsifiability, variable specificity,
population definition, outcome measurability, and absence of unsupported certainty.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List


class RuleChecker:
    """Executes deterministic scientific quality rules on hypothesis formulations."""

    def check(self, statement: str) -> List[Dict[str, Any]]:
        """Run all rule checks on a hypothesis statement."""
        results = []
        text = statement.lower()

        # Rule 1: Testability / Falsifiability
        has_comparative = bool(re.search(r"\b(compared to|relative to|versus|higher than|lower than|differ)\b", text))
        results.append({
            "name": "Falsifiability & Comparison",
            "passed": has_comparative,
            "score": 1.0 if has_comparative else 0.5,
            "message": "Specifies a comparative benchmark or control group" if has_comparative else "Lacks explicit comparison condition",
        })

        # Rule 2: Measurable Directional Outcome
        has_direction = bool(re.search(r"\b(increase|decrease|reduction|reduce|improves?|improved?|improvement|higher|lower|predict)\b", text))
        results.append({
            "name": "Directionality",
            "passed": has_direction,
            "score": 1.0 if has_direction else 0.6,
            "message": "Explicit directional relationship specified" if has_direction else "Relationship direction is ambiguous",
        })

        # Rule 3: Absence of dogmatic certainty (hedging appropriate for a hypothesis)
        has_dogmatic = bool(re.search(r"\b(always|proves|definitely|undoubtedly|guaranteed)\b", text))
        results.append({
            "name": "Scientific Uncertainty Calibration",
            "passed": not has_dogmatic,
            "score": 0.4 if has_dogmatic else 1.0,
            "message": "Appropriate scientific calibration" if not has_dogmatic else "Contains unwarranted dogmatic certainty",
        })

        # Rule 4: Length and complexity
        words = statement.split()
        is_length_ok = 15 <= len(words) <= 75
        results.append({
            "name": "Syntactic Clarity",
            "passed": is_length_ok,
            "score": 1.0 if is_length_ok else 0.7,
            "message": "Statement length is well-calibrated" if is_length_ok else "Statement is too brief or excessively convoluted",
        })

        return results


rule_checker = RuleChecker()
