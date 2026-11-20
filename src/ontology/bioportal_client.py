"""BioPortal REST API Client for Biomedical Ontology Mapping.

Queries BioPortal for standardized ontology concepts (SNOMED-CT, MeSH, NCIT)
with graceful fallback when an API key is not configured.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import requests

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

BIOPORTAL_BASE_URL = "https://data.bioontology.org"


class BioPortalClient:
    """Queries NCBO BioPortal REST API for biomedical concept lookups."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.bioportal_api_key
        self.has_key = bool(self.api_key) and self.api_key != "your_bioportal_api_key_here"

    def search_concept(self, term: str, ontologies: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search BioPortal for a biomedical concept."""
        if not self.has_key:
            logger.debug("BioPortal API key not configured; returning local ontology lookup.")
            return self._local_fallback_search(term)

        ontologies = ontologies or ["MESH", "SNOMEDCT", "NCIT"]
        url = f"{BIOPORTAL_BASE_URL}/search"
        params = {
            "q": term,
            "ontologies": ",".join(ontologies),
            "pagesize": 5,
            "apikey": self.api_key,
        }

        try:
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for item in data.get("collection", []):
                    results.append({
                        "prefLabel": item.get("prefLabel"),
                        "ontology": item.get("links", {}).get("ontology", "").split("/")[-1],
                        "id": item.get("@id"),
                        "synonyms": item.get("synonym", []),
                    })
                return results
            else:
                logger.warning("BioPortal responded with HTTP %d", resp.status_code)
                return self._local_fallback_search(term)
        except Exception as exc:
            logger.warning("BioPortal search failed: %s", exc)
            return self._local_fallback_search(term)

    def _local_fallback_search(self, term: str) -> List[Dict[str, Any]]:
        """Offline fallback concept mappings for mHealth domains."""
        from src.ontology.mesh_mapper import MHEALTH_MESH_HIERARCHY

        t_clean = term.lower()
        results = []
        for name, data in MHEALTH_MESH_HIERARCHY.items():
            if t_clean in name.lower() or any(t_clean in s.lower() for s in data["synonyms"]):
                results.append({
                    "prefLabel": name,
                    "ontology": "MESH",
                    "id": f"http://id.nlm.nih.gov/mesh/{data['tree_number']}",
                    "synonyms": data["synonyms"],
                })
        return results


bioportal_client = BioPortalClient()
