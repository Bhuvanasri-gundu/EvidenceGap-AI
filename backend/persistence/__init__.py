"""Persistence layer — SQLAlchemy models and database management."""
from backend.persistence.database import get_session, init_db, engine
from backend.persistence.models import Base, Run, Document, Topic, ResearchGap, Hypothesis, EvidenceRecord
