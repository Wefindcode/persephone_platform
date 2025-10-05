import { ReactNode } from 'react';

interface CardProps {
  title: string;
  children: ReactNode;
  actions?: ReactNode;
  className?: string;
}

export default function Card({ title, children, actions, className }: CardProps): JSX.Element {
  return (
    <section
      className={`rounded-xl border border-zinc-800 bg-black/60 p-6 shadow-lg shadow-black/50 backdrop-blur ${className ?? ''}`.trim()}
    >
      <div className="mb-4 flex items-center justify-between gap-4">
        <h2 className="text-lg font-semibold text-silver-light">{title}</h2>
        {actions}
      </div>
      <div className="text-sm text-silver">{children}</div>
    </section>
  );
}
