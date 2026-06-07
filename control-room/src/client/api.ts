import type { ActionRun, ProjectSnapshot, WorkflowRecord } from '@shared/types';
import type { FileInfo } from '@server/scanner/documents';

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
  });
  const body = await response.json();
  if (!response.ok) {
    throw new Error(
      body.summary ?? body.error ?? `Request failed: ${response.status}`
    );
  }
  return body as T;
}

export const fetchProject = () => api<ProjectSnapshot>('/api/project');

export const fetchWorkflows = () => api<WorkflowRecord[]>('/api/workflows');

export const updateWorkflow = (
  key: string,
  data: { status: string; notes: string; recordedBy?: string; evidencePath?: string }
) => api('/api/workflows/' + key, { method: 'PUT', body: JSON.stringify(data) });

export const fetchActivity = () =>
  api<Array<Record<string, string>>>('/api/activity');

export const fetchActions = () =>
  api<Array<{ id: string; label: string; description: string; mutatesFiles: boolean; cancellable: boolean; running: boolean }>>('/api/actions');

export const startAction = (actionId: string, confirmed = false) =>
  api<ActionRun>(`/api/actions/${actionId}/runs`, {
    method: 'POST',
    body: JSON.stringify({ confirmed }),
  });

export const fetchActionRun = (runId: string) =>
  api<ActionRun>(`/api/action-runs/${runId}`);

export const cancelActionRun = (runId: string) =>
  api(`/api/action-runs/${runId}/cancel`, { method: 'POST' });

export const fetchFiles = () => api<FileInfo[]>('/api/files');

export const revealFile = (path: string) =>
  api(`/api/files/${encodeURIComponent(path)}/reveal`, { method: 'POST' });

export const fetchSettings = () => api<Record<string, string>>('/api/settings');
