# ESP32 IoT Switch — Full Assembly (PCBA) Package

Upload ESP32_IoT_Switch_MacroFab_FINAL.zip to MacroFab or JLCPCB Assembly.

**What this is:** Gerbers + drill + BOM + pick-and-place for full PCB assembly.
**What you get back:** Fully assembled boards with all components soldered on.
**You do NOT need to solder anything.**

## Files
- Gerbers + drill: Board fabrication
- pick_and_place.csv: Component positions (KiCad format, inches)
- ESP32_IoT_Switch.XYRS: MacroFab-specific placement + BOM with MPNs

## Components (19 total)
- U1: ESP32-WROOM-32 (WiFi/BT MCU)
- U2: AMS1117-3.3 (3.3V LDO regulator)
- U3: HLK-PM01 (AC-DC power module)
- K1: SRD-05VDC-SL-C (5V SPDT relay)
- Q1: 2N7000 (N-channel MOSFET)
- R1-R4: 10K, 1K, 330R, 10K (0603 resistors)
- C1-C4: 100uF, 22uF, 100nF, 10uF (capacitors)
- L1: 22uH inductor (0805)
- D1: 1N4007 (rectifier diode)
- D2-D3: Green/Red LEDs (0603)
- SW1: Tactile switch (6x6mm)
- J1: 2-pin terminal block

## Specs
- 2-layer board, 1.6mm
- Mix of SMD (0603) and through-hole components
- Generated: 2026-05-06 via KiCad 7.0.11 headless CLI
