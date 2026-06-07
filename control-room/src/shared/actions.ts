export interface ActionDefinition {
  id: string;
  label: string;
  description: string;
  mutatesFiles: boolean;
  cancellable: boolean;
}

export const ACTIONS: ActionDefinition[] = [
  {
    id: 'run-all-checks',
    label: 'Run all checks',
    description: 'Check PCB files, firmware, and Android app.',
    mutatesFiles: false,
    cancellable: true
  },
  {
    id: 'run-drc',
    label: 'Run PCB check',
    description: 'Run KiCad DRC and the blocking gate.',
    mutatesFiles: false,
    cancellable: true
  },
  {
    id: 'compile-production-firmware',
    label: 'Compile production firmware',
    description: 'Compile the WiFi controller firmware.',
    mutatesFiles: false,
    cancellable: true
  },
  {
    id: 'compile-test-firmware',
    label: 'Compile hardware-test firmware',
    description: 'Compile the hardware test image with huge_app.',
    mutatesFiles: false,
    cancellable: true
  },
  {
    id: 'run-android-tests',
    label: 'Run Android tests',
    description: 'Run the Gradle test task.',
    mutatesFiles: false,
    cancellable: true
  },
  {
    id: 'regenerate-rev2',
    label: 'Regenerate Rev2 manufacturing files',
    description: 'Replace production PCB and manufacturing artifacts.',
    mutatesFiles: true,
    cancellable: false
  }
];
