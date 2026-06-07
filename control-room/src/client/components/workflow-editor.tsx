import { useState } from 'react';
import type { GateResult, ResultStatus } from '@shared/types';
import { updateWorkflow } from '../api';

interface WorkflowEditorProps {
  gate: GateResult;
  onSaved: () => void;
}

const STATUS_OPTIONS: { value: ResultStatus; label: string }[] = [
  { value: 'waiting', label: 'Not started / Waiting' },
  { value: 'passed', label: 'Passed' },
  { value: 'failed', label: 'Failed' },
  { value: 'blocked', label: 'Blocked' },
  { value: 'skipped', label: 'Skipped' },
];

export function WorkflowEditor({ gate, onSaved }: WorkflowEditorProps) {
  const [status, setStatus] = useState<ResultStatus>(gate.status);
  const [notes, setNotes] = useState(gate.summary ?? '');
  const [recordedBy, setRecordedBy] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async () => {
    setSaving(true);
    setError('');
    try {
      await updateWorkflow(gate.id, { status, notes, recordedBy: recordedBy || undefined });
      onSaved();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="workflow-editor">
      <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: 12 }}>{gate.label}</h3>

      <label htmlFor={`status-${gate.id}`}>Status</label>
      <select
        id={`status-${gate.id}`}
        value={status}
        onChange={(e) => setStatus(e.target.value as ResultStatus)}
      >
        {STATUS_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>

      <label htmlFor={`notes-${gate.id}`}>Notes</label>
      <textarea
        id={`notes-${gate.id}`}
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        placeholder="Describe what was tested or observed..."
      />

      <label htmlFor={`recorded-${gate.id}`}>Recorded by</label>
      <input
        id={`recorded-${gate.id}`}
        value={recordedBy}
        onChange={(e) => setRecordedBy(e.target.value)}
        placeholder="Your name"
      />

      {gate.updatedAt && (
        <p style={{ fontSize: 11, color: 'var(--muted)', marginTop: 8 }}>
          Last updated: {new Date(gate.updatedAt).toLocaleString()}
        </p>
      )}

      {error && <p style={{ color: 'var(--danger)', fontSize: 12, marginTop: 8 }}>{error}</p>}

      <div className="btn-group">
        <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? 'Saving...' : 'Save'}
        </button>
      </div>
    </div>
  );
}
