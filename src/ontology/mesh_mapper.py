"""Medical Subject Headings (MeSH) Ontology Mapper.

Extracts, normalizes, and navigates hierarchical MeSH descriptors and qualifiers
for query expansion and ontology-guided gap detection.
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from config.settings import ONTOLOGY_DIR

logger = logging.getLogger(__name__)

# Standard mHealth-relevant MeSH hierarchy fragments
MHEALTH_MESH_HIERARCHY = {
    "Mobile Applications": {
        "tree_number": "L01.224.230.110.500",
        "broader": ["Software", "Informatics"],
        "narrower": ["Smartphone Apps"],
        "synonyms": ["mHealth Apps", "Mobile Apps", "Health Applications"],
    },
    "Telemedicine": {
        "tree_number": "L01.224.230.110.875",
        "broader": ["Remote Consultation", "Telehealth"],
        "narrower": ["Telerehabilitation", "Teledermatology"],
        "synonyms": ["Telehealth", "eHealth", "Remote Medicine"],
    },
    "Wearable Electronic Devices": {
        "tree_number": "E07.950",
        "broader": ["Electronic Devices", "Equipment and Supplies"],
        "narrower": ["Fitness Trackers", "Smartwatches", "Biosensors"],
        "synonyms": ["Wearables", "Activity Trackers", "Smart Wearables"],
    },
    "Remote Sensing Technology": {
        "tree_number": "J01.897",
        "broader": ["Technology"],
        "narrower": ["Patient Remote Monitoring"],
        "synonyms": ["Remote Monitoring", "Sensor Telemetry"],
    },
    "Diabetes Mellitus, Type 1": {
        "tree_number": "C18.452.394.750.315",
        "broader": ["Diabetes Mellitus", "Endocrine System Diseases"],
        "narrower": ["Pediatric Type 1 Diabetes"],
        "synonyms": ["T1D", "Type 1 Diabetes", "Juvenile Diabetes"],
    },
    "Hypertension": {
        "tree_number": "C14.907.489",
        "broader": ["Vascular Diseases", "Cardiovascular Diseases"],
        "narrower": ["Essential Hypertension", "Pregnancy-Induced Hypertension"],
        "synonyms": ["High Blood Pressure", "Elevated Blood Pressure"],
    },
    "Patient Compliance": {
        "tree_number": "F01.145.126.990",
        "broader": ["Behavior and Behavior Mechanisms"],
        "narrower": ["Medication Adherence"],
        "synonyms": ["Adherence", "Treatment Adherence", "Compliance"],
    },
    "Self-Management": {
        "tree_number": "E02.760.169.063.500",
        "broader": ["Self Care"],
        "narrower": ["Chronic Disease Self-Management"],
        "synonyms": ["Self Care", "Disease Management"],
    },
}


class MeSHMapper:
    """Navigates and expands biomedical concepts using MeSH ontologies."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = Path(output_dir or ONTOLOGY_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.hierarchy = MHEALTH_MESH_HIERARCHY

    def get_synonyms(self, term: str) -> List[str]:
        """Find synonym terms for a MeSH descriptor."""
        normalized = term.strip().lower()
        for mesh_name, data in self.hierarchy.items():
            if mesh_name.lower() == normalized or normalized in [s.lower() for s in data["synonyms"]]:
                return [mesh_name] + data["synonyms"]
        return [term]

    def get_related_concepts(self, term: str) -> Dict[str, List[str]]:
        """Retrieve broader and narrower ontological concepts."""
        normalized = term.strip().lower()
        for mesh_name, data in self.hierarchy.items():
            if mesh_name.lower() == normalized or normalized in [s.lower() for s in data["synonyms"]]:
                return {
                    "broader": data["broader"],
                    "narrower": data["narrower"],
                    "synonyms": data["synonyms"],
                }
        return {"broader": [], "narrower": [], "synonyms": []}

    def expand_query(self, query: str) -> List[str]:
        """Expand a query string into a list of synonymous and narrower MeSH terms."""
        expanded_terms = set()
        words = query.lower().split()

        for mesh_name, data in self.hierarchy.items():
            if any(w in mesh_name.lower() for w in words):
                expanded_terms.add(mesh_name)
                expanded_terms.update(data["synonyms"])
                expanded_terms.update(data["narrower"])

        return list(expanded_terms) if expanded_terms else [query]

    def build_mesh_cooccurrence_matrix(
        self, records: List[Dict[str, Any]], top_n: int = 50
    ) -> Dict[str, Dict[str, int]]:
        """Build term-term co-occurrence matrix from article MeSH annotations."""
        matrix: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for r in records:
            terms = r.get("mesh_terms") or []
            for i, t1 in enumerate(terms):
                for t2 in terms[i + 1 :]:
                    matrix[t1][t2] += 1
                    matrix[t2][t1] += 1
        return matrix


mesh_mapper = MeSHMapper()
