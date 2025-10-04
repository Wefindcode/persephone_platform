import { ReactNode } from 'react';

export type AlertVariant = 'info' | 'success' | 'error';

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  children: ReactNode;
}

const variantClasses: Record<AlertVariant, string> = {
  info: 'border-sky-500/40 bg-sky-500/10 text-sky-200',
  success: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200',
  error: 'border-rose-500/40 bg-rose-500/10 text-rose-200',
};

export default function Alert({ variant = 'info', title, children }: AlertProps): JSX.Element {
  return (
    <div className={`rounded-lg border px-4 py-3 text-sm ${variantClasses[variant]}`}>
      {title ? <div className="mb-1 font-semibold text-neutral-100">{title}</div> : null}
      <div className="text-sm leading-relaxed">{children}</div>
    </div>
  );
}
