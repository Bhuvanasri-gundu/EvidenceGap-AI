// --- EvidenceGap AI 2026 -- Comprehensive TypeScript Types ----------------

// --- Run & Pipeline ------------------------------------------------

export type RunStatus = 'pending' | 'collecting' | 'processing' | 'analyzing' | 'complete' | 'failed';

export interface Run {
  id: string;
  theme: string;
  research_theme?: string;
  target_population?: string;
  research_objective?: string;
  objective?: string;
  num_hypotheses: number;
  status: RunStatus;
  created_at: string;
  updated_at?: string;
  hypothesis_count?: number;
  error?: string | null;
}

export interface RunDetail extends Run {
  hypotheses: Hypothesis[];
  gaps: ResearchGap[];
  topics?: Topic[];
  evidence_count?: number;
  validation_summary?: ValidationSummary;
  pipeline_steps?: PipelineStep[];
}

export interface PipelineStep {
  name: string;
  status: RunStatus;
  started_at?: string;
  completed_at?: string;
  message?: string;
}

// --- Hypotheses ----------------------------------------------------

export type HypothesisStatus = 'generated' | 'validating' | 'validated' | 'refined' | 'challenged' | 'ranked' | 'failed';

export interface Hypothesis {
  id: string;
  run_id: string;
  text: string;
  statement?: string;
  refined_text?: string;
  refined_statement?: string;
  research_question?: string;
  population?: string;
  intervention?: string;
  outcome?: string;
  mechanism?: string;
  relationship?: string;
  status: HypothesisStatus;
  score?: number;
  rank?: number;
  rank_score?: number;
  novelty_score?: number;
  testability_score?: number;
  evidence_support_score?: number;
  clarity_score?: number;
  relevance_score?: number;
  created_at: string;
  updated_at?: string;
  tags?: string[];
  citations?: string[];
  assumptions?: string[];
  limitations?: string[];
  evidence_records?: any[];
  validation_results?: any;
  challenge_results?: any;
}

// --- Topics & Ontology --------------------------------------------

export interface Topic {
  id: string;
  topic_id?: number;
  label: string;
  keywords?: string[];
  count?: number;
  document_count?: number;
  relevance?: number;
  parent_topic?: string;
  mesh_id?: string;
}

export interface TopicTrend {
  topic: string;
  year: number;
  count: number;
  growth_rate?: number;
}

// --- Research Gaps -------------------------------------------------

export interface ResearchGap {
  id: string;
  description: string;
  score: number;
  related_topics?: string[];
  related_concepts?: string[];
  evidence?: any[];
  evidence_density?: number;
  publication_trend?: 'increasing' | 'decreasing' | 'stable';
  gap_type?: 'methodological' | 'population' | 'outcome' | 'intervention' | 'conceptual';
  source_articles?: number;
  created_at?: string;
}

// --- Evidence ------------------------------------------------------

export type EvidenceType = 'supporting' | 'contradictory' | 'neutral';

export interface Evidence {
  id: string;
  hypothesis_id: string;
  passage: string;
  source_title: string;
  source_pmid?: string;
  source_pmcid?: string;
  source_doi?: string;
  authors?: string[];
  publication_year?: number;
  pub_year?: number;
  journal?: string;
  evidence_type: EvidenceType;
  type?: EvidenceType;
  relevance_score?: number;
  nli_label?: string;
  nli_score?: number;
  section?: string;
  source_type?: string;
}

export interface RetrievalResult {
  query: string;
  total_results: number;
  passages: RetrievalPassage[];
}

export interface RetrievalPassage {
  text: string;
  score: number;
  source: string;
  pmid?: string;
  section?: string;
}

// --- Validation ----------------------------------------------------

export interface ValidationResult {
  hypothesis_id: string;
  citation_check?: CitationCheck;
  citation_valid?: boolean;
  nli_results?: NLIResult[];
  nli_label?: string;
  nli_score?: number;
  novelty?: NoveltyAssessment;
  novelty_score?: number;
  rule_checks?: RuleCheck[];
  overall_validity_score?: number;
  prior_art?: any[];
}

export interface CitationCheck {
  hypothesis_id: string;
  verified: boolean;
  total_citations: number;
  valid_citations: number;
  invalid_citations: number;
  details?: CitationDetail[];
}

export interface CitationDetail {
  citation: string;
  found: boolean;
  pmid?: string;
  title?: string;
}

export interface NLIResult {
  hypothesis_id: string;
  premise: string;
  hypothesis_text: string;
  label: 'entailment' | 'contradiction' | 'neutral';
  score: number;
  source?: string;
}

export interface NoveltyAssessment {
  hypothesis_id: string;
  novelty_score: number;
  prior_art: PriorArt[];
  assessment?: string;
}

export interface PriorArt {
  title: string;
  similarity: number;
  pmid?: string;
  year?: number;
}

export interface RuleCheck {
  rule_name?: string;
  name?: string;
  passed: boolean;
  score?: number;
  message?: string;
}

export interface ValidationSummary {
  total_hypotheses: number;
  validated_count: number;
  avg_novelty: number;
  avg_evidence_score: number;
}

// --- Challenge -----------------------------------------------------

export interface ChallengeRequest {
  challenge_type?: 'contradiction' | 'methodology' | 'population' | 'comprehensive';
  max_counter_evidence?: number;
}

export interface ChallengeReport {
  hypothesis_id: string;
  claims: string[];
  retrieval_queries: string[];
  supporting_passages: Evidence[];
  contradictory_passages: Evidence[];
  neutral_passages: Evidence[];
  counter_evidence_count: number;
  confidence_score: number;
  summary: string;
}

export interface RefineRequest {
  run_id?: string;
  hypothesis_id?: string;
  refinement_notes?: string;
  incorporate_evidence?: boolean;
}

// --- Evaluation ----------------------------------------------------

export interface EvaluationMetrics {
  run_id: string;
  metrics?: { name: string; value: number }[];
  baselines?: BaselineComparison[];
  precision_at_k: Record<string, number>;
  recall_at_k: Record<string, number>;
  mrr: number;
  ndcg_at_k: Record<string, number>;
  topic_coherence: number;
  topic_diversity: number;
  citation_precision: number;
  nli_agreement: number;
  novelty_score: number;
  ablation_results?: Record<string, any>;
}

export interface BaselineComparison {
  baseline_name: string;
  baseline_score: number;
  system_score: number;
  improvement: number;
  metric: string;
}

// --- Knowledge Graph -----------------------------------------------

export interface KnowledgeGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'paper' | 'topic' | 'concept' | 'disease' | 'intervention' | 'technology' | 'population' | 'outcome';
  properties?: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation: string;
  weight?: number;
  source_type?: 'ontology' | 'literature';
}

// --- Corpus --------------------------------------------------------

export interface CorpusStats {
  total_documents?: number;
  total_articles?: number;
  fulltext_count?: number;
  abstract_count?: number;
  total_passages?: number;
  indexed_topics?: number;
  date_range?: any;
  last_updated?: string;
  sources?: CorpusSource[];
  top_journals?: any[];
  mesh_term_count?: number;
}

export interface CorpusSource {
  name: string;
  count: number;
  percentage: number;
}

// --- API Payloads --------------------------------------------------

export interface GenerateRequest {
  theme: string;
  research_theme?: string;
  target_population?: string;
  research_objective?: string;
  objective?: string;
  num_hypotheses: number;
}

export interface GenerateResponse {
  run_id: string;
  status: RunStatus;
  message?: string;
}
