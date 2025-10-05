'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import Card from '@/components/Card';
import Alert from '@/components/Alert';
import { ApiError, uploadArtifact } from '@/lib/api';

export default function UploadPage(): JSX.Element {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!file) {
      setError('Пожалуйста, выберите файл артефакта.');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const response = await uploadArtifact(file);
      const { runId } = response;
      window.localStorage.setItem('currentRunId', runId);
      router.push(`/prepare?runId=${encodeURIComponent(runId)}`);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Не удалось загрузить артефакт. Попробуйте позже.';
      setError(message);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl">
      <Card title="Загрузка артефакта">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-silver-light" htmlFor="artifact">
              Файл модели или пакета
            </label>
            <input
              id="artifact"
              type="file"
              accept=".zip,.tar,.tar.gz,.onnx,.pt,.pkl"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              className="w-full rounded-lg border border-dashed border-zinc-700 bg-black/40 px-4 py-12 text-center text-silver-dark transition hover:border-silver/60 hover:text-silver"
            />
            <p className="text-xs text-zinc-500">
              Поддерживаются архивы и бинарные файлы моделей. Максимальный размер — 500&nbsp;МБ.
            </p>
          </div>

          {error ? <Alert variant="error">{error}</Alert> : null}

          <div className="flex items-center justify-end gap-3">
            <button
              type="submit"
              disabled={isUploading}
              className="inline-flex items-center justify-center rounded-lg bg-silver px-5 py-2 text-sm font-semibold text-black transition hover:bg-silver-light focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-silver-light"
            >
              {isUploading ? 'Загрузка…' : 'Загрузить артефакт'}
            </button>
          </div>
        </form>
      </Card>
    </div>
  );
}
