import { readFile } from 'node:fs/promises';

function rows(text: string) {
  return text
    .trim()
    .split(/\r?\n/)
    .filter(Boolean);
}

export interface BomResult {
  lineItems: number;
  valid: boolean;
  headers: string;
}

export interface CplResult {
  placements: number;
  valid: boolean;
  headers: string;
}

export async function parseBom(path: string): Promise<BomResult> {
  const data = rows(await readFile(path, 'utf8'));
  const headers = data[0] ?? '';
  return {
    lineItems: Math.max(0, data.length - 1),
    valid: headers.includes('Designator') && headers.includes('LCSC Part Number'),
    headers,
  };
}

export async function parseCpl(path: string): Promise<CplResult> {
  const data = rows(await readFile(path, 'utf8'));
  const headers = data[0] ?? '';
  return {
    placements: Math.max(0, data.length - 1),
    valid: headers.includes('Mid X') && headers.includes('Rotation'),
    headers,
  };
}
