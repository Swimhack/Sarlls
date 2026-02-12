# MacroFab Deliverables

This folder contains the minimum files MacroFab requires to build the PCB assembly per their guidance.

Included:

- ESP32_IoT_Switch_Gerber_Files.zip
  - RS-274X Gerbers and NC drill for board fabrication
- ESP32_IoT_Switch.XYRS
  - Combined placement + BOM mapping for assembly

Notes:
- Coordinates converted from mm to mils. Rotation preserved. Top=1, Bottom=2. Type inferred: SMD=1, PTH=2.
- Value/Footprint/MPN merged from BOM (ESP32_IoT_Switch_BOM_v2.csv).
- If MacroFab asks for .xlsx BOM, convert the CSV to XLSX and upload; the .XYRS will merge with their BoM per their rules.

Reference: MacroFab Required Design Files
https://help.macrofab.com/knowledge/macrofab-required-design-files


