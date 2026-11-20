import type { LucideIcon } from 'lucide-react';
import { Inbox } from 'lucide-react';
import clsx from 'clsx';

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export default function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div className={clsx('flex flex-col items-center justify-center gap-3 py-16', className)}>
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-100">
        <Icon className="h-6 w-6 text-slate-400" />
      </div>
      <div className="text-center">
        <p className="text-sm font-medium text-slate-900">{title}</p>
        {description && (
          <p className="mt-1 text-sm text-slate-500 max-w-sm">{description}</p>
        )}
      </div>
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
