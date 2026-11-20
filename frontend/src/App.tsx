import { Routes, Route } from 'react-router-dom';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
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
      <Footer />
    </div>
  );
}
