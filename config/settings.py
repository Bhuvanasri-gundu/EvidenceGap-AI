"""EvidenceGap AI 2026 -- Central Configuration Module.

Loads settings from environment variables and .env file.
All configuration is centralized here to avoid scattered hardcoded values.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Key directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
FULLTEXT_DIR = DATA_DIR / "fulltext"
PROCESSED_DIR = DATA_DIR / "processed"
METADATA_DIR = DATA_DIR / "metadata"

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
EMBEDDINGS_DIR = ARTIFACTS_DIR / "embeddings"
FAISS_DIR = ARTIFACTS_DIR / "faiss"
TOPICS_DIR = ARTIFACTS_DIR / "topics"
ONTOLOGY_DIR = ARTIFACTS_DIR / "ontology"
GRAPHS_DIR = ARTIFACTS_DIR / "graphs"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
GAPS_DIR = OUTPUTS_DIR / "gaps"
HYPOTHESES_DIR = OUTPUTS_DIR / "hypotheses"
VALIDATION_DIR = OUTPUTS_DIR / "validation"
EVALUATION_DIR = OUTPUTS_DIR / "evaluation"
FIGURES_DIR = OUTPUTS_DIR / "figures"

MODELS_DIR = PROJECT_ROOT / "models"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    bioportal_api_key: str = Field(default="", description="BioPortal API key")
    pubmed_email: str = Field(default="", description="Email for PubMed E-utilities")
    pubmed_api_key: str = Field(default="", description="NCBI API key")

    # Application
    app_env: str = Field(default="development")
    app_debug: bool = Field(default=True)
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)
    frontend_url: str = Field(default="http://localhost:5173")

    # Database
    database_url: str = Field(
        default=f"sqlite+aiosqlite:///{DATA_DIR / 'evidencegap.db'}"
    )

    # Models
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    specter_model: str = Field(default="allenai/specter2")
    nli_model: str = Field(default="cross-encoder/nli-deberta-v3-base")

    # Data Collection
    pubmed_batch_size: int = Field(default=500)
    pubmed_rate_limit_per_second: float = Field(default=3.0)
    pmc_fulltext_batch_size: int = Field(default=50)
    max_articles: int = Field(default=10000)

    # Topic Modeling
    bertopic_min_topic_size: int = Field(default=10)
    bertopic_nr_topics: str = Field(default="auto")
    lda_num_topics: int = Field(default=20)

    # FAISS
    faiss_index_type: str = Field(default="IVFFlat")
    faiss_nprobe: int = Field(default=10)

    # Hypothesis Generation
    gemini_model: str = Field(default="gemini-2.0-flash")
    gemini_temperature: float = Field(default=0.7)
    gemini_max_output_tokens: int = Field(default=8192)
    max_hypotheses_per_run: int = Field(default=10)

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    model_config = {
        "env_file": str(PROJECT_ROOT / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def has_gemini_key(self) -> bool:
        return bool(self.gemini_api_key) and self.gemini_api_key != "your_gemini_api_key_here"

    @property
    def has_bioportal_key(self) -> bool:
        return bool(self.bioportal_api_key) and self.bioportal_api_key != "your_bioportal_api_key_here"

    @property
    def has_pubmed_credentials(self) -> bool:
        return bool(self.pubmed_email) and self.pubmed_email != "your_email@example.com"


def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


def ensure_directories():
    """Create all required project directories."""
    for d in [
        RAW_DATA_DIR, FULLTEXT_DIR, PROCESSED_DIR, METADATA_DIR,
        EMBEDDINGS_DIR, FAISS_DIR, TOPICS_DIR, ONTOLOGY_DIR, GRAPHS_DIR,
        GAPS_DIR, HYPOTHESES_DIR, VALIDATION_DIR, EVALUATION_DIR, FIGURES_DIR,
        MODELS_DIR,
    ]:
        d.mkdir(parents=True, exist_ok=True)
