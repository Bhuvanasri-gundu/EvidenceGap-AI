import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import clsx from 'clsx';

interface MetricCardProps {
  label: string;
  value: string | number;
  change?: number;
  icon?: React.ReactNode;
  className?: string;
}

export default function MetricCard({ label, value, change, icon, className }: MetricCardProps) {
  const trend = change !== undefined ? (change > 0 ? 'up' : change < 0 ? 'down' : 'flat') : null;

  return (
    <div className={clsx('card p-5', className)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{label}</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">{value}</p>
          {trend && (
            <div className="mt-2 flex items-center gap-1">
              {trend === 'up' && <TrendingUp className="h-3.5 w-3.5 text-emerald-500" />}
              {trend === 'down' && <TrendingDown className="h-3.5 w-3.5 text-red-500" />}
              {trend === 'flat' && <Minus className="h-3.5 w-3.5 text-slate-400" />}
              <span
                className={clsx('text-xs font-medium', {
                  'text-emerald-600': trend === 'up',
                  'text-red-600': trend === 'down',
                  'text-slate-500': trend === 'flat',
                })}
              >
                {change !== undefined && change > 0 ? '+' : ''}{change?.toFixed(1)}%
              </span>
            </div>
          )}
        </div>
        {icon && (
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
