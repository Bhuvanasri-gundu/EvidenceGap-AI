"""Generates all 24 mandatory Jupyter Notebooks for Phases 1, 2, and 3.

Each notebook uses real project modules, imports from src.*, includes scientific objectives,
reproducible configurations, and executable analysis cells.
"""

import json
from pathlib import Path

NOTEBOOKS_DIR = Path(__file__).resolve().parent.parent / "notebooks"


def make_notebook(title: str, objective: str, code_cells: list[str]) -> dict:
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                f"# {title}\n\n",
                f"**EvidenceGap AI 2026 — Scientific Research Notebook**\n\n",
                f"### Scientific Objective\n{objective}\n\n",
                "### Reproducibility & Environment Setup\n",
                "Ensure project root is in Python path and dependencies are active.\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": 1,
            "metadata": {},
            "outputs": [],
            "source": [
                "import os\n",
                "import sys\n",
                "from pathlib import Path\n\n",
                "# Add project root to sys.path\n",
                "PROJECT_ROOT = Path('.').resolve().parent.parent if 'phase' in str(Path('.').resolve()) else Path('.').resolve()\n",
                "if str(PROJECT_ROOT) not in sys.path:\n",
                "    sys.path.insert(0, str(PROJECT_ROOT))\n\n",
                "print(f'Active working directory: {PROJECT_ROOT}')\n",
            ],
        },
    ]

    for i, code in enumerate(code_cells, start=2):
        cells.append({
            "cell_type": "code",
            "execution_count": i,
            "metadata": {},
            "outputs": [],
            "source": [line + "\n" for line in code.strip().split("\n")],
        })

    return {
        "cells": cells,
        "metadata": {
            "language_info": {"name": "python", "version": "3.11"},
            "kernelspec": {"name": "python3", "display_name": "Python 3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def write_nb(path: Path, title: str, objective: str, code_cells: list[str]):
    data = make_notebook(title, objective, code_cells)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Generated: {path.name}")


def generate_all():
    # ─── PHASE 1 NOTEBOOKS ──────────────────────────────────────────
    p1 = NOTEBOOKS_DIR / "phase1"

    write_nb(
        p1 / "01_dataset_ingestion_and_audit.ipynb",
        "Dataset Ingestion and Comprehensive Data Audit",
        "Inspect the raw mHealth corpus, record counts, metadata fields, missing value distributions, and publication year coverage.",
        [
            "from src.data_collection.pubmed_collector import collector\nfrom src.preprocessing.text_processor import text_processor\nimport json",
            "corpus_file = collector.output_dir / 'mhealth_corpus.json'\nwith open(corpus_file, 'r', encoding='utf-8') as f:\n    data = json.load(f)\nprint(f'Total records in raw corpus: {len(data)}')",
            "report = text_processor.generate_quality_report(data)\nprint('Data Quality Audit:')\nfor k, v in report.items():\n    print(f'  {k}: {v}')",
        ],
    )

    write_nb(
        p1 / "02_pubmed_pmc_fulltext_collection.ipynb",
        "PubMed Metadata and PMC Open Access Full-Text Retrieval",
        "Retrieve open-access full-text XML for articles with PMCIDs, parse scientific sections (Introduction, Methods, Results, Discussion), and track source type provenance.",
        [
            "from src.data_collection.pmc_fulltext import fulltext_retriever\nfrom src.data_collection.pubmed_collector import collector\nimport json",
            "with open(collector.output_dir / 'mhealth_corpus.json', 'r', encoding='utf-8') as f:\n    corpus = json.load(f)\npmc_articles = [r for r in corpus if r.get('pmcid')]\nprint(f'Articles with PMC identifiers: {len(pmc_articles)}')",
            "sample_pmcid = pmc_articles[0]['pmcid'] if pmc_articles else 'PMC6751234'\nprint(f'Demonstrating full-text parsing for: {sample_pmcid}')\ndoc = fulltext_retriever.fetch_fulltext(sample_pmcid)\nif doc:\n    print(f'Title: {doc.get(\"title\")}')\n    print(f'Parsed sections: {len(doc.get(\"sections\", []))}')",
        ],
    )

    write_nb(
        p1 / "03_preprocessing_and_deduplication.ipynb",
        "Corpus Preprocessing, Unicode Normalization, and Deduplication",
        "Clean scientific text, normalize character encodings, segment sentences, and identify duplicate records using composite PMID/DOI/Title matching.",
        [
            "from src.preprocessing.text_processor import text_processor\nfrom src.data_collection.pubmed_collector import collector\nimport json",
            "with open(collector.output_dir / 'mhealth_corpus.json', 'r', encoding='utf-8') as f:\n    raw = json.load(f)",
            "unique, duplicates = text_processor.detect_duplicates(raw)\nprint(f'Total unique records: {len(unique)}')\nprint(f'Duplicates identified: {len(duplicates)}')",
        ],
    )

    write_nb(
        p1 / "04_relevance_filtering.ipynb",
        "Domain Relevance Filtering for Mobile Health Literature",
        "Evaluate document relevance using keyword heuristics and concept density scoring to isolate genuine mHealth research from unrelated biomedical articles.",
        [
            "from src.preprocessing.relevance_filter import relevance_filter\nfrom config.settings import PROCESSED_DIR\nimport json",
            "with open(PROCESSED_DIR / 'cleaned_corpus.json', 'r', encoding='utf-8') as f:\n    corpus = json.load(f)\nrelevant, excluded = relevance_filter.filter_corpus(corpus)\nprint(f'Retained mHealth articles: {len(relevant)}')\nprint(f'Excluded articles: {len(excluded)}')",
        ],
    )

    write_nb(
        p1 / "05_scientific_document_embeddings.ipynb",
        "Scientific Document Embedding Generation and Validation",
        "Compute dense vector representations of document titles and abstracts using Sentence-Transformers with dimensionality and normalization checks.",
        [
            "from src.embeddings.document_embedder import embedder\nfrom config.settings import PROCESSED_DIR\nimport json",
            "with open(PROCESSED_DIR / 'cleaned_corpus.json', 'r', encoding='utf-8') as f:\n    corpus = json.load(f)\nembeddings, pmids = embedder.embed_documents(corpus[:50])\nprint(f'Embeddings shape: {embeddings.shape}')\nprint(f'Sample L2 norm: {(embeddings[0]**2).sum():.4f}')",
        ],
    )

    write_nb(
        p1 / "06_bertopic_topic_modeling.ipynb",
        "BERTopic Research Theme Discovery and Temporal Trajectories",
        "Discover latent clinical and technical research clusters in mHealth using BERTopic with c-TF-IDF keyword extraction and temporal trend analysis.",
        [
            "from src.topic_modeling.bertopic_modeler import modeler\nfrom config.settings import PROCESSED_DIR\nimport json",
            "with open(PROCESSED_DIR / 'cleaned_corpus.json', 'r', encoding='utf-8') as f:\n    corpus = json.load(f)\nabstracts = [r['abstract'] for r in corpus if r.get('abstract')]\ntopics = modeler.fit_transform(abstracts)\nprint(f'Discovered {len(topics)} topic clusters.')\nfor t in topics[:5]:\n    print(f'Topic {t[\"topic_id\"]}: {t[\"keywords\"][:5]} (Docs: {t[\"document_count\"]})')",
        ],
    )

    write_nb(
        p1 / "07_lda_baseline_and_topic_evaluation.ipynb",
        "Latent Dirichlet Allocation (LDA) Baseline & Topic Diversity Evaluation",
        "Train an LDA probabilistic topic model as a statistical baseline and calculate topic diversity metrics to compare against BERTopic.",
        [
            "from src.topic_modeling.lda_baseline import lda_baseline\nfrom config.settings import PROCESSED_DIR\nimport json",
            "with open(PROCESSED_DIR / 'cleaned_corpus.json', 'r', encoding='utf-8') as f:\n    corpus = json.load(f)\nabstracts = [r['abstract'] for r in corpus if r.get('abstract')]\ntopics = lda_baseline.fit(abstracts)\ndiversity = lda_baseline.evaluate_diversity()\nprint(f'LDA Topic Diversity Score: {diversity}')",
        ],
    )

    write_nb(
        p1 / "08_mesh_bioportal_mapping.ipynb",
        "MeSH and BioPortal Biomedical Concept Mapping",
        "Extract, normalize, and navigate biomedical hierarchies using Medical Subject Headings (MeSH) and BioPortal synonym dictionaries.",
        [
            "from src.ontology.mesh_mapper import mesh_mapper\nfrom src.ontology.concept_normalizer import concept_normalizer",
            "term = 'Diabetes Mellitus, Type 1'\nrelated = mesh_mapper.get_related_concepts(term)\nprint(f'Concept: {term}')\nprint(f'  Synonyms: {related[\"synonyms\"]}')\nprint(f'  Narrower: {related[\"narrower\"]}')",
            "norm = concept_normalizer.normalize('smartphone health application')\nprint('Canonical normalizer output:', norm)",
        ],
    )

    write_nb(
        p1 / "09_knowledge_graph_construction.ipynb",
        "Multi-Relational Biomedical Knowledge Graph Construction",
        "Construct a NetworkX multi-relational graph linking publications, research topics, diseases, and technologies, differentiating ontology-defined edges from literature co-occurrence edges.",
        [
            "from src.knowledge_graph.graph_builder import builder as kg_builder\nfrom config.settings import PROCESSED_DIR\nimport json",
            "with open(PROCESSED_DIR / 'cleaned_corpus.json', 'r', encoding='utf-8') as f:\n    corpus = json.load(f)\ngraph = kg_builder.build_from_corpus(corpus)\nprint(f'Graph Nodes: {graph.number_of_nodes()}, Graph Edges: {graph.number_of_edges()}')\nviz_data = kg_builder.get_visualization_data(max_nodes=10)\nprint('Sample Viz Nodes:', [n['id'] for n in viz_data['nodes'][:5]])",
        ],
    )

    write_nb(
        p1 / "10_temporal_research_gap_discovery.ipynb",
        "Temporal and Co-Occurrence Research Gap Discovery",
        "Identify candidate underexplored concept relationships by intersecting topic trends with concept pair co-occurrence frequencies.",
        [
            "from src.gap_discovery.gap_detector import discoverer\nfrom config.settings import PROCESSED_DIR\nimport json",
            "with open(PROCESSED_DIR / 'cleaned_corpus.json', 'r', encoding='utf-8') as f:\n    corpus = json.load(f)\ngaps = discoverer.detect_gaps(corpus, query='mHealth chronic disease')\nprint(f'Discovered {len(gaps)} candidate research gaps:')\nfor g in gaps[:3]:\n    print(f'Gap Score: {g[\"score\"]} | {g[\"description\"]}')",
        ],
    )

    # ─── PHASE 2 NOTEBOOKS ──────────────────────────────────────────
    p2 = NOTEBOOKS_DIR / "phase2"

    write_nb(
        p2 / "11_fulltext_semantic_chunking.ipynb",
        "Section-Aware Semantic Chunking with Provenance Tracking",
        "Chunk full-text articles and abstracts respecting section boundaries and sentence integrity while preserving academic provenance (PMID, section, DOI).",
        [
            "from src.chunking.semantic_chunker import chunker\nfrom config.settings import PROCESSED_DIR\nimport json",
            "with open(PROCESSED_DIR / 'cleaned_corpus.json', 'r', encoding='utf-8') as f:\n    corpus = json.load(f)\nchunks = chunker.chunk_corpus(corpus[:10])\nprint(f'Generated {len(chunks)} semantic passages from 10 sample articles.')\nprint('Sample chunk provenance:', {k: chunks[0][k] for k in ['chunk_id', 'pmid', 'section_name']})",
        ],
    )

    write_nb(
        p2 / "12_passage_embeddings_and_faiss.ipynb",
        "Dense Passage Embeddings and Persistent FAISS Vector Index",
        "Embed semantic passages and construct a persistent FAISS vector index with Cosine Inner Product similarity and diversity reranking.",
        [
            "from src.retrieval.faiss_index import vector_index\nfrom config.settings import PROCESSED_DIR\nimport json",
            "with open(PROCESSED_DIR / 'corpus_chunks.json', 'r', encoding='utf-8') as f:\n    chunks = json.load(f)\nvector_index.build_index(chunks[:50])\nhits = vector_index.search('continuous glucose monitoring adherence', top_k=3)\nprint(f'Retrieved {len(hits)} matching passages.')\nfor h in hits:\n    print(f'PMID: {h[\"pmid\"]} (Score: {h[\"score\"]}) -> {h[\"text\"][:80]}...')",
        ],
    )

    write_nb(
        p2 / "13_ontology_guided_retrieval.ipynb",
        "Ontology-Guided RAG Retrieval vs Vanilla Semantic Search",
        "Evaluate retrieval query expansion using MeSH hierarchical concepts and quantify the expansion's impact on candidate passage relevance.",
        [
            "from src.retrieval.ontology_guided_retrieval import retriever",
            "query = 'smartphone diabetes adherence'\nvanilla_results = retriever.retrieve(query, top_k=5, use_ontology=False)\nontology_results = retriever.retrieve(query, top_k=5, use_ontology=True)\nprint(f'Vanilla results count: {len(vanilla_results)}')\nprint(f'Ontology-guided results count: {len(ontology_results)}')\nif ontology_results:\n    print('Matched ontology terms:', ontology_results[0].get('matched_ontology_terms'))",
        ],
    )

    write_nb(
        p2 / "14_llm_rag_hypothesis_generation.ipynb",
        "Evidence-Grounded Hypothesis Generation with LLMs",
        "Synthesize structured, testable hypotheses grounded in retrieved literature passages using Google Gemini or deterministic domain templates.",
        [
            "from src.hypothesis_generation.generator import generator",
            "theme = 'Mobile health gamification for adolescent type 1 diabetes adherence'\nhypotheses = generator.generate(research_theme=theme, num_hypotheses=3, mode='ontology_rag')\nprint(f'Generated {len(hypotheses)} hypotheses:')\nfor i, h in enumerate(hypotheses, 1):\n    print(f'H{i}: {h[\"statement\"]}')\n    print(f'   Citations: {h.get(\"citations\")}')",
        ],
    )

    write_nb(
        p2 / "15_evidence_challenge_and_contradiction.ipynb",
        "Adversarial Evidence Challenge & Contradiction Discovery",
        "Decompose hypotheses into verifiable claims, formulate independent counter-queries, and search the corpus for conflicting, null, or opposing evidence.",
        [
            "from src.evidence_challenge.challenger import challenger",
            "statement = 'Automated continuous glucose monitoring smartphone feedback will produce a statistically significant reduction in glycemic emergencies.'\nchallenge_report = challenger.challenge('hyp_demo', statement)\nprint('Challenge Summary:', challenge_report['summary'])\nprint(f'Supporting Passages: {len(challenge_report[\"supporting_passages\"])}')\nprint(f'Contradictory / Opposing Passages: {len(challenge_report[\"contradictory_passages\"])}')",
        ],
    )

    write_nb(
        p2 / "16_citation_and_nli_validation.ipynb",
        "Citation Verification and Natural Language Inference (NLI)",
        "Confirm cited PMIDs exist in the corpus and evaluate claim-evidence entailment using Cross-Encoder / DeBERTa NLI predictions.",
        [
            "from src.validation.citation_verifier import citation_verifier\nfrom src.validation.nli_validator import nli_validator",
            "premise = 'Patients using mobile continuous monitoring showed statistically significant HbA1c reductions.'\nclaim = 'Mobile health applications improve glycemic adherence.'\nnli_res = nli_validator.predict(premise, claim)\nprint(f'NLI Relationship: {nli_res[\"label\"]} (Confidence: {nli_res[\"score\"]})')",
            "cite_check = citation_verifier.verify_citations(['31548842'], claim)\nprint('Citation Verification:', cite_check['verified'])",
        ],
    )

    write_nb(
        p2 / "17_novelty_assessment_and_rule_checks.ipynb",
        "Novelty Assessment and Rule-Based Scientific Rigor Checks",
        "Assess hypothesis novelty against existing literature research questions and execute deterministic scientific quality checks for falsifiability.",
        [
            "from src.validation.novelty_assessor import novelty_assessor\nfrom src.validation.rule_checker import rule_checker",
            "hyp = 'In rural adolescents with type 1 diabetes, cellular CGM telemonitoring will reduce 90-day readmissions compared to asynchronous SMS.'\nnov = novelty_assessor.assess_novelty(hyp)\nprint('Novelty Score:', nov['novelty_score'])\nprint('Assessment:', nov['assessment'])",
            "rules = rule_checker.check(hyp)\nfor r in rules:\n    print(f'Rule: {r[\"name\"]} -> Passed: {r[\"passed\"]}')",
        ],
    )

    write_nb(
        p2 / "18_hypothesis_refinement.ipynb",
        "Iterative Hypothesis Refinement from Challenge Evidence",
        "Refine hypotheses by incorporating qualification criteria and boundary conditions derived from the adversarial evidence challenge report.",
        [
            "from src.refinement.hypothesis_refiner import refiner",
            "orig = 'Mobile phone alerts will eliminate emergency room visits for all diabetic patients.'\nrefined = refiner.refine(orig, {'counter_evidence_count': 2})\nprint('Original Formulation:\\n ', refined['original_statement'])\nprint('Refined Formulation:\\n ', refined['refined_statement'])\nprint('Changes applied:', refined['changes_made'])",
        ],
    )

    write_nb(
        p2 / "19_ranking_and_semantic_deduplication.ipynb",
        "Transparent Multi-Factor Ranking & Semantic Deduplication",
        "Rank candidate hypotheses using an open multi-factor scoring formula and cluster redundant formulations using embedding cosine similarity.",
        [
            "from src.ranking.hypothesis_ranker import ranker",
            "candidates = [\n    'Mobile health CGM applications improve HbA1c adherence in adolescent diabetes.',\n    'Smartphone continuous glucose monitors enhance glycemic control in youth with T1D.',\n    'Automated cellular blood pressure cuffs reduce hypertension in rural older adults.',\n]\nkept = ranker.deduplicate(candidates)\nprint(f'Retained indices after deduplication: {kept}')\nscores = ranker.rank([candidates[i] for i in kept])\nfor i, s in zip(kept, scores):\n    print(f'Score: {s} -> {candidates[i]}')",
        ],
    )

    # ─── PHASE 3 NOTEBOOKS ──────────────────────────────────────────
    p3 = NOTEBOOKS_DIR / "phase3"

    write_nb(
        p3 / "20_retrieval_evaluation.ipynb",
        "Retrieval Benchmarking: Precision@k, Recall@k, MRR, and nDCG",
        "Evaluate retrieval precision, recall, and nDCG across varying query top-k settings comparing dense retrieval with ontology query expansion.",
        [
            "from src.evaluation.retrieval_metrics import retrieval_evaluator",
            "retrieved = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']\nrelevant = {'doc2', 'doc4', 'doc8'}\np5 = retrieval_evaluator.precision_at_k(retrieved, relevant, k=5)\nr5 = retrieval_evaluator.recall_at_k(retrieved, relevant, k=5)\nprint(f'Precision@5: {p5}')\nprint(f'Recall@5: {r5}')",
        ],
    )

    write_nb(
        p3 / "21_hypothesis_quality_evaluation.ipynb",
        "Scientific Rubric Quality Scoring Across Generated Hypotheses",
        "Quantify multi-dimensional quality metrics across collections of generated hypotheses, including testability, clarity, plausibility, and evidence grounding.",
        [
            "from src.evaluation.hypothesis_metrics import hypothesis_evaluator",
            "sample_hyps = [\n    {'statement': 'Cellular BP cuffs reduce systolic pressure by 8 mm Hg compared to usual care in rural hypertension.', 'mechanism': 'Direct telemetric feedback', 'citations': ['32678912']},\n    {'statement': 'Apps will help people feel better.', 'mechanism': None, 'citations': []}\n]\nscores = hypothesis_evaluator.evaluate_collection(sample_hyps)\nprint('Hypothesis Collection Rubric Evaluation:')\nfor k, v in scores.items():\n    print(f'  {k}: {v}')",
        ],
    )

    write_nb(
        p3 / "22_baseline_comparison.ipynb",
        "Comparative Baseline Benchmark Across 4 Methodological Systems",
        "Execute an identical clinical research prompt across Plain LLM, Standard RAG, Ontology RAG, and the Full Evidence Challenge Pipeline.",
        [
            "from src.evaluation.baseline_runner import baseline_runner",
            "theme = 'Wearable sensor tracking of physical activity in heart failure remote monitoring'\nresults = baseline_runner.run_benchmark(theme, num_hypotheses=2)\nprint('Benchmark Results Summary:')\nfor baseline, data in results['baselines'].items():\n    print(f'System: {baseline}')\n    print('  Rubric scores:', data['scores'])",
        ],
    )

    write_nb(
        p3 / "23_ablation_studies.ipynb",
        "Architectural Component Ablation Experiments",
        "Quantify the individual performance contribution of ontology expansion, adversarial evidence challenge, and iterative refinement.",
        [
            "from src.evaluation.evaluator import evaluator",
            "ablation = evaluator.ablation_study('run_eval_demo')\nprint('Ablation Study Results:')\nfor comp, metrics in ablation['components'].items():\n    print(f'Component [{comp}]:', metrics)",
        ],
    )

    write_nb(
        p3 / "24_end_to_end_research_case_study.ipynb",
        "End-to-End Scientific Research Case Study",
        "Demonstrate the full workflow: literature ingestion -> gap discovery -> ontology retrieval -> hypothesis synthesis -> evidence challenge -> refinement -> ranking.",
        [
            "from src.data_collection.pubmed_collector import collector\nfrom src.gap_discovery.gap_detector import discoverer\nfrom src.hypothesis_generation.generator import generator\nfrom src.evidence_challenge.challenger import challenger\nfrom src.refinement.hypothesis_refiner import refiner\nfrom src.ranking.hypothesis_ranker import ranker",
            "theme = 'Mobile health interventions for improving adherence in type 1 diabetes'\nprint(f'=== Case Study: {theme} ===')",
            "gaps = discoverer.discover(theme)\nprint(f'Step 1: Top gap identified: {gaps[0][\"description\"][:80]}...')",
            "hyps = generator.generate(theme, num_hypotheses=1, mode='ontology_rag')\norig_statement = hyps[0]['statement']\nprint(f'Step 2: Generated Hypothesis:\\n  {orig_statement}')",
            "challenge = challenger.challenge('case_study_1', orig_statement)\nprint(f'Step 3: Evidence Challenge counter-evidence count: {challenge[\"counter_evidence_count\"]}')",
            "refined = refiner.refine(orig_statement, challenge)\nprint(f'Step 4: Refined Hypothesis Formulation:\\n  {refined[\"refined_statement\"]}')",
            "rank = ranker.score_hypothesis(evidence_score=0.9, novelty_score=0.85, testability_score=0.95)\nprint(f'Step 5: Final Composite Ranking Score: {rank}')",
        ],
    )


if __name__ == "__main__":
    generate_all()
