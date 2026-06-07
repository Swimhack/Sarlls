import { spawn } from 'node:child_process';

export interface CommandSpec {
  executable: string;
  args: string[];
  cwd: string;
}

export interface ExecutionHandle {
  cancel: () => void;
  result: Promise<{ exitCode: number; output: string }>;
}

export class CommandExecutor {
  execute(spec: CommandSpec): ExecutionHandle {
    const child = spawn(spec.executable, spec.args, {
      cwd: spec.cwd,
      windowsHide: true,
      shell: false,
    });
    let output = '';
    child.stdout.on('data', (chunk: Buffer) => {
      output += chunk.toString();
    });
    child.stderr.on('data', (chunk: Buffer) => {
      output += chunk.toString();
    });
    return {
      cancel: () => child.kill(),
      result: new Promise<{ exitCode: number; output: string }>(
        (resolve, reject) => {
          child.on('error', reject);
          child.on('close', (exitCode) =>
            resolve({ exitCode: exitCode ?? -1, output })
          );
        }
      ),
    };
  }
}
