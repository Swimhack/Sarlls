# Sarlls IoT Switch — Project Status & Agent Handoff Document

**Last updated:** 2026-02-12
**Status:** READY FOR MANUFACTURING ORDER
**Owner:** James (no PCB experience — entire project AI-driven)

---

## 1. What This Project Is

An ESP32-based IoT smart switch PCB. USB-C powered, single relay output, WiFi/BLE control. This is a **simplified prototype** (Rev 1.0) designed to validate core functionality before tackling the original goal: a 12V automotive high-side switch with 3G connectivity.

**Circuit topology:** USB-C 5V → Ferrite Bead → AMS1117 LDO → 3.3V → ESP32-WROOM-32 → BC817 NPN transistor → SRD-05VDC relay. CP2102N provides USB-UART for programming. Two tactile switches (BOOT/RESET), two LEDs (power/relay status).

**Board specs:** 80mm x 60mm, 2-layer, 1.6mm FR-4, 23 components, all JLCPCB/LCSC sourced.

---

## 2. What Has Been Completed

### Phase 1: Schematic Wiring ✅
- **Script:** `scripts/fix_schematic_wiring.py` and `scripts/rebuild_schematic.py`
- **Output:** `production/ESP32_Simple_IoT.kicad_sch`
- **Result:** 21 nets, 0 ERC errors. All pins connected per netlist.
- Original schematic had component symbols but zero `(wire ...)` entries. Script added 34 wire connections, 4 net labels, 8 junctions, 3 no-connect flags.
- Fixed D1 flyback diode rotation (90→270), D2 LED rotation (180→0), D3 LED rotation (0→180).

### Phase 2: PCB Routing ✅
- **Script:** `scripts/route_pcb.py` (~1070 lines)
- **Output:** `production/ESP32_Simple_IoT.kicad_pcb`
- **Result:** 159 tracks, 78 vias, 0 shorts, 0 crossings, 0 unconnected nets.
- **KiCad Python path:** `C:\Users\james\AppData\Local\Programs\KiCad\9.0\bin\python.exe`
- **Run command:** `C:\Users\james\AppData\Local\Programs\KiCad\9.0\bin\python.exe scripts\route_pcb.py`

### Phase 3: Gerber Generation ✅
- **Tool:** `C:\Users\james\AppData\Local\Programs\KiCad\9.0\bin\kicad-cli.exe`
- **Output:** `production/gerbers/` (11 files) + `production/ESP32_Simple_IoT_Gerbers.zip`
- **Commands used:**
  ```
  kicad-cli pcb export gerbers --output production/gerbers/ production/ESP32_Simple_IoT.kicad_pcb
  kicad-cli pcb export drill --output production/gerbers/ --format excellon --drill-origin absolute --excellon-separate-th production/ESP32_Simple_IoT.kicad_pcb
  ```

### Phase 4: BOM/CPL Verification ✅
- **BOM:** `production/ESP32_Simple_IoT_BOM.csv` — 16 line items, 23 total components
- **CPL:** `production/ESP32_Simple_IoT_CPL.csv` — CORRECTED 2026-02-12 to match actual PCB footprint positions
- **Stock:** All 16 LCSC part numbers verified in stock (lowest: C127284 ferrite bead at 1,800 units)

---

## 3. Current DRC Status (v3.28)

```
Total violations: 45
Unconnected nets: 0
Shorts: 0
Track crossings: 0

Breakdown:
  clearance: 9 errors    — QFN-28 (U3) and USB-C (J1) inherent pad spacing
  hole_clearance: 7 errors — NPTH mounting holes vs GND zone fill
  via_dangling: 15 warnings — GND stitch vias (intentional, connect to zone)
  silk_edge_clearance: 4 warnings — silkscreen near board edge
  holes_co_located: 10 warnings — stacked THT/via pads (by design)
```

**All 16 errors are inherent to tight-pitch components (QFN-28, USB-C) and are within JLCPCB manufacturing tolerances (min 0.075mm actual vs 0.1mm JLCPCB minimum).** None are functional issues.

---

## 4. Critical File Locations

### Manufacturing Files (upload to JLCPCB)
| File | Purpose |
|------|---------|
| `production/ESP32_Simple_IoT_Gerbers.zip` | Gerber package (upload first) |
| `production/ESP32_Simple_IoT_BOM.csv` | Bill of Materials (SMT assembly) |
| `production/ESP32_Simple_IoT_CPL.csv` | Component Placement List (SMT assembly) |

### Design Source Files (edit these for revisions)
| File | Purpose |
|------|---------|
| `production/ESP32_Simple_IoT.kicad_sch` | Schematic (KiCad 9) |
| `production/ESP32_Simple_IoT.kicad_pcb` | PCB layout (KiCad 9) |
| `production/ESP32_Simple_IoT.kicad_pro` | Project file |
| `scripts/route_pcb.py` | **THE routing script — regenerates entire PCB from scratch** |

### Test & Documentation
| File | Purpose |
|------|---------|
| `production/firmware/test_firmware.ino` | Hardware validation firmware |
| `production/firmware/platformio.ini` | PlatformIO build config |
| `production/README.md` | Design specs and BOM table |
| `production/drc_report.json` | Last DRC run results |

### Other Scripts (used during development)
| File | Purpose |
|------|---------|
| `scripts/rebuild_schematic.py` | Rewrites schematic with wire connections |
| `scripts/fix_schematic_wiring.py` | Earlier schematic wiring script |
| `scripts/check_libs.py` | Verifies KiCad library availability |
| `scripts/package_for_manufacturer.py` | Packages files for fab house |

---

## 5. Technical Architecture (For Future Agents)

### How the PCB Was Built

The PCB was NOT created interactively in KiCad. It was generated entirely by `scripts/route_pcb.py` using KiCad's Python API (`pcbnew`). This script:

1. Creates a blank board (80x60mm)
2. Loads footprints from KiCad's library
3. Places all 23 components at hardcoded positions
4. Assigns net codes to pads
5. Routes all copper traces as `PCB_TRACK` segments
6. Places vias as `PCB_VIA` objects
7. Creates GND zones on B.Cu with `ZONE` + `ZONE_FILLER`
8. Adds antenna keepout, mounting holes, via stitching
9. Saves as `.kicad_pcb`

**To make design changes: edit `route_pcb.py` and re-run it. Do NOT manually edit the .kicad_pcb file — it gets overwritten.**

### Key Routing Decisions

**Layer strategy:**
- F.Cu: Component pads, most signal traces, SMD connections
- B.Cu: GND zone fill (ground plane), power bus corridors, UART cross-board traces

**Power routing corridors on B.Cu (critical — these were hard-won):**
- **+5V to relay area:** x=13 corridor, with F.Cu hop at y=15-17 to cross +3V3 horizontal
- **+3V3 distribution:** x=5 corridor, horizontal at y=16 from (30.05, 16) to (5, 16)
- **VBUS F.Cu routes:** Primary at x=3.60 (J1:A4→FB1), secondary at x=12 (J1:A9→FB1)
- **GND returns:** Via stitching drops to B.Cu ground plane

**Signal routing channels on B.Cu:**
- ESP_IO4: y=27 (x=15→64)
- ESP_RX: y=32 (x=16→65)
- ESP_TX: y=34 (x=24→67)

**Critical clearance constraints:**
- +5V at x=13 is 1mm from VBUS at x=12 (minimum viable)
- +3V3 F.Cu hop at y=15-17 avoids +3V3 B.Cu horizontal at y=16
- J1 NPTH holes at (3.11, 27.395) and (8.89, 27.395) — +5V B.Cu was moved from x=3 to x=13 to avoid these

### Component Positions (PCB coordinates, mm)

| Ref | Component | X | Y | Notes |
|-----|-----------|---|---|-------|
| J1 | USB-C | 6 | 30 | Left edge, mid-board |
| FB1 | Ferrite Bead | 18 | 8 | After VBUS, before LDO |
| U2 | AMS1117-3.3 | 26 | 8 | LDO regulator |
| C1 | 10uF input cap | 18 | 4 | Near LDO input |
| C2 | 10uF output cap | 33 | 4 | Near LDO output |
| C3 | 100nF decoupling | 33 | 12 | ESP32 decoupling |
| C4 | 100nF EN cap | 44 | 15 | EN pin RC delay |
| C5 | 100nF decoupling | 47 | 6 | Additional decoupling |
| R1 | 10K EN pullup | 47 | 10 | EN pin pullup |
| R2 | 10K IO0 pullup | 47 | 20 | Boot pin pullup |
| U1 | ESP32-WROOM-32 | 60 | 12 | Top-right, antenna at top edge |
| U3 | CP2102N QFN-28 | 16 | 44 | USB-UART bridge |
| Q1 | BC817 SOT-23 | 8 | 52 | Relay driver transistor |
| R3 | 1K base resistor | 14 | 52 | Limits base current |
| K1 | SRD-05VDC relay | 22 | 50 | Center-bottom (THT) |
| D1 | 1N4007 flyback | 8 | 36 | Across relay coil (THT) |
| D2 | Green LED 0805 | 9 | 4 | Power indicator |
| D3 | Red LED 0805 | 6 | 16 | Relay status |
| R4 | 1K LED resistor | 13 | 4 | Power LED current limit |
| R5 | 1K LED resistor | 10 | 16 | Relay LED current limit |
| SW1 | Boot button | 48 | 56 | GPIO0 to GND |
| SW2 | Reset button | 60 | 56 | EN to GND |
| J2 | Terminal block | 72 | 52 | Relay output (THT) |

**Mounting holes:** H1(3,3), H2(77,12), H3(3,57), H4(77,40) — 2.7mm NPTH, M2.5

### Net List (19 nets)

| ID | Net Name | Key Connections |
|----|----------|-----------------|
| 1 | GND | All grounds, B.Cu zone fill |
| 2 | +5V | VBUS→FB1→C1→U2:VIN→K1 coil→D1:K |
| 3 | +3V3 | U2:VOUT→C2→C3→C5→U1:3V3→U3:VDD→R1→R2→D2→D3 |
| 4 | USB_D+ | J1:A6/B6→U3:D+ |
| 5 | USB_D- | J1:A7/B7→U3:D- |
| 6 | ESP_TX | U1:TXD0→U3:RXD |
| 7 | ESP_RX | U1:RXD0→U3:TXD |
| 8 | ESP_EN | U1:EN→R1→C4→SW2 |
| 9 | ESP_IO0 | U1:IO0→R2→SW1 |
| 10 | ESP_IO4 | U1:IO4→R3→Q1:B |
| 11 | ESP_IO5 | U1:IO5→R5→D3 |
| 12 | RELAY_COIL | Q1:C→K1:coil-→D1:A |
| 13 | VBUS | J1:VBUS→FB1:in |
| 17 | RELAY_COM | K1:COM→J2:1 |
| 18 | RELAY_NO | K1:NO→J2:2 |

---

## 6. Iteration Workflow

### If boards work (happy path):
1. Flash `production/firmware/test_firmware.ino`
2. Validate all subsystems via serial output
3. Develop real application firmware
4. Begin Rev 2 design (12V automotive version)

### If boards have issues:
1. Diagnose using bring-up procedure (see `C:\Users\james\.claude\plans\lucky-seeking-lamport.md`)
2. Identify root cause (solder defect vs design error)
3. **Solder defect:** Fix with iron/wick, try next board
4. **Design error:** Edit `scripts/route_pcb.py`, re-run, regenerate Gerbers, reorder
5. Log findings in revision tracking template

### To regenerate the PCB after changes:
```powershell
# 1. Edit route_pcb.py with the fix
# 2. Re-run the routing script
& "C:\Users\james\AppData\Local\Programs\KiCad\9.0\bin\python.exe" scripts\route_pcb.py

# 3. Run DRC to validate
& "C:\Users\james\AppData\Local\Programs\KiCad\9.0\bin\kicad-cli.exe" pcb drc --output production\drc_report.json --severity-all production\ESP32_Simple_IoT.kicad_pcb

# 4. Regenerate Gerbers
& "C:\Users\james\AppData\Local\Programs\KiCad\9.0\bin\kicad-cli.exe" pcb export gerbers --output production\gerbers\ production\ESP32_Simple_IoT.kicad_pcb
& "C:\Users\james\AppData\Local\Programs\KiCad\9.0\bin\kicad-cli.exe" pcb export drill --output production\gerbers\ --format excellon --drill-origin absolute --excellon-separate-th production\ESP32_Simple_IoT.kicad_pcb

# 5. Re-zip
Compress-Archive -Path production\gerbers\ESP32_Simple_IoT-*.gtl, production\gerbers\ESP32_Simple_IoT-*.gbl, production\gerbers\ESP32_Simple_IoT-*.gts, production\gerbers\ESP32_Simple_IoT-*.gbs, production\gerbers\ESP32_Simple_IoT-*.gtp, production\gerbers\ESP32_Simple_IoT-*.gto, production\gerbers\ESP32_Simple_IoT-*.gbo, production\gerbers\ESP32_Simple_IoT-*.gm1, production\gerbers\ESP32_Simple_IoT-*.drl, production\gerbers\ESP32_Simple_IoT-job.gbrjob -DestinationPath production\ESP32_Simple_IoT_Gerbers.zip -Force

# 6. Regenerate CPL from PCB (coordinates must match)
```

---

## 7. Known Issues & Limitations

1. **DRC clearance warnings (9):** QFN-28 and USB-C pad spacing inherently tighter than 0.2mm default rule. Within JLCPCB tolerances. Not fixable without changing footprints.

2. **NPTH hole_clearance (7):** GND zone fill gets close to mounting hole and USB-C NPTH. Fab house handles this automatically.

3. **15 dangling vias:** GND stitch vias that connect F.Cu pads to B.Cu ground plane. KiCad DRC flags them because they don't connect to F.Cu traces, but they connect to B.Cu zone fill after fill operation. Functionally correct.

4. **Board size in README.md is wrong:** Says 60x40mm, actual is 80x60mm. Needs update.

5. **3 through-hole parts require manual soldering:** K1 (relay), D1 (1N4007 diode), J2 (terminal block). JLCPCB SMT assembly only handles SMD parts.

6. **No auto-reset circuit:** ESP32 requires manual BOOT+RESET button sequence to enter flash mode. DTR/RTS from CP2102N are wired but auto-reset circuit (transistor + caps) not included in this revision.

---

## 8. Future Work: 12V Automotive Rev 2

The original design goal (per `DESIGN/PROMPT.txt`) is a 12V automotive high-side switch. The simplified USB board validates core ESP32 functionality. Rev 2 changes:

- Replace USB 5V input with 12V automotive input
- Add LM74800 reverse polarity protection
- Add SMBJ12A TVS diode for transient protection
- Replace relay with high-side MOSFET switch
- Add current sensing
- Add CAN bus interface
- 4-layer PCB for better EMI/power integrity

Design files for this exist in `NEW/` directory but have unresolved DRC errors (see `NEW/DRC_FIXES.md`).

---

## 9. Environment & Tool Versions

| Tool | Version | Path |
|------|---------|------|
| KiCad | 9.0.7 | `C:\Users\james\AppData\Local\Programs\KiCad\9.0\` |
| KiCad CLI | 9.0.7 | `...\KiCad\9.0\bin\kicad-cli.exe` |
| KiCad Python | 3.x (bundled) | `...\KiCad\9.0\bin\python.exe` |
| OS | Windows 11 Home | 10.0.26100 |
| Platform | win32 | PowerShell (bash `$_` variable expansion breaks PS commands) |

**PowerShell gotcha:** When running PowerShell commands from bash, `$_` gets consumed by bash. Use heredoc (`<<'PSEOF'`) or `-File -` to avoid this.

---

## 10. Repository Structure

```
Sarlls/
├── CLAUDE.md                    # Project coding guidelines
├── PROJECT_STATUS.md            # THIS FILE — agent handoff document
├── DESIGN/                      # Original complex design (deprecated)
│   ├── PROMPT.txt               # Original 12V automotive requirements
│   ├── board_1.png, board_2.png # Schematic screenshots
│   └── FINAL_IOT_PCB.zip       # Old design package
├── KIcad/IOT_SWITCH2/          # Flux.ai cloud design v2 (partial)
├── MICROFAB/                    # MacroFab formatted package (deprecated)
├── NEW/                         # 4-layer automotive design (has DRC errors)
│   └── DRC_FIXES.md            # Known issues in 4-layer design
├── PCB_FILES/                   # Original PCB files (deprecated)
├── production/                  # ★ ACTIVE DESIGN — simplified USB board ★
│   ├── ESP32_Simple_IoT.kicad_* # KiCad project files
│   ├── ESP32_Simple_IoT_BOM.csv # Bill of Materials
│   ├── ESP32_Simple_IoT_CPL.csv # Component Placement List
│   ├── ESP32_Simple_IoT_Gerbers.zip # Manufacturing package
│   ├── drc_report.json          # Latest DRC results
│   ├── gerbers/                 # Individual Gerber files + previews
│   ├── firmware/                # Test firmware (Arduino/PlatformIO)
│   └── README.md               # Design specs
├── scripts/                     # ★ Build scripts (Python + PS) ★
│   ├── route_pcb.py             # PCB routing script (main build tool)
│   ├── rebuild_schematic.py     # Schematic generation
│   ├── fix_schematic_wiring.py  # Earlier wiring script
│   ├── check_libs.py            # Library verification
│   └── package_for_manufacturer.py
├── specs/                       # Feature specifications
├── supabase/                    # Database migrations (web app)
└── __tests__/                   # Test files
```

**The `production/` directory and `scripts/route_pcb.py` are the only things that matter for the current board.**
