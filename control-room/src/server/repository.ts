import type { DatabaseSync } from 'node:sqlite';
import type { ActionRun, WorkflowRecord } from '@shared/types';

export class ControlRoomRepository {
  constructor(private readonly database: DatabaseSync) {}

  upsertWorkflow(record: WorkflowRecord) {
    this.database
      .prepare(
        `INSERT INTO workflows (key, status, notes, evidence_path, recorded_by, updated_at)
       VALUES (?, ?, ?, ?, ?, ?)
       ON CONFLICT(key) DO UPDATE SET
         status=excluded.status, notes=excluded.notes, evidence_path=excluded.evidence_path,
         recorded_by=excluded.recorded_by, updated_at=excluded.updated_at`
      )
      .run(
        record.key,
        record.status,
        record.notes,
        record.evidencePath ?? null,
        record.recordedBy ?? null,
        record.updatedAt
      );
    this.addActivity(
      'workflow.updated',
      `${record.key} changed to ${record.status}`,
      record.status
    );
  }

  getWorkflow(key: string) {
    return this.database
      .prepare(
        'SELECT key, status, notes, evidence_path AS evidencePath, recorded_by AS recordedBy, updated_at AS updatedAt FROM workflows WHERE key = ?'
      )
      .get(key) as unknown as WorkflowRecord | undefined;
  }

  listWorkflows() {
    return this.database
      .prepare(
        'SELECT key, status, notes, evidence_path AS evidencePath, recorded_by AS recordedBy, updated_at AS updatedAt FROM workflows ORDER BY key'
      )
      .all() as unknown as WorkflowRecord[];
  }

  addActionRun(run: ActionRun) {
    this.database
      .prepare(
        `INSERT INTO action_runs (id, action_id, status, summary, technical_output, started_at, finished_at)
       VALUES (?, ?, ?, ?, ?, ?, ?)`
      )
      .run(
        run.id,
        run.actionId,
        run.status,
        run.summary,
        run.technicalOutput ?? null,
        run.startedAt,
        run.finishedAt ?? null
      );
  }

  updateActionRun(
    id: string,
    updates: { status: string; summary: string; technicalOutput?: string; finishedAt?: string }
  ) {
    this.database
      .prepare(
        `UPDATE action_runs SET status=?, summary=?, technical_output=?, finished_at=? WHERE id=?`
      )
      .run(
        updates.status,
        updates.summary,
        updates.technicalOutput ?? null,
        updates.finishedAt ?? null,
        id
      );
  }

  getActionRun(id: string) {
    return this.database
      .prepare(
        'SELECT id, action_id AS actionId, status, summary, technical_output AS technicalOutput, started_at AS startedAt, finished_at AS finishedAt FROM action_runs WHERE id = ?'
      )
      .get(id) as unknown as ActionRun | undefined;
  }

  listRecentRuns(limit = 20) {
    return this.database
      .prepare(
        'SELECT id, action_id AS actionId, status, summary, technical_output AS technicalOutput, started_at AS startedAt, finished_at AS finishedAt FROM action_runs ORDER BY started_at DESC LIMIT ?'
      )
      .all(limit) as unknown as ActionRun[];
  }

  markInterruptedRuns() {
    this.database
      .prepare(
        `UPDATE action_runs SET status='cancelled', summary='Interrupted by server restart', finished_at=? WHERE status='running'`
      )
      .run(new Date().toISOString());
  }

  addActivity(
    eventType: string,
    summary: string,
    outcome: string,
    details?: string
  ) {
    this.database
      .prepare(
        'INSERT INTO activity (event_type, summary, outcome, details, created_at) VALUES (?, ?, ?, ?, ?)'
      )
      .run(
        eventType,
        summary,
        outcome,
        details ?? null,
        new Date().toISOString()
      );
  }

  listActivity(limit = 50) {
    return this.database
      .prepare(
        'SELECT event_type AS eventType, summary, outcome, details, created_at AS createdAt FROM activity ORDER BY id DESC LIMIT ?'
      )
      .all(limit) as unknown as Array<Record<string, string>>;
  }

  getSetting(key: string): string | undefined {
    const row = this.database
      .prepare('SELECT value FROM settings WHERE key = ?')
      .get(key) as unknown as { value: string } | undefined;
    return row?.value;
  }

  setSetting(key: string, value: string) {
    this.database
      .prepare(
        'INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value'
      )
      .run(key, value);
  }
}
