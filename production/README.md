# ESP32 Simple IoT Switch - Rev 2 Controller Prototype

This directory contains the active SafeSwitch controller-board manufacturing
candidate. It is a USB-C-powered ESP32 relay controller used to validate the
control path before developing the complete automotive battery-disconnect
system.

## Board

| Parameter | Value |
|---|---|
| Size | 80 mm x 60 mm |
| Layers | 2 |
| Thickness | 1.6 mm FR-4 |
| Copper | 1 oz |
| Input | USB-C 5V |
| Logic | ESP32-WROOM-32, CP2102N USB-UART |
| Output | 5V relay dry contacts on J2 |

## Manufacturing Files

- `ESP32_Simple_IoT.kicad_pcb`: active generated PCB
- `ESP32_Simple_IoT_BOM.csv`: JLCPCB BOM, 20 line items
- `ESP32_Simple_IoT_CPL.csv`: placement list, 28 placements
- `ESP32_Simple_IoT_Gerbers.zip`: clean fabrication ZIP
- `Sarlls_IoT_Switch_Rev2_JLCPCB.zip`: identical Rev 2 fabrication ZIP
- `drc_report.json`: production DRC report

The fabrication ZIP contains only copper, mask, top paste, silkscreen, edge,
job, PTH drill, and NPTH drill files.

## DRC Status

Run `scripts/validate_drc.py` after every DRC export. Current expected result:

```text
DRC gate: 0 blocking, 26 approved J1 edge errors, 11 warnings
```

The 26 approved errors are limited to the intentional edge-mounted USB-C
contact row. Shorts, crossings, unconnected items, ordinary clearances, and
hole-clearance errors block release.

## Before Ordering

1. Confirm the assembler accepts the two small J1 VBUS via-in-pad escapes.
2. Confirm SW1, SW2, and J2 selected parts match their footprints.
3. Review the assembler DFM report and placement preview.
4. Confirm all BOM parts are available.

## Firmware

- `firmware/wifi_switch.ino`: local WiFi web/API controller; default ESP32
  partition.
- `firmware/test_firmware.ino`: hardware test image; requires the `huge_app`
  partition.

Rev 1 physical boards have not yet completed USB enumeration, flashing, and
relay bring-up. Rev 2 is therefore a pre-fabrication candidate, not a validated
production board.
