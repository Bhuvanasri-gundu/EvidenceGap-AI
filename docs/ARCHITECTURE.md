# EvidenceGap AI 2026 -- Architecture

## System Architecture

### Overview

EvidenceGap AI 2026 is a three-tier application:

1. **Frontend** -- React SPA for research interaction
2. **Backend** -- FastAPI REST API with background job processing
3. **Research Pipeline** -- Python modules for scientific analysis

### Component Diagram

```
+--------------------------------------------------------------+
|                        CLIENT LAYER                           |
|                                                               |
|  +---------------------------------------------------------+ |
|  |                React + TypeScript + Vite                  | |
|  |                                                           | |
|  |  Route /                    Route /workspace/:runId       | |
|  |  +-------------------+     +--------------------------+  | |
|  |  | Hypothesis         |     | Research Workspace       |  | |
|  |  | Generation Page    |     | +----------------------+|  | |
|  |  |                    |     | |Gaps  |Evid. |Valid.  ||  | |
|  |  | - Theme input      |     | |      |      |        ||  | |
|  |  | - Parameters       |     | |------+------+--------||  | |
|  |  | - Recent runs      |     | |Refine|Rank  |Eval.   ||  | |
|  |  | - Corpus stats     |     | +----------------------+|  | |
|  |  +-------------------+     +--------------------------+  | |
|  +---------------------------------------------------------+ |
+--------------------------------------------------------------+
                                | HTTP/REST
+-------------------------------v------------------------------+
|                        API LAYER                              |
|                                                               |
|  +---------------------------------------------------------+ |
|  |                   FastAPI Application                     | |
|  |                                                           | |
|  |  Routes:                    Services:                     | |
|  |  /api/v1/corpus     ->      CorpusService                 | |
|  |  /api/v1/research   ->      ResearchService               | |
|  |  /api/v1/hypotheses ->      HypothesisService             | |
|  |  /api/v1/evaluation ->      EvaluationService             | |
|  |  /api/v1/export     ->      ExportService                 | |
|  |                                                           | |
|  |  Background Jobs:          Persistence:                   | |
|  |  TaskManager        ->      SQLAlchemy + SQLite            | |
|  +---------------------------------------------------------+ |
+--------------------------------------------------------------+
                                |
+-------------------------------v------------------------------+
|                     RESEARCH PIPELINE                         |
|                                                               |
|  Phase 1: Literature Analysis                                 |
|  +----------+ +----------+ +----------+ +----------+       |
|  | Data     |->| Preproc  |->| Embed    |->| Topics   |       |
|  | Collect  | |          | |          | |          |       |
|  +----------+ +----------+ +----------+ +----------+       |
|                                                  |            |
|  +----------+ +----------+ +----------+        |            |
|  | Ontology |->| Knowl.   |->| Gap      |<--------+            |
|  | Mapping  | | Graph    | | Discovery|                      |
|  +----------+ +----------+ +----------+                      |
|                                    |                          |
|  Phase 2: RAG & Hypothesis                                    |
|  +----------+ +----------+        |                          |
|  | Semantic |->| FAISS    |<--------+                          |
|  | Chunking | | Retrieval|                                    |
|  +----------+ +----------+                                    |
|                       |                                       |
|  +----------+ +------v---+ +----------+ +----------+       |
|  | Ontology |->| Hypothesis|->| Evidence |->| Validation|       |
|  | RAG      | | Generate | | Challenge| |          |       |
|  +----------+ +----------+ +----------+ +----------+       |
|                                                  |            |
|  +----------+ +----------+                      |            |
|  | Refine   |->| Rank &   |<----------------------+            |
|  |          | | Dedup    |                                    |
|  +----------+ +----------+                                    |
|                                                               |
|  Phase 3: Evaluation                                          |
|  +----------+ +----------+ +----------+                     |
|  | Retrieval| | Hypothesis| | Baseline |                     |
|  | Metrics  | | Quality  | | Compare  |                     |
|  +----------+ +----------+ +----------+                      |
+--------------------------------------------------------------+

+--------------------------------------------------------------+
|                      DATA LAYER                               |
|                                                               |
|  SQLite DB     FAISS Index    File Artifacts                  |
|  +----------+ +----------+  +------------------------------+|
|  | Runs     | | Passage  |  | data/raw/     -> Raw corpus   ||
|  | Documents| | Vectors  |  | data/fulltext/-> Full texts   ||
|  | Topics   | |          |  | data/processed/-> Clean data  ||
|  | Gaps     | +----------+  | artifacts/    -> Embeddings,  ||
|  | Hypoths. |                |                topics, etc.  ||
|  | Evidence |                | outputs/      -> Results      ||
|  +----------+                +------------------------------+|
+--------------------------------------------------------------+
```

### Data Flow

1. **Data Collection**: PubMed E-utilities -> raw XML/CSV -> parsed documents
2. **Preprocessing**: Raw documents -> cleaned, deduplicated, filtered corpus
3. **Embeddings**: Corpus -> document vectors (SPECTER2) + passage vectors (MiniLM)
4. **Topic Modeling**: Document vectors -> BERTopic/LDA topics + temporal trends
5. **Ontology Mapping**: MeSH terms + extracted concepts -> normalized ontology graph
6. **Knowledge Graph**: Papers + topics + concepts -> NetworkX graph
7. **Gap Discovery**: Graph analysis + temporal trends -> ranked candidate gaps
8. **Chunking**: Full-text/abstracts -> semantic chunks with provenance
9. **FAISS Retrieval**: Chunk vectors -> searchable index
10. **Hypothesis Generation**: Gaps + retrieved evidence + Gemini -> structured hypotheses
11. **Evidence Challenge**: Hypotheses -> independent evidence search -> challenge report
12. **Validation**: Citation checks + NLI + novelty + rules -> validation results
13. **Refinement**: Hypotheses + challenge results -> refined hypotheses
14. **Ranking**: Validated hypotheses -> deduplicated, ranked list

### External Dependencies

| Service | Protocol | Purpose |
|---------|----------|---------|
| PubMed E-utilities | HTTPS REST | Article metadata and search |
| PMC OA | HTTPS REST | Full-text article retrieval |
| NCBI ID Converter | HTTPS REST | PMID/PMCID/DOI reconciliation |
| BioPortal | HTTPS REST | Ontology concept lookup |
| Google Gemini | HTTPS gRPC | LLM hypothesis generation |
| HuggingFace Hub | HTTPS | Model downloads (one-time) |

### Database Schema

See `backend/persistence/models.py` for the complete SQLAlchemy schema.

Key entities: Run, Document, Topic, ResearchGap, Hypothesis, EvidenceRecord.

### Security Considerations

- API keys stored in `.env`, never committed
- No user authentication (single-user research tool)
- PubMed rate limits respected programmatically
- CORS restricted to frontend origin
