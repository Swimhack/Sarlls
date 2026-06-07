import { REV2_ORDER_GATE_IDS, VEHICLE_GATE_IDS } from '@shared/gates';
import type { GateResult, ReadinessSummary } from '@shared/types';

export function deriveReadiness(gates: GateResult[]): ReadinessSummary {
  const byId = new Map(gates.map((gate) => [gate.id, gate]));
  const required = REV2_ORDER_GATE_IDS.map((id) => byId.get(id)).filter(
    Boolean
  ) as GateResult[];
  const blockers = required.filter((gate) => gate.status !== 'passed');
  const vehicleReady = VEHICLE_GATE_IDS.every(
    (id) => byId.get(id)?.status === 'passed'
  );
  const rev2Ready =
    required.length === REV2_ORDER_GATE_IDS.length && blockers.length === 0;

  return {
    phase: vehicleReady
      ? 'ready_for_vehicle_test'
      : rev2Ready
        ? 'controller_ready_to_order'
        : 'controller_pre_fabrication',
    rev2ReadyToOrder: rev2Ready,
    readyForVehicleTest: vehicleReady,
    completedRequired: required.filter((gate) => gate.status === 'passed')
      .length,
    totalRequired: REV2_ORDER_GATE_IDS.length,
    nextAction: blockers[0],
    blockers
  };
}
