"""PMC Open Access Full-Text Retriever.

Retrieves and parses full-text XML for open-access articles via NCBI PMC E-utilities.
Distinguishes sections (Introduction, Methods, Results, Discussion, Conclusion).
"""

from __future__ import annotations

import json
import logging
import os
import socket
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
try:
    import urllib3.util.connection as urllib3_cn
    urllib3_cn.allowed_gai_family = lambda: socket.AF_INET
except Exception:
    pass

from config.settings import FULLTEXT_DIR, METADATA_DIR, get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

NCBI_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


class PMCFullTextRetriever:
    """Retrieves and parses full-text XML articles from PubMed Central Open Access."""

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        email: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.output_dir = Path(output_dir or FULLTEXT_DIR)
        self.metadata_dir = Path(METADATA_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        self.email = email or settings.pubmed_email
        self.api_key = api_key or settings.pubmed_api_key
        self.min_interval = 0.15 if (self.api_key and self.api_key != "your_ncbi_api_key_here") else 0.4
        self.last_request_time = 0.0

    def _rate_limit(self) -> None:
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

    def fetch_fulltext(self, pmcid: str) -> Optional[Dict[str, Any]]:
        """Fetch and parse full-text article for a PMCID."""
        # Clean PMCID format (ensure PMC prefix)
        clean_pmcid = pmcid if pmcid.startswith("PMC") else f"PMC{pmcid}"

        # Check if already cached
        json_file = self.output_dir / f"{clean_pmcid}.json"
        if json_file.exists():
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        url = f"{NCBI_BASE_URL}/efetch.fcgi"
        params = {
            "db": "pmc",
            "id": clean_pmcid,
            "retmode": "xml",
            "tool": "EvidenceGapAI",
            "email": self.email or "research@example.com",
        }
        if self.api_key and self.api_key != "your_ncbi_api_key_here":
            params["api_key"] = self.api_key

        self._rate_limit()
        logger.info("Fetching PMC full-text for %s...", clean_pmcid)

        try:
            resp = requests.get(url, params=params, timeout=45)
            if resp.status_code != 200:
                logger.warning("Failed to fetch %s: HTTP %d", clean_pmcid, resp.status_code)
                return None

            parsed = self.parse_pmc_xml(resp.text, clean_pmcid)
            if parsed:
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=2, ensure_ascii=False)
            return parsed

        except Exception as exc:
            logger.error("Exception fetching %s: %s", clean_pmcid, exc)
            return None

    def parse_pmc_xml(self, xml_content: str, pmcid: str) -> Optional[Dict[str, Any]]:
        """Parse PMC JATS XML into structured sections."""
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as err:
            logger.error("XML parse error for %s: %s", pmcid, err)
            return None

        # Title
        title_elem = root.find(".//article-title")
        title = "".join(title_elem.itertext()).strip() if title_elem is not None else ""

        # Abstract
        abstract_elem = root.find(".//abstract")
        abstract = "".join(abstract_elem.itertext()).strip() if abstract_elem is not None else ""

        # Body sections
        sections: List[Dict[str, str]] = []
        body_elem = root.find(".//body")

        if body_elem is not None:
            for sec in body_elem.findall(".//sec"):
                sec_title_elem = sec.find("title")
                sec_title = "".join(sec_title_elem.itertext()).strip() if sec_title_elem is not None else "Main"

                paragraphs = []
                for p in sec.findall(".//p"):
                    p_text = "".join(p.itertext()).strip()
                    if p_text:
                        paragraphs.append(p_text)

                if paragraphs:
                    sec_type = self._classify_section_type(sec_title)
                    sections.append({
                        "section_title": sec_title,
                        "section_type": sec_type,
                        "text": "\n\n".join(paragraphs),
                    })

        full_text = "\n\n".join([f"## {s['section_title']}\n{s['text']}" for s in sections])

        return {
            "pmcid": pmcid,
            "title": title,
            "abstract": abstract,
            "sections": sections,
            "full_text": full_text,
            "section_count": len(sections),
            "source_type": "fulltext",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _classify_section_type(title: str) -> str:
        """Classify a section heading into standard scientific sections."""
        t = title.lower()
        if any(w in t for w in ["intro", "background"]):
            return "introduction"
        if any(w in t for w in ["method", "design", "procedure", "participant", "material"]):
            return "methods"
        if any(w in t for w in ["result", "finding", "analysis"]):
            return "results"
        if any(w in t for w in ["discuss", "implication", "limitation"]):
            return "discussion"
        if any(w in t for w in ["conclu"]):
            return "conclusion"
        return "other"

    def batch_retrieve(self, pmcids: List[str], max_count: int = 100) -> Dict[str, Any]:
        """Retrieve full text for a list of PMCIDs up to max_count."""
        results = {}
        for pmcid in pmcids[:max_count]:
            if not pmcid:
                continue
            doc = self.fetch_fulltext(pmcid)
            if doc:
                results[pmcid] = doc
        return results


# Module singleton
fulltext_retriever = PMCFullTextRetriever()
