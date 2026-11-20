"""Natural Language Inference (NLI) Validation Module.

Evaluates claim-evidence alignment using Cross-Encoder / DeBERTa NLI models.
Classifies pairs into entailment, contradiction, and neutral.
Preserves continuous model scores while explicitly acknowledging that
NLI predictions are statistical approximations, not absolute clinical judgments.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class NLIValidator:
    """Evaluates scientific entailment and contradiction between claims and evidence."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.nli_model
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from transformers import pipeline
                logger.info("Attempting to load local NLI pipeline: %s", self.model_name)
                # First try loading strictly local files to avoid blocking server on 500MB downloads
                self._model = pipeline(
                    "text-classification",
                    model=self.model_name,
                    top_k=None,
                    device=-1,  # CPU execution default
                    model_kwargs={"local_files_only": True},
                )
            except Exception as exc:
                logger.info("Local NLI weights not pre-cached (%s). Using high-speed scientific heuristic evaluator.", exc)
                self._model = "fallback"

    def predict(self, premise: str, hypothesis: str) -> Dict[str, Any]:
        """Evaluate relationship between an evidence passage (premise) and hypothesis claim."""
        self._load_model()

        if self._model != "fallback":
            try:
                input_text = f"{premise} </s></s> {hypothesis}"
                outputs = self._model(input_text)[0]
                # Map DeBERTa outputs
                label_scores = {o["label"].lower(): o["score"] for o in outputs}
                top_label = max(label_scores, key=label_scores.get)
                return {
                    "label": top_label,
                    "score": round(float(label_scores[top_label]), 4),
                    "probabilities": label_scores,
                    "model": self.model_name,
                }
            except Exception as exc:
                logger.debug("Error running neural NLI: %s", exc)

        # Scientific keyword heuristic fallback
        return self._heuristic_nli(premise, hypothesis)

    @staticmethod
    def _heuristic_nli(premise: str, hypothesis: str) -> Dict[str, Any]:
        """Heuristic NLI evaluation based on semantic overlap and contradiction cues."""
        p_lower = premise.lower()
        h_lower = hypothesis.lower()

        contradiction_cues = ["no significant", "failed to", "ineffective", "did not improve", "no difference", "worsened"]
        has_contra = any(c in p_lower for c in contradiction_cues)

        p_words = set(p_lower.split())
        h_words = set(h_lower.split())
        overlap = len(p_words.intersection(h_words)) / max(1, len(h_words))

        if has_contra and overlap > 0.3:
            label = "contradiction"
            score = 0.82
        elif overlap > 0.4:
            label = "entailment"
            score = round(min(0.95, 0.5 + overlap * 0.5), 3)
        else:
            label = "neutral"
            score = 0.65

        return {
            "label": label,
            "score": score,
            "probabilities": {label: score},
            "model": "heuristic_baseline",
        }


nli_validator = NLIValidator()
