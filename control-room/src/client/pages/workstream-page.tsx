import { useState } from 'react';
import type { GateResult, ProjectSnapshot } from '@shared/types';
import { GateList } from '../components/gate-list';
import { WorkflowEditor } from '../components/workflow-editor';
import { ActionButton } from '../components/action-button';

interface WorkstreamPageProps {
  workstreamId: string;
  snapshot: ProjectSnapshot;
  onRefresh: () => void;
  onRunAction: (actionId: string) => void;
  runningActions: Set<string>;
}

const WORKSTREAM_CONFIG: Record<string, {
  title: string;
  description: string;
  physical: boolean;
  actions?: Array<{ id: string; label: string; description: string }>;
}> = {
  hardware: {
    title: 'Hardware Bring-Up',
    description: 'Physical testing of assembled boards. Each gate requires hands-on verification.',
    physical: true,
  },
  firmware: {
    title: 'Firmware',
    description: 'Compile and validate firmware images for the ESP32 controller.',
    physical: false,
    actions: [
      { id: 'compile-production-firmware', label: 'Compile production firmware', description: 'WiFi controller (wifi_switch.ino)' },
      { id: 'compile-test-firmware', label: 'Compile test firmware', description: 'Hardware validation (test_firmware.ino) with huge_app partition' },
    ],
  },
  mobile: {
    title: 'Mobile App',
    description: 'Android SafeSwitch app. Currently a UI prototype without device connectivity.',
    physical: false,
    actions: [
      { id: 'run-android-tests', label: 'Run Android tests', description: 'Gradle test task' },
    ],
  },
  automotive: {
    title: 'Automotive Integration',
    description: 'Vehicle battery disconnect system. Requires controller validation, contactor, and bench testing.',
    physical: true,
  },
};

export function WorkstreamPage({
  workstreamId,
  snapshot,
  onRefresh,
  onRunAction,
  runningActions,
}: WorkstreamPageProps) {
  const [editingGate, setEditingGate] = useState<GateResult | null>(null);
  const config = WORKSTREAM_CONFIG[workstreamId];
  const workstream = snapshot.workstreams.find((ws) => ws.id === workstreamId);

  if (!config || !workstream) {
    return <div className="loading">Workstream not found</div>;
  }

  return (
    <div>
      <h1 className="page-title">{config.title}</h1>
      <p style={{ color: 'var(--muted)', marginBottom: 20, fontSize: 14 }}>
        {config.description}
      </p>

      {config.physical && (
        <div className="physical-note">
          Software cannot verify physical steps. Record the result only after completing the physical test.
        </div>
      )}

      {/* Actions */}
      {config.actions && config.actions.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          {config.actions.map((action) => (
            <ActionButton
              key={action.id}
              label={action.label}
              description={action.description}
              running={runningActions.has(action.id)}
              onStart={() => onRunAction(action.id)}
              cancellable
            />
          ))}
        </div>
      )}

      {/* Gates */}
      {workstream.gates.length > 0 && (
        <div className="card">
          <div className="card-title">Gates</div>
          <GateList gates={workstream.gates} onGateClick={(g) => g.source === 'human' ? setEditingGate(g) : undefined} />
        </div>
      )}

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

      {workstreamId === 'mobile' && (
        <div className="card">
          <div className="card-title">Status</div>
          <p style={{ fontSize: 13, color: 'var(--muted)' }}>
            The Android app is currently a UI prototype. It does not communicate with the ESP32 controller.
            App-to-device integration is blocked until controller hardware is validated.
          </p>
        </div>
      )}

      {workstreamId === 'firmware' && (
        <div className="card">
          <div className="card-title">Flashing Instructions</div>
          <p style={{ fontSize: 13, color: 'var(--muted)' }}>
            Connect the ESP32 board via USB data cable (not charge-only).
            Use Arduino CLI or PlatformIO to flash. Production firmware exposes a local
            WiFi web interface for relay control.
          </p>
          <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 8 }}>
            <strong>Production:</strong> wifi_switch.ino — default partition, 981KB<br/>
            <strong>Test:</strong> test_firmware.ino — huge_app partition, 1.6MB
          </div>
        </div>
      )}
    </div>
  );
}
