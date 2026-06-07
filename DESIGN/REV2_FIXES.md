# Rev 2 PCB Design Fixes

Issues identified during rev 1 board bring-up on 2026-05-18.

## Critical Fixes

### 1. D1 Placement — Blocks USB-C Port
- **Problem:** D1 (flyback diode, through-hole) is placed directly in front of the USB-C connector (J1), physically preventing cable insertion
- **Root cause:** `route_pcb.py` placed D1 too close to J1 without accounting for cable plug clearance
- **Fix:** Move D1 at least 5mm away from J1, or orient it horizontally (flat against board) in the design

### 2. SW1, SW2, J2 Footprint Mismatch
- **Problem:** JLCPCB left SW1, SW2, and J2 unpopulated due to footprint mismatch with available components
- **Fix:** Update footprints to match LCSC in-stock components, or source components that match existing footprints

## Potential Issues (Pending Validation)

### 3. U3 (CP2102N) QFN Solder Joint
- **Problem:** Windows reports "Device Descriptor Request Failed" when connected via USB
- **Status:** May be caused by D1 blocking full cable insertion, not a solder defect. Needs validation after D1 fix.
- **If confirmed solder issue:** QFN-28 exposed ground pad may need larger thermal relief or paste aperture adjustment

## Design Improvements

### 4. 12V Input Power Option
- **Current:** Board only accepts USB-C 5V power
- **Needed:** For automotive use case, board needs 12V input with buck converter to 5V
- **Reason:** When board disconnects car battery via contactor, USB-C has no power source. Need to tap 12V before the contactor.

### 5. Automotive Contactor Interface
- **Current:** Board has 10A relay only
- **Needed:** The 10A relay is sufficient to drive an external automotive contactor coil (~0.5A at 12V), but the screw terminal (J2) needs to be populated for wiring
- **Consider:** Adding a dedicated 2-pin connector for contactor coil output

## Rev 2 Pre-Fabrication Status - 2026-06-06

Implemented in the deterministic PCB generator:

- Rotated J1 and placed it at the board edge for cable access.
- Moved D1 away from the USB-C connector.
- Rerouted USB, CC, power, relay-coil, and relay-output nets.
- Added via-in-pad VBUS escapes around J1 locating holes.
- Direct-connected J1 ground and shield pads to the ground planes.
- Generated separate plated and non-plated drill files.
- Added `scripts/validate_drc.py` as the release DRC gate.

Verified production DRC result:

- 0 unconnected items
- 0 shorts
- 0 track crossings
- 0 ordinary clearance errors
- 0 hole-clearance errors
- 26 approved USB-C edge-clearance reports caused by J1's intentional
  edge-mounted contact row
- 11 silkscreen warnings

Remaining before ordering:

1. Review the USB-C via-in-pad escapes with the selected assembler.
2. Confirm SW1, SW2, and J2 purchasable parts match the PCB footprints.
3. Review JLCPCB placement preview and DFM output.
4. Complete Rev 1 physical USB enumeration and relay bring-up if possible.
