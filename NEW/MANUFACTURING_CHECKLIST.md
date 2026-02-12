### Manufacturing Sign-off Checklist

1) DRC/ERC
- [ ] 0 DRC errors (airwires, overlaps, invalid layers cleared)
- [ ] 0 ERC errors; NC pins verified; power pins correct

2) Routing/Planes
- [ ] F1→D1→U3:A→U3:OUT→L1→PROTECTED_12V_BUS path is short, >= 40 mil
- [ ] TVS (D1) anode to GND has 1–2 vias within 1–2 mm
- [ ] L2 GND plane continuous; stitching vias 10–15 mm grid and near ESD/TVS
- [ ] VS/OV sense are Kelvin to protected bus
- [ ] No copper under ESP32 antenna (all layers)

3) Components/BOM
- [ ] Footprints verified for SMBJ, 1812 PTC, SON/QFN LM74800, SOT-553, DLP31, ESP32
- [ ] BOM includes final MPNs; automotive-rated where required

4) Outputs present in /Gerber zip
- [ ] Top/Bottom/Inner copper (GTL/GBL/G1/G2)
- [ ] Soldermask (GTS/GBS), Paste (GTP/GBP), Silks (GTO/GBO)
- [ ] Outline/Mechanical (GKO/GM1) with slots/cutouts
- [ ] Drill PTH and NPTH with tool table and map
- [ ] FAB_NOTES.txt, BOM.csv, XY.csv, Assembly_Drawing.pdf, GERBER_README.md

5) Validation
- [ ] Visual check of polarity/orientation on assembly drawing
- [ ] Netlist compare (if tool supports) or flying-probe test requested
- [ ] Impedance-controlled nets identified to fabricator

Sign-off:
Engineer: __________________  Date: __________
