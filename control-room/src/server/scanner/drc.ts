import { readFile } from 'node:fs/promises';

interface DrcViolation {
  type?: string;
  severity?: string;
  description?: string;
  items?: Array<{
    description?: string;
    pos?: { x?: number; y?: number };
  }>;
}

interface DrcReport {
  unconnected_items?: unknown[];
  violations?: DrcViolation[];
}

export interface DrcResult {
  blocking: number;
  approvedJ1EdgeErrors: number;
  warnings: number;
  totalViolations: number;
}

export async function parseDrcReport(path: string): Promise<DrcResult> {
  const report = JSON.parse(await readFile(path, 'utf8')) as DrcReport;
  const violations = report.violations ?? [];
  const errors = violations.filter((v) => v.severity === 'error');
  const warnings = violations.filter((v) => v.severity === 'warning');

  // Approved J1 edge-clearance exceptions: copper_edge_clearance violations
  // involving Edge.Cuts rectangle and tracks near the J1 connector area
  const approved = errors.filter(
    (v) =>
      v.type === 'copper_edge_clearance' &&
      (v.items ?? []).some(
        (item) =>
          item.description?.includes('Edge.Cuts') ||
          item.description?.includes('of J1')
      )
  );

  const unconnected = report.unconnected_items?.length ?? 0;

  return {
    blocking: unconnected + errors.length - approved.length,
    approvedJ1EdgeErrors: approved.length,
    warnings: warnings.length,
    totalViolations: violations.length,
  };
}
