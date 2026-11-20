# EvidenceGap AI 2026 -- Scientific Research Notebooks

This directory contains the 24 reproducible Jupyter Notebooks structured across three research phases. Each notebook imports production modules from `src/` and conducts transparent data analysis.

---

## Execution Guide & Notebook Inventory

### Phase 1 -- Scientific Literature Analysis & Gap Discovery
Located in `notebooks/phase1/`

| # | Notebook File | Objective | Key Inputs | Outputs / Artifacts |
|---|---|---|---|---|
| **01** | `01_dataset_ingestion_and_audit.ipynb` | Ingestion & audit of raw mHealth corpus | `data/raw/mhealth_corpus.json` | Data quality metrics, field coverage |
| **02** | `02_pubmed_pmc_fulltext_collection.ipynb` | Full-text XML collection via PMC Open Access | PMCIDs from corpus | `data/fulltext/`, section segmentation |
| **03** | `03_preprocessing_and_deduplication.ipynb` | Text normalization & composite deduplication | Raw documents | `data/processed/cleaned_corpus.json` |
| **04** | `04_relevance_filtering.ipynb` | mHealth domain relevance filtering | Cleaned corpus | Retained vs excluded distributions |
| **05** | `05_scientific_document_embeddings.ipynb` | SPECTER2 / MiniLM document vectorization | Document abstracts | `artifacts/embeddings/doc_embeddings.npy` |
| **06** | `06_bertopic_topic_modeling.ipynb` | BERTopic theme discovery & trajectories | Document embeddings | `artifacts/topics/topic_summary.json` |
| **07** | `07_lda_baseline_and_topic_evaluation.ipynb` | LDA probabilistic baseline & topic diversity | Corpus texts | Topic diversity score, word distributions |
| **08** | `08_mesh_bioportal_mapping.ipynb` | MeSH hierarchy & BioPortal concept lookup | Extracted terms | Normalized concepts, synonym dictionaries |
| **09** | `09_knowledge_graph_construction.ipynb` | Multi-relational NetworkX graph building | Papers & concepts | `artifacts/graphs/knowledge_graph.json` |
| **10** | `10_temporal_research_gap_discovery.ipynb` | Co-occurrence & temporal gap detection | Topics & MeSH pairs | `outputs/gaps/candidate_gaps.json` |

---

### Phase 2 -- RAG and Hypothesis Development
Located in `notebooks/phase2/`

| # | Notebook File | Objective | Key Inputs | Outputs / Artifacts |
|---|---|---|---|---|
| **11** | `11_fulltext_semantic_chunking.ipynb` | Section-aware semantic chunking | Full-text articles | `data/processed/corpus_chunks.json` |
| **12** | `12_passage_embeddings_and_faiss.ipynb` | FAISS vector index construction | Semantic chunks | `artifacts/faiss/passage_index.index` |
| **13** | `13_ontology_guided_retrieval.ipynb` | MeSH query expansion vs vanilla search | Search queries | Comparative passage retrieval logs |
| **14** | `14_llm_rag_hypothesis_generation.ipynb` | Gemini structured hypothesis synthesis | Candidate gaps + passages | Validated hypothesis JSON objects |
| **15** | `15_evidence_challenge_and_contradiction.ipynb` | Adversarial evidence challenge engine | Hypotheses | Counter-evidence reports |
| **16** | `16_citation_and_nli_validation.ipynb` | Citation resolution & DeBERTa NLI scoring | Claims + citations | Entailment / contradiction scores |
| **17** | `17_novelty_assessment_and_rule_checks.ipynb` | Novelty estimation & falsifiability rules | Hypotheses | Novelty scores, rule compliance |
| **18** | `18_hypothesis_refinement.ipynb` | Evidence-grounded iterative refinement | Hypotheses + challenge | Refined, qualified formulations |
| **19** | `19_ranking_and_semantic_deduplication.ipynb` | Multi-factor ranking & cosine dedup | Refined hypotheses | Leaderboard rankings, dedup clusters |

---

### Phase 3 -- Evaluation
Located in `notebooks/phase3/`

| # | Notebook File | Objective | Key Inputs | Outputs / Artifacts |
|---|---|---|---|---|
| **20** | `20_retrieval_evaluation.ipynb` | Precision@k, Recall@k, MRR, nDCG | Retrieval runs | Quantitative IR benchmark tables |
| **21** | `21_hypothesis_quality_evaluation.ipynb` | Rubric evaluation (testability, clarity) | Hypothesis batches | Multi-dimensional quality metrics |
| **22** | `22_baseline_comparison.ipynb` | 4-system comparative benchmark | Common queries | Plain LLM vs Std RAG vs Ours comparison |
| **23** | `23_ablation_studies.ipynb` | Component ablations (ontology, challenge) | Pipeline flags | Component contribution deltas |
| **24** | `24_end_to_end_research_case_study.ipynb` | Complete end-to-end clinical case study | Real mHealth topic | Full auditable scientific research report |

---

## How to Execute the Notebooks

Launch Jupyter from the project root:

```bash
jupyter lab
```

Navigate to `notebooks/phase1/01_dataset_ingestion_and_audit.ipynb` and execute sequentially.
All notebooks use relative path resolution to automatically locate the project root and Python source modules.
