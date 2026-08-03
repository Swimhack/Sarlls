# Assembly Notes — SafeSwitch IoT Smart Switch Rev 2

## SMT Components (JLCPCB assembled)

All 0402/0805/SOT-23/SOT-223/QFN components are placed by JLCPCB.

## Through-Hole Components (manual or specify THT assembly)

| Ref | Part | Notes |
|-----|------|-------|
| K1 | SRD-05VDC-SL-C relay | Verify D1 is NOT underneath. Must seat flush. |
| D1 | 1N4007 (DO-41) | Flyback diode. Observe polarity (cathode band toward +5V). Mounted 6mm north of K1. |
| J2 | Phoenix Contact MC 1,5/2-G-3.81mm | Screw terminal for relay output wires. |
| J1 | USB4105-GF-A USB-C | Edge-mount. Opening must face outward (left board edge). |
| SW1 | TL3342 tactile switch | BOOT button (IO0). |
| SW2 | TL3342 tactile switch | RESET button (EN). |

## Critical Assembly Checks

1. **D1/K1 clearance** — D1 body must not be under K1 relay housing. Rev 1.2 had D1 at y=40, interfering with K1 body (extends to ~y=42). Rev 2 moves D1 to y=34.
2. **J1 USB-C orientation** — Connector opening faces left board edge. Verify before soldering.
3. **U1 ESP32-WROOM-32** — Antenna keepout zone extends 48mm beyond top board edge. No copper/components in keepout.
4. **D1 polarity** — Cathode (band) connects to +5V net. Anode connects to RELAY_COIL.
5. **K1 relay seating** — Must sit flat against PCB. Check no components underneath before placing.

## Post-Assembly Inspection

- [ ] Visual: No solder bridges on QFN-28 (U3 CP2102N)
- [ ] Visual: D1 clears K1 body completely
- [ ] Visual: J1 USB-C opening faces outward
- [ ] Continuity: +5V to GND should NOT be shorted
- [ ] Continuity: +3V3 to GND should NOT be shorted
- [ ] USB: CP2102N enumerates when USB-C plugged in
