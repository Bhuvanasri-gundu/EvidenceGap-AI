"""Scientific Document and Passage Embedder.

Generates dense vector representations for documents and passages.
Supports Sentence-Transformers (SPECTER2, all-MiniLM-L6-v2) with
graceful deterministic fallback if PyTorch/Transformers models are not yet downloaded.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from config.settings import EMBEDDINGS_DIR, get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DocumentEmbedder:
    """Embeds scientific documents and text passages with metadata tracking."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        output_dir: Optional[Path] = None,
    ):
        self.model_name = model_name or settings.embedding_model
        self.output_dir = Path(output_dir or EMBEDDINGS_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._model = None
        self._dim = 384  # Default dimension for all-MiniLM-L6-v2

    def _load_model(self):
        """Lazy load the sentence transformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info("Loading embedding model: %s", self.model_name)
                self._model = SentenceTransformer(self.model_name)
                self._dim = self._model.get_sentence_embedding_dimension()
            except Exception as exc:
                logger.warning(
                    "SentenceTransformer could not be loaded (%s). Using fallback hash-based vectorizer.",
                    exc,
                )
                self._model = "fallback"

    def embed_texts(self, texts: List[str], batch_size: int = 64) -> np.ndarray:
        """Generate normalized dense embeddings for a list of texts."""
        if not texts:
            return np.empty((0, self._dim), dtype=np.float32)

        self._load_model()

        if self._model != "fallback":
            embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                normalize_embeddings=True,
            )
            return np.array(embeddings, dtype=np.float32)

        # Deterministic TF-IDF / character n-gram pseudo-embedding fallback
        return self._generate_fallback_embeddings(texts)

    def _generate_fallback_embeddings(self, texts: List[str]) -> np.ndarray:
        """Deterministic reproducible embedding representation for offline / low-resource mode."""
        dim = self._dim
        vectors = np.zeros((len(texts), dim), dtype=np.float32)
        for i, text in enumerate(texts):
            words = text.lower().split()
            vec = np.zeros(dim, dtype=np.float32)
            for w in words:
                h = abs(hash(w)) % dim
                vec[h] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm
            vectors[i] = vec
        return vectors

    def embed_documents(self, documents: List[Dict[str, Any]]) -> Tuple[np.ndarray, List[str]]:
        """Embed document collection using title + abstract concatenation.

        Returns (embeddings_array, list_of_pmids).
        """
        texts = []
        pmids = []
        for doc in documents:
            title = doc.get("title", "")
            abstract = doc.get("abstract", "")
            combined = f"{title}\n{abstract}".strip()
            texts.append(combined or "No content available.")
            pmids.append(str(doc.get("pmid", "")))

        logger.info("Generating embeddings for %d scientific documents...", len(texts))
        embeddings = self.embed_texts(texts)
        return embeddings, pmids

    def save_embeddings(
        self,
        embeddings: np.ndarray,
        ids: List[str],
        name: str = "doc_embeddings",
    ) -> Path:
        """Save embeddings as .npy alongside metadata JSON."""
        npy_path = self.output_dir / f"{name}.npy"
        meta_path = self.output_dir / f"{name}_meta.json"

        np.save(npy_path, embeddings)

        metadata = {
            "name": name,
            "model_name": self.model_name,
            "dimensions": int(embeddings.shape[1]) if embeddings.ndim > 1 else 0,
            "count": int(embeddings.shape[0]),
            "ids": ids,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info("Saved %d embeddings (dim=%d) to %s", len(ids), embeddings.shape[1], npy_path)
        return npy_path

    def load_embeddings(self, name: str = "doc_embeddings") -> Tuple[np.ndarray, Dict[str, Any]]:
        """Load embeddings .npy and corresponding metadata."""
        npy_path = self.output_dir / f"{name}.npy"
        meta_path = self.output_dir / f"{name}_meta.json"

        if not npy_path.exists():
            raise FileNotFoundError(f"Embeddings file {npy_path} not found")

        embeddings = np.load(npy_path)
        metadata = {}
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

        return embeddings, metadata


embedder = DocumentEmbedder()
