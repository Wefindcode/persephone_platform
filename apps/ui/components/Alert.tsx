import { ReactNode } from 'react';

export type AlertVariant = 'info' | 'success' | 'error';

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  children: ReactNode;
}

const variantClasses: Record<AlertVariant, string> = {
  info: 'border-zinc-700 bg-zinc-900/80 text-silver-light',
  success: 'border-silver/70 bg-silver/10 text-silver-light',
  error: 'border-rose-500/60 bg-rose-500/10 text-rose-200',
};

export default function Alert({ variant = 'info', title, children }: AlertProps): JSX.Element {
  return (
    <div className={`rounded-lg border px-4 py-3 text-sm ${variantClasses[variant]}`}>
      {title ? <div className="mb-1 font-semibold text-silver-light">{title}</div> : null}
      <div className="text-sm leading-relaxed text-inherit">{children}</div>
    </div>
  );
}
