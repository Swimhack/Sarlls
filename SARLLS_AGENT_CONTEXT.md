# Sarlls SafeSwitch Agent Context

**Last updated:** 2026-06-06

Use `PROJECT_STATUS.md` as the authoritative project status.

## Product

SafeSwitch is intended to remotely disconnect/reconnect a vehicle battery:

`phone/app -> ESP32 controller -> onboard relay -> external 12V contactor -> vehicle battery`

The active PCB is only the USB-C-powered controller prototype. It does not yet
include protected automotive 12V power or the high-current disconnect.

## Current Phase

- Rev 1 physical boards: incomplete bring-up; USB enumeration, flashing, and
  relay operation are not confirmed.
- Rev 2 controller PCB: verified pre-fabrication candidate.
- Android app: UI prototype; no ESP32 communication.
- Production firmware: local-network web/API controller; compiles.

## Rev 2 Release

- PCB generator: `scripts/route_pcb.py`
- DRC gate: `scripts/validate_drc.py`
- Active PCB: `production/ESP32_Simple_IoT.kicad_pcb`
- Gerber ZIP: `production/Sarlls_IoT_Switch_Rev2_JLCPCB.zip`

Do not use `scripts/patch_pcb_rev2.py`; the Rev 2 fixes are now implemented
directly and deterministically in `scripts/route_pcb.py`.

Current DRC gate result:

```text
DRC gate: 0 blocking, 26 approved J1 edge errors, 11 warnings
```

The approved errors are limited to the intentional edge-mounted USB-C contact
row. Do not waive shorts, crossings, unconnected items, ordinary clearances, or
hole-clearance errors.

## Before Ordering Rev 2

1. Confirm the assembler accepts the J1 VBUS via-in-pad escapes.
2. Confirm SW1, SW2, and J2 selected parts match their footprints.
3. Review DFM and placement previews.
4. Confirm BOM availability.

## Required Tools

- KiCad Python:
  `C:\Users\james\AppData\Local\Programs\KiCad\9.0\bin\python.exe`
- KiCad CLI:
  `C:\Users\james\AppData\Local\Programs\KiCad\9.0\bin\kicad-cli.exe`
- Arduino CLI:
  `C:\Users\james\bin\arduino-cli.exe`

The hardware test firmware requires the ESP32 `huge_app` partition.
