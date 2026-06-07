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
