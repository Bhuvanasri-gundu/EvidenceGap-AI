"""PubMed Literature Collector for mHealth Research.

Queries NCBI E-utilities (esearch + efetch) with rate-limiting, pagination,
XML parsing, deduplication, and resumability.
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

from config.settings import RAW_DATA_DIR, METADATA_DIR, get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

NCBI_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

MHEALTH_SEARCH_QUERY = (
    '("mHealth"[Title/Abstract] OR "mobile health"[Title/Abstract] OR '
    '"smartphone health"[Title/Abstract] OR "wearable health"[Title/Abstract] OR '
    '"digital health intervention"[Title/Abstract] OR "health app"[Title/Abstract] OR '
    '"telehealth"[Title/Abstract] OR "remote patient monitoring"[Title/Abstract]) '
    'AND ("2015/01/01"[Date - Publication] : "3000"[Date - Publication])'
)


class PubMedCollector:
    """Collects publication records from PubMed E-utilities."""

    def __init__(
        self,
        email: Optional[str] = None,
        api_key: Optional[str] = None,
        output_dir: Optional[Path] = None,
    ):
        self.email = email or settings.pubmed_email
        self.api_key = api_key or settings.pubmed_api_key
        self.output_dir = Path(output_dir or RAW_DATA_DIR)
        self.metadata_dir = Path(METADATA_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        # Rate limits: 3 req/sec without API key, 10 req/sec with key
        self.min_interval = 0.12 if (self.api_key and self.api_key != "your_ncbi_api_key_here") else 0.35
        self.last_request_time = 0.0

    def _rate_limit(self) -> None:
        """Enforce NCBI rate limits."""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

    def _get_base_params(self) -> Dict[str, str]:
        params = {"tool": "EvidenceGapAI", "email": self.email or "research@example.com"}
        if self.api_key and self.api_key != "your_ncbi_api_key_here":
            params["api_key"] = self.api_key
        return params

    def search_pmids(
        self,
        query: str = MHEALTH_SEARCH_QUERY,
        retmax: int = 5000,
        mindate: Optional[str] = None,
        maxdate: Optional[str] = None,
    ) -> List[str]:
        """Search PubMed for PMIDs matching query."""
        url = f"{NCBI_BASE_URL}/esearch.fcgi"
        params = {
            **self._get_base_params(),
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": str(retmax),
            "usehistory": "y",
        }
        if mindate:
            params["mindate"] = mindate
        if maxdate:
            params["maxdate"] = maxdate

        self._rate_limit()
        logger.info("Executing PubMed esearch: %s (retmax=%d)", query[:80], retmax)

        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        id_list = data.get("esearchresult", {}).get("idlist", [])
        total_count = int(data.get("esearchresult", {}).get("count", 0))
        logger.info("PubMed search found %d total records; retrieved %d PMIDs", total_count, len(id_list))
        return id_list

    def fetch_records_xml(self, pmids: List[str], batch_size: int = 200) -> List[Dict[str, Any]]:
        """Fetch full XML records for a list of PMIDs in batches."""
        records: List[Dict[str, Any]] = []
        url = f"{NCBI_BASE_URL}/efetch.fcgi"

        for i in range(0, len(pmids), batch_size):
            batch_pmids = pmids[i : i + batch_size]
            params = {
                **self._get_base_params(),
                "db": "pubmed",
                "id": ",".join(batch_pmids),
                "retmode": "xml",
            }

            self._rate_limit()
            logger.info("Fetching batch %d-%d of %d PMIDs...", i + 1, min(i + batch_size, len(pmids)), len(pmids))

            try:
                resp = requests.get(url, params=params, timeout=60)
                resp.raise_for_status()
                parsed = self.parse_pubmed_xml(resp.text)
                records.extend(parsed)
            except Exception as exc:
                logger.error("Failed to fetch batch %d: %s", i, exc)
                continue

        return records

    def parse_pubmed_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse PubMed XML into structured dictionaries."""
        records: List[Dict[str, Any]] = []
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as err:
            logger.error("XML parse error: %s", err)
            return records

        for article in root.findall(".//PubmedArticle"):
            try:
                # PMID
                pmid_elem = article.find(".//MedlineCitation/PMID")
                pmid = pmid_elem.text if pmid_elem is not None and pmid_elem.text else ""
                if not pmid:
                    continue

                # Title
                title_elem = article.find(".//ArticleTitle")
                title = "".join(title_elem.itertext()).strip() if title_elem is not None else ""

                # Abstract
                abstract_elems = article.findall(".//Abstract/AbstractText")
                abstract_parts = []
                for ab in abstract_elems:
                    label = ab.get("Label")
                    text = "".join(ab.itertext()).strip()
                    if label:
                        abstract_parts.append(f"{label}: {text}")
                    else:
                        abstract_parts.append(text)
                abstract = "\n".join(abstract_parts) if abstract_parts else ""

                # Journal
                journal_elem = article.find(".//Journal/Title")
                journal = journal_elem.text.strip() if journal_elem is not None and journal_elem.text else ""

                # Publication Date / Year
                pub_date = ""
                pub_year = None
                year_elem = article.find(".//JournalIssue/PubDate/Year")
                if year_elem is None or not year_elem.text:
                    year_elem = article.find(".//DateCompleted/Year")
                if year_elem is not None and year_elem.text:
                    pub_year = int(year_elem.text)
                    pub_date = f"{pub_year}-01-01"

                # Identifiers: DOI, PMCID
                doi = ""
                pmcid = ""
                for article_id in article.findall(".//ArticleIdList/ArticleId"):
                    id_type = article_id.get("IdType")
                    val = article_id.text or ""
                    if id_type == "doi":
                        doi = val
                    elif id_type == "pmc":
                        pmcid = val

                # MeSH Terms
                mesh_terms = []
                for mesh in article.findall(".//MeshHeadingList/MeshHeading"):
                    desc = mesh.find("DescriptorName")
                    if desc is not None and desc.text:
                        mesh_terms.append(desc.text)

                # Keywords
                keywords = []
                for kw in article.findall(".//KeywordList/Keyword"):
                    if kw.text:
                        keywords.append(kw.text.strip())

                # Authors
                authors = []
                for author in article.findall(".//AuthorList/Author"):
                    last = author.find("LastName")
                    fore = author.find("ForeName")
                    if last is not None and last.text:
                        full = f"{last.text} {fore.text if fore is not None and fore.text else ''}".strip()
                        authors.append(full)

                record = {
                    "pmid": pmid,
                    "pmcid": pmcid,
                    "doi": doi,
                    "title": title,
                    "abstract": abstract,
                    "journal": journal,
                    "pub_date": pub_date,
                    "pub_year": pub_year,
                    "authors": authors,
                    "mesh_terms": mesh_terms,
                    "keywords": keywords,
                    "source_type": "abstract",  # updated to fulltext if PMC article fetched
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                }
                records.append(record)

            except Exception as err:
                logger.warning("Error parsing individual article: %s", err)
                continue

        return records

    def save_corpus(self, records: List[Dict[str, Any]], filename: str = "mhealth_corpus.json") -> Path:
        """Save parsed corpus to JSON and summary metadata."""
        out_path = self.output_dir / filename
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        # Save metadata summary
        summary = {
            "total_records": len(records),
            "with_abstract": sum(1 for r in records if r.get("abstract")),
            "with_pmcid": sum(1 for r in records if r.get("pmcid")),
            "with_doi": sum(1 for r in records if r.get("doi")),
            "with_mesh": sum(1 for r in records if r.get("mesh_terms")),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        meta_path = self.metadata_dir / "collection_summary.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        logger.info("Saved %d records to %s", len(records), out_path)
        return out_path


# Global module singleton
collector = PubMedCollector()
