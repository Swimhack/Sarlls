import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { parseBom, parseCpl } from '@server/scanner/csv';
import { parseDrcReport } from '@server/scanner/drc';
import { inspectFile } from '@server/scanner/documents';
import { inspectGerberZip } from '@server/scanner/gerber';

const repoRoot = resolve(process.cwd(), '..');
const productionRoot = resolve(repoRoot, 'production');

describe('project scanners', () => {
  it('reads the current DRC report and approved J1 exceptions', async () => {
    const result = await parseDrcReport(resolve(productionRoot, 'drc_report.json'));

    expect(result.blocking).toBe(0);
    expect(result.approvedJ1EdgeErrors).toBe(26);
    expect(result.warnings).toBe(11);
    expect(result.totalViolations).toBeGreaterThanOrEqual(37);
  });

  it('counts BOM and CPL records from the production exports', async () => {
    const bom = await parseBom(resolve(productionRoot, 'ESP32_Simple_IoT_BOM.csv'));
    const cpl = await parseCpl(resolve(productionRoot, 'ESP32_Simple_IoT_CPL.csv'));

    expect(bom.valid).toBe(true);
    expect(bom.lineItems).toBe(20);
    expect(cpl.valid).toBe(true);
    expect(cpl.placements).toBe(28);
  });

  it('validates the Rev2 manufacturing ZIP package', async () => {
    const result = await inspectGerberZip(
      resolve(productionRoot, 'Sarlls_IoT_Switch_Rev2_JLCPCB.zip')
    );

    expect(result.valid).toBe(true);
    expect(result.fileCount).toBe(11);
    expect(result.missing).toEqual([]);
    expect(result.unexpected).toEqual([]);
  });

  it('reports an existing authoritative project file', async () => {
    const file = await inspectFile(
      resolve(productionRoot, 'ESP32_Simple_IoT.kicad_pcb'),
      'PCB Layout',
      true
    );

    expect(file.exists).toBe(true);
    expect(file.authoritative).toBe(true);
    expect(file.size).toBeGreaterThan(0);
  });
});
