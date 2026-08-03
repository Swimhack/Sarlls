# Bill of Materials — SafeSwitch IoT Smart Switch Rev 2

## Active Components

| Ref | Value | Package | Description | LCSC Part # |
|-----|-------|---------|-------------|-------------|
| U1 | ESP32-WROOM-32 | Module | WiFi/BLE MCU | C82899 |
| U2 | AMS1117-3.3 | SOT-223 | 3.3V LDO regulator | C6186 |
| U3 | CP2102N | QFN-28 | USB-UART bridge | C165948 |
| Q1 | S8050 | SOT-23 | NPN transistor (relay driver) | C2146 |
| D1 | 1N4007 | DO-41 | Flyback diode | C181139 |
| D2 | LED (green) | 0805 | Power indicator | C72043 |
| D3 | LED (red) | 0805 | Relay status indicator | C84256 |
| K1 | SRD-05VDC-SL-C | THT | 5V SPDT relay (10A) | C35449 |

## Passive Components

| Ref | Value | Package | Description | LCSC Part # |
|-----|-------|---------|-------------|-------------|
| C1 | 10µF | 0805 | +5V bypass | C15850 |
| C2 | 10µF | 0805 | +3V3 bypass | C15850 |
| C3 | 100nF | 0805 | +3V3 decoupling | C49678 |
| C4 | 100nF | 0805 | EN filter | C49678 |
| C5 | 100nF | 0805 | +3V3 decoupling | C49678 |
| C6 | 100nF | 0805 | +3V3 decoupling | C49678 |
| C7 | 100nF | 0402 | +5V decoupling | C307331 |
| C8 | 100nF | 0402 | +5V decoupling | C307331 |
| R1 | 10kΩ | 0805 | EN pull-up | C17414 |
| R2 | 10kΩ | 0805 | IO0 pull-up | C17414 |
| R3 | 1kΩ | 0805 | Relay base resistor | C17513 |
| R4 | 330Ω | 0805 | Power LED resistor | C25104 |
| R5 | 330Ω | 0805 | Relay LED resistor | C25104 |
| R6 | 5.1kΩ | 0402 | USB-C CC1 pull-down | C25905 |
| R7 | 5.1kΩ | 0402 | USB-C CC2 pull-down | C25905 |
| FB1 | 600Ω@100MHz | 0805 | VBUS ferrite bead | C1015 |

## Connectors & Mechanical

| Ref | Value | Package | Description | LCSC Part # |
|-----|-------|---------|-------------|-------------|
| J1 | USB4105-GF-A | USB-C 16P | USB-C receptacle (edge-mount) | C165948 |
| J2 | MC 1,5/2-G-3.81 | THT | 2-pin screw terminal | — |
| SW1 | TL3342 | THT | BOOT tactile switch | C318884 |
| SW2 | TL3342 | THT | RESET tactile switch | C318884 |
| — | M2.5 | 2.7mm hole | Mounting holes (x4) | — |

## Vehicle Integration (not on PCB)

| Item | Description | Est. Cost |
|------|-------------|-----------|
| Automotive contactor | 12V DC, 200A+ continuous | ~$20 |
| Buck converter | 12V→5V, 2A USB-C output | ~$5 |
| Wiring harness | 10AWG for contactor, 22AWG for signal | ~$10 |
| Enclosure | IP65 weatherproof box | ~$15 |
