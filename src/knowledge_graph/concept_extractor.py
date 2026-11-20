"""Biomedical Concept and Entity Extractor.

Extracts biomedical entities categorized into:
- Disease / Condition
- Intervention / Therapy
- Technology / Device
- Population / Demographics
- Outcome / Clinical Metric
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)

# Domain patterns for rule-based biomedical entity extraction
ENTITY_PATTERNS = {
    "Disease": [
        r"\b(type 1 diabetes|type 2 diabetes|diabetes mellitus|t1d|t2d)\b",
        r"\b(hypertension|high blood pressure|cardiovascular disease|heart failure)\b",
        r"\b(major depressive disorder|depression|anxiety|bipolar|ptsd)\b",
        r"\b(asthma|copd|respiratory illness)\b",
        r"\b(obesity|overweight|metabolic syndrome)\b",
    ],
    "Technology": [
        r"\b(mobile app|smartphone application|mhealth app|ios|android)\b",
        r"\b(wearable sensor|smartwatch|biosensor|fitbit|apple watch|accelerometer)\b",
        r"\b(continuous glucose monitor|cgm|blood pressure monitor|cuff)\b",
        r"\b(telehealth platform|video consultation|remote monitoring system)\b",
        r"\b(sms|text messaging reminder|automated push notification)\b",
    ],
    "Intervention": [
        r"\b(cognitive behavioral therapy|cbt|internet-delivered cbt)\b",
        r"\b(gamification|peer support|digital coaching)\b",
        r"\b(self-management intervention|behavior change technique|nudge)\b",
        r"\b(tele-rehabilitation|remote physical therapy)\b",
    ],
    "Population": [
        r"\b(pediatric|adolescents?|children|youth|teenagers?)\b",
        r"\b(older adults?|geriatric|elderly|seniors?)\b",
        r"\b(rural population|underserved communities|low-income)\b",
        r"\b(pregnant women|maternal|postpartum)\b",
    ],
    "Outcome": [
        r"\b(glycemic control|hba1c|glucose variability)\b",
        r"\b(medication adherence|treatment compliance|app retention)\b",
        r"\b(systolic blood pressure|diastolic blood pressure)\b",
        r"\b(quality of life|qol|well-being|psychological distress)\b",
        r"\b(physical activity|step count|daily active minutes)\b",
    ],
}


class ConceptExtractor:
    """Extracts typed biomedical concepts from clinical and research literature."""

    def __init__(self):
        self.compiled_patterns = {
            cat: [re.compile(p, re.IGNORECASE) for p in patterns]
            for cat, patterns in ENTITY_PATTERNS.items()
        }

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract typed entities from text."""
        entities: Dict[str, Set[str]] = {cat: set() for cat in ENTITY_PATTERNS}

        for cat, patterns in self.compiled_patterns.items():
            for pat in patterns:
                matches = pat.findall(text)
                for m in matches:
                    entities[cat].add(m.strip().lower())

        return {cat: sorted(list(items)) for cat, items in entities.items()}


concept_extractor = ConceptExtractor()
