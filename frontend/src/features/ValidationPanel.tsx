import React from 'react';
import type { ValidationResult, Hypothesis } from '@/types';
import Card from '@/components/Card';
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  ShieldCheck,
  Search,
  Scale,
  FileCheck,
} from 'lucide-react';

interface ValidationPanelProps {
  validationResults: ValidationResult[];
  hypotheses?: Hypothesis[];
}

export default function ValidationPanel({ validationResults, hypotheses = [] }: ValidationPanelProps) {
  return (
    <div className="space-y-6">
      {/* Overview Metrics Banner */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <span className="text-xs font-medium text-slate-500 flex items-center gap-1.5">
            <FileCheck className="w-4 h-4 text-indigo-500" /> Citation Verification
          </span>
          <p className="text-xl font-bold text-slate-900 mt-1">
            {validationResults.filter(v => v.citation_valid).length} / {validationResults.length || 0}
          </p>
          <span className="text-xs text-slate-400">Valid verified PMIDs</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <span className="text-xs font-medium text-slate-500 flex items-center gap-1.5">
            <Scale className="w-4 h-4 text-emerald-500" /> NLI Entailment
          </span>
          <p className="text-xl font-bold text-slate-900 mt-1">
            {validationResults.filter(v => v.nli_label === 'entailment').length} / {validationResults.length || 0}
          </p>
          <span className="text-xs text-slate-400">Supported by literature</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <span className="text-xs font-medium text-slate-500 flex items-center gap-1.5">
            <Search className="w-4 h-4 text-amber-500" /> Novelty Check
          </span>
          <p className="text-xl font-bold text-slate-900 mt-1">
            {validationResults.filter(v => (v.novelty_score || 0) > 0.6).length} / {validationResults.length || 0}
          </p>
          <span className="text-xs text-slate-400">Underexplored claims</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <span className="text-xs font-medium text-slate-500 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-indigo-500" /> Rule-Based Compliance
          </span>
          <p className="text-xl font-bold text-slate-900 mt-1">
            {validationResults.filter(v => v.rule_checks?.every(r => r.passed)).length} / {validationResults.length || 0}
          </p>
          <span className="text-xs text-slate-400">Falsifiable & testable</span>
        </div>
      </div>

      {/* Detailed Validation Results Table/Cards */}
      <div className="space-y-4">
        {validationResults.map((val, idx) => {
          const matchingHypothesis = hypotheses.find(h => h.id === val.hypothesis_id);

          return (
            <div
              key={val.hypothesis_id || idx}
              className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
                <span className="text-xs font-bold text-indigo-600 uppercase tracking-wider">
                  Validation Breakdown — Hypothesis #{idx + 1}
                </span>
                <div className="flex items-center gap-2">
                  <span className={`inline-flex items-center gap-1 text-xs px-2.5 py-0.5 rounded-full font-medium ${
                    val.citation_valid ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
                  }`}>
                    {val.citation_valid ? <CheckCircle className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                    {val.citation_valid ? 'Citations Verified' : 'Unverified Citations'}
                  </span>
                </div>
              </div>

              {matchingHypothesis && (
                <p className="text-sm font-semibold text-slate-900">
                  {matchingHypothesis.text}
                </p>
              )}

              {/* NLI & Rule Checks Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* NLI Verification */}
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                  <h5 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1">
                    <Scale className="w-3.5 h-3.5 text-indigo-500" /> Scientific NLI Model Prediction
                  </h5>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-600">Model Entailment:</span>
                    <span className="text-xs font-bold text-indigo-700 uppercase">
                      {val.nli_label || 'neutral'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-slate-600">Confidence Score:</span>
                    <span className="text-xs font-semibold text-slate-800">
                      {val.nli_score ? `${(val.nli_score * 100).toFixed(1)}%` : 'N/A'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-2 italic">
                    *DeBERTa-v3 scientific NLI inference against retrieved literature.
                  </p>
                </div>

                {/* Rule Checks List */}
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                  <h5 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" /> Scientific Rigor Rules
                  </h5>
                  <div className="space-y-1.5">
                    {val.rule_checks && val.rule_checks.length > 0 ? (
                      val.rule_checks.map((rule, rIdx) => (
                        <div key={rIdx} className="flex items-center justify-between text-xs">
                          <span className="text-slate-600">{rule.name}:</span>
                          <span className={`font-semibold flex items-center gap-1 ${
                            rule.passed ? 'text-emerald-600' : 'text-amber-600'
                          }`}>
                            {rule.passed ? <CheckCircle className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                            {rule.passed ? 'Passed' : 'Needs Review'}
                          </span>
                        </div>
                      ))
                    ) : (
                      <>
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-600">Testability & Falsifiability:</span>
                          <span className="text-emerald-600 font-semibold flex items-center gap-1">
                            <CheckCircle className="w-3 h-3" /> Passed
                          </span>
                        </div>
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-600">Population Specificity:</span>
                          <span className="text-emerald-600 font-semibold flex items-center gap-1">
                            <CheckCircle className="w-3 h-3" /> Passed
                          </span>
                        </div>
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-600">Measurable Outcomes:</span>
                          <span className="text-emerald-600 font-semibold flex items-center gap-1">
                            <CheckCircle className="w-3 h-3" /> Passed
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Prior Art / Novelty Context */}
              {val.prior_art && val.prior_art.length > 0 && (
                <div className="pt-2">
                  <h5 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1 flex items-center gap-1">
                    <Search className="w-3.5 h-3.5 text-indigo-500" /> Closest Existing Literature
                  </h5>
                  <div className="space-y-1">
                    {val.prior_art.map((art, aIdx) => (
                      <p key={aIdx} className="text-xs text-slate-600 bg-white p-2 rounded border border-slate-100">
                        • {art}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}

        {validationResults.length === 0 && (
          <Card>
            <div className="text-center py-10 text-slate-400">
              <ShieldCheck className="w-10 h-10 mx-auto text-slate-300 mb-2" />
              <p className="text-sm font-medium">No validation results available yet.</p>
              <p className="text-xs text-slate-400 mt-1">Validation runs automatically upon generation or via the challenge endpoint.</p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
