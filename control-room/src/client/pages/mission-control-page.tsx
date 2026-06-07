import type { ProjectSnapshot } from '@shared/types';
import type { PageId } from '../components/app-shell';
import { GateList } from '../components/gate-list';
import { StatusDot } from '../components/status-mark';
import { Play, ShoppingCart, FolderOpen, Code, Smartphone, ClipboardCheck } from 'lucide-react';

const PHASE_LABELS: Record<string, string> = {
  engineering_prototype: 'Engineering Prototype',
  controller_pre_fabrication: 'Controller Pre-Fabrication',
  controller_ready_to_order: 'Controller Ready to Order',
  controller_ordered: 'Controller Ordered',
  controller_bring_up: 'Controller Bring-Up',
  controller_validated: 'Controller Validated',
  automotive_integration: 'Automotive Integration',
  bench_validated: 'Bench Validated',
  ready_for_vehicle_test: 'Ready for Vehicle Test',
};

interface MissionControlPageProps {
  snapshot: ProjectSnapshot;
  onRunAction: (actionId: string) => void;
  onNavigate: (page: PageId) => void;
}

export function MissionControlPage({
  snapshot,
  onRunAction,
  onNavigate,
}: MissionControlPageProps) {
  const { readiness, gates, workstreams, recentRuns } = snapshot;
  const pct =
    readiness.totalRequired > 0
      ? Math.round(
          (readiness.completedRequired / readiness.totalRequired) * 100
        )
      : 0;

  return (
    <div>
      <h1 className="page-title">Mission Control</h1>

      {/* Phase banner */}
      <div className="phase-banner">
        <div className="phase-label">Current Phase</div>
        <div className="phase-value">
          {PHASE_LABELS[readiness.phase] ?? readiness.phase}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 8 }}>
          <div className="progress-bar" style={{ flex: 1 }}>
            <div className="progress-fill" style={{ width: `${pct}%` }} />
          </div>
          <span style={{ fontSize: 13, color: 'var(--muted)' }}>
            {readiness.completedRequired}/{readiness.totalRequired} gates
          </span>
        </div>
      </div>

      {/* Next action */}
      {readiness.nextAction && (
        <div className="next-action">
          <div className="next-action-label">Next Required Action</div>
          <div className="next-action-text">{readiness.nextAction.label}</div>
          {readiness.nextAction.summary && (
            <p style={{ fontSize: 13, color: 'var(--muted)', marginTop: 4 }}>
              {readiness.nextAction.summary}
            </p>
          )}
        </div>
      )}

      {/* Primary actions */}
      <div className="card">
        <div className="card-title">Quick Actions</div>
        <div className="action-grid">
          <button className="btn btn-primary" onClick={() => onRunAction('run-all-checks')}>
            <Play size={14} /> Run all checks
          </button>
          <button className="btn" onClick={() => onNavigate('ordering')}>
            <ShoppingCart size={14} /> Prepare Rev2 order
          </button>
          <button className="btn" onClick={() => onNavigate('files')}>
            <FolderOpen size={14} /> View manufacturing files
          </button>
          <button className="btn" onClick={() => onRunAction('compile-production-firmware')}>
            <Code size={14} /> Compile firmware
          </button>
          <button className="btn" onClick={() => onRunAction('run-android-tests')}>
            <Smartphone size={14} /> Run Android tests
          </button>
          <button className="btn" onClick={() => onNavigate('ordering')}>
            <ClipboardCheck size={14} /> Record progress
          </button>
        </div>
      </div>

      {/* Blockers */}
      {readiness.blockers.length > 0 && (
        <div className="card">
          <div className="card-title">
            Blockers ({readiness.blockers.length})
          </div>
          <GateList gates={readiness.blockers} />
        </div>
      )}

      {/* Workstreams */}
      <div className="card">
        <div className="card-title">Workstreams</div>
        {workstreams.map((ws) => (
          <div key={ws.id} style={{ marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <span style={{ fontWeight: 600, fontSize: 14 }}>{ws.label}</span>
              <span style={{ fontSize: 12, color: 'var(--muted)' }}>
                {ws.summary}
              </span>
            </div>
            {ws.gates.length > 0 && (
              <div style={{ marginLeft: 8 }}>
                {ws.gates.map((g) => (
                  <div
                    key={g.id}
                    style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0', fontSize: 13 }}
                  >
                    <StatusDot status={g.status} />
                    <span>{g.label}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Recent runs */}
      {recentRuns.length > 0 && (
        <div className="card">
          <div className="card-title">Recent Runs</div>
          {recentRuns.slice(0, 5).map((run) => (
            <div key={run.id} className="activity-item">
              <StatusDot status={run.status} />
              <span style={{ flex: 1 }}>{run.summary}</span>
              <span className="activity-time">
                {new Date(run.startedAt).toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
