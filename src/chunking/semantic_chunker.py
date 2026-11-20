"""Section-Aware Semantic Text Chunker.

Chunks scientific documents respecting section boundaries and sentence integrity.
Preserves full academic provenance (PMID, PMCID, DOI, chunk_id, section, source_type).
Passages from different publications are strictly isolated.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from src.preprocessing.text_processor import text_processor

logger = logging.getLogger(__name__)


class SemanticChunker:
    """Creates provenance-preserving semantic chunks from scientific articles."""

    def __init__(
        self,
        target_chunk_words: int = 250,
        overlap_sentences: int = 1,
    ):
        self.target_chunk_words = target_chunk_words
        self.overlap_sentences = overlap_sentences

    def chunk_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Chunk an individual document into section-aware passages."""
        pmid = str(doc.get("pmid", ""))
        pmcid = str(doc.get("pmcid", ""))
        doi = str(doc.get("doi", ""))
        title = doc.get("title", "")
        source_type = doc.get("source_type", "abstract")

        chunks: List[Dict[str, Any]] = []

        # If document has full-text sections
        sections = doc.get("sections")
        if sections and isinstance(sections, list):
            for sec in sections:
                sec_title = sec.get("section_title", "Body")
                sec_type = sec.get("section_type", "body")
                sec_text = sec.get("text", "")
                chunks.extend(
                    self._create_chunks_from_text(
                        text=sec_text,
                        section_name=sec_title,
                        section_type=sec_type,
                        pmid=pmid,
                        pmcid=pmcid,
                        doi=doi,
                        title=title,
                        source_type="fulltext",
                    )
                )
        else:
            # Fall back to title + abstract chunking
            abstract = doc.get("abstract", "")
            full_abstract = f"{title}. {abstract}".strip()
            chunks.extend(
                self._create_chunks_from_text(
                    text=full_abstract,
                    section_name="Abstract",
                    section_type="abstract",
                    pmid=pmid,
                    pmcid=pmcid,
                    doi=doi,
                    title=title,
                    source_type=source_type,
                )
            )

        return chunks

    def _create_chunks_from_text(
        self,
        text: str,
        section_name: str,
        section_type: str,
        pmid: str,
        pmcid: str,
        doi: str,
        title: str,
        source_type: str,
    ) -> List[Dict[str, Any]]:
        """Segment a block of text into sentence-aware overlapping chunks."""
        sentences = text_processor.segment_sentences(text)
        if not sentences:
            return []

        chunks = []
        current_sentences: List[str] = []
        current_word_count = 0
        chunk_idx = 0

        for sentence in sentences:
            word_count = len(sentence.split())
            if current_word_count + word_count > self.target_chunk_words and current_sentences:
                # Flush current chunk
                passage = " ".join(current_sentences)
                chunks.append({
                    "chunk_id": f"{pmid}_chk_{chunk_idx}",
                    "pmid": pmid,
                    "pmcid": pmcid,
                    "doi": doi,
                    "doc_title": title,
                    "section_name": section_name,
                    "section_type": section_type,
                    "source_type": source_type,
                    "text": passage,
                    "word_count": current_word_count,
                })
                chunk_idx += 1

                # Keep overlap sentences
                current_sentences = current_sentences[-self.overlap_sentences :] if self.overlap_sentences > 0 else []
                current_word_count = sum(len(s.split()) for s in current_sentences)

            current_sentences.append(sentence)
            current_word_count += word_count

        # Final trailing chunk
        if current_sentences:
            passage = " ".join(current_sentences)
            chunks.append({
                "chunk_id": f"{pmid}_chk_{chunk_idx}",
                "pmid": pmid,
                "pmcid": pmcid,
                "doi": doi,
                "doc_title": title,
                "section_name": section_name,
                "section_type": section_type,
                "source_type": source_type,
                "text": passage,
                "word_count": current_word_count,
            })

        return chunks

    def chunk_corpus(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk an entire corpus of documents into individual passages."""
        all_chunks = []
        for doc in documents:
            doc_chunks = self.chunk_document(doc)
            all_chunks.extend(doc_chunks)
        logger.info(
            "Chunked %d documents into %d semantic passages", len(documents), len(all_chunks)
        )
        return all_chunks


chunker = SemanticChunker()
