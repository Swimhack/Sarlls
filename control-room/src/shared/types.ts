export type ResultStatus =
  | 'passed'
  | 'failed'
  | 'waiting'
  | 'blocked'
  | 'running'
  | 'cancelled'
  | 'skipped';

export type GateSource = 'automatic' | 'human';

export interface GateResult {
  id: string;
  label: string;
  status: ResultStatus;
  source: GateSource;
  blocking: boolean;
  summary?: string;
  technicalDetails?: string;
  updatedAt?: string;
}

export interface ReadinessSummary {
  phase:
    | 'engineering_prototype'
    | 'controller_pre_fabrication'
    | 'controller_ready_to_order'
    | 'controller_ordered'
    | 'controller_bring_up'
    | 'controller_validated'
    | 'automotive_integration'
    | 'bench_validated'
    | 'ready_for_vehicle_test';
  rev2ReadyToOrder: boolean;
  readyForVehicleTest: boolean;
  completedRequired: number;
  totalRequired: number;
  nextAction?: GateResult;
  blockers: GateResult[];
}

export interface ProjectSnapshot {
  scannedAt: string;
  readiness: ReadinessSummary;
  gates: GateResult[];
  workstreams: WorkstreamSummary[];
  recentRuns: ActionRun[];
}

export interface WorkstreamSummary {
  id: string;
  label: string;
  summary: string;
  gates: GateResult[];
}

export interface WorkflowRecord {
  key: string;
  status: ResultStatus;
  notes: string;
  evidencePath?: string;
  recordedBy?: string;
  updatedAt: string;
}

export interface ActionRun {
  id: string;
  actionId: string;
  status: ResultStatus;
  summary: string;
  technicalOutput?: string;
  startedAt: string;
  finishedAt?: string;
}
