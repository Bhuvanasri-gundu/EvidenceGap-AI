"""Expand mHealth Corpus to 5,000 Real PubMed Publications.

End-to-End Pipeline:
1. Resumable PubMed E-utilities collection (esearch + efetch in batches of 200).
2. PMC Open Access full-text retrieval for accessible PMCIDs.
3. Deduplication (PMID, PMCID, DOI, title similarity) & relevance filtering.
4. Section-aware semantic chunking with source_type distinction.
5. Dense scientific vector embeddings & FAISS index.
6. BERTopic topic modeling & LDA baseline.
7. MeSH ontology mapping & comprehensive knowledge graph.
8. Research gap discovery.
9. Populate SQLite persistence database.
10. Scientific evaluation & reporting.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Enforce IPv4 on Windows to prevent getaddrinfo timeouts
try:
    import urllib3.util.connection as urllib3_cn
    urllib3_cn.allowed_gai_family = lambda: socket.AF_INET
except Exception:
    pass

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import (
    DATA_DIR,
    RAW_DATA_DIR,
    FULLTEXT_DIR,
    PROCESSED_DIR,
    METADATA_DIR,
    EMBEDDINGS_DIR,
    FAISS_DIR,
    TOPICS_DIR,
    ONTOLOGY_DIR,
    GRAPHS_DIR,
    GAPS_DIR,
    EVALUATION_DIR,
    get_settings,
)
from src.data_collection.pubmed_collector import PubMedCollector, MHEALTH_SEARCH_QUERY
from src.data_collection.pmc_fulltext import PMCFullTextRetriever
from src.preprocessing.text_processor import text_processor
from src.preprocessing.relevance_filter import relevance_filter
from src.chunking.semantic_chunker import chunker
from src.embeddings.document_embedder import embedder
from src.retrieval.faiss_index import vector_index
from src.topic_modeling.bertopic_modeler import modeler as topic_modeler
from src.topic_modeling.lda_baseline import lda_baseline
from src.ontology.mesh_mapper import mesh_mapper
from src.knowledge_graph.graph_builder import builder as kg_builder
from src.gap_discovery.gap_detector import discoverer as gap_discoverer
from backend.persistence.database import init_db, async_session_factory
from backend.persistence.models import Document, SourceType, Topic, ResearchGap

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(PROJECT_ROOT / "outputs" / "expand_corpus_5000.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("expand_corpus_5000")
settings = get_settings()

TARGET_RELEVANT_COUNT = 5000
RAW_FETCH_TARGET = 6200
CHECKPOINT_FILE = METADATA_DIR / "crawl_checkpoint_5000.json"
RAW_CORPUS_FILE = RAW_DATA_DIR / "mhealth_corpus_5000_raw.json"
CLEANED_CORPUS_FILE = PROCESSED_DIR / "cleaned_corpus.json"
CHUNKS_FILE = PROCESSED_DIR / "corpus_chunks.json"


def step_1_collect_pubmed_records() -> List[Dict[str, Any]]:
    """Collect candidate mHealth publications via PubMed E-utilities with checkpointing."""
    logger.info("=== STEP 1: PubMed E-utilities Collection (Target: %d raw) ===", RAW_FETCH_TARGET)

    collector = PubMedCollector()
    collector.output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Check if raw corpus is already collected
    if RAW_CORPUS_FILE.exists():
        try:
            with open(RAW_CORPUS_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
            if len(cached) >= TARGET_RELEVANT_COUNT:
                logger.info("Loaded %d pre-collected raw records from %s", len(cached), RAW_CORPUS_FILE)
                return cached
        except Exception as exc:
            logger.warning("Could not read cached raw corpus: %s", exc)

    # 2. Resumable search
    pmids: List[str] = []
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
            pmids = checkpoint.get("pmids", [])
            logger.info("Resumed from checkpoint with %d PMIDs", len(pmids))
        except Exception:
            pmids = []

    if not pmids:
        logger.info("Searching PubMed for mHealth publications: %s", MHEALTH_SEARCH_QUERY[:70])
        pmids = collector.search_pmids(query=MHEALTH_SEARCH_QUERY, retmax=RAW_FETCH_TARGET)
        logger.info("Retrieved %d PMIDs from PubMed search", len(pmids))
        with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
            json.dump({"pmids": pmids, "fetched_count": 0, "timestamp": datetime.now(timezone.utc).isoformat()}, f, indent=2)

    # 3. Fetch XML records in batches of 200
    batch_size = 200
    all_records: List[Dict[str, Any]] = []

    # Check for partially saved raw records
    temp_raw_file = RAW_DATA_DIR / "mhealth_corpus_5000_partial.json"
    if temp_raw_file.exists():
        try:
            with open(temp_raw_file, "r", encoding="utf-8") as f:
                all_records = json.load(f)
            logger.info("Loaded %d previously fetched partial records", len(all_records))
        except Exception:
            all_records = []

    fetched_pmids = {r["pmid"] for r in all_records if r.get("pmid")}
    remaining_pmids = [p for p in pmids if p not in fetched_pmids]

    logger.info("Need to fetch %d remaining PMIDs in batches of %d...", len(remaining_pmids), batch_size)

    for i in range(0, len(remaining_pmids), batch_size):
        batch = remaining_pmids[i : i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(remaining_pmids) + batch_size - 1) // batch_size
        logger.info("Fetching batch %d/%d (%d PMIDs)...", batch_num, total_batches, len(batch))

        try:
            batch_records = collector.fetch_records_xml(batch, batch_size=len(batch))
            all_records.extend(batch_records)
            logger.info("Fetched %d records. Total collected so far: %d", len(batch_records), len(all_records))

            # Checkpoint save
            with open(temp_raw_file, "w", encoding="utf-8") as f:
                json.dump(all_records, f, indent=2, ensure_ascii=False)

        except Exception as exc:
            logger.error("Error fetching batch %d: %s. Pausing 2s and continuing...", batch_num, exc)
            time.sleep(2.0)

    # Save final complete raw corpus
    with open(RAW_CORPUS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2, ensure_ascii=False)

    if temp_raw_file.exists():
        try:
            temp_raw_file.unlink()
        except Exception:
            pass

    logger.info("Successfully completed Step 1: %d total raw records saved to %s", len(all_records), RAW_CORPUS_FILE)
    return all_records


def step_2_retrieve_pmc_fulltexts(records: List[Dict[str, Any]], max_fulltext: int = 500) -> List[Dict[str, Any]]:
    """Retrieve PMC Open Access full texts for articles with PMCIDs."""
    logger.info("=== STEP 2: PMC Open Access Full-Text Retrieval (Max: %d) ===", max_fulltext)

    cache_file = RAW_DATA_DIR / "mhealth_corpus_5000_with_fulltext.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_records = json.load(f)
            ft_count = sum(1 for r in cached_records if r.get("source_type") == "fulltext")
            logger.info("Loaded %d records with %d full-text articles from %s", len(cached_records), ft_count, cache_file)
            return cached_records
        except Exception as exc:
            logger.warning("Could not load cached fulltext records: %s", exc)

    ft_retriever = PMCFullTextRetriever()
    FULLTEXT_DIR.mkdir(parents=True, exist_ok=True)

    pmcid_records = [r for r in records if r.get("pmcid")]
    logger.info("Found %d records with PMCIDs out of %d total (%.1f%%)",
                len(pmcid_records), len(records), (len(pmcid_records) / max(1, len(records))) * 100)

    fulltext_count = 0
    abstract_count = 0

    # Retrieve full texts up to max_fulltext
    for i, r in enumerate(records):
        pmcid = r.get("pmcid")
        if pmcid and fulltext_count < max_fulltext:
            clean_pmcid = pmcid if pmcid.startswith("PMC") else f"PMC{pmcid}"
            cached_json = FULLTEXT_DIR / f"{clean_pmcid}.json"

            if cached_json.exists():
                try:
                    with open(cached_json, "r", encoding="utf-8") as f:
                        ft_data = json.load(f)
                    r["sections"] = ft_data.get("sections", {})
                    r["source_type"] = "fulltext"
                    fulltext_count += 1
                    continue
                except Exception:
                    pass

            # Fetch via API
            try:
                ft_data = ft_retriever.fetch_fulltext(clean_pmcid)
                if ft_data and ft_data.get("sections"):
                    r["sections"] = ft_data.get("sections", {})
                    r["source_type"] = "fulltext"
                    fulltext_count += 1
                else:
                    r["source_type"] = "abstract"
                    abstract_count += 1
            except Exception as exc:
                logger.warning("Could not fetch fulltext for %s: %s", clean_pmcid, exc)
                r["source_type"] = "abstract"
                abstract_count += 1
        else:
            r["source_type"] = "abstract"
            abstract_count += 1

        if (i + 1) % 200 == 0:
            logger.info("Full-text progress: %d/%d processed (%d fulltext, %d abstract)",
                        i + 1, len(records), fulltext_count, abstract_count)

    # Save cached version
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
    except Exception as exc:
        logger.warning("Could not save fulltext cache: %s", exc)

    logger.info("Completed Step 2: %d full-text articles, %d abstract-only records", fulltext_count, abstract_count)
    return records


def step_3_deduplicate_and_filter(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate records by PMID, PMCID, DOI, and title similarity, and apply relevance filtering."""
    logger.info("=== STEP 3: Deduplication & Scientific Relevance Filtering ===")

    # 1. Deduplicate by identifiers
    seen_pmids: Set[str] = set()
    seen_pmcids: Set[str] = set()
    seen_dois: Set[str] = set()
    seen_titles: Set[str] = set()
    deduped: List[Dict[str, Any]] = []

    for r in records:
        pmid = str(r.get("pmid", "")).strip()
        pmcid = str(r.get("pmcid", "")).strip()
        doi = str(r.get("doi", "")).strip().lower()
        title_norm = text_processor.normalize_text(r.get("title", ""))[:80].lower()

        if pmid and pmid in seen_pmids:
            continue
        if pmcid and pmcid in seen_pmcids:
            continue
        if doi and doi in seen_dois:
            continue
        if title_norm and title_norm in seen_titles:
            continue

        if pmid:
            seen_pmids.add(pmid)
        if pmcid:
            seen_pmcids.add(pmcid)
        if doi:
            seen_dois.add(doi)
        if title_norm:
            seen_titles.add(title_norm)

        deduped.append(r)

    logger.info("Deduplication: %d raw -> %d unique publications", len(records), len(deduped))

    # 2. Relevance filtering
    relevant_records: List[Dict[str, Any]] = []
    for r in deduped:
        title = r.get("title", "")
        abstract = r.get("abstract", "")
        # Require title and at least minimum abstract
        if not title or len(abstract.strip()) < 40:
            continue

        score = relevance_filter.score_record(r)
        if score >= 1.0:
            r["relevance_score"] = round(score, 3)
            relevant_records.append(r)

    logger.info("Relevance filtering: %d unique -> %d relevant publications", len(deduped), len(relevant_records))

    # Retain target count (up to TARGET_RELEVANT_COUNT)
    if len(relevant_records) > TARGET_RELEVANT_COUNT:
        # Sort by relevance score descending
        relevant_records.sort(key=lambda x: x.get("relevance_score", 0.0), reverse=True)
        final_corpus = relevant_records[:TARGET_RELEVANT_COUNT]
    else:
        final_corpus = relevant_records

    # Save processed corpus
    with open(CLEANED_CORPUS_FILE, "w", encoding="utf-8") as f:
        json.dump(final_corpus, f, indent=2, ensure_ascii=False)

    summary = {
        "total_records": len(final_corpus),
        "fulltext_count": sum(1 for r in final_corpus if r.get("source_type") == "fulltext"),
        "abstract_count": sum(1 for r in final_corpus if r.get("source_type") == "abstract"),
        "with_mesh_terms": sum(1 for r in final_corpus if r.get("mesh_terms")),
        "with_doi": sum(1 for r in final_corpus if r.get("doi")),
        "with_pmcid": sum(1 for r in final_corpus if r.get("pmcid")),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(METADATA_DIR / "corpus_summary_5000.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info("Completed Step 3: %d publications retained (%d fulltext, %d abstract)",
                len(final_corpus), summary["fulltext_count"], summary["abstract_count"])
    return final_corpus


def step_4_chunk_corpus(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate section-aware semantic chunks preserving provenance."""
    logger.info("=== STEP 4: Section-Aware Semantic Chunking ===")

    all_chunks: List[Dict[str, Any]] = []

    for r in records:
        doc_chunks = chunker.chunk_document(r)
        all_chunks.extend(doc_chunks)

    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    logger.info("Completed Step 4: Generated %d passage chunks across %d documents",
                len(all_chunks), len(records))
    return all_chunks


def step_5_build_embeddings_and_vector_index(chunks: List[Dict[str, Any]]) -> None:
    """Generate dense scientific embeddings and build persistent vector index."""
    logger.info("=== STEP 5: Scientific Embeddings & Vector Indexing ===")

    emb_path = EMBEDDINGS_DIR / "chunk_embeddings.npy"
    import numpy as np

    if emb_path.exists():
        logger.info("Loading pre-computed embeddings array from %s...", emb_path)
        embeddings = np.load(emb_path)
        logger.info("Loaded embeddings shape: %s", embeddings.shape)
    else:
        texts = [c.get("text", "") for c in chunks]
        logger.info("Embedding %d passages with %s...", len(texts), settings.embedding_model)
        embeddings = embedder.embed_texts(texts, batch_size=256)
        np.save(emb_path, embeddings)
        logger.info("Saved %s embeddings array to %s (shape: %s)", embeddings.dtype, emb_path, embeddings.shape)

    # Build vector index (build_index automatically saves index and metadata)
    vector_index.build_index(chunks=chunks, embeddings=embeddings)
    logger.info("Completed Step 5: Vector index built with %d indexed passages", len(chunks))


def step_6_topic_modeling(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Run BERTopic modeling and LDA baseline on the 5,000-document corpus."""
    logger.info("=== STEP 6: Topic Modeling (BERTopic & LDA Baseline) ===")

    docs = [f"{r.get('title', '')}. {r.get('abstract', '')}" for r in records]
    timestamps = [r.get("pub_year") for r in records if r.get("pub_year")]

    # Run BERTopic
    topic_info = topic_modeler.fit_transform(docs, timestamps=timestamps)
    topic_modeler.save_results()
    logger.info("BERTopic discovered %d coherent scientific topics", len(topic_info))

    # Run LDA baseline for diversity & evaluation
    try:
        lda_res = lda_baseline.fit(docs)
        div = lda_baseline.evaluate_diversity()
        logger.info("LDA Baseline fitted (%d topics, diversity=%.3f)", len(lda_res), div)
    except Exception as exc:
        logger.warning("LDA baseline error: %s", exc)

    logger.info("Completed Step 6: Topic models fitted and saved")
    return topic_info


def step_7_mesh_ontology_and_knowledge_graph(records: List[Dict[str, Any]], topic_info: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Map MeSH ontologies and construct comprehensive knowledge graph."""
    logger.info("=== STEP 7: MeSH Ontology Mapping & Knowledge Graph Construction ===")

    # MeSH Mapping
    mesh_matrix = mesh_mapper.build_mesh_cooccurrence_matrix(records)
    logger.info("MeSH co-occurrence matrix built with %d base concepts", len(mesh_mapper.hierarchy))

    # Knowledge Graph
    kg_builder.build_from_corpus(records, max_docs=800)
    kg_builder.save_graph()
    graph_data = kg_builder.get_visualization_data(max_nodes=500)

    logger.info("Completed Step 7: Knowledge Graph built with %d nodes and %d edges",
                len(graph_data.get("nodes", [])), len(graph_data.get("edges", [])))
    return graph_data


def step_8_gap_discovery(records: List[Dict[str, Any]], topic_info: List[Dict[str, Any]], graph_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Detect candidate research gaps using topic frequencies and concept co-occurrences."""
    logger.info("=== STEP 8: Research Gap Discovery ===")

    gaps = gap_discoverer.detect_gaps(documents=records, topics=topic_info)
    gap_discoverer.save_gaps()

    logger.info("Completed Step 8: Discovered %d candidate research gaps", len(gaps))
    return gaps


async def step_9_populate_database(records: List[Dict[str, Any]], topic_info: List[Dict[str, Any]], gaps: List[Dict[str, Any]]) -> None:
    """Populate SQLite database with all publications, topics, and gaps."""
    logger.info("=== STEP 9: Populating SQLite Persistence Database ===")

    await init_db()

    async with async_session_factory() as session:
        # Delete existing documents to refresh with the 5,000 corpus
        from sqlalchemy import delete
        await session.execute(delete(Document))
        await session.commit()

        # Batch insert documents
        batch_size = 500
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            for r in batch:
                st = SourceType.fulltext if r.get("source_type") == "fulltext" else SourceType.abstract
                doc = Document(
                    pmid=str(r.get("pmid", "")),
                    pmcid=r.get("pmcid"),
                    doi=r.get("doi"),
                    title=r.get("title", ""),
                    abstract=r.get("abstract", ""),
                    journal=r.get("journal"),
                    pub_date=r.get("pub_date"),
                    source_type=st,
                    mesh_terms=json.dumps(r.get("mesh_terms", [])),
                )
                session.add(doc)
            await session.commit()
            logger.info("Inserted %d/%d documents into database...", min(i + batch_size, len(records)), len(records))

    logger.info("Completed Step 9: Database populated successfully")


def step_10_scientific_evaluation_and_report() -> Dict[str, Any]:
    """Execute scientific evaluation and generate summary report."""
    logger.info("=== STEP 10: Scientific Evaluation & Artifact Summary ===")

    # Read summaries
    with open(METADATA_DIR / "corpus_summary_5000.json", "r", encoding="utf-8") as f:
        corpus_summary = json.load(f)

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    with open(TOPICS_DIR / "topic_summary.json", "r", encoding="utf-8") as f:
        topics_raw = json.load(f)
        topics = topics_raw.get("topics", topics_raw) if isinstance(topics_raw, dict) else topics_raw

    with open(GRAPHS_DIR / "knowledge_graph.json", "r", encoding="utf-8") as f:
        graph = json.load(f)

    with open(GAPS_DIR / "candidate_gaps.json", "r", encoding="utf-8") as f:
        gaps_raw = json.load(f)
        gaps = gaps_raw.get("gaps", gaps_raw) if isinstance(gaps_raw, dict) else gaps_raw

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_publications_collected": corpus_summary.get("total_records", 0),
        "relevant_publications_retained": corpus_summary.get("total_records", 0),
        "fulltext_articles": corpus_summary.get("fulltext_count", 0),
        "abstract_only_records": corpus_summary.get("abstract_count", 0),
        "fulltext_percentage": round((corpus_summary.get("fulltext_count", 0) / max(1, corpus_summary.get("total_records", 1))) * 100, 2),
        "total_chunks_indexed": len(chunks),
        "topics_discovered": len(topics),
        "knowledge_graph_nodes": len(graph.get("nodes", [])),
        "knowledge_graph_edges": len(graph.get("edges", [])),
        "candidate_gaps_identified": len(gaps),
    }

    report_path = EVALUATION_DIR / "corpus_5000_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info("=== FINAL PIPELINE EXECUTION REPORT ===")
    for k, v in report.items():
        logger.info("  %s: %s", k, v)

    return report


def main():
    start_time = time.time()
    logger.info("STARTING AUTOMATED 5,000 PUBMED PUBLICATION CRAWL & PIPELINE BUILD")

    # Step 1: Collect PubMed
    records = step_1_collect_pubmed_records()

    # Step 2: Retrieve PMC Full Texts
    records = step_2_retrieve_pmc_fulltexts(records, max_fulltext=500)

    # Step 3: Deduplicate and Filter
    clean_records = step_3_deduplicate_and_filter(records)

    # Step 4: Chunking
    chunks = step_4_chunk_corpus(clean_records)

    # Step 5: Embeddings & Vector Index
    step_5_build_embeddings_and_vector_index(chunks)

    # Step 6: Topic Modeling
    topic_info = step_6_topic_modeling(clean_records)

    # Step 7: MeSH & Knowledge Graph
    graph_data = step_7_mesh_ontology_and_knowledge_graph(clean_records, topic_info)

    # Step 8: Gap Discovery
    gaps = step_8_gap_discovery(clean_records, topic_info, graph_data)

    # Step 9: Database Population
    asyncio.run(step_9_populate_database(clean_records, topic_info, gaps))

    # Step 10: Scientific Evaluation & Report
    report = step_10_scientific_evaluation_and_report()

    elapsed = time.time() - start_time
    logger.info("ALL 10 STEPS COMPLETED IN %.1f MINUTES (%.1f SECONDS)", elapsed / 60, elapsed)
    return report


if __name__ == "__main__":
    main()
