# Board Bring-Up Log — 2026-05-18

## Boards Received
- JLCPCB Order W2026050802124660 arrived May 18, 2026 (a few days early, ETA was May 18-20)
- 5x assembled PCBs received
- Visual inspection: all components placed correctly, solder quality looks professional
- Photos saved in `DESIGN/BOARDS/`

## Known Issues from Manufacturing
- **SW1, SW2, J2 left unpopulated** — footprint mismatch, expected, fix in rev 2
- **D1 (flyback diode) blocks USB-C port** — through-hole component stands upright directly in front of USB-C connector, preventing cable insertion. Design placement error in `route_pcb.py`. Needs to be bent flat or repositioned.

## USB Connection Attempts
1. Attempted USB-C connection — D1 physically blocks cable from seating
2. Briefly got cable partially inserted — Windows saw a COM port momentarily (unconfirmed)
3. With different cables, Windows shows: **"Unknown USB Device (Device Descriptor Request Failed)"** VID_0000 PID_0002
4. Likely cause: cable cannot fully seat due to D1 obstruction, USB data pins not making full contact
5. U3 (CP2102N) solder may be fine — never had a clean connection to confirm

## Driver Installation
- CP2102N requires Silicon Labs CP210x driver
- Driver downloaded and installed via `pnputil` — confirmed in Windows driver store as `oem180.inf`
- Arduino CLI installed at `C:\Users\james\bin\arduino-cli.exe`
- ESP32 board support package `esp32:esp32@3.3.8` installed

## Next Steps
1. Take board to Bits & Bytes Computers — (281) 395-9800, 628 S Mason Rd, Katy TX 77450
2. Ask them to bend D1 flat away from USB-C port (30-second fix)
3. Come home, plug in USB-C, check for COM port in Device Manager
4. If COM port appears — flash firmware via `arduino-cli`
5. If still "Device Descriptor Request Failed" — U3 needs reflow (go back to shop)

## Firmware Ready to Flash
- Test firmware: `production/firmware/test_firmware.ino`
- Production firmware: `production/firmware/wifi_switch.ino` (WiFi remote on/off v1.5)
- Flash command: `arduino-cli compile --fqbn esp32:esp32:esp32 && arduino-cli upload --fqbn esp32:esp32:esp32 --port COMx`
