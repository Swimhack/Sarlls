# SafeSwitch IoT Smart Switch — Production Handoff

**Date:** 2026-08-03
**Revision:** Rev 2 (D1 clearance fix)
**Client:** Eric Sarll
**Project:** 12V vehicle battery disconnect with WiFi/BLE control

## Changes from Rev 1.2

- **D1 flyback diode moved** from (30, 40) to (30, 34) — was physically under K1 relay, preventing flush seating
- USB-C connector (J1) orientation verified correct for edge-mount

## Folder Structure

```
handoff/
├── manufacturing/       PCB fabrication & assembly files
│   ├── ESP32_Simple_IoT.kicad_pcb    KiCad board file
│   ├── ESP32_Simple_IoT.kicad_sch    Schematic
│   ├── ESP32_Simple_IoT_BOM.csv      Bill of Materials
│   ├── ESP32_Simple_IoT_CPL.csv      Component Placement List
│   ├── ESP32_Simple_IoT_Gerbers.zip  Gerber files
│   ├── Sarlls_IoT_Switch_v1.2_JLCPCB.zip  JLCPCB submission package
│   ├── FABRICATION_SPEC.txt          Fab specifications
│   ├── drc_report.json               Design Rule Check results
│   └── erc_report.json               Electrical Rule Check results
├── firmware/            ESP32 firmware
│   ├── wifi_switch.ino               WiFi remote on/off v1.5
│   └── platformio.ini                Build configuration
├── assembly/            Assembly instructions & notes
│   └── ASSEMBLY_NOTES.md             Board assembly guide
├── testing/             Test procedures
│   └── TEST_PROCEDURES.md            Hardware test checklist
├── 3d/                  3D models & viewer
│   ├── ESP32_Simple_IoT_3D.glb       3D model (GLTF binary)
│   ├── ESP32_Simple_IoT.step         STEP file for CAD
│   └── 3d_viewer.html                Browser-based 3D viewer
├── app/                 Android application
│   └── Safe Switch.apk               SafeSwitch Android app
└── docs/                Project documentation
    └── BILL_OF_MATERIALS.md           Annotated BOM with sourcing
```

## Key Specifications

| Parameter | Value |
|-----------|-------|
| Board Size | 80mm x 60mm |
| Layers | 2 (F.Cu, B.Cu) |
| MCU | ESP32-WROOM-32 |
| USB-UART | CP2102N (QFN-28) |
| Power Input | USB-C (5V) |
| Relay | SANYOU SRD-05VDC-SL-C (SPDT, 10A) |
| Flyback Diode | 1N4007 (DO-41) — moved to clear relay |
| Status LEDs | Power (D2), Relay (D3) |
| Buttons | BOOT (SW1/IO0), RESET (SW2/EN) |
| Connector | Phoenix Contact MC 1,5/2-G-3.81mm (J2) |

## Manufacturing Notes

- **Fabricator:** JLCPCB (recommended)
- **Assembly:** SMT + through-hole (K1, D1, J2 are THT)
- **D1 CRITICAL:** Verify D1 does NOT overlap K1 relay footprint. Min 6mm clearance required.
- **J1 USB-C:** Edge-mount, verify connector opening faces board edge (outward)

## Firmware Flashing

1. Connect USB-C data cable
2. Install CP2102N drivers if needed
3. Hold BOOT (SW1), press RESET (SW2), release BOOT
4. Flash via Arduino IDE or PlatformIO: `pio run -t upload`

## Online 3D Viewer

http://137.184.136.55/sarlls-3d/
