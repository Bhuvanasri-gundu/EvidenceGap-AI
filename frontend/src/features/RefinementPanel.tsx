import React, { useState } from 'react';
import type { Hypothesis } from '@/types';
import Card from '@/components/Card';
import { ArrowRight, Sparkles, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';

interface RefinementPanelProps {
  hypotheses: Hypothesis[];
  onRefineHypothesis?: (hypothesisId: string) => Promise<void>;
}

export default function RefinementPanel({ hypotheses, onRefineHypothesis }: RefinementPanelProps) {
  const [refiningId, setRefiningId] = useState<string | null>(null);

  const handleRefine = async (id: string) => {
    if (!onRefineHypothesis) return;
    setRefiningId(id);
    try {
      await onRefineHypothesis(id);
    } finally {
      setRefiningId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-5 flex items-start gap-4">
        <Sparkles className="w-6 h-6 text-indigo-600 flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="text-sm font-bold text-indigo-950">
            Evidence-Grounded Iterative Refinement
          </h3>
          <p className="text-xs text-indigo-800 mt-1 leading-relaxed">
            Hypotheses are evaluated against retrieved literature to detect unsupported claims,
            vague variables, or conflicting findings. Refinement produces an updated, testable
            formulation that explicitly incorporates qualifying conditions and verified evidence.
          </p>
        </div>
      </div>

      <div className="space-y-6">
        {hypotheses.map((h, idx) => {
          const isRefined = !!h.refined_text;
          const isProcessing = refiningId === h.id;

          return (
            <div
              key={h.id || idx}
              className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-5"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-indigo-600 uppercase tracking-wider">
                  Hypothesis #{idx + 1}
                </span>
                <div className="flex items-center gap-2">
                  {isRefined ? (
                    <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Refined Version Available
                    </span>
                  ) : (
                    <button
                      onClick={() => handleRefine(h.id)}
                      disabled={isProcessing}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${isProcessing ? 'animate-spin' : ''}`} />
                      {isProcessing ? 'Refining...' : 'Refine Hypothesis'}
                    </button>
                  )}
                </div>
              </div>

              {/* Side-by-side or stacked Before/After */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Original Formulation */}
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-500 uppercase tracking-wider">
                    <span>Original Formulation</span>
                    <span className="text-slate-400">Pre-Refinement</span>
                  </div>
                  <p className="text-sm text-slate-800 font-medium leading-relaxed">
                    {h.text}
                  </p>
                  {h.score !== undefined && (
                    <div className="pt-2 text-xs text-slate-500">
                      Initial Quality: {(h.score * 100).toFixed(0)}%
                    </div>
                  )}
                </div>

                {/* Refined Formulation */}
                <div className={`p-4 rounded-lg border space-y-2 ${
                  isRefined
                    ? 'bg-emerald-50/40 border-emerald-200'
                    : 'bg-slate-50/50 border-dashed border-slate-200 flex flex-col justify-center items-center text-center'
                }`}>
                  {isRefined ? (
                    <>
                      <div className="flex items-center justify-between text-xs font-bold text-emerald-800 uppercase tracking-wider">
                        <span>Refined Formulation</span>
                        <span className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded text-[10px]">
                          Evidence-Grounded
                        </span>
                      </div>
                      <p className="text-sm text-slate-900 font-semibold leading-relaxed">
                        {h.refined_text}
                      </p>
                      <div className="pt-2 text-xs text-emerald-700 flex items-center gap-1">
                        <Sparkles className="w-3.5 h-3.5" />
                        Variables disambiguated & citations verified
                      </div>
                    </>
                  ) : (
                    <div className="py-6 text-slate-400 text-xs">
                      <AlertCircle className="w-6 h-6 mx-auto mb-1 text-slate-300" />
                      Click "Refine Hypothesis" to trigger the evidence-challenge refinement loop.
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {hypotheses.length === 0 && (
          <Card>
            <p className="text-sm text-slate-500 py-6 text-center">
              No hypotheses to refine. Generate hypotheses first.
            </p>
          </Card>
        )}
      </div>
    </div>
  );
}
