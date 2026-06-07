export const REV2_ORDER_GATE_IDS = [
  'drc',
  'bom_cpl',
  'gerber_zip',
  'usb_approval',
  'sw1',
  'sw2',
  'j2',
  'dfm_preview',
  'manufacturer_warnings'
] as const;

export const VEHICLE_GATE_IDS = [
  'controller_hardware',
  'app_device_control',
  'protected_12v',
  'contactor_operation',
  'bench_safety',
  'safety_blockers'
] as const;
