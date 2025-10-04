import { API_BASE } from './config';

export class ApiError extends Error {
  public readonly status: number;
  public readonly data: unknown;

  constructor(status: number, message: string, data?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

export interface UploadResponse {
  runId: string;
}

export type RunPhase = 'Pending' | 'Running' | 'Succeeded' | 'Failed';

export interface RunStatusStep {
  name: string;
  status: RunPhase;
  message?: string;
  completedAt?: string;
}

export interface PrepareStatusResponse {
  runId: string;
  phase: RunPhase;
  steps: RunStatusStep[];
  updatedAt?: string;
}

export interface DeployStatusResponse {
  runId: string;
  environment: string;
  phase: RunPhase;
  message?: string;
  version?: string;
  startedAt?: string;
  updatedAt?: string;
}

export interface MonitorSummaryResponse {
  runId: string;
  red: {
    rps: number;
    errorsPercent: number;
    p95DurationMs: number;
  };
  slo: {
    availability: number;
    latencyP95Ms: number;
  };
  updatedAt?: string;
}

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

type RequestOptions = Omit<RequestInit, 'method'> & { method?: HttpMethod };

export async function req<T>(path: string, init: RequestOptions = {}): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers = new Headers(init.headers ?? {});
  const body = init.body;

  if (body && !(body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(url, {
    ...init,
    headers,
    body,
    cache: 'no-store',
    credentials: init.credentials ?? 'include',
  });

  const contentType = response.headers.get('content-type') ?? '';
  let payload: unknown = null;

  if (contentType.includes('application/json')) {
    payload = await response.json();
  } else {
    const text = await response.text();
    payload = text.length > 0 ? text : null;
  }

  if (!response.ok) {
    const message =
      typeof payload === 'object' && payload !== null && 'message' in payload
        ? String((payload as { message: unknown }).message)
        : `Request failed with status ${response.status}`;
    throw new ApiError(response.status, message, payload);
  }

  return payload as T;
}

export async function uploadArtifact(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  return req<UploadResponse>('/upload', {
    method: 'POST',
    body: formData,
  });
}

export async function prepareStart(runId: string): Promise<PrepareStatusResponse> {
  const params = new URLSearchParams({ runId });
  return req<PrepareStatusResponse>(`/prepare/start?${params.toString()}`, {
    method: 'POST',
  });
}

export async function prepareStatus(runId: string): Promise<PrepareStatusResponse> {
  const params = new URLSearchParams({ runId });
  return req<PrepareStatusResponse>(`/prepare/status?${params.toString()}`);
}

export async function deployStart(runId: string, env: string = 'dev'): Promise<DeployStatusResponse> {
  const params = new URLSearchParams({ runId, env });
  return req<DeployStatusResponse>(`/deploy/start?${params.toString()}`, {
    method: 'POST',
  });
}

export async function deployStatus(runId: string, env: string = 'dev'): Promise<DeployStatusResponse> {
  const params = new URLSearchParams({ runId, env });
  return req<DeployStatusResponse>(`/deploy/status?${params.toString()}`);
}

export async function monitorSummary(runId: string): Promise<MonitorSummaryResponse> {
  const params = new URLSearchParams({ runId });
  return req<MonitorSummaryResponse>(`/monitor/summary?${params.toString()}`);
}
