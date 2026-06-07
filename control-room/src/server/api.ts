import { mkdirSync, existsSync } from 'node:fs';
import { resolve, isAbsolute } from 'node:path';
import { spawn } from 'node:child_process';
import express from 'express';
import { z } from 'zod';
import { createDatabase } from './database';
import { ControlRoomRepository } from './repository';
import { scanProject, scanFiles } from './scanner/project-scanner';
import { ActionRunner } from './actions/action-runner';
import { CommandExecutor } from './actions/command-executor';
import { createConfig } from './config';
import { ACTIONS } from '@shared/actions';

const ALLOWED_ORIGINS = new Set([
  'http://127.0.0.1:4173',
  'http://localhost:4173',
  'http://127.0.0.1:4174',
  'http://localhost:4174',
  'https://sarlls.stricklandai.com',
  'http://sarlls.stricklandai.com',
]);

const LOCAL_HOSTS = new Set([
  '127.0.0.1', 'localhost', '::1',
  'sarlls.stricklandai.com',
]);

const WorkflowBody = z.object({
  status: z.enum([
    'passed',
    'failed',
    'waiting',
    'blocked',
    'running',
    'cancelled',
    'skipped',
  ]),
  notes: z.string().default(''),
  evidencePath: z.string().optional(),
  recordedBy: z.string().optional(),
});

const ActionBody = z.object({
  confirmed: z.boolean().default(false),
});

const RevealBody = z.object({
  path: z.string().min(1),
});

function hostIsLocal(host: string | undefined) {
  if (!host) return false;
  const value = host.startsWith('[')
    ? host.slice(1, host.indexOf(']'))
    : host.split(':')[0] ?? '';
  return LOCAL_HOSTS.has(value);
}

function originIsAllowed(origin: string) {
  try {
    const parsed = new URL(origin);
    return ALLOWED_ORIGINS.has(`${parsed.protocol}//${parsed.host}`);
  } catch {
    return false;
  }
}

function resolveWithinRoot(root: string, candidate: string) {
  const resolved = isAbsolute(candidate) ? resolve(candidate) : resolve(root, candidate);
  const rootResolved = resolve(root);
  const normalized = resolved.toLowerCase();
  const normalizedRoot = rootResolved.toLowerCase();
  if (normalized !== normalizedRoot && !normalized.startsWith(`${normalizedRoot}\\`)) {
    return null;
  }
  return resolved;
}

function revealInExplorer(path: string) {
  spawn('explorer.exe', [`/select,${path}`], {
    detached: true,
    stdio: 'ignore',
    windowsHide: true,
  }).unref();
}

export function createApi(opts?: { root?: string; databasePath?: string }) {
  const config = createConfig(opts?.root);
  const dbPath = opts?.databasePath ?? config.databasePath;

  if (dbPath !== ':memory:') {
    mkdirSync(resolve(dbPath, '..'), { recursive: true });
  }

  const db = createDatabase(dbPath);
  const repository = new ControlRoomRepository(db);
  repository.markInterruptedRuns();

  const executor = new CommandExecutor();
  const runner = new ActionRunner(executor, repository, config);

  const app = express();
  app.use(express.json());

  // Local-only boundary: reject non-local hosts and foreign origins.
  app.use((req, res, next) => {
    if (!hostIsLocal(req.headers.host)) {
      res.status(403).json({ error: 'Forbidden host' });
      return;
    }

    const origin = req.headers.origin;
    if (typeof origin === 'string' && !originIsAllowed(origin)) {
      res.status(403).json({ error: 'Forbidden origin' });
      return;
    }

    if (typeof origin === 'string') {
      res.setHeader('Access-Control-Allow-Origin', origin);
      res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    }

    if (req.method === 'OPTIONS') {
      res.status(204).end();
      return;
    }

    next();
  });

  // Health
  app.get('/api/health', (_req, res) => {
    res.json({ status: 'ok', service: 'safeswitch-control-room' });
  });

  // Project snapshot
  app.get('/api/project', async (_req, res) => {
    try {
      const snapshot = await scanProject(config.root, repository);
      res.json(snapshot);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      res.status(500).json({ summary: 'Failed to scan project', technicalDetails: message });
    }
  });

  // Workflows
  app.get('/api/workflows', (_req, res) => {
    res.json(repository.listWorkflows());
  });

  app.put('/api/workflows/:key', (req, res) => {
    const parsed = WorkflowBody.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ error: 'Invalid body', details: parsed.error.issues });
      return;
    }
    repository.upsertWorkflow({
      key: req.params.key!,
      status: parsed.data.status,
      notes: parsed.data.notes,
      evidencePath: parsed.data.evidencePath,
      recordedBy: parsed.data.recordedBy,
      updatedAt: new Date().toISOString(),
    });
    res.json({ ok: true });
  });

  // Activity
  app.get('/api/activity', (_req, res) => {
    res.json(repository.listActivity());
  });

  // Actions catalog
  app.get('/api/actions', (_req, res) => {
    const actions = ACTIONS.map((a) => ({
      ...a,
      running: runner.isRunning(a.id),
    }));
    res.json(actions);
  });

  // Start action
  app.post('/api/actions/:actionId/runs', async (req, res) => {
    const { actionId } = req.params;
    const parsed = ActionBody.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ error: 'Invalid body', details: parsed.error.issues });
      return;
    }
    try {
      const run = await runner.start(actionId!, parsed.data.confirmed);
      res.status(201).json(run);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      if (message.includes('confirmation')) {
        res.status(409).json({ error: message });
      } else if (message.includes('already running')) {
        res.status(409).json({ error: message });
      } else if (message.includes('Unknown action')) {
        res.status(404).json({ error: message });
      } else {
        res.status(500).json({ summary: 'Action failed to start', technicalDetails: message });
      }
    }
  });

  // Get action run
  app.get('/api/action-runs/:runId', (req, res) => {
    const run = repository.getActionRun(req.params.runId!);
    if (!run) {
      res.status(404).json({ error: 'Run not found' });
      return;
    }
    res.json(run);
  });

  // Cancel action
  app.post('/api/action-runs/:runId/cancel', (req, res) => {
    const run = repository.getActionRun(req.params.runId!);
    if (!run) {
      res.status(404).json({ error: 'Run not found' });
      return;
    }
    const cancelled = runner.cancel(run.actionId);
    res.json({ ok: cancelled });
  });

  // Files
  app.get('/api/files', async (_req, res) => {
    try {
      const files = await scanFiles(config.root);
      res.json(files);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      res.status(500).json({ summary: 'Failed to scan files', technicalDetails: message });
    }
  });

  const revealHandler = (req: express.Request, res: express.Response) => {
    const body = RevealBody.safeParse(req.body);
    const rawPath = typeof req.params.fileId === 'string'
      ? req.params.fileId
      : body.success
        ? body.data.path
        : undefined;

    if (!rawPath) {
      res.status(400).json({ error: 'Path required' });
      return;
    }

    const resolved = resolveWithinRoot(config.root, rawPath);
    if (!resolved) {
      res.status(403).json({ error: 'Path outside project root' });
      return;
    }

    if (!existsSync(resolved)) {
      res.status(404).json({ error: 'File not found' });
      return;
    }

    try {
      revealInExplorer(resolved);
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      res.status(500).json({ summary: 'Failed to reveal file', technicalDetails: message });
      return;
    }

    res.json({ ok: true, path: resolved });
  };

  app.post('/api/files/reveal', revealHandler);
  app.post('/api/files/:fileId/reveal', revealHandler);

  // 3D model — serve the GLB from production/
  app.get('/api/model/pcb', (_req, res) => {
    const glbPath = resolve(config.root, 'production', 'ESP32_Simple_IoT_3D.glb');
    if (!existsSync(glbPath)) {
      res.status(404).json({ error: '3D model not found' });
      return;
    }
    res.setHeader('Content-Type', 'model/gltf-binary');
    res.setHeader('Cache-Control', 'public, max-age=3600');
    res.sendFile(glbPath);
  });

  // Settings
  app.get('/api/settings', (_req, res) => {
    res.json({
      root: config.root,
      kicadCli: config.kicadCli,
      kicadPython: config.kicadPython,
      arduinoCli: config.arduinoCli,
      gradle: config.gradle,
      databasePath: dbPath,
    });
  });

  return app;
}
