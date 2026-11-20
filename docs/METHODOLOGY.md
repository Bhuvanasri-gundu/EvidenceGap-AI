# EvidenceGap AI 2026 -- Methodology

## Research Methodology

### 1. Problem Statement

Mobile health (mHealth) research is a rapidly expanding field spanning hundreds of disease areas, intervention types, technologies, and populations. Researchers face challenges in:

- Navigating the vast and growing literature
- Identifying truly underexplored research directions
- Generating hypotheses grounded in existing evidence
- Verifying that generated hypotheses are not redundant with prior work
- Assessing the strength of evidence for or against proposed research directions

### 2. Proposed Approach

#### 2.1 Ontology-Guided RAG

Standard RAG retrieves passages based on semantic similarity to a query. Our approach extends this by:

1. **Topic-Informed Retrieval**: Using BERTopic-discovered research themes to contextualize queries
2. **Ontology Expansion**: Expanding queries with MeSH synonyms, related concepts, and hierarchical relationships
3. **Gap-Directed Search**: Focusing retrieval on concept pairs identified as potentially underexplored

This provides structured, domain-informed retrieval rather than purely lexical or semantic matching.

#### 2.2 Evidence Challenge Engine

For every generated hypothesis, the system:

1. **Decomposes** the hypothesis into verifiable scientific claims
2. **Independently searches** for related prior studies using different query formulations
3. **Searches specifically** for contradictory or null findings
4. **Checks** whether the same or similar hypotheses have been previously investigated
5. **Compares** retrieved evidence against generated claims using NLI
6. **Produces** an auditable evidence challenge report

This addresses a known limitation of LLM-generated hypotheses: they may sound plausible but be redundant, contradicted by existing evidence, or based on unsupported assumptions.

#### 2.3 Iterative Refinement

Hypotheses that fail evidence challenge are refined using:

- Identified weaknesses from the challenge report
- Supporting evidence from the literature
- Contradictory evidence that must be acknowledged
- Rule-based quality checks

The refinement preserves both original and revised versions for comparison.

### 3. Pipeline Stages

#### Stage 1: Corpus Construction

- **Source**: PubMed E-utilities with mHealth-related search queries
- **Full text**: PMC Open Access for available articles
- **Identifiers**: PMID, PMCID, DOI reconciliation via NCBI
- **Metadata**: Authors, journal, publication date, MeSH terms, keywords
- **Quality**: Duplicate removal, language filtering, relevance scoring

#### Stage 2: Document Analysis

- **Embeddings**: SPECTER2 for document-level, all-MiniLM-L6-v2 for passage-level
- **Topic Modeling**: BERTopic (primary) with LDA (baseline)
- **Temporal Analysis**: Topic trends over publication years
- **Coherence**: c_v coherence score for topic quality

#### Stage 3: Ontology Integration

- **MeSH**: Extract and normalize existing PubMed MeSH terms
- **BioPortal**: Additional concept lookup (when API key available)
- **Entity Extraction**: scispaCy NER or rule-based for diseases, interventions, technologies, populations, outcomes
- **Concept Normalization**: Unified concept vocabulary with provenance

#### Stage 4: Knowledge Graph

- **Nodes**: Papers, Topics, Concepts (typed: Disease, Intervention, Technology, Population, Outcome)
- **Edges**: Literature-derived associations and ontology-defined relationships (clearly distinguished)
- **Analysis**: Connectivity, clustering, centrality

#### Stage 5: Gap Discovery

- **Methods**: Low concept co-occurrence + high ontological relatedness, temporal decline, sparse coverage
- **Ranking**: Composite score from multiple signals
- **Transparency**: Each gap has an explanation of contributing factors
- **Caveat**: Low publication count != confirmed gap

#### Stage 6: Semantic Chunking and Retrieval

- **Chunking**: Section-aware, sentence-boundary-respecting, ~300-500 tokens
- **Indexing**: FAISS IVFFlat for efficient similarity search
- **Retrieval**: Semantic search with source diversity reranking
- **Ontology Enhancement**: Query expansion with MeSH terms and ontology relationships

#### Stage 7: Hypothesis Generation

- **LLM**: Google Gemini with structured output
- **Input**: Research gaps, retrieved evidence, ontology context
- **Output**: Structured hypotheses with citations, mechanisms, assumptions
- **Modes**: Plain LLM, standard RAG, ontology-guided RAG (for comparison)

#### Stage 8: Evidence Challenge

- **Claim Decomposition**: Break hypotheses into verifiable statements
- **Independent Search**: New queries per claim, not reusing generation context
- **Contradiction Search**: Explicitly seek opposing evidence
- **Prior Art Check**: Semantic similarity to existing research questions
- **NLI Evaluation**: Entailment/contradiction scoring

#### Stage 9: Validation

- **Citation Verification**: Identifier exists, passage belongs to source, claim supported
- **NLI**: DeBERTa-based entailment classification
- **Rule Checks**: Testability, variable clarity, falsifiability, etc.
- **Novelty**: Comparison against corpus research questions

#### Stage 10: Refinement and Ranking

- **Refinement**: Address issues identified by evidence challenge
- **Ranking**: Composite score from validation, evidence quality, novelty
- **Deduplication**: Semantic similarity clustering
- **Transparency**: All scores and criteria exposed

### 4. Evaluation Framework

See [EVALUATION.md](EVALUATION.md) for the complete evaluation methodology.

### 5. Limitations

1. Corpus limited to PubMed-indexed articles; may miss non-indexed research
2. Full-text availability depends on PMC Open Access; most articles abstract-only
3. Topic modeling quality depends on corpus size and diversity
4. Ontology mapping limited to MeSH and optionally BioPortal
5. Hypothesis generation quality depends on LLM capabilities
6. NLI predictions are approximations, not definitive scientific judgments
7. Gap detection identifies candidates, not confirmed knowledge gaps
8. Evaluation without expert annotations is limited to automated metrics
9. This is a proposed methodology; claims of superiority require empirical validation
