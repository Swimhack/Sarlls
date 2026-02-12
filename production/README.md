# ESP32 Simple IoT Switch - Production Files

## Overview

Simplified ESP32-based IoT control board designed to address all issues identified in the Jordan Lake engineering review. This design removes problematic circuits (CAN bus, current sensing, switching converter) and focuses on core functionality: USB-powered ESP32 with single relay output and WiFi/BLE control.

## Design Specifications

| Parameter | Specification |
|-----------|---------------|
| Board Size | 60mm x 40mm |
| Layers | 2-layer |
| Thickness | 1.6mm FR4 |
| Copper | 1oz (35µm) |
| Surface Finish | HASL lead-free |
| Power Input | USB-C 5V |
| Output Voltage | 3.3V (AMS1117) |
| WiFi/BLE | ESP32-WROOM-32 |
| Relay | SRD-05VDC-SL-C (5V coil) |

## Key Design Improvements

Based on Jordan Lake engineering review findings:

1. **All ESP32 GND pins connected to main ground** - Critical fix for proper operation
2. **Solid ground plane on bottom layer** - EMI shielding, low impedance return
3. **Correct flyback diode orientation** - Cathode to 5V, anode to collector
4. **Proper decoupling** - 100nF within 5mm of ESP32 VCC pin
5. **RC delay on EN pin** - 10K pullup + 100nF for reliable startup
6. **Wide power traces** - 20 mil (0.5mm) for power, 10 mil for signal
7. **Antenna keepout zone** - No copper under ESP32 antenna area

## File Structure

```
production/
├── ESP32_Simple_IoT.kicad_pro    # KiCad 6+ project file
├── ESP32_Simple_IoT.kicad_sch    # Schematic
├── ESP32_Simple_IoT.kicad_pcb    # PCB layout
├── ESP32_Simple_IoT_BOM.csv      # Bill of Materials (JLCPCB format)
├── ESP32_Simple_IoT_CPL.csv      # Component Placement List
├── gerbers/                       # Manufacturing Gerber files
│   └── (generate from KiCad)
├── firmware/
│   ├── test_firmware.ino          # Arduino test sketch
│   └── platformio.ini             # PlatformIO configuration
└── README.md                      # This file
```

## Bill of Materials (BOM)

| Ref | Value | Package | LCSC | Qty |
|-----|-------|---------|------|-----|
| U1 | ESP32-WROOM-32 | Module | C82899 | 1 |
| U2 | AMS1117-3.3 | SOT-223 | C6186 | 1 |
| U3 | CP2102N | QFN-28 | C6568 | 1 |
| Q1 | BC817 | SOT-23 | C8664 | 1 |
| K1 | SRD-05VDC-SL-C | Relay | C35449 | 1 |
| D1 | 1N4007 | DO-41 | C727110 | 1 |
| D2 | LED Green | 0805 | C2286 | 1 |
| D3 | LED Red | 0805 | C2286 | 1 |
| C1,C2 | 10µF | 0805 | C15850 | 2 |
| C3,C4,C5 | 100nF | 0805 | C49678 | 3 |
| R1,R2 | 10K | 0805 | C17414 | 2 |
| R3,R4,R5 | 1K | 0805 | C17513 | 3 |
| FB1 | Ferrite Bead | 0805 | C127284 | 1 |
| SW1,SW2 | Tactile | 6x6mm | C127509 | 2 |
| J1 | USB-C | SMD | C165948 | 1 |
| J2 | Terminal 2-pos | 3.81mm | C8269 | 1 |

**Total: 23 components**

## Manufacturing Instructions

### 1. Generate Gerber Files

In KiCad:
1. Open `ESP32_Simple_IoT.kicad_pcb`
2. File → Plot → Gerber
3. Select layers: F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, F.SilkS, Edge.Cuts
4. Click "Plot" then "Generate Drill Files"
5. Output goes to `gerbers/` folder

### 2. JLCPCB Order

1. Go to [jlcpcb.com](https://jlcpcb.com)
2. Upload Gerber ZIP from `gerbers/` folder
3. Settings:
   - Layers: 2
   - Size: 60 x 40 mm
   - Thickness: 1.6mm
   - Copper: 1oz
   - Surface: HASL lead-free
   - Soldermask: Green
   - Silkscreen: White
4. Enable SMT Assembly
5. Upload `ESP32_Simple_IoT_BOM.csv` and `ESP32_Simple_IoT_CPL.csv`
6. Review placement preview
7. Order (minimum 5 boards)

Estimated cost: $50-80 for 5 boards + assembly

### 3. DFM Check

Before ordering, verify:
- [ ] Run KiCad DRC - zero errors
- [ ] Run KiCad ERC - zero errors
- [ ] All LCSC parts in stock
- [ ] Gerber preview looks correct
- [ ] Component placement matches preview

## Testing Procedure

### Power Tests

| Test | Expected | Pass Criteria |
|------|----------|---------------|
| USB 5V | 5V on VBUS | ±5% (4.75-5.25V) |
| 3.3V rail | 3.3V on ESP32 VCC | ±3% (3.2-3.4V) |
| Idle current | <100mA | Measure at USB |
| Relay current | +70mA when active | Total <170mA |

### Functional Tests

1. **USB-UART**: Connect USB, should enumerate as serial port
2. **Serial**: Open terminal at 115200 baud, see boot messages
3. **WiFi**: Test firmware scans and lists networks
4. **BLE**: Advertises as "ESP32_IoT_Switch"
5. **Relay**: Toggles every 2 seconds with audible click
6. **LEDs**: Power LED on, relay LED follows relay state
7. **Buttons**: BOOT button triggers relay, RESET restarts

### Test Firmware

Upload `firmware/test_firmware.ino` using:

**Arduino IDE:**
1. Install ESP32 board package
2. Select "ESP32 Dev Module"
3. Upload at 115200 baud

**PlatformIO:**
1. Open `firmware/` folder
2. Run `pio run -t upload`

## Schematic Block Diagram

```
USB-C (5V)
    │
    └─►[Ferrite]─►[10µF]─►[AMS1117]─►[10µF+100nF]─►[3.3V]
                              │                        │
                          [5V Rail]              [ESP32-WROOM-32]
                              │                        │
                         [CP2102N]◄───────────────[TX/RX]
                              │                        │
                         [USB D+/D-]              [GPIO4]─►[1K]─►[BC817]─►[Relay]
                                                       │              │
                                                   [Status LEDs]  [1N4007]
```

## Known Limitations

1. **No 12V input**: USB-C only (5V), designed for prototype simplicity
2. **Single relay**: Expandable in future revisions
3. **No CAN bus**: Removed due to complexity issues in original design
4. **No current sensing**: Removed due to op-amp voltage mismatch

## Revision History

| Rev | Date | Changes |
|-----|------|---------|
| 1.0 | 2026-01-16 | Initial simplified design |
| 1.1 | 2026-02-11 | Complete schematic wiring: 34 wire connections, 4 net labels, 8 junctions, 3 no-connect flags. Fixed D1 flyback diode rotation (90->270) for correct polarity. Fixed D2 LED rotation (180->0) for forward bias. Fixed D3 LED rotation (0->180) for forward bias. Added R5 component to schematic. PCB still needs interactive routing in KiCad. |

## Support

For issues or questions, refer to the original Jordan Lake engineering review for context on design decisions.
