import { Loader2 } from 'lucide-react';
import clsx from 'clsx';

interface LoadingSpinnerProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export default function LoadingSpinner({ message, size = 'md', className }: LoadingSpinnerProps) {
  const sizeMap = { sm: 'h-4 w-4', md: 'h-6 w-6', lg: 'h-10 w-10' };

  return (
    <div className={clsx('flex flex-col items-center justify-center gap-3 py-12', className)}>
      <Loader2 className={clsx('animate-spin text-indigo-600', sizeMap[size])} />
      {message && (
        <p className="text-sm text-slate-500 animate-pulse">{message}</p>
      )}
    </div>
  );
}
