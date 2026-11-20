import clsx from 'clsx';

interface CardProps {
  title?: string;
  subtitle?: string;
  headerAction?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  noPadding?: boolean;
}

export default function Card({
  title,
  subtitle,
  headerAction,
  children,
  className,
  noPadding = false,
}: CardProps) {
  return (
    <div className={clsx('card', className)}>
      {(title || headerAction) && (
        <div className="flex items-start justify-between gap-4 border-b border-slate-100 px-6 py-4">
          <div>
            {title && <h3 className="text-sm font-semibold text-slate-900">{title}</h3>}
            {subtitle && <p className="mt-0.5 text-xs text-slate-500">{subtitle}</p>}
          </div>
          {headerAction}
        </div>
      )}
      <div className={clsx({ 'p-6': !noPadding })}>
        {children}
      </div>
    </div>
  );
}
