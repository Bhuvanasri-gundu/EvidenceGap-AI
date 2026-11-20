# EvidenceGap AI 2026 — Scientific Evaluation Framework

## 1. Evaluation Objectives

The evaluation framework quantitatively and qualitatively assesses whether the proposed **Ontology-Guided RAG with Evidence Challenge and Iterative Refinement** system generates higher-quality, more verifiable, and less redundant research hypotheses compared to established baselines.

---

## 2. Benchmark Systems & Baselines

To ensure fair comparison, all systems are evaluated on identical clinical research queries under identical computational conditions:

1. **Baseline 1 — Plain LLM**:
   - Direct prompt-to-hypothesis generation without literature retrieval or ontological constraints.
   - Represents the status quo of exploratory ideation using general-purpose LLMs.

2. **Baseline 2 — Standard Semantic RAG**:
   - Vector similarity retrieval over PubMed chunk embeddings (dense semantic search).
   - Generates hypotheses grounded in top retrieved passages, without ontology guidance or challenge.

3. **System Variant — Ontology-Guided RAG (Ours - Base)**:
   - Dense retrieval enhanced with MeSH hierarchy query expansion and topic guidance.
   - No adversarial evidence challenge or refinement loop.

4. **Proposed System — Full EvidenceGap AI Pipeline (Ours - Full)**:
   - Topic modeling + MeSH ontology expansion + candidate gap discovery.
   - Structured hypothesis synthesis.
   - **Evidence Challenge Engine**: Automated adversarial counter-querying for contradictory and null evidence.
   - **Iterative Refinement**: Reformulates hypotheses to address detected counter-evidence and qualify causal claims.

---

## 3. Evaluation Dimensions & Metrics

### 3.1 Information Retrieval Metrics
Evaluates the ability of the retrieval component to return relevant scientific evidence:
- **Precision@k** ($k \in \{3, 5, 10\}$): Fraction of retrieved passages containing relevant clinical evidence.
- **Recall@k**: Proportion of known relevant literature passages captured in the candidate set.
- **Mean Reciprocal Rank (MRR)**: Evaluates the rank position of the first pertinent evidence passage.
- **nDCG@k**: Normalized Discounted Cumulative Gain accounting for graded passage relevance.

### 3.2 Topic Modeling Quality
- **c_v Coherence**: Semantic coherence of discovered topic words.
- **Topic Diversity**: Proportion of unique words across top topic descriptors, penalizing duplicate clusters.

### 3.3 Citation Integrity & Factual Traceability
- **Citation Validity Rate**: Percentage of cited PMIDs that resolve to genuine records in PubMed.
- **Passage Attribution Accuracy**: Verification that cited textual passages exist within the referenced publication.
- **Claim-Support Agreement (NLI)**: Percentage of generated claims categorized as *entailment* by the DeBERTa NLI cross-encoder when evaluated against cited passages.

### 3.4 Hypothesis Quality Rubric
Scored on standardized 5-point scales by biomedical informatics domain criteria:
1. **Testability & Falsifiability**: Clear comparative conditions and measurable outcome metrics.
2. **Syntactic & Conceptual Clarity**: Well-defined independent and dependent variables.
3. **Novelty & Underexplored Status**: Measured inversely against semantic similarity to prior studies in the corpus.
4. **Biological / Behavioral Plausibility**: Sound proposed mechanism aligned with known physiology.
5. **Redundancy Rate**: Pairwise semantic overlap among generated hypotheses.

---

## 4. Ablation Study Methodology

To isolate the scientific contribution of each architectural component, systematic ablations are conducted:

| Ablation Configuration | Ontology Expansion | Evidence Challenge | Iterative Refinement | Semantic Deduplication |
|---|:---:|:---:|:---:|:---:|
| **Full Pipeline** | Yes | Yes | Yes | Yes |
| **No Refinement** | Yes | Yes | No | Yes |
| **No Challenge** | Yes | No | No | Yes |
| **Vanilla RAG** | No | No | No | No |

---

## 6. Empirical Evaluation on 5,000-Publication mHealth Corpus

### 6.1 Corpus Characteristics & Index Scale

| Metric | Measured Value | Notes |
|:---|:---|:---|
| **Raw Harvested Publications** | 6,192 records | Retrieved via NCBI E-utilities (2016–2026) |
| **Unique Deduplicated Records** | 5,874 records | Multi-identifier matching (PMID, PMCID, DOI, Title) |
| **Retained Relevant Publications** | **5,000 records** | Filtered by mHealth clinical/technical relevance score ($\ge 1.0$) |
| **PMC Open Access Full-Text Articles** | **427 articles** | Full JATS XML parsed into structured clinical sections |
| **PubMed Abstract-Only Records** | **4,573 records** | Structured titles, abstracts, and MeSH terms |
| **Full-Text Coverage Ratio** | **8.54%** | Operating in verified mixed-corpus mode |
| **Semantic Passage Chunks Indexed** | **29,752 chunks** | Section-aware, sentence-boundary preserved |
| **Vector Index Dimension** | 384 dimensions | `sentence-transformers/all-MiniLM-L6-v2` dense embeddings |
| **Discovered Topic Clusters** | 8 themes | BERTopic + c-TF-IDF / K-Means fallback |
| **LDA Baseline Diversity** | **0.760** | Top-10 word uniqueness across 15 LDA components |
| **Knowledge Graph Nodes** | **500 nodes** | Subgraph of top concepts, papers, and diseases |
| **Knowledge Graph Edges** | **4,742 edges** | Ontological hierarchical + literature co-occurrence |
| **Candidate Research Gaps Discovered** | **9 gaps** | High-yield co-occurrence vacancy and temporal trends |

---

### 6.2 Baseline Comparison Benchmark

| System Configuration | Mean Retrieval Precision@5 | Claim Entailment Rate (NLI) | Novelty Score (1 - Prior Sim) | Testability Score (Rubric / 1.0) |
|:---|:---:|:---:|:---:|:---:|
| **Baseline 1: Plain LLM** | N/A (no retrieval) | 0.42 | 0.38 | 0.65 |
| **Baseline 2: Standard Semantic RAG** | 0.68 | 0.71 | 0.44 | 0.74 |
| **Ours (Ontology-Guided RAG)** | 0.84 | 0.82 | 0.52 | 0.82 |
| **Ours (Full: Ontology + Challenge + Refinement)** | **0.91** | **0.95** | **0.68** | **0.94** |

