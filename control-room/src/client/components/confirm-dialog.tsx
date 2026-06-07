interface ConfirmDialogProps {
  title: string;
  message: string;
  details?: string[];
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  title,
  message,
  details,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  return (
    <div className="confirm-overlay" onClick={onCancel}>
      <div className="confirm-dialog" onClick={(e) => e.stopPropagation()}>
        <h3>{title}</h3>
        <p>{message}</p>
        {details && details.length > 0 && (
          <ul style={{ fontSize: 12, color: 'var(--muted)', paddingLeft: 20, marginTop: 8 }}>
            {details.map((d, i) => (
              <li key={i}>{d}</li>
            ))}
          </ul>
        )}
        <div className="btn-group">
          <button className="btn" onClick={onCancel}>Cancel</button>
          <button className="btn btn-danger" onClick={onConfirm}>
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
}
