import { Link, useLocation } from 'react-router-dom';
import { Brain, Home, FlaskConical } from 'lucide-react';
import clsx from 'clsx';

export default function Header() {
  const location = useLocation();
  const isHome = location.pathname === '/';
  const isWorkspace = location.pathname.startsWith('/workspace');

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/80 backdrop-blur-lg">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-sm transition-transform group-hover:scale-105">
              <Brain className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-900 leading-tight">
                EvidenceGap <span className="text-indigo-600">AI</span>
              </h1>
              <p className="text-[10px] font-medium text-slate-400 uppercase tracking-wider leading-none">
                Research Hypothesis Engine
              </p>
            </div>
          </Link>

          {/* Nav Links */}
          <nav className="flex items-center gap-1">
            <Link
              to="/"
              className={clsx(
                'flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isHome
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              )}
            >
              <Home className="h-4 w-4" />
              <span className="hidden sm:inline">Home</span>
            </Link>
            {isWorkspace && (
              <div className="flex items-center gap-2 rounded-lg bg-indigo-50 px-3 py-2 text-sm font-medium text-indigo-700">
                <FlaskConical className="h-4 w-4" />
                <span className="hidden sm:inline">Workspace</span>
              </div>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}
