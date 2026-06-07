import { stat } from 'node:fs/promises';

export interface FileInfo {
  path: string;
  label: string;
  authoritative: boolean;
  exists: boolean;
  size: number;
  modifiedAt?: string;
}

export async function inspectFile(
  path: string,
  label: string,
  authoritative = true
): Promise<FileInfo> {
  try {
    const details = await stat(path);
    return {
      path,
      label,
      authoritative,
      exists: true,
      size: details.size,
      modifiedAt: details.mtime.toISOString(),
    };
  } catch {
    return { path, label, authoritative, exists: false, size: 0 };
  }
}
