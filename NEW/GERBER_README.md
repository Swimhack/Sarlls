### Gerber/Manufacturing Package Checklist (Submit to PCB Fabricator)

Provide the entire `/Gerber` directory as a zip. Ensure file extensions and layer mapping match your CAD export. This checklist aligns with `PROMPT.txt` and `ROUTING_PLAN.md`.

#### Required Fabrication Outputs
- Copper: `Top (GTL)`, `Inner1 (G1)`, `Inner2 (G2)`, `Bottom (GBL)`
- Solder Mask: `Top Mask (GTS)`, `Bottom Mask (GBS)`
- Paste: `Top Paste (GTP)`, `Bottom Paste (GBP)`
- Silkscreen: `Top Silk (GTO)`, `Bottom Silk (GBO)`
- Board Outline/Mechanical: `GKO` (or `GM1`) with exact outline, slots, cutouts
- Drill: `PTH (TXT/DRL)`, `NPTH (TXT/DRL)` with drill map and tool table

Naming examples (adjust to your CAD):
- `Sarlls-IOT_F_Cu.gtl`, `Sarlls-IOT_B_Cu.gbl`, `Sarlls-IOT_Edges.gko`, `Sarlls-IOT.drl`

#### Assembly Outputs
- `BOM.csv` with MPNs (AEC-Q/automotive where specified)
- `Centroid/XY.csv` with refdes, package, X/Y, rotation, side
- `Assembly_Drawing.pdf` with polarity/orientation notes

#### Design Rule Targets (unless fab overrides)
- 4-layer: L1 signal 1 oz, L2 GND 0.5 oz, L3 PWR 0.5 oz, L4 signal 1 oz
- Min trace/space: 4/4 mil (prefer ≥6/6 mil)
- Min drill: 0.3 mm (12 mil pad 24 mil typical)
- Impedance: 50 Ω SE, 100 Ω diff (note controlled lines in fab notes)

#### Pre-Submission Sign-off
1) ERC/DRC: 0 errors; resolve airwires on `F1_OUT`, `PROTECTED_12V_BUS`, `3.3V`
2) GND plane continuity: no antenna copper under ESP32; keepout applied all layers
3) TVS `D1` return to GND via within 1–2 mm; add 1–2 vias
4) LM74800 `VSNS/OV` Kelvin-sense to protected bus; not on high-current pour
5) Stitching vias on pour edges and near ESD/TVS; islands removed
6) Footprints verified: SMBJ, 1812 PTC, SON/QFN LM74800, SOT-553 TPD3E001, DLP31 array, ESP32 module
7) BOM MPNs set; any generics replaced with automotive-rated parts per `PROMPT.txt`
8) Outline layer contains exact board edge; slots/cutouts in mechanical layer and NPTH drill
9) Drill files generate correctly with tool table and plated/NPTH separation
10) Silkscreen: refdes legible, no over pads; polarity markers present

#### Fab Notes (include as `FAB_NOTES.txt`)
- Material: FR-4 Tg ≥ 170°C; Thickness 1.6 mm
- Finish: ENIG (preferred) or OSP
- Mask: Green (or specify), Legend: White
- Copper: 1 oz outer, 0.5 oz inner (unless specified otherwise)
- Impedance control for specified nets; fabricator to tune dielectric
- IPC-6012 Class 2 (or 3 if required)

#### Known Design Intents from `PROMPT.txt`
- 12 V automotive environment with surge immunity (ISO 7637-2)
- Front-end: Battery → Fuse → TVS → Ideal-diode/HS switch → PROTECTED_12V_BUS
- Support for PFET simple path or NFET+driver robust path in future revisions
- ESP32 3.3 V rail with close decoupling; UART and 3G socket with 50 Ω RF lines

#### What to include in the zip
- All Gerber layers, drills, `FAB_NOTES.txt`, `BOM.csv`, `XY.csv`, `Assembly_Drawing.pdf`
- Optional: `Readme_version.txt` with CAD tool/version and export settings


