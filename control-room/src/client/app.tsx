import { useCallback, useEffect, useState } from 'react';
import type { ProjectSnapshot, ActionRun } from '@shared/types';
import { AppShell, type PageId } from './components/app-shell';
import { ConfirmDialog } from './components/confirm-dialog';
import { MissionControlPage } from './pages/mission-control-page';
import { OrderingPage } from './pages/ordering-page';
import { WorkstreamPage } from './pages/workstream-page';
import { FilesPage } from './pages/files-page';
import { ActivityPage } from './pages/activity-page';
import { SettingsPage } from './pages/settings-page';
import { ModelViewerPage } from './pages/model-viewer-page';
import { fetchProject, startAction, fetchActionRun, cancelActionRun } from './api';

const REGEN_FILES = [
  'production/ESP32_Simple_IoT.kicad_pcb',
  'production/ESP32_Simple_IoT_BOM.csv',
  'production/ESP32_Simple_IoT_CPL.csv',
  'production/drc_report.json',
  'production/gerbers/*',
  'Rev2 Gerber ZIPs',
];

export function App() {
  const [page, setPage] = useState<PageId>('mission-control');
  const [snapshot, setSnapshot] = useState<ProjectSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [runningActions, setRunningActions] = useState<Set<string>>(new Set());
  const [activeRun, setActiveRun] = useState<ActionRun | null>(null);
  const [confirmAction, setConfirmAction] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const snap = await fetchProject();
      setSnapshot(snap);
      setError('');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load project');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleRunAction = useCallback(
    async (actionId: string) => {
      // Check if it needs confirmation
      if (actionId === 'regenerate-rev2') {
        setConfirmAction(actionId);
        return;
      }

      try {
        setRunningActions((prev) => new Set(prev).add(actionId));
        const run = await startAction(actionId);
        setActiveRun(run);

        // Poll for completion
        const poll = setInterval(async () => {
          try {
            const updated = await fetchActionRun(run.id);
            setActiveRun(updated);
            if (updated.status !== 'running') {
              clearInterval(poll);
              setRunningActions((prev) => {
                const next = new Set(prev);
                next.delete(actionId);
                return next;
              });
              refresh();
            }
          } catch {
            clearInterval(poll);
            setRunningActions((prev) => {
              const next = new Set(prev);
              next.delete(actionId);
              return next;
            });
          }
        }, 1500);
      } catch (err: unknown) {
        setRunningActions((prev) => {
          const next = new Set(prev);
          next.delete(actionId);
          return next;
        });
        setError(err instanceof Error ? err.message : 'Action failed');
      }
    },
    [refresh]
  );

  const handleConfirmRegen = useCallback(async () => {
    setConfirmAction(null);
    try {
      setRunningActions((prev) => new Set(prev).add('regenerate-rev2'));
      const run = await startAction('regenerate-rev2', true);
      setActiveRun(run);

      const poll = setInterval(async () => {
        try {
          const updated = await fetchActionRun(run.id);
          setActiveRun(updated);
          if (updated.status !== 'running') {
            clearInterval(poll);
            setRunningActions((prev) => {
              const next = new Set(prev);
              next.delete('regenerate-rev2');
              return next;
            });
            refresh();
          }
        } catch {
          clearInterval(poll);
        }
      }, 1500);
    } catch (err: unknown) {
      setRunningActions((prev) => {
        const next = new Set(prev);
        next.delete('regenerate-rev2');
        return next;
      });
      setError(err instanceof Error ? err.message : 'Regeneration failed');
    }
  }, [refresh]);

  if (loading) return <div className="loading">Loading SafeSwitch Control Room...</div>;

  if (error && !snapshot) {
    return (
      <div style={{ padding: 40 }}>
        <div className="error-card">
          <h3>Failed to Connect</h3>
          <p>{error}</p>
          <p>Make sure the API server is running on port 4174.</p>
          <div className="btn-group">
            <button className="btn btn-primary" onClick={refresh}>
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const workstreamMap: Record<string, string> = {
    hardware: 'hardware',
    firmware: 'firmware',
    mobile: 'mobile',
    automotive: 'automotive',
  };

  const renderPage = () => {
    if (!snapshot) return null;

    if (workstreamMap[page]) {
      return (
        <WorkstreamPage
          workstreamId={workstreamMap[page]!}
          snapshot={snapshot}
          onRefresh={refresh}
          onRunAction={handleRunAction}
          runningActions={runningActions}
        />
      );
    }

    switch (page) {
      case 'mission-control':
        return (
          <MissionControlPage
            snapshot={snapshot}
            onRunAction={handleRunAction}
            onNavigate={setPage}
          />
        );
      case 'ordering':
        return <OrderingPage snapshot={snapshot} onRefresh={refresh} />;
      case '3d-viewer':
        return <ModelViewerPage />;
      case 'files':
        return <FilesPage />;
      case 'activity':
        return <ActivityPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return null;
    }
  };

  return (
    <>
      <AppShell active={page} onNavigate={setPage}>
        {error && (
          <div className="error-card" style={{ marginBottom: 16 }}>
            <h3>Error</h3>
            <p>{error}</p>
            <button className="btn" onClick={() => setError('')} style={{ marginTop: 8 }}>
              Dismiss
            </button>
          </div>
        )}

        {activeRun && activeRun.status !== 'running' && (
          <div
            className={`card`}
            style={{
              marginBottom: 16,
              borderColor:
                activeRun.status === 'passed' ? 'var(--pass)' : 'var(--danger)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span
                  className={`status-label ${activeRun.status}`}
                  style={{ marginRight: 8 }}
                >
                  {activeRun.status}
                </span>
                <span style={{ fontSize: 14 }}>{activeRun.summary}</span>
              </div>
              <button className="btn" onClick={() => setActiveRun(null)} style={{ padding: '4px 12px' }}>
                Dismiss
              </button>
            </div>
            {activeRun.technicalOutput && (
              <details>
                <summary>Technical output</summary>
                <div className="action-output">{activeRun.technicalOutput}</div>
              </details>
            )}
          </div>
        )}

        {activeRun && activeRun.status === 'running' && (
          <div className="card" style={{ marginBottom: 16, borderColor: 'var(--info)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span className="status-dot running" />
              <span style={{ flex: 1, fontSize: 14 }}>{activeRun.summary}</span>
              <button
                className="btn btn-danger"
                style={{ padding: '4px 12px' }}
                onClick={() => {
                  cancelActionRun(activeRun.id);
                  setActiveRun(null);
                  setRunningActions(new Set());
                  refresh();
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {renderPage()}
      </AppShell>

      {confirmAction && (
        <ConfirmDialog
          title="Regenerate Rev2 Manufacturing Files"
          message="This will overwrite the following production files. This cannot be undone."
          details={REGEN_FILES}
          onConfirm={handleConfirmRegen}
          onCancel={() => setConfirmAction(null)}
        />
      )}
    </>
  );
}
