import { resolve } from 'node:path';
import { mkdirSync } from 'node:fs';
import type { CommandSpec } from './command-executor';

interface CatalogConfig {
  root: string;
  stateDir: string;
  kicadCli: string;
  kicadPython: string;
  arduinoCli: string;
  gradle: string;
}

export function commandFor(
  actionId: string,
  runId: string,
  config: CatalogConfig
): CommandSpec {
  const runDir = resolve(config.stateDir, 'runs', runId);
  mkdirSync(runDir, { recursive: true });

  switch (actionId) {
    case 'run-drc':
      return {
        executable: config.kicadCli,
        args: [
          'pcb',
          'drc',
          '--format',
          'json',
          '--output',
          resolve(runDir, 'drc.json'),
          '--severity-all',
          resolve(config.root, 'production', 'ESP32_Simple_IoT.kicad_pcb'),
        ],
        cwd: config.root,
      };

    case 'compile-production-firmware':
      return {
        executable: config.arduinoCli,
        args: [
          'compile',
          '--fqbn',
          'esp32:esp32:esp32',
          '--build-path',
          resolve(runDir, 'wifi'),
          resolve(config.root, 'production', 'firmware', 'wifi_switch.ino'),
        ],
        cwd: config.root,
      };

    case 'compile-test-firmware':
      return {
        executable: config.arduinoCli,
        args: [
          'compile',
          '--fqbn',
          'esp32:esp32:esp32:PartitionScheme=huge_app',
          '--build-path',
          resolve(runDir, 'test'),
          resolve(config.root, 'production', 'firmware', 'test_firmware.ino'),
        ],
        cwd: config.root,
      };

    case 'run-android-tests':
      return {
        executable: config.gradle,
        args: ['test'],
        cwd: config.root,
      };

    case 'regenerate-rev2':
      return {
        executable: 'powershell.exe',
        args: [
          '-ExecutionPolicy',
          'Bypass',
          '-File',
          resolve(config.root, 'scripts', 'build_rev2_release.ps1'),
        ],
        cwd: config.root,
      };

    default:
      throw new Error(`Unknown action: ${actionId}`);
  }
}
