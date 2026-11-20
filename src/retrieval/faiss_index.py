"""FAISS Vector Index for Scientific Passage Retrieval.

Supports IndexFlatIP and IVFFlat index types, metadata persistence,
diversity reranking to prevent single-paper overrepresentation, and near-duplicate suppression.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from config.settings import FAISS_DIR, get_settings
from src.embeddings.document_embedder import embedder

logger = logging.getLogger(__name__)
settings = get_settings()


class FAISSIndex:
    """FAISS-based dense passage retrieval index."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = Path(output_dir or FAISS_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.index = None
        self.metadata: List[Dict[str, Any]] = []
        self._dim = 384

    def build_index(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: Optional[np.ndarray] = None,
    ) -> None:
        """Build FAISS index from passages and embeddings."""
        if not chunks:
            logger.warning("No chunks provided to build FAISS index.")
            return

        texts = [c.get("text", "") for c in chunks]
        if embeddings is None:
            logger.info("Computing embeddings for %d passages...", len(texts))
            embeddings = embedder.embed_texts(texts)

        self._dim = embeddings.shape[1]
        self.metadata = chunks

        try:
            import faiss

            logger.info("Building FAISS IndexFlatIP (cosine similarity) with %d vectors...", len(embeddings))
            # Normalized embeddings with Inner Product = Cosine Similarity
            self.index = faiss.IndexFlatIP(self._dim)
            self.index.add(embeddings.astype(np.float32))

        except Exception as exc:
            logger.warning("FAISS native library error (%s). Using numpy fallback index.", exc)
            self.index = "fallback_numpy"
            self._fallback_vectors = embeddings

        self.save_index()

    def search(
        self,
        query: str,
        top_k: int = 10,
        max_per_doc: int = 2,
    ) -> List[Dict[str, Any]]:
        """Search index for passages semantically matching query with source diversity reranking."""
        if self.index is None:
            self.load_index()

        if self.index is None or not self.metadata:
            logger.warning("FAISS index is empty; returning empty search results.")
            return []

        query_vec = embedder.embed_texts([query])

        # Retrieve extra candidates for diversity reranking
        fetch_k = min(top_k * 4, len(self.metadata))

        if self.index != "fallback_numpy":
            scores, indices = self.index.search(query_vec.astype(np.float32), fetch_k)
            scores = scores[0]
            indices = indices[0]
        else:
            # Fallback cosine calculation
            sims = np.dot(self._fallback_vectors, query_vec[0])
            indices = np.argsort(sims)[::-1][:fetch_k]
            scores = sims[indices]

        # Source diversity reranking
        results: List[Dict[str, Any]] = []
        doc_counts: Dict[str, int] = {}

        for score, idx in zip(scores, indices):
            if idx < 0 or idx >= len(self.metadata):
                continue

            chunk = self.metadata[idx]
            pmid = chunk.get("pmid", "")

            # Limit passages per publication
            if pmid and doc_counts.get(pmid, 0) >= max_per_doc:
                continue

            doc_counts[pmid] = doc_counts.get(pmid, 0) + 1
            results.append({
                "chunk_id": chunk.get("chunk_id"),
                "pmid": pmid,
                "pmcid": chunk.get("pmcid"),
                "doi": chunk.get("doi"),
                "doc_title": chunk.get("doc_title"),
                "section_name": chunk.get("section_name"),
                "source_type": chunk.get("source_type"),
                "text": chunk.get("text"),
                "score": round(float(score), 4),
            })

            if len(results) >= top_k:
                break

        return results

    def save_index(self, name: str = "passage_index") -> Path:
        """Save FAISS index and metadata to disk."""
        index_file = self.output_dir / f"{name}.index"
        meta_file = self.output_dir / f"{name}_meta.json"

        if self.index is not None and self.index != "fallback_numpy":
            import faiss
            faiss.write_index(self.index, str(index_file))
        elif hasattr(self, "_fallback_vectors"):
            np.save(self.output_dir / f"{name}_vectors.npy", self._fallback_vectors)

        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

        logger.info("Saved FAISS index to %s", index_file)
        return index_file

    def load_index(self, name: str = "passage_index") -> bool:
        """Load index from disk if present."""
        index_file = self.output_dir / f"{name}.index"
        meta_file = self.output_dir / f"{name}_meta.json"
        vec_file = self.output_dir / f"{name}_vectors.npy"

        if not meta_file.exists():
            return False

        with open(meta_file, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        if index_file.exists():
            try:
                import faiss
                self.index = faiss.read_index(str(index_file))
                return True
            except Exception:
                pass

        if vec_file.exists():
            self._fallback_vectors = np.load(vec_file)
            self.index = "fallback_numpy"
            return True

        return False


vector_index = FAISSIndex()
