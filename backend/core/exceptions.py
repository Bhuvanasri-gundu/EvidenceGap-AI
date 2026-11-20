"""Custom application exceptions for EvidenceGap AI."""

from typing import Any, Optional


class EvidenceGapException(Exception):
    """Base exception for all EvidenceGap AI errors."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class CorpusNotFoundException(EvidenceGapException):
    """Raised when a requested corpus document or PMID does not exist."""
    pass


class RunNotFoundException(EvidenceGapException):
    """Raised when a research run session ID is not found."""
    pass


class HypothesisGenerationException(EvidenceGapException):
    """Raised when hypothesis generation pipeline encounters a failure."""
    pass


class InvalidRetrievalQueryException(EvidenceGapException):
    """Raised when retrieval parameters or query strings are malformed."""
    pass
