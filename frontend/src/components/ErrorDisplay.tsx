import { AlertCircle, RefreshCw } from 'lucide-react';
import clsx from 'clsx';

interface ErrorDisplayProps {
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export default function ErrorDisplay({
  message = 'Something went wrong',
  onRetry,
  className,
}: ErrorDisplayProps) {
  return (
    <div className={clsx('flex flex-col items-center justify-center gap-4 py-12', className)}>
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-50">
        <AlertCircle className="h-6 w-6 text-red-500" />
      </div>
      <div className="text-center">
        <p className="text-sm font-medium text-slate-900">Error</p>
        <p className="mt-1 text-sm text-slate-500 max-w-md">{message}</p>
      </div>
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary text-sm">
          <RefreshCw className="h-4 w-4" />
          Try Again
        </button>
      )}
    </div>
  );
}
