# EvidenceGap AI 2026

## Ontology-Guided Hypothesis Generation Using LLMs and RAG

**Academic Title:** Ontology-Guided Hypothesis Generation Using LLMs and Topic Modeling in mHealth Research

An intelligent, evidence-grounded research assistant for mobile health (mHealth) literature that integrates scientific document analysis, topic modeling, biomedical ontologies, retrieval-augmented generation (RAG), and LLM-based hypothesis development.

---

## Project Objective

Help researchers:

1. **Understand** existing mHealth research through automated literature analysis
2. **Identify** potentially underexplored relationships using ontology-guided gap detection
3. **Investigate** what has already been studied via knowledge graph exploration
4. **Discover** supporting and conflicting evidence through semantic retrieval
5. **Generate** structured, testable hypotheses grounded in source passages
6. **Verify** citations and assess evidence quality
7. **Refine** unsupported or redundant hypotheses using evidence challenge
8. **Prioritize** promising research directions through transparent ranking

## Core Research Contribution

**Ontology-Guided RAG with Evidence Challenge and Iterative Hypothesis Refinement**

Unlike standard LLM or RAG-based hypothesis generation, this system additionally:

- Uses topic modeling (BERTopic + LDA) to identify research trends
- Uses biomedical ontologies (MeSH, BioPortal) to normalize and connect concepts
- Detects candidate underexplored concept relationships
- Independently retrieves literature that challenges each hypothesis
- Identifies whether similar research already exists
- Detects unsupported or conflicting claims
- Refines hypotheses using verified evidence
- Produces auditable evidence reports

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Setup

```bash
# 1. Clone and enter the project
cd EvidenceGap_AI_2026

# 2. Create Python virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Download spaCy model
python -m spacy download en_core_web_sm

# 5. Configure environment
# Edit .env with your API keys (see .env.example)

# 6. Install frontend dependencies
cd frontend
npm install
cd ..
```

### Running the Application

```bash
# Terminal 1: Start backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

Access the application at **http://localhost:5173**

### Running the Research Pipeline

Execute notebooks in order from `notebooks/phase1/` through `notebooks/phase3/`.

See [notebooks/README.md](notebooks/README.md) for detailed execution guide.

### Running Tests

```bash
pytest tests/ -v --cov=src --cov=backend
```

---

## Architecture Overview

```
+-----------------------------------------------------+
|                   React Frontend                      |
|  +--------------+  +----------------------------+   |
|  |  Hypothesis   |  |  Research & Validation      |   |
|  |  Generation   |  |  Workspace                  |   |
|  +--------------+  +----------------------------+   |
+---------+------------------------+------------------+
          |       REST API         |
+---------+------------------------+------------------+
|         v       FastAPI          v                    |
|  +------------------------------------------------+  |
|  |  API Layer -> Services -> Background Jobs         |  |
|  +------------------------------------------------+  |
|                       |                               |
|  +--------------------v---------------------------+  |
|  |          Research Pipeline (src/)                |  |
|  |                                                  |  |
|  |  Data Collection -> Preprocessing -> Embeddings    |  |
|  |  -> Topic Modeling -> Ontology Mapping             |  |
|  |  -> Knowledge Graph -> Gap Discovery               |  |
|  |  -> Chunking -> FAISS Retrieval                    |  |
|  |  -> Hypothesis Generation -> Evidence Challenge    |  |
|  |  -> Validation -> Refinement -> Ranking             |  |
|  |  -> Evaluation                                    |  |
|  +--------------------------------------------------+  |
|                       |                               |
|  +--------------------v---------------------------+  |
|  |  SQLite + FAISS Index + File Artifacts           |  |
|  +--------------------------------------------------+  |
+------------------------------------------------------+
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, TypeScript, Vite, Tailwind CSS, Recharts, TanStack Query |
| Backend | FastAPI, Pydantic, SQLAlchemy, SQLite, Uvicorn |
| NLP | spaCy, scispaCy, Sentence-Transformers, BERTopic |
| LLM | Google Gemini API |
| Retrieval | FAISS, Sentence-Transformers |
| Ontology | MeSH, BioPortal API |
| Validation | DeBERTa NLI, rule-based checks |
| Visualization | Recharts, Matplotlib, Plotly, NetworkX |

---

## Project Structure

```
EvidenceGap_AI_2026/
|-- frontend/          # React application
|-- backend/           # FastAPI server
|-- src/               # Research pipeline modules
|-- notebooks/         # Jupyter notebooks (phases 1-3)
|-- data/              # Raw, processed, fulltext data
|-- artifacts/         # Embeddings, FAISS, topics, ontology, graphs
|-- outputs/           # Gaps, hypotheses, validation, evaluation
|-- models/            # Saved model files
|-- tests/             # Test suite
|-- scripts/           # Utility scripts
|-- config/            # Configuration
|-- docs/              # Documentation
|-- requirements.txt   # Python dependencies
|-- .env.example       # Environment template
+-- .gitignore
```

---

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Methodology](docs/METHODOLOGY.md)
- [Evaluation](docs/EVALUATION.md)
- [API Reference](docs/API.md)
- [Notebooks Guide](notebooks/README.md)
- [Model Inventory](models/README.md)

---

## Required API Keys

| Service | Required | Purpose |
|---------|----------|---------|
| Google Gemini | Yes (for hypothesis generation) | LLM-based hypothesis generation and optional evaluation |
| PubMed E-utilities | Recommended | Higher rate limits for data collection |
| BioPortal | Optional | Enhanced ontology concept mapping |

---

## Limitations and Known Issues

1. **Full-text coverage** depends on PMC Open Access availability; most articles will be abstract-only
2. **Hypothesis quality** depends on corpus size and Gemini API access
3. **Ontology mapping** is enhanced with BioPortal API key but functional without it
4. **Evaluation metrics** requiring expert annotations need manual annotation workflow
5. **Large-scale processing** (embeddings, topic modeling) requires adequate compute resources
6. **NLI predictions** are model-based approximations, not definitive scientific judgments

---

## License

Academic research project. See individual dependency licenses.

## Citation

If you use this work, please cite:

```
Ontology-Guided Hypothesis Generation Using LLMs and Topic Modeling in mHealth Research, 2026.
```
