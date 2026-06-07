import type { GateResult } from '@shared/types';
import { StatusDot } from './status-mark';

interface GateListProps {
  gates: GateResult[];
  onGateClick?: (gate: GateResult) => void;
}

export function GateList({ gates, onGateClick }: GateListProps) {
  return (
    <div className="gate-list">
      {gates.map((gate) => (
        <div
          key={gate.id}
          className="gate-item"
          role={onGateClick ? 'button' : undefined}
          tabIndex={onGateClick ? 0 : undefined}
          onClick={() => onGateClick?.(gate)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              onGateClick?.(gate);
            }
          }}
          style={onGateClick ? { cursor: 'pointer' } : undefined}
        >
          <StatusDot status={gate.status} />
          <span className="gate-item-label">{gate.label}</span>
          {gate.summary && (
            <span className="gate-item-summary">{gate.summary}</span>
          )}
          {gate.source === 'human' && (
            <span className="gate-item-summary" style={{ fontStyle: 'italic' }}>
              manual
            </span>
          )}
        </div>
      ))}
    </div>
  );
}
