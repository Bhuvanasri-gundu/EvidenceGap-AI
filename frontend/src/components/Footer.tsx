import React from 'react';
import { ExternalLink, GitBranch, BookOpen } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white/60 py-6 mt-16 text-xs text-slate-500">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <span>(c) 2026 EvidenceGap AI</span>
          <span>-</span>
          <span>Ontology-Guided Research Hypothesis Engine</span>
        </div>
        <div className="flex items-center gap-6">
          <a
            href="https://github.com/Bhuvanasri-gundu/EvidenceGap-AI"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 hover:text-indigo-600 transition-colors"
          >
            <GitBranch className="w-3.5 h-3.5" />
            <span>Repository</span>
          </a>
          <a
            href="https://pubmed.ncbi.nlm.nih.gov/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 hover:text-indigo-600 transition-colors"
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>PubMed E-utilities</span>
          </a>
          <a
            href="https://www.ncbi.nlm.nih.gov/pmc/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 hover:text-indigo-600 transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>PMC Open Access</span>
          </a>
        </div>
      </div>
    </footer>
  );
}
