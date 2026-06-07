import { describe, expect, it } from 'vitest';
import { deriveReadiness } from '@server/readiness/derive-readiness';
import type { GateResult } from '@shared/types';

const pass = (id: string): GateResult => ({
  id,
  label: id,
  status: 'passed',
  source: 'automatic',
  blocking: true
});

describe('deriveReadiness', () => {
  it('keeps Rev2 blocked while a manufacturer gate is waiting', () => {
    const result = deriveReadiness([
      pass('drc'),
      pass('bom_cpl'),
      pass('gerber_zip'),
      {
        id: 'usb_approval',
        label: 'USB approval',
        status: 'waiting',
        source: 'human',
        blocking: true
      }
    ]);

    expect(result.rev2ReadyToOrder).toBe(false);
    expect(result.nextAction?.id).toBe('usb_approval');
  });

  it('marks Rev2 ready only when every required gate passes', () => {
    const required = [
      'drc',
      'bom_cpl',
      'gerber_zip',
      'usb_approval',
      'sw1',
      'sw2',
      'j2',
      'dfm_preview',
      'manufacturer_warnings'
    ];
    const result = deriveReadiness(required.map(pass));

    expect(result.rev2ReadyToOrder).toBe(true);
    expect(result.phase).toBe('controller_ready_to_order');
  });
});
