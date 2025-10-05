'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Card from '@/components/Card';
import Alert from '@/components/Alert';
import { ApiError, MonitorSummaryResponse, monitorSummary } from '@/lib/api';

export default function MonitorRunPage(): JSX.Element {
  const params = useParams<{ runId: string }>();
  const runId = params.runId;
  const [summary, setSummary] = useState<MonitorSummaryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    setSummary(null);
    setError(null);
  }, [runId]);

  useEffect(() => {
    let cancelled = false;

    const fetchSummary = async () => {
      if (!runId) {
        return;
      }
      try {
        const response = await monitorSummary(runId);
        if (!cancelled) {
          setSummary(response);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          const message = err instanceof ApiError ? err.message : 'Не удалось загрузить метрики мониторинга.';
          setError(message);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    fetchSummary();
    const interval = window.setInterval(fetchSummary, 5000);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [runId]);

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <Card title={`Мониторинг запуска ${runId}`}>
        <div className="space-y-4">
          {error ? <Alert variant="error">{error}</Alert> : null}
          {isLoading && !summary ? <p className="text-sm text-zinc-500">Загрузка метрик…</p> : null}
          {summary ? (
            <div className="grid gap-4 md:grid-cols-2">
              <Card title="RED метрики">
                <dl className="space-y-3">
                  <div>
                    <dt className="text-xs uppercase tracking-wide text-zinc-500">RPS</dt>
                    <dd className="text-2xl font-semibold text-silver-light">{summary.red.rps.toFixed(1)}</dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase tracking-wide text-zinc-500">Ошибки, %</dt>
                    <dd className="text-2xl font-semibold text-rose-300">{summary.red.errorsPercent.toFixed(2)}%</dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase tracking-wide text-zinc-500">P95, мс</dt>
                    <dd className="text-2xl font-semibold text-silver-light">{summary.red.p95DurationMs.toFixed(0)}</dd>
                  </div>
                </dl>
              </Card>
              <Card title="SLO">
                <dl className="space-y-3">
                  <div>
                    <dt className="text-xs uppercase tracking-wide text-zinc-500">Доступность</dt>
                    <dd className="text-2xl font-semibold text-silver-light">{summary.slo.availability.toFixed(2)}%</dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase tracking-wide text-zinc-500">Задержка P95, мс</dt>
                    <dd className="text-2xl font-semibold text-silver-light">{summary.slo.latencyP95Ms.toFixed(0)}</dd>
                  </div>
                </dl>
              </Card>
            </div>
          ) : null}
          {summary?.updatedAt ? (
            <p className="text-xs text-zinc-600">Последнее обновление: {new Date(summary.updatedAt).toLocaleString()}</p>
          ) : null}
        </div>
      </Card>
    </div>
  );
}
