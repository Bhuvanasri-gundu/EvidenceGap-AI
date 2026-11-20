# EvidenceGap AI 2026 — REST API Documentation

The EvidenceGap AI backend is built with FastAPI and provides RESTful endpoints under `/api/v1`.

Base URL: `http://localhost:8000/api/v1`
Interactive Swagger Docs: `http://localhost:8000/docs`

---

## 1. Health & Status

### `GET /health`
Returns service availability, connected database, and configured API status.

**Response `200 OK`:**
```json
{
  "status": "healthy",
  "service": "EvidenceGap AI 2026",
  "version": "1.0.0",
  "database": "sqlite+aiosqlite",
  "gemini_configured": true,
  "bioportal_configured": false
}
```

---

## 2. Corpus Endpoints (`/api/v1/corpus`)

### `GET /api/v1/corpus/`
Returns high-level corpus statistics.

**Response `200 OK`:**
```json
{
  "total_documents": 158,
  "fulltext_count": 82,
  "abstract_count": 76,
  "date_range": {
    "earliest": "2019-09-18",
    "latest": "2024-05-10"
  },
  "top_journals": [
    { "journal": "Journal of Medical Internet Research", "count": 78 },
    { "journal": "The Lancet Digital Health", "count": 22 }
  ],
  "mesh_term_count": 158
}
```

### `GET /api/v1/corpus/documents`
Paginated search and filter across literature records.

**Parameters:**
- `page` (int, default: 1)
- `page_size` (int, default: 20)
- `journal` (optional string)
- `source_type` (optional string: `fulltext` | `abstract`)
- `search` (optional string query for title/abstract)

### `GET /api/v1/corpus/documents/{pmid}`
Retrieves a single publication by its PubMed Identifier.

---

## 3. Research & Gap Endpoints (`/api/v1/research`)

### `GET /api/v1/research/gaps`
Lists identified candidate research gaps with scores and related ontological concepts.

### `GET /api/v1/research/knowledge-graph`
Returns nodes and edges formatted for interactive network visualization.

**Parameters:**
- `max_nodes` (int, default: 100)

**Response `200 OK`:**
```json
{
  "nodes": [
    { "id": "Mobile Applications", "label": "Mobile Applications", "type": "technology" },
    { "id": "Diabetes Mellitus, Type 1", "label": "Type 1 Diabetes", "type": "disease" }
  ],
  "edges": [
    { "source": "Mobile Applications", "target": "Diabetes Mellitus, Type 1", "relation": "targets", "source_type": "literature" }
  ]
}
```

### `POST /api/v1/research/retrieve`
Performs dense semantic or ontology-guided passage retrieval.

**Request Body:**
```json
{
  "query": "telehealth adherence in pediatric type 1 diabetes",
  "top_k": 10,
  "use_ontology": true
}
```

---

## 4. Hypothesis Pipeline (`/api/v1/hypotheses`)

### `POST /api/v1/hypotheses/generate`
Spawns an asynchronous background hypothesis generation session.

**Request Body:**
```json
{
  "research_theme": "Mobile health interventions for pediatric type 1 diabetes adherence",
  "target_population": "Adolescents (12-18 years)",
  "objective": "Identify determinants of long-term app engagement",
  "num_hypotheses": 5
}
```

**Response `200 OK`:**
```json
{
  "id": "c39f1c7d-81e0-4a82-a722-114400dd88aa",
  "status": "pending",
  "research_theme": "Mobile health interventions for pediatric type 1 diabetes adherence",
  "hypothesis_count": 0
}
```

### `GET /api/v1/hypotheses/runs/{run_id}`
Retrieves full details for a run, including all generated hypotheses, identified research gaps, and associated evidence passages.

### `GET /api/v1/hypotheses/runs/{run_id}/status`
Lightweight polling endpoint returning current execution state (`collecting` -> `processing` -> `analyzing` -> `complete`).

### `POST /api/v1/hypotheses/runs/{run_id}/hypotheses/{hyp_id}/challenge`
Triggers the Evidence Challenge Engine for an individual hypothesis.

### `POST /api/v1/hypotheses/runs/{run_id}/hypotheses/{hyp_id}/refine`
Reformulates a hypothesis incorporating counter-evidence and qualification criteria.

---

## 5. Evaluation & Export (`/api/v1/evaluation`, `/api/v1/export`)

### `GET /api/v1/evaluation/runs/{run_id}/metrics`
Returns quantitative quality rubric scores and retrieval benchmarks for a run.

### `POST /api/v1/evaluation/baseline`
Runs comparative baselines (Plain LLM vs Standard RAG vs Ontology RAG).

### `GET /api/v1/export/runs/{run_id}/report`
Exports complete auditable research report in structured JSON format.

### `GET /api/v1/export/runs/{run_id}/report/markdown`
Exports formatted scientific Markdown document suitable for peer review.
