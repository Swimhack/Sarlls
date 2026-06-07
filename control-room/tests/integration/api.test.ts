// @vitest-environment node
import { resolve } from 'node:path';
import { spawn } from 'node:child_process';
import { beforeAll, afterAll, describe, expect, it } from 'vitest';

const serverEntry = resolve(process.cwd(), 'node_modules/tsx/dist/cli.mjs');
const port = 4175;
const baseUrl = `http://127.0.0.1:${port}`;

let server: ReturnType<typeof spawn>;

async function sleep(ms: number) {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForServer() {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      const response = await fetch(`${baseUrl}/api/health`);
      if (response.ok) return;
    } catch {
      // keep waiting
    }
    await sleep(250);
  }
  throw new Error('Control room server did not start');
}

async function requestJson(
  path: string,
  init?: { method?: string; headers?: Record<string, string>; body?: unknown }
) {
  const response = await fetch(`${baseUrl}${path}`, {
    method: init?.method ?? 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    body: init?.body === undefined ? undefined : JSON.stringify(init.body),
  });
  return {
    status: response.status,
    body: await response.json(),
  };
}

beforeAll(async () => {
  server = spawn(process.execPath, [serverEntry, 'src/server/index.ts'], {
    cwd: process.cwd(),
    env: { ...process.env, CONTROL_ROOM_PORT: String(port) },
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  await waitForServer();
});

afterAll(() => {
  server?.kill('SIGTERM');
});

describe('control room API', () => {
  it('serves the project snapshot and readiness state', async () => {
    const response = await requestJson('/api/project');

    expect(response.status).toBe(200);
    expect((response.body as { readiness: { rev2ReadyToOrder: boolean; nextAction: { id: string } } }).readiness.rev2ReadyToOrder).toBe(false);
    expect((response.body as { readiness: { nextAction: { id: string } } }).readiness.nextAction.id).toBe('usb_approval');
  });

  it('rejects foreign origins', async () => {
    const response = await requestJson('/api/health', {
      headers: { Origin: 'https://example.com' },
    });

    expect(response.status).toBe(403);
  });

  it('requires confirmation before changing production files', async () => {
    const response = await requestJson('/api/actions/regenerate-rev2/runs', {
      method: 'POST',
      body: { confirmed: false },
    });

    expect(response.status).toBe(409);
  });

  it('rejects revealing paths outside the repository', async () => {
    const response = await requestJson('/api/files/reveal', {
      method: 'POST',
      body: { path: '../../Windows/System32' },
    });

    expect(response.status).toBe(403);
  });
});
