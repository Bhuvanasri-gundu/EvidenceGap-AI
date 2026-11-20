import React from 'react';
import type { RunDetail, Hypothesis } from '@/types';
import StatusBadge from '@/components/StatusBadge';
import MetricCard from '@/components/MetricCard';
import Card from '@/components/Card';
import { Target, Lightbulb, Compass, Award, ExternalLink } from 'lucide-react';

interface OverviewPanelProps {
  run: RunDetail;
  onSelectHypothesis?: (hypothesis: Hypothesis) => void;
}

export default function OverviewPanel({ run, onSelectHypothesis }: OverviewPanelProps) {
  const avgScore = run.hypotheses.length > 0
    ? (run.hypotheses.reduce((acc, h) => acc + (h.score || 0), 0) / run.hypotheses.length).toFixed(2)
    : '0.00';

  return (
    <div className="space-y-6">
      {/* Run Summary Top Card */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
                Research Run Details
              </span>
              <StatusBadge status={run.status} />
            </div>
            <h2 className="text-xl font-bold text-slate-900">{run.theme}</h2>
          </div>
          <div className="text-sm text-slate-500">
            Created: {new Date(run.created_at).toLocaleDateString()}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 text-sm">
          {run.target_population && (
            <div className="flex items-start gap-2 bg-slate-50 p-3 rounded-lg border border-slate-100">
              <Target className="w-4 h-4 text-indigo-500 mt-0.5 flex-shrink-0" />
              <div>
                <span className="font-medium text-slate-700">Target Population:</span>
                <p className="text-slate-600 mt-0.5">{run.target_population}</p>
              </div>
            </div>
          )}
          {run.research_objective && (
            <div className="flex items-start gap-2 bg-slate-50 p-3 rounded-lg border border-slate-100">
              <Compass className="w-4 h-4 text-indigo-500 mt-0.5 flex-shrink-0" />
              <div>
                <span className="font-medium text-slate-700">Research Objective:</span>
                <p className="text-slate-600 mt-0.5">{run.research_objective}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <MetricCard
          label="Generated Hypotheses"
          value={run.hypotheses.length}
          icon={<Lightbulb className="w-5 h-5 text-indigo-600" />}
        />
        <MetricCard
          label="Identified Gaps"
          value={run.gaps?.length || 0}
          icon={<Compass className="w-5 h-5 text-indigo-600" />}
        />
        <MetricCard
          label="Evidence Passages"
          value={run.evidence_count || 0}
          icon={<Target className="w-5 h-5 text-indigo-600" />}
        />
        <MetricCard
          label="Avg Quality Score"
          value={avgScore}
          icon={<Award className="w-5 h-5 text-indigo-600" />}
        />
      </div>

      {/* Hypotheses Quick List */}
      <Card title="Generated Hypotheses" subtitle="Click on any hypothesis to inspect its evidence and validation breakdown">
        <div className="divide-y divide-slate-100">
          {run.hypotheses.map((h, idx) => (
            <div
              key={h.id || idx}
              onClick={() => onSelectHypothesis?.(h)}
              className="py-4 hover:bg-slate-50 px-3 rounded-lg transition-colors cursor-pointer group"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700">
                      H{idx + 1}
                    </span>
                    <span className="text-xs text-slate-500 capitalize">{h.status}</span>
                    {h.score !== undefined && (
                      <span className="text-xs font-medium text-emerald-600">
                        Score: {(h.score * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                  <p className="text-sm font-medium text-slate-900 group-hover:text-indigo-600 transition-colors">
                    {h.text}
                  </p>
                  {h.refined_text && (
                    <p className="text-xs text-slate-500 italic mt-1">
                      Refined: {h.refined_text}
                    </p>
                  )}
                </div>
                <ExternalLink className="w-4 h-4 text-slate-400 group-hover:text-indigo-600 flex-shrink-0 mt-1" />
              </div>
            </div>
          ))}
          {run.hypotheses.length === 0 && (
            <p className="text-sm text-slate-500 py-4 text-center">
              No hypotheses generated yet for this run.
            </p>
          )}
        </div>
      </Card>
    </div>
  );
}
