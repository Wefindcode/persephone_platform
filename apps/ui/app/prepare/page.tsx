'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Card from '@/components/Card';
import Alert from '@/components/Alert';
import { ApiError, PrepareStatusResponse, prepareStart, prepareStatus } from '@/lib/api';

function useRunId(): string | null {
  const searchParams = useSearchParams();
  const [runId, setRunId] = useState<string | null>(null);

  useEffect(() => {
    const queryRunId = searchParams.get('runId');
    if (queryRunId) {
      setRunId(queryRunId);
      window.localStorage.setItem('currentRunId', queryRunId);
      return;
    }

    const stored = window.localStorage.getItem('currentRunId');
    if (stored) {
      setRunId(stored);
    }
  }, [searchParams]);

  return runId;
}

export default function PreparePage(): JSX.Element {
  const router = useRouter();
  const runId = useRunId();
  const [status, setStatus] = useState<PrepareStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);

  const fetchStatus = useCallback(async () => {
    if (!runId) {
      return;
    }
    try {
      const response = await prepareStatus(runId);
      setStatus(response);
      setError(null);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Не удалось получить статус подготовки.';
      setError(message);
    }
  }, [runId]);

  useEffect(() => {
    if (!runId) {
      return;
    }
    void fetchStatus();
  }, [fetchStatus, runId]);

  useEffect(() => {
    if (status && !hasStarted) {
      setHasStarted(true);
    }
  }, [hasStarted, status]);

  useEffect(() => {
    if (!runId || !hasStarted) {
      return;
    }

    let cancelled = false;

    const poll = async () => {
      if (cancelled) {
        return;
      }
      await fetchStatus();
    };

    poll();
    const interval = window.setInterval(poll, 2000);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [fetchStatus, hasStarted, runId]);

  const handleStart = async () => {
    if (!runId) {
      setError('Не найден идентификатор запуска. Вернитесь к загрузке артефакта.');
      return;
    }
    setIsStarting(true);
    setError(null);
    try {
      const response = await prepareStart(runId);
      setStatus(response);
      setHasStarted(true);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Не удалось запустить подготовку.';
      setError(message);
    } finally {
      setIsStarting(false);
    }
  };

  const steps = useMemo(() => status?.steps ?? [], [status]);
  const phase = status?.phase;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <Card
        title="Подготовка окружения"
        actions={
          <button
            type="button"
            onClick={handleStart}
            disabled={isStarting || !runId}
            className="inline-flex items-center rounded-lg bg-silver px-4 py-2 text-sm font-semibold text-black transition hover:bg-silver-light focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-silver-light"
          >
            {isStarting ? 'Запуск…' : 'Стартовать'}
          </button>
        }
      >
        <div className="space-y-4">
          <p className="text-silver-dark">
            Настраиваем зависимости, проверяем артефакт и готовим инфраструктуру. Шаги обновляются каждые 2 секунды.
          </p>
          {error ? <Alert variant="error">{error}</Alert> : null}
          <div className="space-y-3">
            {steps.length === 0 ? (
              <p className="text-sm text-zinc-500">Шаги будут показаны после запуска подготовки.</p>
            ) : (
              <ol className="space-y-2">
                {steps.map((step) => (
                  <li
                    key={step.name}
                    className="flex items-start justify-between gap-4 rounded-lg border border-zinc-800 bg-black/40 px-4 py-3"
                  >
                    <div>
                      <p className="font-medium text-silver-light">{step.name}</p>
                      {step.message ? <p className="text-xs text-zinc-500">{step.message}</p> : null}
                    </div>
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide ${
                        step.status === 'Succeeded'
                          ? 'bg-silver/10 text-silver-light'
                          : step.status === 'Running'
                          ? 'bg-white/5 text-silver'
                          : step.status === 'Failed'
                          ? 'bg-rose-500/10 text-rose-300'
                          : 'bg-zinc-800 text-zinc-400'
                      }`}
                    >
                      {step.status}
                    </span>
                  </li>
                ))}
              </ol>
            )}
          </div>
          {phase ? (
            <Alert variant={phase === 'Succeeded' ? 'success' : phase === 'Failed' ? 'error' : 'info'}>
              Текущая фаза: <strong className="font-semibold text-silver-light">{phase}</strong>
            </Alert>
          ) : null}
          {phase === 'Succeeded' && runId ? (
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => router.push(`/deploy?runId=${encodeURIComponent(runId)}`)}
                className="inline-flex items-center rounded-lg border border-silver/60 px-4 py-2 text-sm font-semibold text-silver-light transition hover:bg-silver/10"
              >
                Перейти к деплою
              </button>
            </div>
          ) : null}
        </div>
      </Card>
    </div>
  );
}
