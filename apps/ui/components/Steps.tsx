'use client';

import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
import { useMemo } from 'react';

interface StepItem {
  label: string;
  href: string;
}

const steps: StepItem[] = [
  { label: 'Загрузка', href: '/upload' },
  { label: 'Подготовка', href: '/prepare' },
  { label: 'Деплой', href: '/deploy' },
  { label: 'Мониторинг', href: '/monitor' },
];

const PATH_TO_INDEX: { predicate: (pathname: string) => boolean; index: number }[] = [
  { predicate: (pathname) => pathname.startsWith('/monitor'), index: 3 },
  { predicate: (pathname) => pathname.startsWith('/deploy'), index: 2 },
  { predicate: (pathname) => pathname.startsWith('/prepare'), index: 1 },
  { predicate: (pathname) => pathname.startsWith('/upload'), index: 0 },
];

export function Steps(): JSX.Element {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const queryRunId = searchParams.get('runId') ?? undefined;
  const pathRunId = pathname.startsWith('/monitor/') ? pathname.split('/')[2] : undefined;
  const runId = queryRunId ?? pathRunId;

  const activeIndex = useMemo(() => {
    const matcher = PATH_TO_INDEX.find((item) => item.predicate(pathname));
    return matcher?.index ?? 0;
  }, [pathname]);

  return (
    <nav aria-label="Процесс Persephone" className="flex items-center gap-4 text-sm text-silver-dark">
      {steps.map((step, index) => {
        const isActive = index === activeIndex;
        const isCompleted = index < activeIndex;
        const color = isActive ? 'text-silver-light' : isCompleted ? 'text-silver' : 'text-zinc-500';
        const separator = index < steps.length - 1 ? (
          <span key={`${step.label}-separator`} className="text-zinc-700">
            /
          </span>
        ) : null;

        const href = step.href === '/monitor' && runId ? `${step.href}/${encodeURIComponent(runId)}` : step.href;

        return (
          <div key={step.label} className="flex items-center gap-4">
            <Link
              href={href}
              className={`transition-colors hover:text-silver ${color}`}
              aria-current={isActive ? 'step' : undefined}
            >
              <span className="uppercase tracking-wide">{step.label}</span>
            </Link>
            {separator}
          </div>
        );
      })}
    </nav>
  );
}
