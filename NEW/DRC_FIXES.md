### DRC Error Fixes and Routing Corrections

This checklist maps your review-panel errors to concrete actions on the PCB. Apply these in order, then re-run DRC/ERC.

#### Airwires (Unrouted Nets)
- 3.3V: `Trace auto:Trace auto, C6:P1`
  - Action: Place `C6` within 2–3 mm of the ESP32 3.3V pin. Route a short 12–20 mil trace from the 3.3V trunk to `C6:P1`; drop a direct GND via at `C6:P2`. Ensure the 3.3V trunk reaches all decouplers (`C1..C6`).

- F1_OUT: `D1:K, L1:1`, `D1:K, U3:A`, `L1:1, L1:2`, `U3:A, F1:P2`
  - Action: Create a continuous, wide copper path (≥40 mil) from `F1:P2` → node to `D1:K` (TVS cathode) → `U3:A` (input) and to `L1:1/2` if required by the filter topology. Keep the path short. Add 1–2 GND vias directly adjacent to `D1` anode to L2 GND.
  - Note: If `L1:1` to `L1:2` airwire exists, verify symbol pin mapping; if the array pins are internally connected or should be separate, update the schematic to remove unintended short.

- PROTECTED_12V_BUS: `D1:A, L1:4`, `D1:A, L1:3`, `U3:VS`, `U3:OUT`
  - Action: Route `U3:OUT` to a `PROTECTED_12V_BUS` pour/trunk (≥40 mil). Connect `L1:3/4` per datasheet footprint close to the bus. Tie `D1:A` only if using bidirectional TVS across the protected bus (check intent); otherwise `D1` typically sits at the unprotected input node with anode to GND. Correct the net if mis-assigned.
  - `U3:VS`: Kelvin-sense from the protected bus using a thin trace to the sense node; do not pull from the middle of the high-current pour.

#### Floating Copper (2)
- Cause: Orphaned pours or stubs not tied to their net with a via or trace.
- Action: Repour with “remove islands” enabled, or add stitching vias to connect islands to the main copper region. For PROTECTED_12V_BUS on L3, add vias tying the island to the trunk every 10–15 mm.

#### Unroutable Pins (Auto-Layout)
- Objects: `U3:A`, `U3:OUT`, `U3:VS`
- Causes:
  - Overlapping keepouts or pour boundaries blocking escape.
  - Insufficient clearance vs. design rules.
  - Pin trapped between pads with no via escape.
- Actions:
  1) Nudge `U3` placement to align `A` toward `F1`/input, and `OUT` toward the bus. Keep `VS` accessible to the protected side.
  2) Reduce local pour clearance or add a small neck-down window to allow a via near the pins.
  3) Pre-route short escapes from `A` and `OUT` on L1 with 40–60 mil width; drop vias if needed to L3 trunk.
  4) Route `VS` as a thin Kelvin trace to the protected bus node, avoiding high-current copper.

#### Overlapping Copper
- Action: Inspect layer pairs around U3 and L1. Ensure pours of different nets do not overlap; set pour priorities so GND has highest continuity. Trim shapes or increase clearance.

#### Missing Footprints / Manufacturer Part Number (6)
- Action: Assign verified footprints and MPNs:
  - `U3` LM74800: package QFN/SON per `QDRRRQ1` (check TI datasheet for pad map, exposed pad to GND).
  - `D1` SMBJ package (DO-214AA) for SMBJ12A-13-F.
  - `F1` 1812 resettable fuse footprint.
  - `U2` TPD3E001 in SOT-553 (DRL) footprint.
  - `L1` DLP31 series 1206 array footprint per Murata datasheet.
  - Capacitors `C1..C6` footprints (0603/0805 as chosen).
  - Fill MPNs in BOM fields to clear manufacturing checks.

#### Invalid Layer / Component Overrides
- Action: Move any traces accidentally on mechanical/keepout layers back to signal layers. Clear local rule overrides that conflict with global rules.

#### Protected Intrusions
- Action: For ESP32 antenna keepout: ensure no copper/pours under the antenna region; move any traces/pours away and set keepout properly on all copper layers.

### Verification Steps
1) Re-pour all planes with “remove islands” on. Ensure GND L2 is continuous.
2) DRC pass: widths/clearances/vias per `ROUTING_PLAN.md` net classes.
3) ERC pass: check NC pins, power pin types, unique refs.
4) High-current path visual: confirm straight, short path F1→D1→U3:A→U3:OUT→L1→bus.
5) Add stitching vias near TVS and pour edges; ensure VS sense is Kelvin.

### Notes on Net Intent
- If `D1:A` currently ties to `PROTECTED_12V_BUS`, confirm design intent. Many designs place the TVS on the unprotected side (cathode to input node, anode to GND). If that’s the intent, change `D1:A` net to `GND` and keep `D1:K` on `F1_OUT`.


