# Vehicle Integration — Battery Disconnect System

## Use Case
Eric wants to remotely disconnect his car battery while parked to prevent theft/parasitic drain, then reconnect before returning.

## System Architecture

```
Phone (SafeSwitch App)
    |
    | WiFi HTTP request
    v
ESP32 Board (brain)
    |
    | 10A relay switches 12V to contactor coil
    v
Automotive Contactor (muscle, 200A+)
    |
    | High-current contacts
    v
Battery Negative Cable (disconnected/connected)
```

## Components Needed

| Component | Purpose | Est. Cost |
|-----------|---------|-----------|
| ESP32 IoT board (have) | WiFi controller | $0 |
| Automotive contactor 200A | Battery disconnect switch | ~$20 |
| 12V to 5V buck converter | Power board from car battery | ~$5 |
| Wire + connectors | Wiring harness | ~$10 |
| **Total** | | **~$35** |

## Power Strategy
- Tap 12V from battery BEFORE the contactor (always-hot)
- Buck converter steps 12V down to 5V for ESP32
- Board stays powered even when main battery is disconnected
- ESP32 deep sleep mode to minimize parasitic draw on battery (~10mA)

## Contactor Selection Criteria
- 12V coil (driven by board's relay)
- 200A+ continuous rating (handles starter current if reconnected while starting)
- Normally-open preferred (battery disconnected when board loses power = fail-safe)
- Consider: normally-closed may be better (battery stays connected if board dies)

## Wiring Plan
1. Battery negative terminal → contactor input terminal
2. Contactor output terminal → chassis ground
3. Contactor coil positive → board relay COM/NO output
4. Contactor coil negative → ground
5. 12V tap (before contactor) → buck converter → board USB-C or direct 5V input

## Safety Considerations
- Fuse on 12V tap to board (1A inline fuse)
- Contactor rated for continuous duty (not intermittent)
- Board should report battery voltage for monitoring
- Consider adding current sense for "monitoring" contract requirement
- Fail-safe behavior: decide if battery should stay connected or disconnected if board loses power

## Rev 2 Board Changes Needed
- Add 12V input with onboard buck converter (eliminate external buck)
- Add battery voltage divider to ESP32 ADC pin (monitoring)
- Larger screw terminal for contactor coil wiring
- Move D1 away from USB-C
- Fix SW1/SW2/J2 footprints
