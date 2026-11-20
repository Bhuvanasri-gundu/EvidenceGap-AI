import { Routes, Route } from 'react-router-dom';
import Header from '@/components/Header';
import HypothesisGenerationPage from '@/pages/HypothesisGenerationPage';
import WorkspacePage from '@/pages/WorkspacePage';

export default function App() {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Header />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<HypothesisGenerationPage />} />
          <Route path="/workspace/:runId" element={<WorkspacePage />} />
        </Routes>
      </main>
      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
            <p className="text-sm text-slate-500">
              © 2026 EvidenceGap AI — Ontology-Guided Research Hypothesis Generation
            </p>
            <p className="text-xs text-slate-400">
              Built for advancing scientific discovery through AI-powered evidence analysis
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
