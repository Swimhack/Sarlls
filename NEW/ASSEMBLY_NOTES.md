### Assembly Notes

- Polarity markings must be visible for diodes, TVS (D1), LEDs (if any), and polarized capacitors.
- Orientation indicators for ICs: pin-1 dots/notches must be visible and not covered by mask.
- ESP32-WROOM-32D: maintain antenna keepout; avoid adhesive under antenna area.
- Stencil: 4–5 mil laser-cut stainless; windowpane large thermal pads; add via-in-pad only if filled/plugged.
- Reflow profile per component manufacturer recommendations (ESP32, LM74800, TVS).
- Do not substitute automotive-rated parts called out in BOM; adhere to MPNs.
- Provide centroid (XY) with refdes, package, X, Y, rotation, side for pick-and-place.
- Through-hole parts (if any) solder after SMT; observe hole tolerance per fab.
