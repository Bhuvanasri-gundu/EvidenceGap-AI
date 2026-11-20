import clsx from 'clsx';
import type { RunStatus, HypothesisStatus } from '@/types';

type BadgeStatus = RunStatus | HypothesisStatus;

const statusConfig: Record<string, { bg: string; text: string; dot: string; label?: string }> = {
  pending: { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-500' },
  processing: { bg: 'bg-blue-50', text: 'text-blue-700', dot: 'bg-blue-500' },
  complete: { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500', label: 'Complete' },
  failed: { bg: 'bg-red-50', text: 'text-red-700', dot: 'bg-red-500' },
  generated: { bg: 'bg-slate-50', text: 'text-slate-700', dot: 'bg-slate-400' },
  validating: { bg: 'bg-blue-50', text: 'text-blue-700', dot: 'bg-blue-500' },
  validated: { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500' },
  refined: { bg: 'bg-purple-50', text: 'text-purple-700', dot: 'bg-purple-500' },
  challenged: { bg: 'bg-orange-50', text: 'text-orange-700', dot: 'bg-orange-500' },
};

interface StatusBadgeProps {
  status: BadgeStatus;
  size?: 'sm' | 'md';
  className?: string;
}

export default function StatusBadge({ status, size = 'sm', className }: StatusBadgeProps) {
  const config = statusConfig[status] ?? statusConfig.pending;
  const label = config.label ?? status.charAt(0).toUpperCase() + status.slice(1);

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 rounded-full font-medium capitalize',
        config.bg,
        config.text,
        size === 'sm' ? 'px-2.5 py-0.5 text-xs' : 'px-3 py-1 text-sm',
        className,
      )}
    >
      <span className={clsx('h-1.5 w-1.5 rounded-full', config.dot, {
        'animate-pulse': status === 'processing' || status === 'validating',
      })} />
      {label}
    </span>
  );
}
