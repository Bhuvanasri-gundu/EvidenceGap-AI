"""Text Preprocessing and Normalization Module.

Handles duplicate detection, text cleaning, language verification,
sentence segmentation, and data quality reporting.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class TextProcessor:
    """Preprocesses and normalizes scientific text while preserving biomedical nomenclature."""

    def __init__(self):
        # Compiled patterns for text cleanup
        self._whitespace_re = re.compile(r"\s+")
        self._html_tag_re = re.compile(r"<[^>]+>")
        self._doi_re = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")

    def normalize_text(self, text: str) -> str:
        """Normalize Unicode, strip HTML tags, fix whitespace, preserve scientific characters."""
        if not text:
            return ""

        # Normalize unicode (NFKC preserves characters like Greek letters and mathematical symbols)
        text = unicodedata.normalize("NFKC", text)

        # Remove HTML/XML markup tags
        text = self._html_tag_re.sub(" ", text)

        # Collapse excessive whitespace
        text = self._whitespace_re.sub(" ", text)

        return text.strip()

    def segment_sentences(self, text: str) -> List[str]:
        """Segment text into sentences with biomedical abbreviation protection."""
        if not text:
            return []

        # Scientific sentence boundary splitter that avoids splitting on e.g., i.e., vs., Fig., etc.
        protected = text
        replacements = {
            "e.g.": "e_g_",
            "i.e.": "i_e_",
            "vs.": "vs_",
            "Fig.": "Fig_",
            "Ref.": "Ref_",
            "et al.": "et_al_",
            "approx.": "approx_",
            "dr.": "dr_",
        }
        for orig, rep in replacements.items():
            protected = re.sub(re.escape(orig), rep, protected, flags=re.IGNORECASE)

        # Split on sentence endings
        raw_sentences = re.split(r"(?<=[.!?])\s+", protected)

        sentences = []
        for s in raw_sentences:
            for orig, rep in replacements.items():
                s = s.replace(rep, orig)
            s = s.strip()
            if len(s) > 10:  # Filter out trivial fragments
                sentences.append(s)

        return sentences

    def detect_duplicates(
        self, records: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Deduplicate records based on PMID, DOI, and normalized title similarity.

        Returns (unique_records, duplicate_records).
        """
        seen_pmids: Set[str] = set()
        seen_dois: Set[str] = set()
        seen_titles: Set[str] = set()

        unique: List[Dict[str, Any]] = []
        duplicates: List[Dict[str, Any]] = []

        for r in records:
            pmid = str(r.get("pmid", "")).strip()
            doi = str(r.get("doi", "")).strip().lower()
            norm_title = re.sub(r"[^\w\s]", "", r.get("title", "").lower()).strip()

            is_dup = False
            if pmid and pmid in seen_pmids:
                is_dup = True
            elif doi and doi in seen_dois:
                is_dup = True
            elif norm_title and norm_title in seen_titles:
                is_dup = True

            if is_dup:
                duplicates.append(r)
            else:
                if pmid:
                    seen_pmids.add(pmid)
                if doi:
                    seen_dois.add(doi)
                if norm_title:
                    seen_titles.add(norm_title)
                unique.append(r)

        logger.info("Deduplication complete: %d unique records, %d duplicates removed", len(unique), len(duplicates))
        return unique, duplicates

    def generate_quality_report(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate audit report of corpus completeness and data quality."""
        total = len(records)
        if total == 0:
            return {"total": 0}

        with_abstract = sum(1 for r in records if r.get("abstract"))
        with_pmcid = sum(1 for r in records if r.get("pmcid"))
        with_doi = sum(1 for r in records if r.get("doi"))
        with_mesh = sum(1 for r in records if r.get("mesh_terms"))
        fulltext_count = sum(1 for r in records if r.get("source_type") == "fulltext")

        years = [r.get("pub_year") for r in records if r.get("pub_year")]
        min_year = min(years) if years else None
        max_year = max(years) if years else None

        return {
            "total_records": total,
            "abstract_coverage_pct": round((with_abstract / total) * 100, 2),
            "fulltext_coverage_pct": round((fulltext_count / total) * 100, 2),
            "pmcid_coverage_pct": round((with_pmcid / total) * 100, 2),
            "doi_coverage_pct": round((with_doi / total) * 100, 2),
            "mesh_coverage_pct": round((with_mesh / total) * 100, 2),
            "year_range": {"min": min_year, "max": max_year},
        }


text_processor = TextProcessor()
