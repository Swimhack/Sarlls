import AdmZip from 'adm-zip';

const REQUIRED = new Set([
  'ESP32_Simple_IoT-F_Cu.gtl',
  'ESP32_Simple_IoT-B_Cu.gbl',
  'ESP32_Simple_IoT-F_Mask.gts',
  'ESP32_Simple_IoT-B_Mask.gbs',
  'ESP32_Simple_IoT-F_Paste.gtp',
  'ESP32_Simple_IoT-F_Silkscreen.gto',
  'ESP32_Simple_IoT-B_Silkscreen.gbo',
  'ESP32_Simple_IoT-Edge_Cuts.gm1',
  'ESP32_Simple_IoT-PTH.drl',
  'ESP32_Simple_IoT-NPTH.drl',
  'ESP32_Simple_IoT-job.gbrjob',
]);

export interface GerberResult {
  valid: boolean;
  fileCount: number;
  missing: string[];
  unexpected: string[];
}

export async function inspectGerberZip(path: string): Promise<GerberResult> {
  const names = new AdmZip(path)
    .getEntries()
    .filter((entry) => !entry.isDirectory)
    .map((entry) => entry.entryName);
  const missing = [...REQUIRED].filter((name) => !names.includes(name));
  const unexpected = names.filter((name) => !REQUIRED.has(name));
  return {
    valid: missing.length === 0 && unexpected.length === 0,
    fileCount: names.length,
    missing,
    unexpected,
  };
}
