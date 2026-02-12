### Sarlls-IOT PCB Routing Plan and Manufacturing Rules

This plan governs routing, copper features, drilling, and outputs for the Sarlls-IOT design. It references `GOVERNING-EE-PERSONA.md` for working style and defaults.

#### 1) Inputs Needed (provide to proceed)
- Board outline and keepouts (DXF or KiCad/Altium outline), mounting holes, height limits.
- Component placement intent (rough map or constraints), connector orientations.
- Fabricator and capabilities (min trace/space, min drill, stack options, materials).
- Target impedances and interfaces (e.g., 50 Ω SE, 100 Ω diff for specific nets).
- Power budget and thermal constraints; copper weights if deviating from defaults.
- Existing Gerbers (in `/Gerber`) and any DRC/ERC logs to reconcile.

#### 2) Stackup Proposal (default, override with fab data)
- 4 layers: L1 (signal, 1 oz), L2 (solid GND, 0.5 oz), L3 (power/aux, 0.5 oz), L4 (signal, 1 oz).
- FR-4, Tg ≥ 170°C, prepreg/core per fab; final thickness ~1.6 mm.
- Impedance: 50 Ω SE (L1 over L2), 100 Ω diff; fab to tune dielectric.

#### 3) Nets and Roles inferred from EDIF
From `sarlls1-sarlls-iot.edif`:
- Power path conditioning:
  - `F1` (resettable fuse 1812L200/12DR) → `D1` TVS SMBJ12A-13-F to GND on input node.
  - `U3` LM74800 ideal diode/ORing controller; ports: A (input), OUT (protected bus), VS/OV sensing, GND.
  - `L1` DLP31SN221ML2L (Murata EMI filter array) around `PROTECTED_12V_BUS` nodes 3/4 → used as common-mode/EMI suppression.
  - Nets: `F1_OUT`, `PROTECTED_12V_BUS`, `GND`.
- Regulated rail:
  - `3.3V` to ESP32 `U1` with decoupling caps `C1...C6`.
- ESD protection:
  - `U2` TPD3E001DRLR TVS array for up to 3 IOs (labelled IO1..IO3), shunted to GND near connectors.
- MCU:
  - `U1` ESP32-WROOM-32D; critical pins: `EN`, `IO0` (boot), `TXD0/RXD0`, RF keepout under module, 3.3V decoupling, AGND/VN/VP analog pins.

#### 4) Net Classes and Rules (defaults)
- POWER_12V (pre/post protection): trace width ≥ 40 mil for up to 2 A; increase per current; clearance ≥ 10 mil.
- 3V3: width 12–20 mil trunks, 8–10 mil branches; clearance ≥ 6 mil.
- SIGNAL: width 6–8 mil, clearance ≥ 6 mil.
- DIFF_PAIRS (if used): 100 Ω differential; pair gap set per fab (typically 6–8 mil with 6–8 mil width on 4-layer).
- ESD_LINES: short, direct to connector, series resistors/RC where applicable; protectors to GND via very short trace and via to L2 plane.
- VIA sizes (mechanical default): 0.3 mm drill, 0.6 mm pad; microvias only if fab supports.
- Annular ring ≥ 4 mil; tent vias on outer layers unless used as test points.

#### 5) Placement Constraints
- `U1` ESP32-WROOM-32D:
  - Keepout copper under antenna; place module at board edge with antenna over board edge/keepout.
  - Decoupling caps within 2–3 mm of 3.3V/VBAT pins; short return to GND via L2.
  - `EN` pull-up and `IO0` boot circuitry near module, keep traces short and away from noisy power.
- Input protection chain (`F1` → input node → `D1` to GND → `U3:A` → `U3:OUT` → `L1` → `PROTECTED_12V_BUS` consumers): place in a straight flow from connector inward.
- `U2` ESD array within 5–10 mm of the external connector pins it protects; shortest path to a low-impedance GND via.
- Bulk caps (`C2..C6`) on `PROTECTED_12V_BUS`; small loop area to GND plane.

#### 6) Routing Guidance
- Return paths: maintain continuous L2 GND plane; avoid splits beneath high-speed or sensitive nets.
- `F1_OUT` to `U3:A`: wide trace, minimize loop to `D1` TVS to GND; stitch GND near TVS.
- `U3:OUT` to `PROTECTED_12V_BUS`: wide, keep sense pins (`VSNS`, `OV`) Kelvin-connected per datasheet; avoid dropping sense on high-current path.
- `L1` filter connections: follow manufacturer pin map; route symmetrically, keep as close to the bus as possible.
- 3.3V distribution: star from regulator output (not shown in EDIF; if on-module, still decouple locally). Place multiple 0.1 µF near `U1` power pins, plus one 10 µF bulk.
- ESD (`U2`) IOs: run from connector → series resistor (if used) → MCU, with the TVS branch to GND as a short stub.
- ESP32 RF: do not place copper under antenna; keep noisy power switching away.

#### 7) Copper Pours and Planes
- L2 solid GND. Stitch with vias at 10–15 mm grid and near net class transitions and TVS devices.
- On L3, create `PROTECTED_12V_BUS` pour with thermals; observe clearance to signals; avoid cutting L2 return.
- Define pour priorities: GND highest continuity; power next; signals last.

#### 8) Drill and Mechanical
- Mounting holes: define diameter and keepouts; add GND via stitching around as needed.
- Via policy: 0.3/0.6 mm standard; use 0.2/0.45 mm only if fab supports; backdrill not required unless high-speed.
- Test points: add for `PROTECTED_12V_BUS`, `3.3V`, `GND`, UART (`TXD0/RXD0`), `EN`, `IO0`.

#### 9) ERC/DRC Checklist
- ERC: power pin types, unconnected pins marked NC, reference designators unique (note duplicates in EDIF should be resolved in schematic).
- DRC: trace/space per fab, annular ring, solder mask clearance, courtyard checks, antenna keepout.
- High-current path loop areas minimized; sense/Kelvin lines verified.

#### 10) Manufacturing Outputs
- Gerbers: RS-274X or IPC-2581 per fab; include all copper layers, solder mask, paste, silks, board outline, mechanical.
- NC Drill: plated/non-plated separated; drill map and README with stack and materials.
- Assembly: BOM with MPNs, centroid/XY, PDF assembly notes with polarity/orientation.
- Fab notes: copper weights, controlled impedance targets, soldermask color, finish (ENIG/OSP), min trace/space, min drill, tolerances.

#### 11) Next Steps
- On receipt of inputs in Section 1 and the `/Gerber` samples, we will:
  1) Import EDIF, resolve symbol/pin mapping, and regenerate netlist.
  2) Apply net classes/rules above and run initial DRC/ERC.
  3) Place protection/MCU per constraints and route power path first.
  4) Route signals; lock antenna keepout; add pours and stitching.
  5) Run full verification and generate manufacturing outputs.


