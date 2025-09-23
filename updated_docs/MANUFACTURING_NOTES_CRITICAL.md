# ESP32 IoT Switch - Manufacturing Notes & Critical Information

## ⚠️ IMPORTANT: Design Scope Change

**This PCB is now a CONTROL BOARD only** - it cannot handle 100A directly as specified in the original requirements. This design provides:
- ESP32-based WiFi/BLE control
- Safe 12V automotive power supply  
- Control output for external 100A automotive contactor

## Critical Manufacturing Requirements

### 1. PCB Specifications
- **Board Size**: 45mm x 35mm (2-layer)
- **Thickness**: 1.6mm standard
- **Via Size**: 0.2mm minimum
- **Track Width**: 
  - Power traces (12V): 1.0mm minimum
  - Control signals: 0.2mm minimum
  - Ground pour: Full coverage

### 2. Component Substitutions (JLCPCB Compatible)
If parts unavailable, use these alternatives:

**Power Management:**
- U2 (LM2596S): Can substitute with MP1584EN (C14070)
- L1 (220uH): Can substitute with 150uH-330uH range
- C1/C2: Electrolytic capacitors can vary ±20%

**Critical - DO NOT SUBSTITUTE:**
- U1 (ESP32-WROOM-32): Must be exact part
- Q1 (IRLZ44N): Logic-level MOSFET required
- D5 (Schottky): Reverse polarity protection - critical

### 3. Assembly Notes
- **Power Input Polarity**: J1 Pin 1 = +12V, Pin 2 = GND
- **Control Output**: J2 provides 12V/5A max for contactor coil
- **Programming**: Via USB-C connector (J3)
- **Status LEDs**: Green = Connected, Red = Error

### 4. Testing Requirements
1. **Power-On Test**: 12V input should produce 3.3V and 5V outputs
2. **Control Test**: GPIO should switch relay K1
3. **WiFi Test**: ESP32 should connect to test network
4. **Load Test**: Verify 5A capability on control output

## External Components Required (Not on PCB)

To complete the 100A vehicle battery disconnect system:

### Automotive Contactor (Required)
- **Part**: Gigavac GX14 or equivalent
- **Rating**: 100A continuous, 12V coil
- **Control**: 12V from PCB J2 output
- **Wiring**: Heavy gauge (4AWG) for main power

### Installation Components
- **Fusing**: 100A ANL fuse in main power line
- **Wire**: 4AWG welding cable for main power
- **Terminals**: Heavy-duty ring terminals
- **Enclosure**: IP65 rated automotive enclosure

## Cost-Effective Production Strategy

### Phase 1: Control Board Prototype (Current Order)
- Order 5 PCBs with 2 assembled
- Test WiFi connectivity and control logic
- Validate power supply performance
- Estimated cost: $150-200

### Phase 2: System Integration
- Source automotive contactor separately
- Create wiring harness
- Field testing with actual vehicle
- Estimated additional cost: $200-300

## Common Pitfalls to Avoid

1. **Power Supply Loading**: Don't exceed 3A total board consumption
2. **Heat Management**: LM2596 may need heatsinking above 2A
3. **WiFi Antenna**: Keep clear of metal components
4. **ESD Protection**: Handle ESP32 with anti-static precautions
5. **Polarity**: Double-check all power connections

## Recommended Testing Sequence

1. **Bench Test**: 12V lab supply, verify all voltages
2. **Control Test**: Command relay switching via USB
3. **WiFi Test**: Connect to network, test MQTT
4. **Integration Test**: Connect to automotive contactor
5. **Vehicle Test**: Install and test complete system

## File Validation

### BOM Validation
- ✅ All parts available at JLCPCB
- ✅ Automotive-grade power supply
- ✅ Logic-level MOSFET for 3.3V control
- ✅ Proper protection diodes
- ✅ RTC crystal for timekeeping

### CPL Validation  
- ✅ No component overlaps
- ✅ Proper spacing for hand assembly
- ✅ Accessible test points
- ✅ Programming connector accessible

## Next Steps for Production

1. **Order Control PCBs** with corrected files
2. **Source automotive contactor** separately 
3. **Create integration documentation**
4. **Plan field testing phase**

---

**CRITICAL**: This design provides the control intelligence but requires external high-current switching components for the full 100A capability specified in your requirements.