import { useEffect, useState } from 'react';
import { fetchFiles, revealFile } from '../api';
import type { FileInfo } from '@server/scanner/documents';
import { FolderOpen, ExternalLink } from 'lucide-react';

function formatSize(bytes: number) {
  if (bytes === 0) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function FilesPage() {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchFiles()
      .then(setFiles)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Scanning files...</div>;
  if (error) return <div className="error-card"><h3>Error</h3><p>{error}</p></div>;

  const authoritative = files.filter((f) => f.authoritative);
  const legacy = files.filter((f) => !f.authoritative);

  const handleReveal = async (path: string) => {
    try {
      await revealFile(path);
    } catch {
      // silently fail
    }
  };

  return (
    <div>
      <h1 className="page-title">Files & Documents</h1>

      <div className="card">
        <div className="card-title">Authoritative Files</div>
        {authoritative.map((f) => (
          <div key={f.path} className="file-item">
            <FolderOpen size={14} style={{ color: f.exists ? 'var(--pass)' : 'var(--danger)', flexShrink: 0 }} />
            <div className="file-name">{f.label}</div>
            <div className="file-meta">
              {f.exists ? (
                <>
                  {formatSize(f.size)}
                  {f.modifiedAt && ` · ${new Date(f.modifiedAt).toLocaleDateString()}`}
                </>
              ) : (
                <span style={{ color: 'var(--danger)' }}>Missing</span>
              )}
            </div>
            {f.exists && (
              <button
                className="btn"
                style={{ padding: '4px 8px', fontSize: 11 }}
                onClick={() => handleReveal(f.path)}
                title="Show in Explorer"
              >
                <ExternalLink size={12} />
              </button>
            )}
          </div>
        ))}
      </div>

      {legacy.length > 0 && (
        <div className="card">
          <div className="card-title">Legacy / Reference Files</div>
          {legacy.map((f) => (
            <div key={f.path} className="file-item" style={{ opacity: 0.7 }}>
              <FolderOpen size={14} style={{ color: f.exists ? 'var(--muted)' : 'var(--danger)', flexShrink: 0 }} />
              <div className="file-name">{f.label}</div>
              <div className="file-meta">
                {f.exists ? formatSize(f.size) : <span style={{ color: 'var(--danger)' }}>Missing</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
