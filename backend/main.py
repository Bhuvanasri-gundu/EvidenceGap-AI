"""EvidenceGap AI 2026 — FastAPI Application Entry Point.

Ontology-Guided Hypothesis Generation Using LLMs and RAG.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.settings import get_settings, ensure_directories
from backend.persistence.database import init_db, close_db
from backend.api import corpus, research, hypotheses, evaluation, export, runs_router

logger = logging.getLogger("evidencegap")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger.info("Initializing EvidenceGap AI 2026 backend...")
    ensure_directories()
    await init_db()
    logger.info("Database initialized successfully.")

    yield

    # Shutdown
    logger.info("Shutting down EvidenceGap AI 2026 backend...")
    await close_db()
    logger.info("Database connections closed.")


app = FastAPI(
    title="EvidenceGap AI 2026 API",
    description=(
        "Ontology-Guided Hypothesis Generation Using LLMs and Topic Modeling in mHealth Research. "
        "Evidence-grounded research assistant for literature analysis, gap detection, "
        "and iterative hypothesis refinement."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
origins = [
    settings.frontend_url,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 routers
app.include_router(runs_router.router, prefix="/api/v1")
app.include_router(corpus.router, prefix="/api/v1")
app.include_router(research.router, prefix="/api/v1")
app.include_router(hypotheses.router, prefix="/api/v1")
app.include_router(evaluation.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")


@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "EvidenceGap AI 2026",
        "version": "1.0.0",
        "database": "sqlite+aiosqlite",
        "gemini_configured": settings.has_gemini_key,
        "bioportal_configured": settings.has_bioportal_key,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error for %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred", "type": type(exc).__name__},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.app_host, port=settings.app_port, reload=settings.app_debug)
