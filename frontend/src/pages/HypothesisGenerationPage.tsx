import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  Database,
  Layers,
  FileText,
  Search,
  BookOpen,
  Calendar,
  AlertCircle,
  Lightbulb,
} from 'lucide-react';
import { useGenerateHypotheses, useRuns, useCorpusStats, useTopics } from '@/hooks/useApi';
import StatusBadge from '@/components/StatusBadge';
import Card from '@/components/Card';
import MetricCard from '@/components/MetricCard';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function HypothesisGenerationPage() {
  const navigate = useNavigate();

  // Form State -- intentionally empty placeholders per requirements
  const [theme, setTheme] = useState('');
  const [population, setPopulation] = useState('');
  const [objective, setObjective] = useState('');
  const [numHypotheses, setNumHypotheses] = useState(5);

  // API Hooks
  const generateMutation = useGenerateHypotheses();
  const { data: runs, isLoading: runsLoading } = useRuns();
  const { data: stats } = useCorpusStats();
  const { data: topics } = useTopics(12);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!theme.trim()) return;

    try {
      const response = await generateMutation.mutateAsync({
        theme: theme.trim(),
        target_population: population.trim() || undefined,
        research_objective: objective.trim() || undefined,
        num_hypotheses: numHypotheses,
      });

      if (response && response.run_id) {
        navigate(`/workspace/${response.run_id}`);
      }
    } catch (err) {
      console.error('Failed to trigger generation:', err);
    }
  };

  const handleSuggestionClick = (suggestedTheme: string) => {
    setTheme(suggestedTheme);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* Hero Header */}
      <div className="text-center max-w-3xl mx-auto space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-700 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          Ontology-Guided RAG & Evidence Challenge Engine
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          EvidenceGap AI 2026
        </h1>
        <p className="text-base text-slate-600 leading-relaxed">
          Discover underexplored research relationships in mobile health literature.
          Generate structured, testable hypotheses grounded in biomedical ontologies,
          independently challenged with peer-reviewed literature, and refined through evidence.
        </p>
      </div>

      {/* Main Generation Form Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-indigo-600" />
                Configure Hypothesis Generation
              </h2>
              <span className="text-xs text-slate-400">Screen 1 of 2</span>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Research Theme Input */}
              <div>
                <label htmlFor="theme" className="block text-sm font-semibold text-slate-800 mb-1">
                  Research Theme or Clinical Domain <span className="text-rose-500">*</span>
                </label>
                <textarea
                  id="theme"
                  rows={3}
                  value={theme}
                  onChange={(e) => setTheme(e.target.value)}
                  placeholder="e.g., Mobile health interventions for pediatric type 1 diabetes adherence and glycemic control"
                  required
                  className="w-full text-sm rounded-xl border-slate-200 border p-3.5 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition"
                />
                <p className="text-xs text-slate-500 mt-1">
                  Specify the health condition, technological intervention, or research focus.
                </p>
              </div>

              {/* Target Population Input */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="population" className="block text-xs font-semibold text-slate-700 mb-1">
                    Target Population (Optional)
                  </label>
                  <input
                    id="population"
                    type="text"
                    value={population}
                    onChange={(e) => setPopulation(e.target.value)}
                    placeholder="e.g., Adolescents and young adults (12-18 years)"
                    className="w-full text-sm rounded-lg border-slate-200 border p-2.5 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition"
                  />
                </div>

                {/* Research Objective */}
                <div>
                  <label htmlFor="objective" className="block text-xs font-semibold text-slate-700 mb-1">
                    Primary Objective (Optional)
                  </label>
                  <input
                    id="objective"
                    type="text"
                    value={objective}
                    onChange={(e) => setObjective(e.target.value)}
                    placeholder="e.g., Identify psychosocial determinants of long-term app engagement"
                    className="w-full text-sm rounded-lg border-slate-200 border p-2.5 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition"
                  />
                </div>
              </div>

              {/* Number of Hypotheses Slider */}
              <div className="pt-2">
                <div className="flex justify-between items-center mb-1">
                  <label htmlFor="count" className="text-xs font-semibold text-slate-700">
                    Number of Hypotheses to Generate: <span className="text-indigo-600 font-bold">{numHypotheses}</span>
                  </label>
                  <span className="text-xs text-slate-400">(Range: 1-20)</span>
                </div>
                <input
                  id="count"
                  type="range"
                  min="1"
                  max="20"
                  value={numHypotheses}
                  onChange={(e) => setNumHypotheses(parseInt(e.target.value, 10))}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                />
              </div>

              {/* Submit Button & Status */}
              <div className="pt-4 flex flex-col sm:flex-row items-center justify-between gap-4">
                <button
                  type="submit"
                  disabled={generateMutation.isPending || !theme.trim()}
                  className="w-full sm:w-auto px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm shadow-sm hover:shadow transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {generateMutation.isPending ? (
                    <>
                      <LoadingSpinner size="sm" />
                      Initiating Pipeline...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Generate Evidence-Grounded Hypotheses
                    </>
                  )}
                </button>

                {generateMutation.isError && (
                  <p className="text-xs text-rose-600 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    Failed to start run. Please check backend connection.
                  </p>
                )}
              </div>
            </form>
          </div>
        </div>

        {/* Sidebar: Suggestions & Corpus Stats */}
        <div className="space-y-6">
          {/* Corpus Statistics Widget */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Database className="w-4 h-4 text-indigo-600" />
              Corpus Overview
            </h3>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                <span className="text-slate-500">Indexed Articles</span>
                <p className="text-lg font-bold text-slate-900 mt-0.5">
                  {stats?.total_documents?.toLocaleString() || '10,000+'}
                </p>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                <span className="text-slate-500">Full-Text Coverage</span>
                <p className="text-lg font-bold text-indigo-600 mt-0.5">
                  {stats?.fulltext_count !== undefined && stats?.total_documents ? `${((stats.fulltext_count / stats.total_documents) * 100).toFixed(0)}%` : 'PMC OA'}
                </p>
              </div>
            </div>
            <div className="text-[11px] text-slate-500 leading-relaxed border-t border-slate-100 pt-3">
              Corpus includes PubMed abstracts and open-access PMC full texts with MeSH ontologies and vector index.
            </div>
          </div>

          {/* Topic Modeling Suggestions */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-3">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-600" />
              Exploratory Topic Prompts
            </h3>
            <p className="text-xs text-slate-500">
              Click a discovered research area to populate the theme:
            </p>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {[
                'mHealth adherence in chronic disease',
                'Wearable biosensors for hypertension',
                'Smartphone CBT for adolescent anxiety',
                'Remote patient monitoring in heart failure',
                'Telehealth nudges for medication compliance',
                'Diabetes self-management digital apps',
              ].map((suggestion, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="px-2.5 py-1 text-xs rounded-lg bg-slate-100 text-slate-700 hover:bg-indigo-50 hover:text-indigo-700 border border-slate-200 hover:border-indigo-200 transition-all text-left"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Research Runs */}
      <div className="space-y-4 pt-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-indigo-600" />
            Previous Research Workspace Runs
          </h3>
          <span className="text-xs text-slate-500">
            {runs?.length || 0} run session(s)
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {runs && runs.map((run) => (
            <div
              key={run.id}
              onClick={() => navigate(`/workspace/${run.id}`)}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:border-indigo-400 hover:shadow-md transition-all cursor-pointer group flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono text-slate-400">
                    ID: {run.id.slice(0, 8)}...
                  </span>
                  <StatusBadge status={run.status} />
                </div>
                <h4 className="text-sm font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors line-clamp-2">
                  {run.theme}
                </h4>
                {run.target_population && (
                  <p className="text-xs text-slate-500 line-clamp-1">
                    Pop: {run.target_population}
                  </p>
                )}
              </div>

              <div className="flex items-center justify-between pt-4 mt-2 border-t border-slate-100 text-xs text-slate-500">
                <span>{new Date(run.created_at).toLocaleDateString()}</span>
                <span className="text-indigo-600 font-medium group-hover:underline flex items-center gap-1">
                  Open Workspace <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          ))}

          {(!runs || runs.length === 0) && !runsLoading && (
            <div className="col-span-full py-8 text-center text-slate-400 bg-white rounded-xl border border-dashed border-slate-200">
              No previous runs found. Configure a research theme above to start your first session.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
