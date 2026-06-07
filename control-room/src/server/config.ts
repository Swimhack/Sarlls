import { resolve } from 'node:path';

export function createConfig(root = resolve('..')) {
  return {
    root,
    stateDir: resolve(root, '.control-room'),
    databasePath: resolve(root, '.control-room', 'control-room.db'),
    kicadPython:
      process.env.KICAD_PYTHON ??
      'C:\\Users\\james\\AppData\\Local\\Programs\\KiCad\\9.0\\bin\\python.exe',
    kicadCli:
      process.env.KICAD_CLI ??
      'C:\\Users\\james\\AppData\\Local\\Programs\\KiCad\\9.0\\bin\\kicad-cli.exe',
    arduinoCli:
      process.env.ARDUINO_CLI ?? 'C:\\Users\\james\\bin\\arduino-cli.exe',
    gradle: resolve(root, 'gradlew.bat'),
  };
}
