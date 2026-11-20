import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as api from '@/services/api';
import type {
  GenerateRequest,
  RefineRequest,
  ChallengeRequest,
} from '@/types';

// ─── Query Keys ────────────────────────────────────────────────────

export const queryKeys = {
  runs: ['runs'] as const,
  run: (id: string) => ['runs', id] as const,
  runStatus: (id: string) => ['runs', id, 'status'] as const,
  hypotheses: (runId: string) => ['runs', runId, 'hypotheses'] as const,
  hypothesis: (runId: string, hId: string) => ['runs', runId, 'hypotheses', hId] as const,
  evidence: (runId: string, hId?: string) => ['runs', runId, 'evidence', hId ?? 'all'] as const,
  validation: (runId: string) => ['runs', runId, 'validation'] as const,
  validationResult: (runId: string, hId: string) => ['runs', runId, 'validation', hId] as const,
  evaluation: (runId: string) => ['runs', runId, 'evaluation'] as const,
  topics: ['topics'] as const,
  gaps: (runId?: string) => ['gaps', runId ?? 'all'] as const,
  knowledgeGraph: (runId?: string) => ['knowledge-graph', runId ?? 'all'] as const,
  corpus: ['corpus'] as const,
};

// ─── Runs ──────────────────────────────────────────────────────────

export function useRuns() {
  return useQuery({
    queryKey: queryKeys.runs,
    queryFn: api.listRuns,
  });
}

export function useRun(runId: string) {
  return useQuery({
    queryKey: queryKeys.run(runId),
    queryFn: () => api.getRun(runId),
    enabled: !!runId,
  });
}

export function useRunStatus(runId: string) {
  return useQuery({
    queryKey: queryKeys.runStatus(runId),
    queryFn: () => api.getRunStatus(runId),
    enabled: !!runId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === 'complete' || status === 'failed') return false;
      return 3000; // Poll every 3 seconds while processing
    },
  });
}

// ─── Hypotheses ────────────────────────────────────────────────────

export function useHypotheses(runId: string) {
  return useQuery({
    queryKey: queryKeys.hypotheses(runId),
    queryFn: () => api.getHypotheses(runId),
    enabled: !!runId,
  });
}

export function useHypothesis(runId: string, hypothesisId: string) {
  return useQuery({
    queryKey: queryKeys.hypothesis(runId, hypothesisId),
    queryFn: () => api.getHypothesis(runId, hypothesisId),
    enabled: !!runId && !!hypothesisId,
  });
}

// ─── Mutations ─────────────────────────────────────────────────────

export function useGenerateHypotheses() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: GenerateRequest) => api.generateHypotheses(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.runs });
    },
  });
}

export function useRefineHypothesis(runId: string, hypothesisId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: RefineRequest) => api.refineHypothesis(runId, hypothesisId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.hypotheses(runId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.hypothesis(runId, hypothesisId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.run(runId) });
    },
  });
}

export function useChallengeHypothesis(runId: string, hypothesisId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ChallengeRequest) => api.challengeHypothesis(runId, hypothesisId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.hypotheses(runId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.run(runId) });
    },
  });
}

// ─── Evidence ──────────────────────────────────────────────────────

export function useEvidence(runId: string, hypothesisId?: string) {
  return useQuery({
    queryKey: queryKeys.evidence(runId, hypothesisId),
    queryFn: () => api.getEvidence(runId, hypothesisId),
    enabled: !!runId,
  });
}

// ─── Validation ────────────────────────────────────────────────────

export function useValidationResults(runId: string) {
  return useQuery({
    queryKey: queryKeys.validation(runId),
    queryFn: () => api.getValidationResults(runId),
    enabled: !!runId,
  });
}

export function useValidationResult(runId: string, hypothesisId: string) {
  return useQuery({
    queryKey: queryKeys.validationResult(runId, hypothesisId),
    queryFn: () => api.getValidationResult(runId, hypothesisId),
    enabled: !!runId && !!hypothesisId,
  });
}

// ─── Topics & Gaps ─────────────────────────────────────────────────

export function useTopics(limit?: number) {
  return useQuery({
    queryKey: queryKeys.topics,
    queryFn: () => api.getTopics(limit),
  });
}

export function useGaps(runId?: string) {
  return useQuery({
    queryKey: queryKeys.gaps(runId),
    queryFn: () => api.getGaps(runId),
  });
}

// ─── Evaluation ────────────────────────────────────────────────────

export function useEvaluationMetrics(runId: string) {
  return useQuery({
    queryKey: queryKeys.evaluation(runId),
    queryFn: () => api.getEvaluationMetrics(runId),
    enabled: !!runId,
  });
}

// ─── Knowledge Graph ───────────────────────────────────────────────

export function useKnowledgeGraph(runId?: string) {
  return useQuery({
    queryKey: queryKeys.knowledgeGraph(runId),
    queryFn: () => api.getKnowledgeGraph(runId),
  });
}

// ─── Corpus ────────────────────────────────────────────────────────

export function useCorpusStats() {
  return useQuery({
    queryKey: queryKeys.corpus,
    queryFn: api.getCorpusStats,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
