'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Card from '@/components/Card';
import Alert from '@/components/Alert';
import { ApiError, DeployStatusResponse, deployStart, deployStatus } from '@/lib/api';

const ENV_OPTIONS = [
  { value: 'dev', label: 'Dev' },
  { value: 'stage', label: 'Stage' },
  { value: 'prod', label: 'Prod' },
];

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

export default function DeployPage(): JSX.Element {
  const router = useRouter();
  const runId = useRunId();
  const [environment, setEnvironment] = useState<string>('dev');
  const [status, setStatus] = useState<DeployStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [isDeploying, setIsDeploying] = useState(false);
  const [isChecking, setIsChecking] = useState(false);

  useEffect(() => {
    if (!runId) {
      return;
    }
    (async () => {
      try {
        const response = await deployStatus(runId, environment);
        setStatus(response);
        setError(null);
      } catch (err) {
        const message = err instanceof ApiError ? err.message : null;
        if (message) {
          setError(message);
        }
      }
    })();
  }, [environment, runId]);

  useEffect(() => {
    if (status?.environment && status.environment !== environment) {
      setEnvironment(status.environment);
    }
  }, [environment, status?.environment]);

  const phase = status?.phase;

  const handleDeploy = async () => {
    if (!runId) {
      setError('Не найден идентификатор запуска. Вернитесь к предыдущим шагам.');
      return;
    }

    setIsDeploying(true);
    setError(null);
    setInfo(null);

    try {
      const response = await deployStart(runId, environment);
      setStatus(response);
      setInfo('Деплой запущен. Обновите статус для проверки прогресса.');
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Не удалось запустить деплой.';
      setError(message);
    } finally {
      setIsDeploying(false);
    }
  };

  const handleRefresh = async () => {
    if (!runId) {
      setError('Не найден идентификатор запуска.');
      return;
    }
    setIsChecking(true);
    setError(null);
    setInfo(null);
    try {
      const response = await deployStatus(runId, environment);
      setStatus(response);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Не удалось получить статус деплоя.';
      setError(message);
    } finally {
      setIsChecking(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Card
        title="Деплой артефакта"
        actions={
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleRefresh}
              disabled={isChecking || !runId}
              className="inline-flex items-center rounded-lg border border-neutral-700 px-4 py-2 text-sm font-semibold text-neutral-200 transition hover:border-neutral-500 hover:text-neutral-50"
            >
              {isChecking ? 'Обновление…' : 'Обновить статус'}
            </button>
            <button
              type="button"
              onClick={handleDeploy}
              disabled={isDeploying || !runId}
              className="inline-flex items-center rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-neutral-900 transition hover:bg-emerald-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-400"
            >
              {isDeploying ? 'Деплой…' : 'Деплоить'}
            </button>
          </div>
        }
      >
        <div className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="environment" className="text-sm font-medium text-neutral-300">
              Целевое окружение
            </label>
            <select
              id="environment"
              value={environment}
              onChange={(event) => setEnvironment(event.target.value)}
              className="w-full rounded-lg border border-neutral-700 bg-neutral-900/80 px-4 py-2 text-sm text-neutral-100 focus:border-emerald-500 focus:outline-none"
            >
              {ENV_OPTIONS.map((env) => (
                <option key={env.value} value={env.value} className="bg-neutral-900">
                  {env.label}
                </option>
              ))}
            </select>
          </div>
          {error ? <Alert variant="error">{error}</Alert> : null}
          {info ? <Alert variant="info">{info}</Alert> : null}
          {status ? (
            <div className="space-y-2 rounded-lg border border-neutral-800 bg-neutral-900/40 p-4">
              <p className="text-sm text-neutral-400">
                Запуск <span className="font-semibold text-neutral-100">{status.runId}</span> в окружении{' '}
                <span className="font-semibold text-neutral-100">{status.environment}</span>.
              </p>
              <p className="text-sm text-neutral-300">
                Текущая фаза: <span className="font-semibold text-neutral-100">{status.phase}</span>
              </p>
              {status.message ? <p className="text-xs text-neutral-500">{status.message}</p> : null}
            </div>
          ) : null}
          {phase === 'Succeeded' && runId ? (
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => router.push(`/monitor/${encodeURIComponent(runId)}`)}
                className="inline-flex items-center rounded-lg border border-emerald-500/40 px-4 py-2 text-sm font-semibold text-emerald-300 transition hover:bg-emerald-500/10"
              >
                К мониторингу
              </button>
            </div>
          ) : null}
        </div>
      </Card>
    </div>
  );
}
