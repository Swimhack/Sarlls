import { useState } from 'react';
import type { GateResult, ProjectSnapshot } from '@shared/types';
import { REV2_ORDER_GATE_IDS } from '@shared/gates';
import { GateList } from '../components/gate-list';
import { WorkflowEditor } from '../components/workflow-editor';

interface OrderingPageProps {
  snapshot: ProjectSnapshot;
  onRefresh: () => void;
}

export function OrderingPage({ snapshot, onRefresh }: OrderingPageProps) {
  const [editingGate, setEditingGate] = useState<GateResult | null>(null);
  const orderGates = snapshot.gates.filter((g) =>
    (REV2_ORDER_GATE_IDS as readonly string[]).includes(g.id)
  );
  const allPassed = orderGates.every((g) => g.status === 'passed');
  const passedCount = orderGates.filter((g) => g.status === 'passed').length;

  return (
    <div>
      <h1 className="page-title">Rev2 Ordering</h1>

      <div className="phase-banner">
        <div className="phase-label">Order Readiness</div>
        <div className="phase-value" style={{ color: allPassed ? 'var(--pass)' : 'var(--waiting)' }}>
          {allPassed ? 'Ready to Order' : `${passedCount}/${orderGates.length} Gates Passed`}
        </div>
        <div className="progress-bar" style={{ marginTop: 12 }}>
          <div
            className="progress-fill"
            style={{ width: `${(passedCount / orderGates.length) * 100}%` }}
          />
        </div>
      </div>

      <div className="card">
        <div className="card-title">Order Gates</div>
        <p style={{ fontSize: 13, color: 'var(--muted)', marginBottom: 12 }}>
          Click a gate to update its status. Human gates require manual verification.
        </p>
        <GateList gates={orderGates} onGateClick={(g) => setEditingGate(g)} />
      </div>

      {editingGate && (
        <div className="card">
          <div className="card-title">Update Gate</div>
          <WorkflowEditor
            gate={editingGate}
            onSaved={() => {
              setEditingGate(null);
              onRefresh();
            }}
          />
        </div>
      )}
    </div>
  );
}
