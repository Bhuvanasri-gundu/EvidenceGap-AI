import React, { useState } from 'react';
import type { ResearchGap, Topic } from '@/types';
import Card from '@/components/Card';
import { Compass, TrendingUp, Tag, Network } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface GapExplorerPanelProps {
  gaps: ResearchGap[];
  topics?: Topic[];
}

export default function GapExplorerPanel({ gaps, topics = [] }: GapExplorerPanelProps) {
  const [selectedGap, setSelectedGap] = useState<ResearchGap | null>(gaps[0] || null);

  const chartData = (topics.length > 0 ? topics : gaps).slice(0, 10).map((item, idx) => ({
    name: 'label' in item ? (item as Topic).label : `Gap ${idx + 1}`,
    score: 'score' in item ? Number(((item as ResearchGap).score * 100).toFixed(0)) : (item as Topic).count || 10,
  }));

  return (
    <div className="space-y-6">
      {/* Top Chart Section */}
      <Card title="Discovered Research Topics & Gap Distribution" subtitle="Top concepts and areas with low coverage or emergent potential">
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} angle={-20} textAnchor="end" />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}
              />
              <Bar dataKey="score" fill="#6366f1" radius={[4, 4, 0, 0]} name="Significance Score" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Gaps List & Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* List of Gaps */}
        <div className="lg:col-span-1 space-y-3">
          <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wider mb-2">
            Identified Research Gaps ({gaps.length})
          </h3>
          <div className="space-y-2 max-h-[550px] overflow-y-auto pr-1">
            {gaps.map((gap, idx) => (
              <div
                key={gap.id || idx}
                onClick={() => setSelectedGap(gap)}
                className={`p-4 rounded-xl border text-left cursor-pointer transition-all ${
                  selectedGap?.id === gap.id
                    ? 'border-indigo-600 bg-indigo-50/50 shadow-sm'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="font-semibold text-indigo-700">Gap #{idx + 1}</span>
                  <span className="bg-indigo-100 text-indigo-800 font-medium px-2 py-0.5 rounded-full">
                    Score: {(gap.score * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-sm font-medium text-slate-900 line-clamp-2">
                  {gap.description}
                </p>
              </div>
            ))}
            {gaps.length === 0 && (
              <p className="text-sm text-slate-500 py-4 text-center bg-white rounded-xl border border-dashed border-slate-200">
                No research gaps identified.
              </p>
            )}
          </div>
        </div>

        {/* Selected Gap Detail */}
        <div className="lg:col-span-2">
          {selectedGap ? (
            <Card title="Gap Analysis & Ontological Context">
              <div className="space-y-4">
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                    Description
                  </h4>
                  <p className="text-base text-slate-800 font-medium bg-slate-50 p-4 rounded-lg border border-slate-100">
                    {selectedGap.description}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white p-3 rounded-lg border border-slate-200">
                    <span className="text-xs text-slate-500 font-medium flex items-center gap-1">
                      <TrendingUp className="w-3.5 h-3.5 text-indigo-500" /> Gap Score
                    </span>
                    <p className="text-lg font-bold text-indigo-600 mt-1">
                      {(selectedGap.score * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-white p-3 rounded-lg border border-slate-200">
                    <span className="text-xs text-slate-500 font-medium flex items-center gap-1">
                      <Compass className="w-3.5 h-3.5 text-indigo-500" /> Evidence Density
                    </span>
                    <p className="text-lg font-bold text-indigo-600 mt-1">
                      {selectedGap.evidence_density ? `${(selectedGap.evidence_density * 100).toFixed(1)}%` : 'Sparse'}
                    </p>
                  </div>
                </div>

                {selectedGap.related_concepts && selectedGap.related_concepts.length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                      <Tag className="w-3.5 h-3.5 text-indigo-500" /> Ontological Concepts & MeSH Terms
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedGap.related_concepts.map((concept, idx) => (
                        <span
                          key={idx}
                          className="px-2.5 py-1 text-xs font-medium bg-slate-100 text-slate-800 rounded-md border border-slate-200"
                        >
                          {concept}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {selectedGap.related_topics && selectedGap.related_topics.length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                      <Network className="w-3.5 h-3.5 text-indigo-500" /> Associated Research Themes
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedGap.related_topics.map((theme, idx) => (
                        <span
                          key={idx}
                          className="px-2.5 py-1 text-xs font-medium bg-indigo-50 text-indigo-700 rounded-md border border-indigo-100"
                        >
                          {theme}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Card>
          ) : (
            <div className="h-full flex items-center justify-center p-8 bg-white rounded-xl border border-slate-200 text-slate-400">
              Select a gap from the list to view its complete ontological analysis.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
