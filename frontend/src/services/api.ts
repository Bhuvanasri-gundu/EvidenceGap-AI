import axios, { AxiosError } from 'axios';
import type {
  Run,
  RunDetail,
  GenerateRequest,
  GenerateResponse,
  Hypothesis,
  Topic,
  TopicTrend,
  ResearchGap,
  Evidence,
  ValidationResult,
  ChallengeReport,
  ChallengeRequest,
  RefineRequest,
  EvaluationMetrics,
  KnowledgeGraphData,
  CorpusStats,
  RetrievalResult,
} from '@/types';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─── Error Handling ────────────────────────────────────────────────

function formatError(error: unknown): string {
  if (error instanceof AxiosError) {
    if (error.response?.data?.detail) {
      return typeof error.response.data.detail === 'string'
        ? error.response.data.detail
        : JSON.stringify(error.response.data.detail);
    }
    if (error.response?.status === 404) return 'Resource not found';
    if (error.response?.status === 422) return 'Invalid request parameters';
    if (error.response?.status === 500) return 'Internal server error — please try again';
    if (error.code === 'ECONNABORTED') return 'Request timed out — the server may be busy';
    if (!error.response) return 'Cannot reach the server — is the backend running?';
    return `Server error (${error.response.status})`;
  }
  return 'An unexpected error occurred';
}

async function request<T>(fn: () => Promise<{ data: T }>): Promise<T> {
  try {
    const { data } = await fn();
    return data;
  } catch (error) {
    throw new Error(formatError(error));
  }
}

// ─── Runs ──────────────────────────────────────────────────────────

export async function listRuns(): Promise<Run[]> {
  return request(() => api.get('/runs'));
}

export async function getRun(runId: string): Promise<RunDetail> {
  return request(() => api.get(`/runs/${runId}`));
}

export async function getRunStatus(runId: string): Promise<{ status: string; message?: string }> {
  return request(() => api.get(`/runs/${runId}/status`));
}

export async function generateHypotheses(payload: GenerateRequest): Promise<GenerateResponse> {
  return request(() => api.post('/runs', payload));
}

export async function deleteRun(runId: string): Promise<void> {
  return request(() => api.delete(`/runs/${runId}`));
}

// ─── Hypotheses ────────────────────────────────────────────────────

export async function getHypotheses(runId: string): Promise<Hypothesis[]> {
  return request(() => api.get(`/runs/${runId}/hypotheses`));
}

export async function getHypothesis(runId: string, hypothesisId: string): Promise<Hypothesis> {
  return request(() => api.get(`/runs/${runId}/hypotheses/${hypothesisId}`));
}

export async function refineHypothesis(
  runId: string,
  hypothesisId: string,
  payload: RefineRequest
): Promise<Hypothesis> {
  return request(() => api.post(`/runs/${runId}/hypotheses/${hypothesisId}/refine`, payload));
}

export async function challengeHypothesis(
  runId: string,
  hypothesisId: string,
  payload: ChallengeRequest
): Promise<ChallengeReport> {
  return request(() => api.post(`/runs/${runId}/hypotheses/${hypothesisId}/challenge`, payload));
}

// ─── Evidence ──────────────────────────────────────────────────────

export async function getEvidence(runId: string, hypothesisId?: string): Promise<Evidence[]> {
  const params = hypothesisId ? { hypothesis_id: hypothesisId } : {};
  return request(() => api.get(`/runs/${runId}/evidence`, { params }));
}

export async function searchEvidence(query: string, limit?: number): Promise<RetrievalResult> {
  return request(() => api.get('/evidence/search', { params: { query, limit } }));
}

// ─── Validation ────────────────────────────────────────────────────

export async function getValidationResults(runId: string): Promise<ValidationResult[]> {
  return request(() => api.get(`/runs/${runId}/validation`));
}

export async function getValidationResult(
  runId: string,
  hypothesisId: string
): Promise<ValidationResult> {
  return request(() => api.get(`/runs/${runId}/validation/${hypothesisId}`));
}

// ─── Topics & Gaps ─────────────────────────────────────────────────

export async function getTopics(limit?: number): Promise<Topic[]> {
  return request(() => api.get('/topics', { params: { limit } }));
}

export async function getTopicTrends(topicId: string): Promise<TopicTrend[]> {
  return request(() => api.get(`/topics/${topicId}/trends`));
}

export async function getGaps(runId?: string): Promise<ResearchGap[]> {
  const params = runId ? { run_id: runId } : {};
  return request(() => api.get('/gaps', { params }));
}

// ─── Evaluation ────────────────────────────────────────────────────

export async function getEvaluationMetrics(runId: string): Promise<EvaluationMetrics> {
  return request(() => api.get(`/runs/${runId}/evaluation`));
}

// ─── Knowledge Graph ───────────────────────────────────────────────

export async function getKnowledgeGraph(runId?: string): Promise<KnowledgeGraphData> {
  const params = runId ? { run_id: runId } : {};
  return request(() => api.get('/knowledge-graph', { params }));
}

// ─── Corpus ────────────────────────────────────────────────────────

export async function getCorpusStats(): Promise<CorpusStats> {
  return request(() => api.get('/corpus/stats'));
}

export default api;
