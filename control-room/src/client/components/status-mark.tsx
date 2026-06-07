import type { ResultStatus } from '@shared/types';

const STATUS_TEXT: Record<ResultStatus, string> = {
  passed: 'Passed',
  failed: 'Failed',
  waiting: 'Waiting',
  blocked: 'Blocked',
  running: 'Running',
  cancelled: 'Cancelled',
  skipped: 'Skipped',
};

export function StatusDot({ status }: { status: ResultStatus }) {
  return (
    <span
      className={`status-dot ${status}`}
      title={STATUS_TEXT[status]}
      aria-label={STATUS_TEXT[status]}
    />
  );
}

export function StatusLabel({ status }: { status: ResultStatus }) {
  return <span className={`status-label ${status}`}>{STATUS_TEXT[status]}</span>;
}
