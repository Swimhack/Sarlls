# JLCPCB Order Checklist - ESP32 IoT Control Board

## Pre-Order Validation ✅

- ✅ **BOM Corrected**: Automotive-compatible power supply
- ✅ **CPL Updated**: Component placement optimized  
- ✅ **Gerber Files**: Use existing iot_switch_gerber.zip (layout should work)
- ✅ **JLCPCB Parts**: All components verified in stock

## Order Configuration

### PCB Specifications
```
Quantity: 5 pieces
Layers: 2
Dimensions: 45mm x 35mm  
Thickness: 1.6mm
Color: Green (standard)
Surface Finish: HASL
Via Covering: Tented
```

### PCBA Configuration
```
Assembly Side: Top side only
Tooling holes: Added by Customer
Confirm Parts Placement: Yes
Quantity for Assembly: 2 pieces
```

### Files to Upload
1. **Gerber**: Use existing `iot_switch_gerber.zip`
2. **BOM**: Upload `ESP32_IoT_Switch_BOM_CORRECTED.csv`
3. **CPL**: Upload `ESP32_IoT_Switch_CPL_CORRECTED.csv`

## Component Verification Steps

### Use JLCPCB BOM Tool
1. Upload corrected BOM file
2. Check for any unavailable parts
3. Accept suggested alternatives for non-critical components
4. **DO NOT substitute**: ESP32, IRLZ44N MOSFET, Schottky diodes

### Expected Substitutions (OK to accept)
- Electrolytic capacitors (±20% value range)
- Ceramic capacitors (same value, different package codes)
- Generic resistors (same value, different manufacturers)

### Critical Parts (Must be exact)
- U1: ESP32-WROOM-32 (C82899)
- Q1: IRLZ44N or equivalent logic-level MOSFET
- D5: Schottky diode for reverse polarity protection

## Cost Estimation
- **PCB Only (5 pieces)**: ~$15
- **Assembly (2 pieces)**: ~$80-120
- **Components**: ~$50-80  
- **Shipping (Standard)**: ~$15
- **Total Expected**: ~$160-230

## Rush Options
- **24-hour PCB**: Add $20-30
- **48-hour Assembly**: Add $40-60
- **DHL Express**: Add $25-35

## Pre-Flight Checklist

Before clicking "Add to Cart":

### ✅ File Verification
- [ ] Corrected BOM uploaded
- [ ] Corrected CPL uploaded  
- [ ] Gerber file selected
- [ ] All critical components verified available

### ✅ Specifications
- [ ] PCB size matches design (45x35mm)
- [ ] Assembly quantity: 2 pieces
- [ ] Color and finish selected
- [ ] Delivery address correct

### ✅ Timeline  
- [ ] Standard delivery: 10-12 days
- [ ] Rush options selected if needed
- [ ] Payment method ready

## Post-Order Actions

### After Order Confirmation
1. **Save order number** for tracking
2. **Monitor order status** daily
3. **Prepare test setup** for when boards arrive
4. **Source external contactor** components

### When Boards Arrive
1. **Visual inspection** for assembly quality
2. **Power supply test** (12V → 3.3V, 5V)
3. **ESP32 programming test** via USB-C
4. **Relay control test** 
5. **WiFi connectivity test**

## Backup Plan

If critical components unavailable:
1. **Place order without assembly** (PCBs only)
2. **Hand-solder critical components** 
3. **Use alternative ESP32 boards** for prototyping

## Contact Information

**For Order Issues:**
- JLCPCB Support Chat
- Email: support@jlcpcb.com
- Reference: ESP32 IoT Control Board

**For Technical Questions:**
- Reference this manufacturing notes document
- Check component datasheets
- Validate pinouts before assembly

---

**READY TO ORDER**: Use corrected files in updated_docs folder