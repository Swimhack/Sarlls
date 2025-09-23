# ESP32 IoT Switch - Complete Technical Specification
## **Professional PCB Manufacturing Documentation**

---

## **PROJECT OVERVIEW**
- **Product**: ESP32 IoT Switch v1.0
- **Purpose**: Wireless relay control for IoT applications
- **Quantity**: 5-10 prototype units
- **Timeline**: Delivery by Friday

---

## **PCB SPECIFICATIONS**
```
Board Size: 60mm x 40mm
Layer Count: 2 layers (Top + Bottom)
Board Thickness: 1.6mm
Copper Weight: 1oz (35μm)
Surface Finish: HASL or ENIG
Solder Mask: Green
Silkscreen: White
Minimum Trace Width: 0.2mm (8 mil)
Minimum Via: 0.3mm drill / 0.6mm pad
Board Material: FR-4
```

---

## **COMPLETE BILL OF MATERIALS (BOM)**

| Ref | Component | Package | Value | Manufacturer P/N | LCSC P/N | Qty |
|-----|-----------|---------|-------|------------------|----------|-----|
| U1 | ESP32-WROOM-32E | ESP32-Module | ESP32 | ESP32-WROOM-32E | C473012 | 1 |
| U2 | Voltage Regulator | SOT-223 | AMS1117-3.3 | AMS1117-3.3 | C6186 | 1 |
| U3 | USB-UART | QFN-28 | CP2102N | CP2102N-A02-GQFN28 | C964632 | 1 |
| K1 | Relay | Relay-SPDT | SRD-05VDC-SL-C | SRD-05VDC-SL-C | C35327 | 1 |
| Q1 | NPN Transistor | SOT-23 | BC817 | BC817 | C8545 | 1 |
| D1 | Diode | DO-41 | 1N4007 | 1N4007 | C53929 | 1 |
| D2 | LED Red | 0805 | Red | KT-0805R | C84256 | 1 |
| D3 | LED Blue | 0805 | Blue | KT-0805B | C72041 | 1 |
| D4 | LED Green | 0805 | Green | KT-0805G | C72043 | 1 |
| C1,C2 | Capacitor | 0805 | 10μF/25V | CL21A106KAYNNNE | C15850 | 2 |
| C3,C4,C5 | Capacitor | 0603 | 100nF/50V | CL10B104KB8NNNC | C14663 | 3 |
| R1,R2,R3 | Resistor | 0603 | 10kΩ | 0603WAF1002T5E | C25804 | 3 |
| R4,R5,R6 | Resistor | 0603 | 1kΩ | 0603WAF1001T5E | C21190 | 3 |
| R7 | Resistor | 0603 | 220Ω | 0603WAF2200T5E | C17560 | 1 |
| J1 | USB Connector | Micro-USB | Micro USB B | 105017-0001 | C132563 | 1 |
| J2 | Terminal Block | 3-pin | 5.08mm pitch | DG301-5.08-03P | C8445 | 1 |
| J3 | Terminal Block | 2-pin | 5.08mm pitch | DG301-5.08-02P | C8444 | 1 |
| J4 | Header | 2x3 | 2.54mm pitch | 2x3 Pin Header | C124375 | 1 |
| SW1,SW2 | Switch | 6x6mm | Tactile Switch | TS-1187A-B-A-B | C318884 | 2 |

---

## **SCHEMATIC CONNECTIONS**

### **Power Supply Circuit**
```
USB 5V (J1) → AMS1117-3.3 (U2) Input
AMS1117-3.3 Output → ESP32 3.3V Rail
C1 (10μF): USB 5V to GND (input filtering)
C2 (10μF): 3.3V to GND (output filtering) 
C3,C4,C5 (100nF): ESP32 power pin decoupling
```

### **ESP32 Core Connections**
```
ESP32 Pin 1 (GND) → Ground plane
ESP32 Pin 2 (3V3) → 3.3V rail
ESP32 Pin 3 (EN) → R1 (10kΩ) → 3.3V + SW1 → GND (Reset)
ESP32 Pin 25 (GPIO0) → R2 (10kΩ) → 3.3V + SW2 → GND (Boot)
ESP32 Pin 34 (RXD0) → U3 Pin 5 (TXD)
ESP32 Pin 35 (TXD0) → U3 Pin 4 (RXD)
```

### **GPIO Assignments**
```
GPIO2 → R4 (1kΩ) → LED D2 Anode (Power indicator)
GPIO4 → R5 (1kΩ) → LED D3 Anode (WiFi status)
GPIO12 → R7 (220Ω) → Q1 Base (Relay control)
GPIO13 → R6 (1kΩ) → LED D4 Anode (Relay status)
All LED cathodes → GND
```

### **Relay Control Circuit**
```
5V → Relay Coil Pin 1
Relay Coil Pin 2 → Q1 Collector
Q1 Emitter → GND
Q1 Base → R7 (220Ω) → ESP32 GPIO12
D1 (1N4007) Anode → 5V
D1 Cathode → Relay Coil Pin 2 (flyback protection)
```

### **Relay Output Connections**
```
Relay COM → J2 Pin 1 (Common)
Relay NO → J2 Pin 2 (Normally Open)
Relay NC → J2 Pin 3 (Normally Closed)
```

### **USB Programming Interface**
```
USB D+ → U3 Pin 16 (USBDP)
USB D- → U3 Pin 17 (USBDM)
USB 5V → 5V rail
USB GND → GND
U3 Pin 20 (VDD) → 3.3V
U3 Pin 9 (GND) → GND
```

### **External Power Input**
```
J3 Pin 1 → 5V rail (alternative power input)
J3 Pin 2 → GND
```

### **Programming Header (J4)**
```
Pin 1: 3.3V
Pin 2: GND
Pin 3: ESP32 TXD0 (GPIO1)
Pin 4: ESP32 RXD0 (GPIO3)
Pin 5: ESP32 GPIO0 (Boot mode)
Pin 6: ESP32 EN (Reset)
```

---

## **PCB LAYOUT REQUIREMENTS**

### **Component Placement Guidelines**
```
TOP SIDE:
- U1 (ESP32): Center, horizontal orientation
- J1 (USB): Left edge, accessible from front
- K1 (Relay): Right side, minimum 5mm clearance from ESP32
- J2,J3 (Terminals): Top edge, easy wire access
- D2,D3,D4 (LEDs): Near USB, front-facing
- SW1,SW2 (Buttons): Adjacent to ESP32, accessible
- J4 (Header): Bottom edge

BOTTOM SIDE:
- U2 (Regulator): Near power input
- U3 (USB chip): Near USB connector  
- Q1 (Transistor): Near relay
- All SMD passives (R, C components)
```

### **Routing Specifications**
```
TRACE WIDTHS:
- Power traces (5V, 3.3V): 0.5mm minimum
- Ground connections: 0.3mm minimum
- Signal traces: 0.2mm minimum
- Relay switching: 0.8mm minimum (isolated routing)

LAYER STACK:
- Layer 1 (Top): Component placement + signal routing
- Layer 2 (Bottom): Ground plane + power distribution

VIA SPECIFICATIONS:
- Standard: 0.3mm drill, 0.6mm pad
- Power: 0.4mm drill, 0.8mm pad
- Minimum via-to-via: 0.3mm
```

### **Critical Design Rules**
```
1. Keep switching relay traces away from ESP32 antenna area
2. Maintain 5mm keepout around ESP32 for RF performance
3. Route crystal traces (if used) with ground guards
4. Use ground plane stitching vias every 5mm
5. Isolate analog and digital grounds at single point
6. Place decoupling caps within 5mm of power pins
```

### **Mechanical Specifications**
```
BOARD OUTLINE: 60.0mm x 40.0mm rectangle
CORNER RADIUS: 0.5mm
MOUNTING HOLES: 4x 3.0mm diameter
HOLE POSITIONS: (3,3), (57,3), (57,37), (3,37) mm
EDGE CLEARANCE: 0.5mm minimum from components
```

---

## **ASSEMBLY REQUIREMENTS**

### **SMT Assembly Process**
```
1. Apply solder paste (lead-free, SAC305)
2. Place components using pick-and-place
3. Reflow solder (RoHS compliant profile)
4. AOI (Automated Optical Inspection)
5. ICT (In-Circuit Test) if available
```

### **Through-Hole Assembly**
```
1. Insert through-hole components
2. Wave solder or selective solder
3. Clean flux residue
4. Visual inspection
```

### **Assembly Order**
```
BOTTOM SIDE FIRST:
- SMD resistors and capacitors
- U2 (SOT-223 regulator)
- U3 (QFN USB chip)
- Q1 (SOT-23 transistor)

TOP SIDE SECOND:
- U1 (ESP32 module)
- Through-hole components (J1, J2, J3, J4, K1, SW1, SW2)
- LEDs (0805 packages)
- D1 (DO-41 diode)
```

---

## **QUALITY & TESTING STANDARDS**

### **Quality Requirements**
```
- IPC-A-610 Class 2 acceptability standards
- RoHS compliant materials and processes
- Lead-free solder (SAC305 or equivalent)
- Conformal coating optional (specify if needed)
```

### **Electrical Testing**
```
POWER SUPPLY TEST:
- Input: 5V ±0.25V
- Output: 3.3V ±0.1V
- Current consumption: <200mA idle

FUNCTIONAL TESTS:
- USB connectivity verification
- ESP32 programming interface
- Relay coil resistance: 70Ω ±10%
- Contact resistance: <100mΩ
- LED forward voltage: 1.8-2.2V
- Button continuity and resistance
```

### **Programming Test Code**
```cpp
// Basic functionality test firmware
#define RELAY_PIN 12
#define POWER_LED 2
#define WIFI_LED 4
#define RELAY_LED 13

void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(POWER_LED, OUTPUT);
  pinMode(WIFI_LED, OUTPUT);  
  pinMode(RELAY_LED, OUTPUT);
  digitalWrite(POWER_LED, HIGH);
  Serial.println("ESP32 IoT Switch Test");
}

void loop() {
  // Relay test cycle
  digitalWrite(RELAY_PIN, HIGH);
  digitalWrite(RELAY_LED, HIGH);
  Serial.println("Relay ON");
  delay(2000);
  
  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(RELAY_LED, LOW);
  Serial.println("Relay OFF");
  delay(2000);
}
```

---

## **DELIVERABLES SPECIFICATION**

### **Required Files**
```
1. Gerber Files Package:
   - .GTL (Top copper)
   - .GBL (Bottom copper)
   - .GTS (Top soldermask)
   - .GBS (Bottom soldermask)
   - .GTO (Top silkscreen)
   - .GBO (Bottom silkscreen)
   - .GKO (Board outline)
   - .DRL (Drill file)

2. Manufacturing Files:
   - Assembly drawings (top/bottom)
   - Component placement drawing
   - Drill chart
   - Fabrication notes

3. Documentation:
   - As-built BOM
   - Test report
   - Certificate of compliance
   - Assembly photos
```

### **Physical Deliverables**
```
- Quantity: 5-10 assembled and tested PCBs
- Packaging: Anti-static bags, protective foam
- Shipping: Express to Houston, TX 77493
- Lead time: Delivery by Friday
```

---

## **SPECIAL INSTRUCTIONS**

### **Critical Notes**
```
1. ESP32 module requires careful reflow profile - avoid overheating
2. Relay must be tested under load conditions (resistive 5A minimum)
3. USB connector must be properly secured to board
4. All LEDs must be tested for proper orientation
5. Programming header must be functional for firmware upload
```

### **Optional Enhancements**
```
- Conformal coating for moisture protection
- Programming/testing fixture if quantity >10
- Custom packaging with project labels
- Extended burn-in testing (24 hours)
```

---

**This specification is complete and ready for professional PCB manufacturing and assembly.**