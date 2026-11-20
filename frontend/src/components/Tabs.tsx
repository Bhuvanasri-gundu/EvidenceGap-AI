import { useState } from 'react';
import clsx from 'clsx';

export interface TabItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  count?: number;
}

interface TabsProps {
  items: TabItem[];
  activeTab?: string;
  onChange?: (tabId: string) => void;
  className?: string;
}

export function useTabs(items: TabItem[], defaultTab?: string) {
  const [activeTab, setActiveTab] = useState(defaultTab ?? items[0]?.id ?? '');
  return { activeTab, setActiveTab, items };
}

export default function Tabs({ items, activeTab, onChange, className }: TabsProps) {
  return (
    <div className={clsx('border-b border-slate-200', className)}>
      <nav className="-mb-px flex gap-1 overflow-x-auto scrollbar-thin px-1" aria-label="Tabs">
        {items.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onChange?.(tab.id)}
            className={clsx(
              'flex items-center gap-2 whitespace-nowrap border-b-2 px-4 py-3 text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700'
            )}
          >
            {tab.icon}
            {tab.label}
            {tab.count !== undefined && (
              <span
                className={clsx(
                  'ml-1 rounded-full px-2 py-0.5 text-xs font-medium',
                  activeTab === tab.id
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'bg-slate-100 text-slate-600'
                )}
              >
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </nav>
    </div>
  );
}
