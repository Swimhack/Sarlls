# Test Procedures — SafeSwitch IoT Smart Switch

## 1. Visual Inspection

- [ ] PCB free of manufacturing defects (solder bridges, missing components)
- [ ] D1 flyback diode NOT under K1 relay — minimum 6mm clearance
- [ ] K1 relay seated flush against PCB
- [ ] J1 USB-C connector opening faces left board edge
- [ ] All SMD components present and properly aligned

## 2. Power Test (NO firmware needed)

**Equipment:** USB-C data cable, multimeter

1. [ ] Measure resistance between +5V and GND pads — should be >1kΩ (no short)
2. [ ] Measure resistance between +3V3 and GND pads — should be >1kΩ (no short)
3. [ ] Connect USB-C cable to J1
4. [ ] Measure voltage at C1 (+5V rail) — expect 4.8-5.2V
5. [ ] Measure voltage at U2 output (+3V3 rail) — expect 3.2-3.4V
6. [ ] D2 power LED should illuminate
7. [ ] Current draw without firmware: ~20-50mA typical

**STOP if any short detected. Do not proceed.**

## 3. USB Enumeration Test

**Equipment:** USB-C data cable (NOT charge-only), computer

1. [ ] Connect board to computer via USB-C
2. [ ] Check Device Manager (Windows) or `lsusb` (Linux) for CP2102N
3. [ ] Should appear as "Silicon Labs CP210x USB to UART Bridge"
4. [ ] Note COM port number for firmware flashing

**If not detected:** Check D1 is not blocking USB-C. Install CP2102N driver from Silicon Labs.

## 4. Firmware Flash Test

**Equipment:** Arduino IDE or PlatformIO

1. [ ] Open `firmware/wifi_switch.ino`
2. [ ] Select board: "ESP32 Dev Module"
3. [ ] Select correct COM port
4. [ ] Hold BOOT (SW1), press RESET (SW2), release BOOT
5. [ ] Upload firmware
6. [ ] Open Serial Monitor at 115200 baud
7. [ ] Press RESET (SW2)
8. [ ] Should see WiFi initialization messages

## 5. WiFi Connectivity Test

1. [ ] After firmware flash, board creates WiFi AP: "SafeSwitch-XXXX"
2. [ ] Connect to AP from phone/laptop
3. [ ] Navigate to 192.168.4.1
4. [ ] Web interface should load
5. [ ] Configure home WiFi credentials
6. [ ] Board connects to home WiFi (check serial output for IP)

## 6. Relay Functional Test

**Equipment:** Multimeter, 12V test load (optional)

1. [ ] Measure continuity between J2 pin 1 (COM) and J2 pin 2 (NO) — should be OPEN
2. [ ] Send relay ON command via web interface
3. [ ] K1 relay should click audibly
4. [ ] D3 relay LED should illuminate
5. [ ] Measure continuity J2:COM to J2:NO — should be CLOSED (<1Ω)
6. [ ] Send relay OFF command
7. [ ] Relay clicks off, D3 LED off
8. [ ] Continuity J2:COM to J2:NO — should be OPEN again

## 7. Vehicle Integration Test

**Equipment:** 12V automotive battery, contactor, buck converter

1. [ ] Wire buck converter: 12V battery → converter → USB-C (5V out)
2. [ ] Wire contactor: Battery+ → contactor coil+ → J2:COM; J2:NO → contactor coil-
3. [ ] Power on board via buck converter
4. [ ] Verify WiFi connectivity from inside vehicle
5. [ ] Test relay ON/OFF cycles the contactor
6. [ ] Verify contactor disconnects battery load

## 8. Endurance Test

1. [ ] Cycle relay ON/OFF 100 times via automated script
2. [ ] Monitor for relay failure or overheating
3. [ ] Monitor ESP32 uptime — should not crash or disconnect
4. [ ] Run for 24 hours continuously — verify WiFi stays connected

## Pass/Fail Criteria

| Test | Pass | Fail |
|------|------|------|
| Power | +5V and +3V3 within spec | Any short or out-of-range voltage |
| USB | CP2102N enumerates | No device detected |
| Flash | Firmware uploads successfully | Upload fails or crashes |
| WiFi | Connects and serves web UI | No AP or connection failure |
| Relay | Clicks on/off, continuity correct | No click, stuck, or intermittent |
| Vehicle | Contactor cycles reliably | Contactor fails to engage/disengage |
