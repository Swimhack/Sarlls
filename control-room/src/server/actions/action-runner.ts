import { randomUUID } from 'node:crypto';
import { ACTIONS } from '@shared/actions';
import type { ActionRun } from '@shared/types';
import type { CommandExecutor } from './command-executor';
import { commandFor } from './command-catalog';
import type { ControlRoomRepository } from '../repository';

interface RunningAction {
  cancel: () => void;
  runId: string;
}

export class ActionRunner {
  private readonly running = new Map<string, RunningAction>();

  constructor(
    private readonly executor: CommandExecutor,
    private readonly repository: ControlRoomRepository,
    private readonly config: {
      root: string;
      stateDir: string;
      kicadCli: string;
      kicadPython: string;
      arduinoCli: string;
      gradle: string;
    }
  ) {}

  async start(actionId: string, confirmed: boolean): Promise<ActionRun> {
    const definition = ACTIONS.find((a) => a.id === actionId);
    if (!definition) throw new Error(`Unknown action: ${actionId}`);
    if (definition.mutatesFiles && !confirmed)
      throw new Error('File-changing action requires confirmation');
    if (this.running.has(actionId))
      throw new Error(`Action ${actionId} is already running`);

    // Handle composite run-all-checks
    if (actionId === 'run-all-checks') {
      return this.runAllChecks();
    }

    const runId = randomUUID();
    const run: ActionRun = {
      id: runId,
      actionId,
      status: 'running',
      summary: `Running ${definition.label}...`,
      startedAt: new Date().toISOString(),
    };
    this.repository.addActionRun(run);
    this.repository.addActivity(
      'action.started',
      `Started: ${definition.label}`,
      'running'
    );

    const command = commandFor(actionId, runId, this.config);
    const execution = this.executor.execute(command);
    this.running.set(actionId, { cancel: execution.cancel, runId });

    // Run asynchronously
    execution.result
      .then(({ exitCode, output }) => {
        const status = exitCode === 0 ? 'passed' : 'failed';
        const summary =
          exitCode === 0
            ? `${definition.label} completed successfully`
            : `${definition.label} failed (exit code ${exitCode})`;
        this.repository.updateActionRun(runId, {
          status,
          summary,
          technicalOutput: output.slice(0, 50000),
          finishedAt: new Date().toISOString(),
        });
        this.repository.addActivity('action.finished', summary, status);
      })
      .catch((error: Error) => {
        this.repository.updateActionRun(runId, {
          status: 'failed',
          summary: `${definition.label} error: ${error.message}`,
          technicalOutput: error.stack,
          finishedAt: new Date().toISOString(),
        });
        this.repository.addActivity(
          'action.error',
          `${definition.label} error`,
          'failed'
        );
      })
      .finally(() => {
        this.running.delete(actionId);
      });

    return run;
  }

  cancel(actionId: string): boolean {
    const running = this.running.get(actionId);
    if (!running) return false;
    running.cancel();
    this.repository.updateActionRun(running.runId, {
      status: 'cancelled',
      summary: 'Cancelled by user',
      finishedAt: new Date().toISOString(),
    });
    this.repository.addActivity('action.cancelled', `Cancelled: ${actionId}`, 'cancelled');
    this.running.delete(actionId);
    return true;
  }

  isRunning(actionId: string): boolean {
    return this.running.has(actionId);
  }

  private async runAllChecks(): Promise<ActionRun> {
    const runId = randomUUID();
    const run: ActionRun = {
      id: runId,
      actionId: 'run-all-checks',
      status: 'running',
      summary: 'Running all project checks...',
      startedAt: new Date().toISOString(),
    };
    this.repository.addActionRun(run);
    this.repository.addActivity('action.started', 'Started: Run all checks', 'running');
    this.running.set('run-all-checks', { cancel: () => {}, runId });

    const checks = ['run-drc', 'compile-production-firmware', 'compile-test-firmware', 'run-android-tests'];
    const results: string[] = [];
    let allPassed = true;

    for (const checkId of checks) {
      try {
        const command = commandFor(checkId, `${runId}-${checkId}`, this.config);
        const execution = this.executor.execute(command);
        const { exitCode, output } = await execution.result;
        const passed = exitCode === 0;
        if (!passed) allPassed = false;
        results.push(`${checkId}: ${passed ? 'PASS' : `FAIL (exit ${exitCode})`}`);
        if (output) results.push(output.slice(0, 5000));
      } catch (err: unknown) {
        allPassed = false;
        results.push(`${checkId}: ERROR — ${err instanceof Error ? err.message : String(err)}`);
      }
    }

    const status = allPassed ? 'passed' : 'failed';
    const summary = allPassed ? 'All checks passed' : 'Some checks failed';
    this.repository.updateActionRun(runId, {
      status,
      summary,
      technicalOutput: results.join('\n'),
      finishedAt: new Date().toISOString(),
    });
    this.repository.addActivity('action.finished', summary, status);
    this.running.delete('run-all-checks');
    return { ...run, status, summary, technicalOutput: results.join('\n') };
  }
}
