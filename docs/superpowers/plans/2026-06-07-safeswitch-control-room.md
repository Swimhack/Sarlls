# SafeSwitch Control Room Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fully wired local Mission Control dashboard that reads the real Sarlls workspace, runs approved engineering actions, persists management workflows, and accurately reports readiness.

**Architecture:** Create an isolated `control-room/` TypeScript application so the existing Android `app/` module and PCB sources remain untouched. A localhost Node/Express API uses built-in `node:sqlite`, a strict action allowlist, and artifact scanners; a React/Vite client consumes that API and presents the approved owner-first Mission Control experience.

**Tech Stack:** Node.js 22, TypeScript, React 19, Vite, Express, built-in `node:sqlite`, Zod, Lucide React, Vitest, Testing Library, Supertest, Playwright.

---

## Scope And Constraints

- The dashboard binds to `127.0.0.1` only.
- Browser requests cannot supply arbitrary shell commands.
- File-changing actions require `confirmed: true`.
- Physical hardware results are recorded manually and never inferred from software checks.
- Existing Android, PCB, firmware, and user-created files are not reverted.
- Existing unfinished Supabase/Next draft files under `specs/`, `supabase/`, `lib/types/pcb.ts`, and `__tests__/` remain legacy and are not used by the new local application.
- Application state is stored under ignored `.control-room/`.

## Planned File Structure

```text
control-room/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── playwright.config.ts
├── index.html
├── src/
│   ├── shared/
│   │   ├── types.ts
│   │   ├── gates.ts
│   │   └── actions.ts
│   ├── server/
│   │   ├── config.ts
│   │   ├── database.ts
│   │   ├── repository.ts
│   │   ├── api.ts
│   │   ├── index.ts
│   │   ├── scanner/
│   │   │   ├── drc.ts
│   │   │   ├── csv.ts
│   │   │   ├── gerber.ts
│   │   │   ├── documents.ts
│   │   │   └── project-scanner.ts
│   │   ├── readiness/
│   │   │   └── derive-readiness.ts
│   │   └── actions/
│   │       ├── command-catalog.ts
│   │       ├── command-executor.ts
│   │       ├── action-runner.ts
│   │       └── output-parsers.ts
│   └── client/
│       ├── main.tsx
│       ├── app.tsx
│       ├── api.ts
│       ├── styles.css
│       ├── components/
│       │   ├── app-shell.tsx
│       │   ├── status-mark.tsx
│       │   ├── gate-list.tsx
│       │   ├── action-button.tsx
│       │   ├── action-run-panel.tsx
│       │   └── workflow-editor.tsx
│       └── pages/
│           ├── mission-control-page.tsx
│           ├── ordering-page.tsx
│           ├── workstream-page.tsx
│           ├── files-page.tsx
│           ├── activity-page.tsx
│           └── settings-page.tsx
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
scripts/
└── build_rev2_release.ps1
```

---

### Task 1: Scaffold The Isolated Full-Stack Application

**Files:**
- Create: `control-room/package.json`
- Create: `control-room/tsconfig.json`
- Create: `control-room/vite.config.ts`
- Create: `control-room/index.html`
- Create: `control-room/src/client/main.tsx`
- Create: `control-room/src/client/app.tsx`
- Create: `control-room/src/server/index.ts`
- Modify: `.gitignore`

- [ ] **Step 1: Add ignored runtime directories**

Add:

```gitignore
/.control-room/
/.superpowers/
/control-room/node_modules/
/control-room/dist/
/control-room/coverage/
/control-room/test-results/
/control-room/playwright-report/
```

- [ ] **Step 2: Create the package manifest**

Create `control-room/package.json`:

```json
{
  "name": "safeswitch-control-room",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "concurrently -k \"npm:dev:server\" \"npm:dev:client\"",
    "dev:server": "tsx watch src/server/index.ts",
    "dev:client": "vite",
    "build": "tsc --noEmit && vite build",
    "start": "tsx src/server/index.ts",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:e2e": "playwright test",
    "test:all": "npm run test && npm run build && npm run test:e2e"
  },
  "dependencies": {
    "adm-zip": "^0.5.16",
    "express": "^5.1.0",
    "lucide-react": "^0.468.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "zod": "^3.24.0"
  },
  "devDependencies": {
    "@playwright/test": "^1.52.0",
    "@testing-library/jest-dom": "^6.6.0",
    "@testing-library/react": "^16.1.0",
    "@types/adm-zip": "^0.5.7",
    "@types/express": "^5.0.0",
    "@types/node": "^22.10.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^4.3.0",
    "concurrently": "^9.1.0",
    "jsdom": "^25.0.0",
    "supertest": "^7.0.0",
    "tsx": "^4.19.0",
    "typescript": "^5.7.0",
    "vite": "^6.0.0",
    "vitest": "^2.1.0"
  }
}
```

- [ ] **Step 3: Create TypeScript and Vite configuration**

Create `control-room/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "types": ["node", "vitest/globals"],
    "baseUrl": ".",
    "paths": {
      "@shared/*": ["src/shared/*"],
      "@server/*": ["src/server/*"],
      "@client/*": ["src/client/*"]
    }
  },
  "include": ["src", "tests", "vite.config.ts", "playwright.config.ts"]
}
```

Create `control-room/vite.config.ts`:

```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  root: '.',
  server: {
    host: '127.0.0.1',
    port: 4173,
    proxy: { '/api': 'http://127.0.0.1:4174' }
  },
  build: { outDir: 'dist/client' },
  test: {
    environment: 'jsdom',
    setupFiles: ['tests/setup.ts']
  }
});
```

- [ ] **Step 4: Create bootable client and server shells**

Create `control-room/src/client/main.tsx`:

```tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './app';
import './styles.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode><App /></StrictMode>
);
```

Create `control-room/src/client/app.tsx`:

```tsx
export function App() {
  return <main><h1>SafeSwitch Control Room</h1></main>;
}
```

Create `control-room/src/server/index.ts`:

```ts
import express from 'express';

const app = express();
app.use(express.json());
app.get('/api/health', (_request, response) => {
  response.json({ status: 'ok', service: 'safeswitch-control-room' });
});

app.listen(4174, '127.0.0.1', () => {
  console.log('SafeSwitch API listening on http://127.0.0.1:4174');
});
```

- [ ] **Step 5: Install dependencies and verify the shell**

Run:

```powershell
cd control-room
npm.cmd install
npm.cmd run build
```

Expected: dependencies install and Vite produces `control-room/dist/client`.

- [ ] **Step 6: Commit**

```powershell
git add .gitignore control-room
git commit -m "feat: scaffold SafeSwitch control room"
```

---

### Task 2: Define Shared Domain Types And Gate Catalog

**Files:**
- Create: `control-room/src/shared/types.ts`
- Create: `control-room/src/shared/gates.ts`
- Create: `control-room/src/shared/actions.ts`
- Create: `control-room/tests/unit/gates.test.ts`
- Create: `control-room/tests/setup.ts`

- [ ] **Step 1: Write failing readiness tests**

Create `control-room/tests/unit/gates.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { deriveReadiness } from '@server/readiness/derive-readiness';
import type { GateResult } from '@shared/types';

const pass = (id: string): GateResult => ({
  id, label: id, status: 'passed', source: 'automatic', blocking: true
});

describe('deriveReadiness', () => {
  it('keeps Rev2 blocked while a manufacturer gate is waiting', () => {
    const result = deriveReadiness([
      pass('drc'),
      pass('bom_cpl'),
      pass('gerber_zip'),
      { id: 'usb_approval', label: 'USB approval', status: 'waiting', source: 'human', blocking: true }
    ]);

    expect(result.rev2ReadyToOrder).toBe(false);
    expect(result.nextAction?.id).toBe('usb_approval');
  });

  it('marks Rev2 ready only when every required gate passes', () => {
    const required = ['drc', 'bom_cpl', 'gerber_zip', 'usb_approval', 'sw1', 'sw2', 'j2', 'dfm_preview', 'manufacturer_warnings'];
    const result = deriveReadiness(required.map(pass));
    expect(result.rev2ReadyToOrder).toBe(true);
    expect(result.phase).toBe('controller_ready_to_order');
  });
});
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
cd control-room
npm.cmd test -- gates.test.ts
```

Expected: FAIL because shared types and `deriveReadiness` do not exist.

- [ ] **Step 3: Define the shared types**

Create `control-room/src/shared/types.ts` with:

```ts
export type ResultStatus = 'passed' | 'failed' | 'waiting' | 'blocked' | 'running' | 'cancelled' | 'skipped';
export type GateSource = 'automatic' | 'human';

export interface GateResult {
  id: string;
  label: string;
  status: ResultStatus;
  source: GateSource;
  blocking: boolean;
  summary?: string;
  technicalDetails?: string;
  updatedAt?: string;
}

export interface ReadinessSummary {
  phase: 'engineering_prototype' | 'controller_pre_fabrication' | 'controller_ready_to_order' | 'controller_ordered' | 'controller_bring_up' | 'controller_validated' | 'automotive_integration' | 'bench_validated' | 'ready_for_vehicle_test';
  rev2ReadyToOrder: boolean;
  readyForVehicleTest: boolean;
  completedRequired: number;
  totalRequired: number;
  nextAction?: GateResult;
  blockers: GateResult[];
}

export interface ProjectSnapshot {
  scannedAt: string;
  readiness: ReadinessSummary;
  gates: GateResult[];
  workstreams: WorkstreamSummary[];
  recentRuns: ActionRun[];
}

export interface WorkstreamSummary {
  id: string;
  label: string;
  summary: string;
  gates: GateResult[];
}

export interface WorkflowRecord {
  key: string;
  status: ResultStatus;
  notes: string;
  evidencePath?: string;
  recordedBy?: string;
  updatedAt: string;
}

export interface ActionRun {
  id: string;
  actionId: string;
  status: ResultStatus;
  summary: string;
  technicalOutput?: string;
  startedAt: string;
  finishedAt?: string;
}
```

- [ ] **Step 4: Define gate and action catalogs**

Create `control-room/src/shared/gates.ts`:

```ts
export const REV2_ORDER_GATE_IDS = [
  'drc', 'bom_cpl', 'gerber_zip', 'usb_approval', 'sw1', 'sw2', 'j2',
  'dfm_preview', 'manufacturer_warnings'
] as const;

export const VEHICLE_GATE_IDS = [
  'controller_hardware', 'app_device_control', 'protected_12v',
  'contactor_operation', 'bench_safety', 'safety_blockers'
] as const;
```

Create `control-room/src/shared/actions.ts`:

```ts
export interface ActionDefinition {
  id: string;
  label: string;
  description: string;
  mutatesFiles: boolean;
  cancellable: boolean;
}

export const ACTIONS: ActionDefinition[] = [
  { id: 'run-all-checks', label: 'Run all checks', description: 'Check PCB files, firmware, and Android app.', mutatesFiles: false, cancellable: true },
  { id: 'run-drc', label: 'Run PCB check', description: 'Run KiCad DRC and the blocking gate.', mutatesFiles: false, cancellable: true },
  { id: 'compile-production-firmware', label: 'Compile production firmware', description: 'Compile the WiFi controller firmware.', mutatesFiles: false, cancellable: true },
  { id: 'compile-test-firmware', label: 'Compile hardware-test firmware', description: 'Compile the hardware test image with huge_app.', mutatesFiles: false, cancellable: true },
  { id: 'run-android-tests', label: 'Run Android tests', description: 'Run the Gradle test task.', mutatesFiles: false, cancellable: true },
  { id: 'regenerate-rev2', label: 'Regenerate Rev2 manufacturing files', description: 'Replace production PCB and manufacturing artifacts.', mutatesFiles: true, cancellable: false }
];
```

- [ ] **Step 5: Implement minimal readiness derivation**

Create `control-room/src/server/readiness/derive-readiness.ts`:

```ts
import { REV2_ORDER_GATE_IDS, VEHICLE_GATE_IDS } from '@shared/gates';
import type { GateResult, ReadinessSummary } from '@shared/types';

export function deriveReadiness(gates: GateResult[]): ReadinessSummary {
  const byId = new Map(gates.map((gate) => [gate.id, gate]));
  const required = REV2_ORDER_GATE_IDS.map((id) => byId.get(id)).filter(Boolean) as GateResult[];
  const blockers = required.filter((gate) => gate.status !== 'passed');
  const vehicleReady = VEHICLE_GATE_IDS.every((id) => byId.get(id)?.status === 'passed');
  const rev2Ready = required.length === REV2_ORDER_GATE_IDS.length && blockers.length === 0;

  return {
    phase: vehicleReady ? 'ready_for_vehicle_test' : rev2Ready ? 'controller_ready_to_order' : 'controller_pre_fabrication',
    rev2ReadyToOrder: rev2Ready,
    readyForVehicleTest: vehicleReady,
    completedRequired: required.filter((gate) => gate.status === 'passed').length,
    totalRequired: REV2_ORDER_GATE_IDS.length,
    nextAction: blockers[0],
    blockers
  };
}
```

- [ ] **Step 6: Run tests and commit**

Run:

```powershell
npm.cmd test -- gates.test.ts
```

Expected: PASS.

```powershell
git add control-room/src/shared control-room/src/server/readiness control-room/tests
git commit -m "feat: define control room readiness model"
```

---

### Task 3: Implement Real Project Artifact Parsers

**Files:**
- Create: `control-room/src/server/scanner/drc.ts`
- Create: `control-room/src/server/scanner/csv.ts`
- Create: `control-room/src/server/scanner/gerber.ts`
- Create: `control-room/src/server/scanner/documents.ts`
- Create: `control-room/tests/unit/scanner.test.ts`

- [ ] **Step 1: Write failing parser tests against real fixtures**

Create `control-room/tests/unit/scanner.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { parseDrcReport } from '@server/scanner/drc';
import { parseBom, parseCpl } from '@server/scanner/csv';
import { inspectGerberZip } from '@server/scanner/gerber';

describe('project scanners', () => {
  it('recognizes the current production DRC result', async () => {
    const result = await parseDrcReport('../production/drc_report.json');
    expect(result.blocking).toBe(0);
    expect(result.approvedJ1EdgeErrors).toBe(26);
    expect(result.warnings).toBe(11);
  });

  it('counts the production BOM and CPL', async () => {
    expect((await parseBom('../production/ESP32_Simple_IoT_BOM.csv')).lineItems).toBe(20);
    expect((await parseCpl('../production/ESP32_Simple_IoT_CPL.csv')).placements).toBe(28);
  });

  it('validates the Rev2 Gerber package', async () => {
    const result = await inspectGerberZip('../production/Sarlls_IoT_Switch_Rev2_JLCPCB.zip');
    expect(result.valid).toBe(true);
    expect(result.fileCount).toBe(11);
  });
});
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
npm.cmd test -- scanner.test.ts
```

Expected: FAIL because parsers do not exist.

- [ ] **Step 3: Implement DRC parsing**

Create `control-room/src/server/scanner/drc.ts`:

```ts
import { readFile } from 'node:fs/promises';

export async function parseDrcReport(path: string) {
  const report = JSON.parse(await readFile(path, 'utf8')) as {
    unconnected_items?: unknown[];
    violations?: Array<{ type?: string; severity?: string; items?: Array<{ description?: string; pos?: { x?: number; y?: number } }> }>;
  };
  const violations = report.violations ?? [];
  const errors = violations.filter((item) => item.severity === 'error');
  const approved = errors.filter((item) =>
    item.type === 'copper_edge_clearance' &&
    (item.items ?? []).every((entry) =>
      entry.description?.includes('Edge.Cuts') ||
      entry.description?.includes('of J1') ||
      (
        entry.description?.includes('Track [') &&
        Math.abs((entry.pos?.x ?? 999) - 0.32) < 0.01 &&
        (entry.pos?.y ?? -999) >= 25.5 &&
        (entry.pos?.y ?? 999) <= 34.5
      )
    )
  );
  return {
    blocking: (report.unconnected_items?.length ?? 0) + errors.length - approved.length,
    approvedJ1EdgeErrors: approved.length,
    warnings: violations.filter((item) => item.severity === 'warning').length
  };
}
```

- [ ] **Step 4: Implement BOM/CPL and ZIP parsing**

Create `control-room/src/server/scanner/csv.ts` using a quoted-CSV row parser that counts non-header records and validates required headers:

```ts
import { readFile } from 'node:fs/promises';

function rows(text: string) {
  return text.trim().split(/\r?\n/).filter(Boolean);
}

export async function parseBom(path: string) {
  const data = rows(await readFile(path, 'utf8'));
  const headers = data[0] ?? '';
  return { lineItems: Math.max(0, data.length - 1), valid: headers.includes('Designator') && headers.includes('LCSC Part Number') };
}

export async function parseCpl(path: string) {
  const data = rows(await readFile(path, 'utf8'));
  const headers = data[0] ?? '';
  return { placements: Math.max(0, data.length - 1), valid: headers.includes('Mid X') && headers.includes('Rotation') };
}
```

Create `control-room/src/server/scanner/gerber.ts` using `adm-zip`:

```ts
import AdmZip from 'adm-zip';

const REQUIRED = new Set([
  'ESP32_Simple_IoT-F_Cu.gtl',
  'ESP32_Simple_IoT-B_Cu.gbl',
  'ESP32_Simple_IoT-F_Mask.gts',
  'ESP32_Simple_IoT-B_Mask.gbs',
  'ESP32_Simple_IoT-F_Paste.gtp',
  'ESP32_Simple_IoT-F_Silkscreen.gto',
  'ESP32_Simple_IoT-B_Silkscreen.gbo',
  'ESP32_Simple_IoT-Edge_Cuts.gm1',
  'ESP32_Simple_IoT-PTH.drl',
  'ESP32_Simple_IoT-NPTH.drl',
  'ESP32_Simple_IoT-job.gbrjob'
]);

export async function inspectGerberZip(path: string) {
  const names = new AdmZip(path).getEntries().filter((entry) => !entry.isDirectory).map((entry) => entry.entryName);
  const missing = [...REQUIRED].filter((name) => !names.includes(name));
  const unexpected = names.filter((name) => !REQUIRED.has(name));
  return { valid: missing.length === 0 && unexpected.length === 0, fileCount: names.length, missing, unexpected };
}
```

- [ ] **Step 5: Implement document-presence scanning**

Create `control-room/src/server/scanner/documents.ts`:

```ts
import { access, stat } from 'node:fs/promises';

export async function inspectFile(path: string, authoritative = true) {
  try {
    const details = await stat(path);
    return { path, authoritative, exists: true, size: details.size, modifiedAt: details.mtime.toISOString() };
  } catch {
    return { path, authoritative, exists: false, size: 0 };
  }
}
```

- [ ] **Step 6: Run parser tests and commit**

Run:

```powershell
npm.cmd test -- scanner.test.ts
```

Expected: PASS against current production files.

```powershell
git add control-room/src/server/scanner control-room/tests/unit/scanner.test.ts
git commit -m "feat: scan real SafeSwitch project artifacts"
```

---

### Task 4: Add SQLite Persistence And Activity History

**Files:**
- Create: `control-room/src/server/config.ts`
- Create: `control-room/src/server/database.ts`
- Create: `control-room/src/server/repository.ts`
- Create: `control-room/tests/unit/repository.test.ts`

- [ ] **Step 1: Write failing repository tests**

Create `control-room/tests/unit/repository.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { createDatabase } from '@server/database';
import { ControlRoomRepository } from '@server/repository';

describe('ControlRoomRepository', () => {
  it('persists workflow records and activity events', () => {
    const repository = new ControlRoomRepository(createDatabase(':memory:'));
    repository.upsertWorkflow({ key: 'usb_approval', status: 'passed', notes: 'Approved', updatedAt: new Date().toISOString() });
    expect(repository.getWorkflow('usb_approval')?.status).toBe('passed');
    expect(repository.listActivity()[0]?.eventType).toBe('workflow.updated');
  });
});
```

- [ ] **Step 2: Run test and verify failure**

Run:

```powershell
npm.cmd test -- repository.test.ts
```

Expected: FAIL because the database and repository do not exist.

- [ ] **Step 3: Create and migrate the local database**

Create `control-room/src/server/config.ts`:

```ts
import { resolve } from 'node:path';

export function createConfig(root = resolve('..')) {
  return {
    root,
    stateDir: resolve(root, '.control-room'),
    databasePath: resolve(root, '.control-room', 'control-room.db'),
    kicadPython: process.env.KICAD_PYTHON ?? 'C:\\Users\\james\\AppData\\Local\\Programs\\KiCad\\9.0\\bin\\python.exe',
    kicadCli: process.env.KICAD_CLI ?? 'C:\\Users\\james\\AppData\\Local\\Programs\\KiCad\\9.0\\bin\\kicad-cli.exe',
    arduinoCli: process.env.ARDUINO_CLI ?? 'C:\\Users\\james\\bin\\arduino-cli.exe',
    gradle: resolve(root, 'gradlew.bat')
  };
}
```

Tool paths are visible in Settings and may be overridden only by server
environment variables, never browser request data.

Create `control-room/src/server/database.ts`:

```ts
import { DatabaseSync } from 'node:sqlite';

export function createDatabase(path: string) {
  const database = new DatabaseSync(path);
  database.exec(`
    PRAGMA journal_mode = WAL;
    CREATE TABLE IF NOT EXISTS workflows (
      key TEXT PRIMARY KEY,
      status TEXT NOT NULL,
      notes TEXT NOT NULL DEFAULT '',
      evidence_path TEXT,
      recorded_by TEXT,
      updated_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS action_runs (
      id TEXT PRIMARY KEY,
      action_id TEXT NOT NULL,
      status TEXT NOT NULL,
      summary TEXT NOT NULL,
      technical_output TEXT,
      started_at TEXT NOT NULL,
      finished_at TEXT
    );
    CREATE TABLE IF NOT EXISTS activity (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      event_type TEXT NOT NULL,
      summary TEXT NOT NULL,
      outcome TEXT NOT NULL,
      details TEXT,
      created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS settings (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL
    );
  `);
  return database;
}
```

- [ ] **Step 4: Implement repository methods**

Create `control-room/src/server/repository.ts` with methods:

```ts
import type { DatabaseSync } from 'node:sqlite';
import type { WorkflowRecord } from '@shared/types';

export class ControlRoomRepository {
  constructor(private readonly database: DatabaseSync) {}

  upsertWorkflow(record: WorkflowRecord) {
    this.database.prepare(`
      INSERT INTO workflows (key, status, notes, evidence_path, recorded_by, updated_at)
      VALUES (?, ?, ?, ?, ?, ?)
      ON CONFLICT(key) DO UPDATE SET
        status=excluded.status, notes=excluded.notes, evidence_path=excluded.evidence_path,
        recorded_by=excluded.recorded_by, updated_at=excluded.updated_at
    `).run(record.key, record.status, record.notes, record.evidencePath ?? null, record.recordedBy ?? null, record.updatedAt);
    this.addActivity('workflow.updated', `${record.key} changed to ${record.status}`, record.status);
  }

  getWorkflow(key: string) {
    return this.database.prepare('SELECT key, status, notes, evidence_path AS evidencePath, recorded_by AS recordedBy, updated_at AS updatedAt FROM workflows WHERE key = ?').get(key) as WorkflowRecord | undefined;
  }

  listWorkflows() {
    return this.database.prepare('SELECT key, status, notes, evidence_path AS evidencePath, recorded_by AS recordedBy, updated_at AS updatedAt FROM workflows ORDER BY key').all() as WorkflowRecord[];
  }

  addActivity(eventType: string, summary: string, outcome: string, details?: string) {
    this.database.prepare('INSERT INTO activity (event_type, summary, outcome, details, created_at) VALUES (?, ?, ?, ?, ?)')
      .run(eventType, summary, outcome, details ?? null, new Date().toISOString());
  }

  listActivity() {
    return this.database.prepare('SELECT event_type AS eventType, summary, outcome, details, created_at AS createdAt FROM activity ORDER BY id DESC').all() as Array<Record<string, string>>;
  }
}
```

- [ ] **Step 5: Run tests and commit**

Run:

```powershell
npm.cmd test -- repository.test.ts
```

Expected: PASS.

```powershell
git add control-room/src/server control-room/tests/unit/repository.test.ts
git commit -m "feat: persist control room workflows and activity"
```

---

### Task 5: Build The Project Scanner And Readiness Service

**Files:**
- Create: `control-room/src/server/scanner/project-scanner.ts`
- Modify: `control-room/src/server/readiness/derive-readiness.ts`
- Create: `control-room/tests/integration/project-scanner.test.ts`

- [ ] **Step 1: Write the failing real-workspace snapshot test**

Create `control-room/tests/integration/project-scanner.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { scanProject } from '@server/scanner/project-scanner';
import { createDatabase } from '@server/database';
import { ControlRoomRepository } from '@server/repository';

describe('scanProject', () => {
  it('returns real automatic gates and waiting human gates', async () => {
    const repository = new ControlRoomRepository(createDatabase(':memory:'));
    const snapshot = await scanProject('..', repository);
    expect(snapshot.gates.find((gate) => gate.id === 'drc')?.status).toBe('passed');
    expect(snapshot.gates.find((gate) => gate.id === 'usb_approval')?.status).toBe('waiting');
    expect(snapshot.readiness.rev2ReadyToOrder).toBe(false);
  });
});
```

- [ ] **Step 2: Run the test and verify failure**

Run:

```powershell
npm.cmd test -- project-scanner.test.ts
```

Expected: FAIL because `scanProject` does not exist.

- [ ] **Step 3: Implement project scanning**

Create `control-room/src/server/scanner/project-scanner.ts` that:

1. Resolves all paths from the repository root.
2. Runs DRC/BOM/CPL/Gerber parsers in parallel with `Promise.all`.
3. Converts automatic results into `GateResult` values.
4. Loads human gates from `ControlRoomRepository`.
5. Seeds missing human gates as `waiting` without marking them passed.
6. Builds workstream summaries and calls `deriveReadiness`.

The automatic gates must use this behavior:

```ts
const gates: GateResult[] = [
  { id: 'drc', label: 'Board design checks', status: drc.blocking === 0 ? 'passed' : 'failed', source: 'automatic', blocking: true, summary: `${drc.blocking} blocking findings` },
  { id: 'bom_cpl', label: 'BOM and placement files', status: bom.valid && cpl.valid ? 'passed' : 'failed', source: 'automatic', blocking: true, summary: `${bom.lineItems} BOM lines, ${cpl.placements} placements` },
  { id: 'gerber_zip', label: 'Manufacturing ZIP', status: gerber.valid ? 'passed' : 'failed', source: 'automatic', blocking: true, summary: `${gerber.fileCount} expected files` }
];
```

- [ ] **Step 4: Add degraded-state tests**

Add a test that scans a temporary root without production files and expects the
automatic gates to be `blocked` or `failed`, never `passed`.

- [ ] **Step 5: Run tests and commit**

Run:

```powershell
npm.cmd test -- project-scanner.test.ts gates.test.ts
```

Expected: PASS.

```powershell
git add control-room/src/server/scanner/project-scanner.ts control-room/src/server/readiness control-room/tests
git commit -m "feat: derive live SafeSwitch project readiness"
```

---

### Task 6: Implement The Strict Action Catalog And Runner

**Files:**
- Create: `control-room/src/server/actions/command-catalog.ts`
- Create: `control-room/src/server/actions/command-executor.ts`
- Create: `control-room/src/server/actions/action-runner.ts`
- Create: `control-room/src/server/actions/output-parsers.ts`
- Create: `scripts/build_rev2_release.ps1`
- Create: `control-room/tests/unit/action-runner.test.ts`

- [ ] **Step 1: Write failing action-safety tests**

Create `control-room/tests/unit/action-runner.test.ts`:

```ts
import { describe, expect, it, vi } from 'vitest';
import { ActionRunner } from '@server/actions/action-runner';

describe('ActionRunner', () => {
  it('rejects unknown action IDs', async () => {
    const runner = new ActionRunner({ execute: vi.fn() } as never);
    await expect(runner.start('arbitrary-shell', false)).rejects.toThrow('Unknown action');
  });

  it('requires confirmation for file-changing actions', async () => {
    const runner = new ActionRunner({ execute: vi.fn() } as never);
    await expect(runner.start('regenerate-rev2', false)).rejects.toThrow('confirmation');
  });

  it('rejects a duplicate running action', async () => {
    const execute = vi.fn(() => new Promise(() => undefined));
    const runner = new ActionRunner({ execute } as never);
    void runner.start('run-android-tests', false);
    await expect(runner.start('run-android-tests', false)).rejects.toThrow('already running');
  });
});
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
npm.cmd test -- action-runner.test.ts
```

Expected: FAIL because the action runner does not exist.

- [ ] **Step 3: Define immutable command factories**

Create `control-room/src/server/actions/command-catalog.ts`. Each action returns
an executable and fixed argument array. No value from the browser becomes a
command or argument.

Required commands:

- `run-drc`: KiCad CLI writes a report under `.control-room/runs/<id>/drc.json`,
  then KiCad Python runs `scripts/validate_drc.py` on that report.
- `compile-production-firmware`: Arduino CLI compiles a copied sketch under
  `.control-room/runs/<id>/wifi`.
- `compile-test-firmware`: Arduino CLI compiles with
  `esp32:esp32:esp32:PartitionScheme=huge_app`.
- `run-android-tests`: `gradlew.bat test`.
- `regenerate-rev2`: `powershell.exe -File scripts/build_rev2_release.ps1`.

- [ ] **Step 4: Implement cancellable action execution**

Create `control-room/src/server/actions/command-executor.ts`:

```ts
import { spawn } from 'node:child_process';

export interface CommandSpec {
  executable: string;
  args: string[];
  cwd: string;
}

export class CommandExecutor {
  execute(spec: CommandSpec) {
    const child = spawn(spec.executable, spec.args, { cwd: spec.cwd, windowsHide: true });
    let output = '';
    child.stdout.on('data', (chunk) => { output += chunk.toString(); });
    child.stderr.on('data', (chunk) => { output += chunk.toString(); });
    return {
      cancel: () => child.kill(),
      result: new Promise<{ exitCode: number; output: string }>((resolve, reject) => {
        child.on('error', reject);
        child.on('close', (exitCode) => resolve({ exitCode: exitCode ?? -1, output }));
      })
    };
  }
}
```

Create `control-room/src/server/actions/action-runner.ts` with:

```ts
export class ActionRunner {
  private readonly running = new Map<string, { cancel: () => void }>();

  constructor(private readonly executor: CommandExecutor, private readonly repository?: ControlRoomRepository) {}

  async start(actionId: string, confirmed: boolean) {
    const definition = ACTIONS.find((action) => action.id === actionId);
    if (!definition) throw new Error('Unknown action');
    if (definition.mutatesFiles && !confirmed) throw new Error('File-changing action requires confirmation');
    if (this.running.has(actionId)) throw new Error('Action is already running');

    const runId = crypto.randomUUID();
    const command = commandFor(actionId, runId);
    const execution = this.executor.execute(command);
    this.running.set(actionId, { cancel: execution.cancel });
    try {
      return await execution.result;
    } finally {
      this.running.delete(actionId);
    }
  }
}
```

Persist started, completed, failed, cancelled, and interrupted action states.

Implement `run-all-checks` as a composite action inside `ActionRunner`: run DRC,
BOM/CPL scan, Gerber ZIP scan, both firmware compiles, and Android tests in
sequence; record one parent result plus each child result. The browser still
cannot provide commands or arguments.

- [ ] **Step 5: Create the confirmed Rev2 release script**

Create `scripts/build_rev2_release.ps1` as the single deterministic release
entry point. It must:

1. Generate into `.build/rev2-control-room`.
2. Run DRC and `scripts/validate_drc.py`.
3. Stop if the gate fails.
4. Copy PCB/BOM/CPL into `production`.
5. Export only the approved fabrication layers and separate PTH/NPTH drills.
6. Rebuild both Rev2 production ZIPs from the explicit 11-file allowlist.
7. Run the production DRC gate again.

- [ ] **Step 6: Run action tests and commit**

Run:

```powershell
npm.cmd test -- action-runner.test.ts
```

Expected: PASS with command execution mocked.

```powershell
git add control-room/src/server/actions control-room/tests/unit/action-runner.test.ts scripts/build_rev2_release.ps1
git commit -m "feat: add safe local project action runner"
```

---

### Task 7: Expose The Local API

**Files:**
- Create: `control-room/src/server/api.ts`
- Modify: `control-room/src/server/index.ts`
- Create: `control-room/tests/integration/api.test.ts`

- [ ] **Step 1: Write failing API tests**

Create `control-room/tests/integration/api.test.ts`:

```ts
import request from 'supertest';
import { describe, expect, it } from 'vitest';
import { createApi } from '@server/api';

describe('control room API', () => {
  it('returns a project snapshot', async () => {
    const response = await request(createApi({ root: '..', databasePath: ':memory:' })).get('/api/project');
    expect(response.status).toBe(200);
    expect(response.body.readiness.rev2ReadyToOrder).toBe(false);
  });

  it('persists a human workflow result', async () => {
    const api = createApi({ root: '..', databasePath: ':memory:' });
    const update = await request(api).put('/api/workflows/usb_approval').send({ status: 'passed', notes: 'Manufacturer approved', recordedBy: 'James' });
    expect(update.status).toBe(200);
    const project = await request(api).get('/api/project');
    expect(project.body.gates.find((gate: { id: string }) => gate.id === 'usb_approval').status).toBe('passed');
  });

  it('rejects unconfirmed regeneration', async () => {
    const response = await request(createApi({ root: '..', databasePath: ':memory:' })).post('/api/actions/regenerate-rev2/runs').send({ confirmed: false });
    expect(response.status).toBe(409);
  });
});
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
npm.cmd test -- api.test.ts
```

Expected: FAIL because `createApi` does not exist.

- [ ] **Step 3: Implement endpoints**

Create `control-room/src/server/api.ts` with:

- `GET /api/health`
- `GET /api/project`
- `GET /api/workflows`
- `PUT /api/workflows/:key`
- `GET /api/activity`
- `GET /api/actions`
- `POST /api/actions/:actionId/runs`
- `GET /api/action-runs/:runId`
- `POST /api/action-runs/:runId/cancel`
- `GET /api/files`
- `POST /api/files/:fileId/reveal`

Validate request bodies with Zod. Return:

- `400` for invalid bodies
- `404` for unknown files, actions, or runs
- `409` for missing confirmation or duplicate actions
- `500` with a plain-English summary and technical details for unexpected failures

Add middleware that rejects non-local `Host` and `Origin` headers. Allowed
origins are `http://127.0.0.1:4173`, `http://localhost:4173`,
`http://127.0.0.1:4174`, and `http://localhost:4174`. Add an API test proving
an origin such as `https://example.com` receives `403`.

- [ ] **Step 4: Serve the built client in production**

Update `control-room/src/server/index.ts` to create the API, serve
`dist/client`, and bind only to `127.0.0.1`.

- [ ] **Step 5: Run API tests and commit**

Run:

```powershell
npm.cmd test -- api.test.ts
```

Expected: PASS.

```powershell
git add control-room/src/server control-room/tests/integration/api.test.ts
git commit -m "feat: expose SafeSwitch local control API"
```

---

### Task 8: Build The Mission Control App Shell And Design System

**Files:**
- Create: `control-room/src/client/styles.css`
- Create: `control-room/src/client/api.ts`
- Create: `control-room/src/client/components/app-shell.tsx`
- Create: `control-room/src/client/components/status-mark.tsx`
- Modify: `control-room/src/client/app.tsx`
- Create: `control-room/tests/unit/app-shell.test.tsx`

- [ ] **Step 1: Write failing shell test**

Create `control-room/tests/unit/app-shell.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { AppShell } from '@client/components/app-shell';

describe('AppShell', () => {
  it('shows every approved navigation destination', () => {
    render(<AppShell active="mission-control" onNavigate={() => undefined}><div>Page</div></AppShell>);
    for (const label of ['Mission Control', 'Rev2 Ordering', 'Hardware', 'Firmware', 'Mobile App', 'Automotive System', 'Files & Documents', 'Activity History', 'Settings']) {
      expect(screen.getByRole('button', { name: label })).toBeInTheDocument();
    }
  });
});
```

- [ ] **Step 2: Run test and verify failure**

Run:

```powershell
npm.cmd test -- app-shell.test.tsx
```

Expected: FAIL because the shell does not exist.

- [ ] **Step 3: Implement the approved Mission Control visual system**

Create CSS tokens in `control-room/src/client/styles.css`:

```css
:root {
  color-scheme: dark;
  --bg: #071011;
  --surface: #10201f;
  --surface-strong: #152826;
  --border: #29413c;
  --text: #edf5ef;
  --muted: #96aaa3;
  --pass: #74efae;
  --waiting: #e3ad54;
  --danger: #ef7771;
  --radius: 14px;
  font-family: Inter, "Segoe UI", sans-serif;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); }
button, input, textarea, select { font: inherit; }
button:focus-visible, input:focus-visible, textarea:focus-visible, select:focus-visible {
  outline: 3px solid var(--pass);
  outline-offset: 2px;
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; animation: none !important; }
}
```

- [ ] **Step 4: Implement the app shell**

Create a fixed desktop sidebar, responsive mobile navigation, page title region,
and content region. Use Lucide icons with text labels; color is never the only
selection signal.

- [ ] **Step 5: Wire local page navigation**

Keep routing dependency-free for the first version. `App` owns an active page
ID and renders the matching page component. Browser back-button support is not
required for the initial localhost application.

- [ ] **Step 6: Run tests and commit**

Run:

```powershell
npm.cmd test -- app-shell.test.tsx
```

Expected: PASS.

```powershell
git add control-room/src/client control-room/tests/unit/app-shell.test.tsx
git commit -m "feat: build Mission Control application shell"
```

---

### Task 9: Implement The Live Mission Control Dashboard

**Files:**
- Create: `control-room/src/client/pages/mission-control-page.tsx`
- Create: `control-room/src/client/components/gate-list.tsx`
- Create: `control-room/src/client/components/action-button.tsx`
- Create: `control-room/src/client/components/action-run-panel.tsx`
- Create: `control-room/tests/unit/mission-control.test.tsx`

- [ ] **Step 1: Write failing owner-view tests**

Create `control-room/tests/unit/mission-control.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { MissionControlPage } from '@client/pages/mission-control-page';

describe('MissionControlPage', () => {
  it('shows the next required action and all primary controls', () => {
    render(<MissionControlPage snapshot={fixtureSnapshot} onRunAction={() => undefined} onNavigate={() => undefined} />);
    expect(screen.getByText('Get manufacturer approval for USB-C area')).toBeInTheDocument();
    for (const label of ['Run all checks', 'Prepare Rev2 order', 'View manufacturing files', 'Compile firmware', 'Run Android tests', 'Record progress']) {
      expect(screen.getByRole('button', { name: label })).toBeInTheDocument();
    }
  });
});
```

- [ ] **Step 2: Run test and verify failure**

Run:

```powershell
npm.cmd test -- mission-control.test.tsx
```

Expected: FAIL because the page does not exist.

- [ ] **Step 3: Implement live API loading**

Create `control-room/src/client/api.ts`:

```ts
export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) }
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.summary ?? body.error ?? `Request failed: ${response.status}`);
  return body as T;
}
```

Load `/api/project` on app start and after actions or workflow updates.

- [ ] **Step 4: Implement the owner-first dashboard**

The dashboard must render:

- Exact plain-English phase
- One next-action panel
- Readiness progress derived from gates
- Blocking gate list
- Workstream summaries
- Recent runs
- Six wired primary actions
- Expandable technical details

Action button mapping:

- Run all checks -> `run-all-checks`
- Prepare Rev2 order -> navigate to ordering
- View manufacturing files -> navigate to files
- Compile firmware -> `compile-production-firmware`
- Run Android tests -> `run-android-tests`
- Record progress -> navigate to ordering or hardware workflow editor

- [ ] **Step 5: Add loading, empty, and failure states**

The failure state must show a plain-English summary, impact, retry button, and
expandable technical message.

- [ ] **Step 6: Run tests and commit**

Run:

```powershell
npm.cmd test -- mission-control.test.tsx
```

Expected: PASS.

```powershell
git add control-room/src/client control-room/tests/unit/mission-control.test.tsx
git commit -m "feat: add live owner Mission Control dashboard"
```

---

### Task 10: Implement Rev2 Ordering And Human Workflow Management

**Files:**
- Create: `control-room/src/client/pages/ordering-page.tsx`
- Create: `control-room/src/client/components/workflow-editor.tsx`
- Create: `control-room/tests/unit/ordering-page.test.tsx`
- Modify: `control-room/src/server/api.ts`
- Modify: `control-room/src/server/repository.ts`

- [ ] **Step 1: Write failing ordering workflow tests**

Test that:

- USB approval, SW1, SW2, J2, DFM preview, and manufacturer warnings appear.
- Saving a result calls `PUT /api/workflows/:key`.
- Physical/manufacturer workflow defaults are never passed.
- A notes field and evidence path are available.

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
npm.cmd test -- ordering-page.test.tsx
```

Expected: FAIL.

- [ ] **Step 3: Implement reusable workflow editing**

`WorkflowEditor` must provide:

- Status selector: not started/waiting, passed, failed, blocked, skipped
- Notes
- Evidence path
- Recorded-by name
- Save button
- Last-updated time

On save, refresh `/api/project` and `/api/activity`.

- [ ] **Step 4: Implement order records**

Extend the database/repository/API with an `order_record` settings document
containing manufacturer, order number, order date, quantity, total cost,
expected delivery, and tracking number. Render and edit it on the ordering
page.

- [ ] **Step 5: Run tests and commit**

Run:

```powershell
npm.cmd test -- ordering-page.test.tsx api.test.ts repository.test.ts
```

Expected: PASS.

```powershell
git add control-room/src/client control-room/src/server control-room/tests
git commit -m "feat: manage Rev2 ordering approvals and records"
```

---

### Task 11: Implement Every Remaining Workstream And File View

**Files:**
- Create: `control-room/src/client/pages/workstream-page.tsx`
- Create: `control-room/src/client/pages/files-page.tsx`
- Create: `control-room/src/client/pages/activity-page.tsx`
- Create: `control-room/src/client/pages/settings-page.tsx`
- Create: `control-room/tests/unit/workstreams.test.tsx`
- Modify: `control-room/src/server/scanner/project-scanner.ts`
- Modify: `control-room/src/server/api.ts`

- [ ] **Step 1: Write failing workstream navigation tests**

Test that Hardware, Firmware, Mobile App, Automotive System, Files & Documents,
Activity History, and Settings each render their real data and controls.

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
npm.cmd test -- workstreams.test.tsx
```

Expected: FAIL.

- [ ] **Step 3: Implement Hardware and Automotive manual gates**

Render guided workflow editors for every physical step defined in the approved
design. Default all missing physical gates to `waiting`. Display the statement:

```text
Software cannot verify this step. Record the result only after completing the physical test.
```

- [ ] **Step 4: Implement Firmware and Mobile App status pages**

Firmware page:

- Latest production/test compile results
- Run buttons
- Program-size results
- Source file links
- Flashing instructions

Mobile page:

- Latest Gradle result
- Run button
- Explicit UI-prototype warning
- App-to-device integration workflow gates

- [ ] **Step 5: Implement Files, Activity, And Settings**

Files page:

- Authoritative files first
- Legacy/deprecated files separated
- Existence, size, and modified time
- Reveal action

Activity page:

- Reverse chronological event list
- Outcome filters
- Expandable details

Settings page:

- Tool-path visibility
- Repository-root visibility
- Local-only security statement
- No arbitrary command fields

- [ ] **Step 6: Run tests and commit**

Run:

```powershell
npm.cmd test -- workstreams.test.tsx
```

Expected: PASS.

```powershell
git add control-room/src/client control-room/src/server control-room/tests
git commit -m "feat: complete SafeSwitch management workstreams"
```

---

### Task 12: Wire Action Progress, Cancellation, Confirmation, And Recovery

**Files:**
- Modify: `control-room/src/client/components/action-button.tsx`
- Modify: `control-room/src/client/components/action-run-panel.tsx`
- Modify: `control-room/src/client/app.tsx`
- Modify: `control-room/src/server/actions/action-runner.ts`
- Modify: `control-room/src/server/repository.ts`
- Create: `control-room/tests/integration/action-flow.test.ts`

- [ ] **Step 1: Write failing action-flow tests**

Test:

- A normal action starts and records activity.
- Duplicate action start returns `409`.
- File-changing action opens confirmation and sends `confirmed: true`.
- Failed action persists its summary and technical output.
- Cancelled action records `cancelled`.
- Backend initialization marks previously running actions as interrupted, not passed.

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
npm.cmd test -- action-flow.test.ts
```

Expected: FAIL.

- [ ] **Step 3: Implement polling and progress UI**

After action start:

1. Show running state immediately.
2. Poll the run endpoint every second.
3. Disable duplicate buttons.
4. Show cancel only when cancellable.
5. Refresh the project snapshot and activity after completion.

- [ ] **Step 4: Implement confirmation UI**

The regeneration dialog must name affected files:

- `production/ESP32_Simple_IoT.kicad_pcb`
- `production/ESP32_Simple_IoT_BOM.csv`
- `production/ESP32_Simple_IoT_CPL.csv`
- `production/drc_report.json`
- `production/gerbers/*`
- Rev2 Gerber ZIPs

- [ ] **Step 5: Implement recovery presentation**

Each failed run displays:

- What failed
- What it blocks
- Recommended next step
- Expandable technical output

- [ ] **Step 6: Run tests and commit**

Run:

```powershell
npm.cmd test -- action-flow.test.ts action-runner.test.ts
```

Expected: PASS.

```powershell
git add control-room/src control-room/tests
git commit -m "feat: complete safe project action workflows"
```

---

### Task 13: Add Browser Workflows And Responsive Verification

**Files:**
- Create: `control-room/playwright.config.ts`
- Create: `control-room/tests/e2e/mission-control.spec.ts`
- Create: `control-room/tests/e2e/ordering.spec.ts`
- Create: `control-room/tests/e2e/actions.spec.ts`
- Create: `control-room/tests/e2e/workstreams.spec.ts`
- Modify: `control-room/src/client/styles.css`

- [ ] **Step 1: Configure Playwright**

Create `control-room/playwright.config.ts`:

```ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: 'tests/e2e',
  webServer: {
    command: 'npm.cmd run dev',
    url: 'http://127.0.0.1:4173',
    reuseExistingServer: true,
    timeout: 120_000
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['Pixel 7'] } }
  ]
});
```

- [ ] **Step 2: Write core browser workflow tests**

Required E2E assertions:

- Mission Control displays real Rev2 state.
- Run-all-checks starts and finishes with a visible result.
- Ordering records persist after reload.
- Physical test can be manually recorded.
- Files page distinguishes authoritative and legacy files.
- Activity page shows workflow changes and action runs.
- Regeneration cannot start without confirmation.
- Mobile layout has no horizontal overflow and preserves status/checklist editing.

- [ ] **Step 3: Run E2E and fix visible failures**

Run:

```powershell
npm.cmd run test:e2e
```

Expected: all desktop and mobile workflow tests pass.

- [ ] **Step 4: Perform accessibility and visual audit**

Verify:

- Keyboard navigation reaches every control.
- Visible focus appears.
- Text remains readable at 200% zoom.
- Color is not the only status indicator.
- Desktop first viewport shows phase, next action, blockers, and primary actions.
- Mobile supports status review and checklist updates.
- Long-running/file-changing actions explain desktop requirements where needed.

- [ ] **Step 5: Commit**

```powershell
git add control-room
git commit -m "test: verify SafeSwitch control room workflows"
```

---

### Task 14: Final End-To-End Verification And Documentation

**Files:**
- Create: `control-room/README.md`
- Modify: `PROJECT_STATUS.md`
- Modify: `SARLLS_AGENT_CONTEXT.md`
- Modify: `docs/superpowers/specs/2026-06-07-safeswitch-control-room-design.md`

- [ ] **Step 1: Document installation and operation**

`control-room/README.md` must include:

- Purpose and local-only security model
- Install command
- Start command
- Test commands
- Action catalog
- File-changing confirmation behavior
- Database location
- Backup/restore procedure for `.control-room/control-room.db`
- Clear statement that physical tests require human verification

- [ ] **Step 2: Run the complete automated suite**

Run:

```powershell
cd control-room
npm.cmd run test:all
```

Expected:

- All unit tests pass
- All API integration tests pass
- TypeScript check passes
- Production build succeeds
- Desktop and mobile Playwright tests pass

- [ ] **Step 3: Run real project actions from the dashboard**

Run and verify:

- PCB DRC gate: `0 blocking, 26 approved J1 edge errors, 11 warnings`
- BOM/CPL validation: `20 line items`, `28 placements`
- Gerber ZIP validation: `11 files`
- Production firmware compile: pass
- Hardware-test firmware compile with `huge_app`: pass
- Android Gradle tests: pass

Do not run the file-changing Rev2 regeneration action during final verification
unless explicitly approved at execution time.

- [ ] **Step 4: Verify the rendered UI**

Open the local dashboard in the Browser plugin, inspect desktop and mobile
screens, click every primary action and navigation destination, and capture
screenshots for comparison with the approved Mission Control direction.

- [ ] **Step 5: Update project status**

Record:

- Control room implementation complete
- Test suite results
- Real action results
- Remaining physical/manufacturer project blockers

Do not state that Rev2 is ready to order unless the human manufacturer gates
have actually been recorded as passed.

- [ ] **Step 6: Run final repository checks**

Run:

```powershell
git diff --check
git status --short
```

Expected: no whitespace errors; unrelated user changes remain untouched.

- [ ] **Step 7: Commit**

```powershell
git add control-room PROJECT_STATUS.md SARLLS_AGENT_CONTEXT.md docs/superpowers/specs/2026-06-07-safeswitch-control-room-design.md
git commit -m "feat: complete SafeSwitch project control room"
```

---

## Plan Self-Review

### Spec Coverage

- Mission Control owner view: Tasks 8-9
- Real project scanner: Tasks 3 and 5
- SQLite workflow persistence: Task 4
- Strict allowlisted actions: Tasks 6, 7, and 12
- Rev2 ordering management: Task 10
- Hardware, firmware, mobile, automotive, files, history, settings: Task 11
- Error handling and confirmation: Task 12
- Unit, API integration, and browser tests: Tasks 2-13
- Desktop/mobile visual verification and documentation: Tasks 13-14

### Type Consistency

- `GateResult`, `ReadinessSummary`, `ProjectSnapshot`, `WorkflowRecord`, and
  `ActionRun` are defined once in Task 2 and reused throughout.
- Workflow updates use `PUT /api/workflows/:key`.
- Actions use `POST /api/actions/:actionId/runs`.
- Human-required gates default to `waiting`, never `passed`.

### Completion Boundary

The control-room software can reach complete implementation and automated-test
coverage while manufacturer approvals and physical hardware tests remain
external blockers. The dashboard must accurately display those blockers rather
than treating them as application defects or inventing successful results.
