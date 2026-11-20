import React, { useState } from 'react';
import type { Evidence, Hypothesis } from '@/types';
import Card from '@/components/Card';
import { BookOpen, ExternalLink, Filter, CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';

interface EvidencePanelProps {
  evidenceList: Evidence[];
  hypotheses?: Hypothesis[];
}

export default function EvidencePanel({ evidenceList, hypotheses = [] }: EvidencePanelProps) {
  const [filterType, setFilterType] = useState<string>('all');
  const [selectedHypothesisId, setSelectedHypothesisId] = useState<string>('all');

  const filteredEvidence = evidenceList.filter((item) => {
    const matchesType = filterType === 'all' || item.type === filterType;
    const matchesHyp = selectedHypothesisId === 'all' || item.hypothesis_id === selectedHypothesisId;
    return matchesType && matchesHyp;
  });

  const supportingCount = evidenceList.filter(e => e.type === 'supporting').length;
  const contradictoryCount = evidenceList.filter(e => e.type === 'contradictory').length;
  const neutralCount = evidenceList.filter(e => e.type === 'neutral').length;

  return (
    <div className="space-y-6">
      {/* Controls & Counts Row */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200">
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => setFilterType('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              filterType === 'all' ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            All ({evidenceList.length})
          </button>
          <button
            onClick={() => setFilterType('supporting')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors ${
              filterType === 'supporting' ? 'bg-emerald-600 text-white' : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" /> Supporting ({supportingCount})
          </button>
          <button
            onClick={() => setFilterType('contradictory')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors ${
              filterType === 'contradictory' ? 'bg-rose-600 text-white' : 'bg-rose-50 text-rose-700 hover:bg-rose-100'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" /> Contradictory ({contradictoryCount})
          </button>
          <button
            onClick={() => setFilterType('neutral')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors ${
              filterType === 'neutral' ? 'bg-amber-600 text-white' : 'bg-amber-50 text-amber-700 hover:bg-amber-100'
            }`}
          >
            <HelpCircle className="w-3.5 h-3.5" /> Inconclusive ({neutralCount})
          </button>
        </div>

        {hypotheses.length > 0 && (
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={selectedHypothesisId}
              onChange={(e) => setSelectedHypothesisId(e.target.value)}
              className="text-xs bg-slate-50 border border-slate-200 rounded-lg p-2 text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500 w-full sm:w-48"
            >
              <option value="all">All Hypotheses</option>
              {hypotheses.map((h, idx) => (
                <option key={h.id || idx} value={h.id}>
                  H{idx + 1}: {h.text.slice(0, 35)}...
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Evidence Items List */}
      <div className="space-y-4">
        {filteredEvidence.map((item, idx) => {
          const typeBadge =
            item.type === 'supporting'
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
              : item.type === 'contradictory'
              ? 'bg-rose-50 text-rose-700 border-rose-200'
              : 'bg-amber-50 text-amber-700 border-amber-200';

          return (
            <div
              key={item.id || idx}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:border-slate-300 transition-all space-y-3"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border capitalize ${typeBadge}`}>
                    {item.type}
                  </span>
                  {item.relevance_score !== undefined && (
                    <span className="text-xs text-slate-500 font-medium">
                      Relevance: {(item.relevance_score * 100).toFixed(0)}%
                    </span>
                  )}
                  {item.nli_score !== undefined && (
                    <span className="text-xs text-slate-500">
                      NLI Score: {(item.nli_score * 100).toFixed(0)}%
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-3 text-xs text-slate-500">
                  {item.source_pmid && (
                    <a
                      href={`https://pubmed.ncbi.nlm.nih.gov/${item.source_pmid}/`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-indigo-600 hover:text-indigo-800 font-medium flex items-center gap-1"
                    >
                      PMID: {item.source_pmid}
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                  {item.source_pmcid && (
                    <a
                      href={`https://www.ncbi.nlm.nih.gov/pmc/articles/${item.source_pmcid}/`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-indigo-600 hover:text-indigo-800 font-medium flex items-center gap-1"
                    >
                      {item.source_pmcid}
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>

              {/* Source Title & Publication Details */}
              <div>
                <h4 className="text-sm font-semibold text-slate-900 flex items-center gap-1.5">
                  <BookOpen className="w-4 h-4 text-indigo-500 flex-shrink-0" />
                  {item.source_title || 'Peer-Reviewed Scientific Publication'}
                </h4>
                {item.journal && (
                  <p className="text-xs text-slate-500 mt-0.5">
                    {item.journal} {item.pub_year ? `(${item.pub_year})` : ''}
                  </p>
                )}
              </div>

              {/* Extracted Passage */}
              <div className="bg-slate-50 rounded-lg p-3.5 border border-slate-100 text-slate-700 text-sm italic leading-relaxed">
                "{item.passage}"
              </div>

              {item.source_type && (
                <div className="flex items-center gap-2 pt-1">
                  <span className="text-xs text-slate-400">Source Type:</span>
                  <span className="text-xs font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-600 uppercase">
                    {item.source_type}
                  </span>
                </div>
              )}
            </div>
          );
        })}

        {filteredEvidence.length === 0 && (
          <Card>
            <div className="text-center py-10 text-slate-400">
              <BookOpen className="w-10 h-10 mx-auto text-slate-300 mb-2" />
              <p className="text-sm font-medium">No evidence passages match your current filter.</p>
              <p className="text-xs text-slate-400 mt-1">Try resetting the filter or running the evidence challenge.</p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
