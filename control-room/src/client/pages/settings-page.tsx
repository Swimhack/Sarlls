import { useEffect, useState } from 'react';
import { fetchSettings } from '../api';
import { Shield } from 'lucide-react';

export function SettingsPage() {
  const [settings, setSettings] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSettings()
      .then(setSettings)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading settings...</div>;

  return (
    <div>
      <h1 className="page-title">Settings</h1>

      <div className="card" style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
        <Shield size={20} style={{ color: 'var(--pass)', flexShrink: 0, marginTop: 2 }} />
        <div>
          <div style={{ fontWeight: 600, fontSize: 14 }}>Local-Only Application</div>
          <p style={{ fontSize: 13, color: 'var(--muted)', marginTop: 4 }}>
            This control room binds to 127.0.0.1 only. No data leaves your machine.
            Browser requests cannot supply arbitrary shell commands.
            File-changing actions require explicit confirmation.
          </p>
        </div>
      </div>

      <div className="card">
        <div className="card-title">Tool Paths</div>
        {Object.entries(settings).map(([key, value]) => (
          <div key={key} className="settings-row">
            <span className="settings-label">{key}</span>
            <span className="settings-value">{value}</span>
          </div>
        ))}
      </div>

      <div className="card">
        <div className="card-title">Database</div>
        <p style={{ fontSize: 13, color: 'var(--muted)' }}>
          Workflow records and activity history are stored in a local SQLite database
          at <code style={{ fontSize: 12 }}>.control-room/control-room.db</code>.
          Back up this file to preserve your recorded progress.
        </p>
      </div>
    </div>
  );
}
