import { Play, Loader, Square } from 'lucide-react';

interface ActionButtonProps {
  label: string;
  description: string;
  running: boolean;
  disabled?: boolean;
  onStart: () => void;
  onCancel?: () => void;
  cancellable?: boolean;
}

export function ActionButton({
  label,
  description,
  running,
  disabled,
  onStart,
  onCancel,
  cancellable,
}: ActionButtonProps) {
  return (
    <div className="action-panel" style={{ padding: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 600, fontSize: 14 }}>{label}</div>
          <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 2 }}>
            {description}
          </div>
        </div>
        {running ? (
          <div style={{ display: 'flex', gap: 8 }}>
            <span className="status-dot running" style={{ marginTop: 4 }} />
            {cancellable && onCancel && (
              <button className="btn btn-danger" onClick={onCancel}>
                <Square size={14} /> Stop
              </button>
            )}
          </div>
        ) : (
          <button className="btn btn-primary" onClick={onStart} disabled={disabled}>
            <Play size={14} /> Run
          </button>
        )}
      </div>
    </div>
  );
}
