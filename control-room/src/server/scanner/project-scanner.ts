import { resolve } from 'node:path';
import type { GateResult, ProjectSnapshot, WorkstreamSummary } from '@shared/types';
import { REV2_ORDER_GATE_IDS, VEHICLE_GATE_IDS } from '@shared/gates';
import { deriveReadiness } from '@server/readiness/derive-readiness';
import { parseDrcReport } from './drc';
import { parseBom, parseCpl } from './csv';
import { inspectGerberZip } from './gerber';
import { inspectFile } from './documents';
import type { ControlRoomRepository } from '../repository';

const HUMAN_GATE_LABELS: Record<string, string> = {
  usb_approval: 'Manufacturer approval for USB-C via-in-pad escapes',
  sw1: 'SW1 part-footprint match confirmed',
  sw2: 'SW2 part-footprint match confirmed',
  j2: 'J2 part-footprint match confirmed',
  dfm_preview: 'DFM/placement preview reviewed',
  manufacturer_warnings: 'Manufacturer warnings addressed',
  controller_hardware: 'Controller hardware validated',
  app_device_control: 'App-to-device control working',
  protected_12v: 'Protected 12V input verified',
  contactor_operation: 'Contactor operation confirmed',
  bench_safety: 'Bench safety test passed',
  safety_blockers: 'All safety blockers resolved',
};

export async function scanProject(
  root: string,
  repository: ControlRoomRepository
): Promise<ProjectSnapshot> {
  const prod = resolve(root, 'production');

  // Run automatic scans in parallel
  const [drc, bom, cpl, gerber] = await Promise.all([
    parseDrcReport(resolve(prod, 'drc_report.json')).catch(() => ({
      blocking: -1,
      approvedJ1EdgeErrors: 0,
      warnings: 0,
      totalViolations: 0,
    })),
    parseBom(resolve(prod, 'ESP32_Simple_IoT_BOM.csv')).catch(() => ({
      lineItems: 0,
      valid: false,
      headers: '',
    })),
    parseCpl(resolve(prod, 'ESP32_Simple_IoT_CPL.csv')).catch(() => ({
      placements: 0,
      valid: false,
      headers: '',
    })),
    inspectGerberZip(resolve(prod, 'Sarlls_IoT_Switch_Rev2_JLCPCB.zip')).catch(
      () => ({ valid: false, fileCount: 0, missing: [] as string[], unexpected: [] as string[] })
    ),
  ]);

  // Build automatic gates
  const automaticGates: GateResult[] = [
    {
      id: 'drc',
      label: 'Board design checks (DRC)',
      status: drc.blocking === 0 ? 'passed' : drc.blocking < 0 ? 'blocked' : 'failed',
      source: 'automatic',
      blocking: true,
      summary:
        drc.blocking === 0
          ? `0 blocking, ${drc.approvedJ1EdgeErrors} approved J1 edge errors, ${drc.warnings} warnings`
          : drc.blocking < 0
            ? 'DRC report not found'
            : `${drc.blocking} blocking findings`,
    },
    {
      id: 'bom_cpl',
      label: 'BOM and placement files',
      status: bom.valid && cpl.valid ? 'passed' : 'failed',
      source: 'automatic',
      blocking: true,
      summary: `${bom.lineItems} BOM lines, ${cpl.placements} placements`,
    },
    {
      id: 'gerber_zip',
      label: 'Manufacturing Gerber ZIP',
      status: gerber.valid ? 'passed' : 'failed',
      source: 'automatic',
      blocking: true,
      summary: gerber.valid
        ? `${gerber.fileCount} expected files`
        : `Missing: ${gerber.missing.join(', ') || 'none'}; Unexpected: ${gerber.unexpected.join(', ') || 'none'}`,
    },
  ];

  // Build human gates — load from DB or default to waiting
  const allHumanIds = [
    ...REV2_ORDER_GATE_IDS.filter(
      (id) => !['drc', 'bom_cpl', 'gerber_zip'].includes(id)
    ),
    ...VEHICLE_GATE_IDS,
  ];

  const humanGates: GateResult[] = allHumanIds.map((id) => {
    const workflow = repository.getWorkflow(id);
    if (workflow) {
      return {
        id,
        label: HUMAN_GATE_LABELS[id] ?? id,
        status: workflow.status,
        source: 'human' as const,
        blocking: true,
        summary: workflow.notes || undefined,
        updatedAt: workflow.updatedAt,
      };
    }
    return {
      id,
      label: HUMAN_GATE_LABELS[id] ?? id,
      status: 'waiting' as const,
      source: 'human' as const,
      blocking: true,
    };
  });

  const gates = [...automaticGates, ...humanGates];
  const readiness = deriveReadiness(gates);

  // Build workstream summaries
  const workstreams: WorkstreamSummary[] = [
    {
      id: 'pcb',
      label: 'PCB Design',
      summary: drc.blocking === 0 ? 'DRC passing' : 'DRC issues remain',
      gates: gates.filter((g) =>
        ['drc', 'bom_cpl', 'gerber_zip'].includes(g.id)
      ),
    },
    {
      id: 'ordering',
      label: 'Rev2 Ordering',
      summary: readiness.rev2ReadyToOrder
        ? 'Ready to order'
        : `${readiness.completedRequired}/${readiness.totalRequired} gates passed`,
      gates: gates.filter((g) =>
        (REV2_ORDER_GATE_IDS as readonly string[]).includes(g.id)
      ),
    },
    {
      id: 'hardware',
      label: 'Hardware Bring-Up',
      summary: 'Physical testing required',
      gates: gates.filter((g) => g.id === 'controller_hardware'),
    },
    {
      id: 'firmware',
      label: 'Firmware',
      summary: 'Compile and flash validation',
      gates: [],
    },
    {
      id: 'mobile',
      label: 'Mobile App',
      summary: 'UI prototype — no device connectivity yet',
      gates: gates.filter((g) => g.id === 'app_device_control'),
    },
    {
      id: 'automotive',
      label: 'Automotive Integration',
      summary: 'Pending controller validation',
      gates: gates.filter((g) =>
        ['protected_12v', 'contactor_operation', 'bench_safety', 'safety_blockers'].includes(g.id)
      ),
    },
  ];

  const recentRuns = repository.listRecentRuns(10);

  return {
    scannedAt: new Date().toISOString(),
    readiness,
    gates,
    workstreams,
    recentRuns,
  };
}

export async function scanFiles(root: string) {
  const prod = resolve(root, 'production');
  const files = await Promise.all([
    inspectFile(resolve(prod, 'ESP32_Simple_IoT.kicad_pcb'), 'PCB Layout', true),
    inspectFile(resolve(prod, 'ESP32_Simple_IoT.kicad_sch'), 'Schematic', true),
    inspectFile(resolve(prod, 'ESP32_Simple_IoT_BOM.csv'), 'Bill of Materials', true),
    inspectFile(resolve(prod, 'ESP32_Simple_IoT_CPL.csv'), 'Component Placement', true),
    inspectFile(resolve(prod, 'drc_report.json'), 'DRC Report', true),
    inspectFile(resolve(prod, 'Sarlls_IoT_Switch_Rev2_JLCPCB.zip'), 'Rev2 JLCPCB Package', true),
    inspectFile(resolve(prod, 'FABRICATION_SPEC.txt'), 'Fabrication Spec', true),
    inspectFile(resolve(prod, 'firmware/wifi_switch.ino'), 'Production Firmware', true),
    inspectFile(resolve(prod, 'firmware/test_firmware.ino'), 'Test Firmware', true),
    inspectFile(resolve(prod, 'firmware/platformio.ini'), 'PlatformIO Config', true),
    inspectFile(resolve(prod, 'ESP32_Simple_IoT.step'), '3D STEP Model', false),
    inspectFile(resolve(prod, 'ESP32_Simple_IoT_3D.glb'), '3D Web Model', false),
    inspectFile(resolve(prod, 'ESP32_MacroFab_Gerbers.zip'), 'MacroFab Gerbers (legacy)', false),
    inspectFile(resolve(prod, 'ESP32_Simple_IoT_Gerbers_PCBWay.zip'), 'PCBWay Gerbers (legacy)', false),
    inspectFile(resolve(prod, 'Sarlls_IoT_Switch_v1.2_JLCPCB.zip'), 'Rev 1.2 JLCPCB (previous)', false),
  ]);
  return files;
}
