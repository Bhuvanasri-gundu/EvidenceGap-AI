"""Identifier Resolver for PubMed, PMC, and DOI.

Reconciles PMID ↔ PMCID ↔ DOI using the NCBI ID Converter API.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

import requests

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

NCBI_IDCONV_URL = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"


class IdentifierResolver:
    """Reconciles academic identifiers (PMID, PMCID, DOI) via NCBI ID Converter API."""

    def __init__(self, email: Optional[str] = None):
        self.email = email or settings.pubmed_email
        self.min_interval = 0.35
        self.last_request_time = 0.0

    def _rate_limit(self) -> None:
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

    def resolve_batch(self, ids: List[str]) -> List[Dict[str, str]]:
        """Resolve a batch of up to 200 identifiers to their mapped IDs."""
        if not ids:
            return []

        self._rate_limit()
        params = {
            "tool": "EvidenceGapAI",
            "email": self.email or "research@example.com",
            "ids": ",".join(ids[:200]),
            "format": "json",
        }

        try:
            resp = requests.get(NCBI_IDCONV_URL, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            records = data.get("records", [])
            resolved = []
            for rec in records:
                resolved.append({
                    "pmid": str(rec.get("pmid", "")),
                    "pmcid": rec.get("pmcid", ""),
                    "doi": rec.get("doi", ""),
                    "status": "resolved" if not rec.get("status") else rec.get("status"),
                })
            return resolved
        except Exception as exc:
            logger.error("Error resolving identifiers: %s", exc)
            return []


resolver = IdentifierResolver()
