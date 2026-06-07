# SafeSwitch Rev2 Board Order Handoff

**Purpose:** Complete every required check before ordering Rev2 boards.  
**Audience:** Project owner, manufacturer, assembler, or engineer completing the order.  
**Current phase:** Rev2 controller PCB pre-fabrication review.  
**Order status:** Do not order until every blocking checklist item passes.

## 1. Rev2 Scope

Rev2 is a USB-C-powered ESP32 relay-controller prototype. It is intended to
validate:

- USB power and programming
- ESP32 operation
- WiFi control
- Relay control
- External contactor control through the relay output

Rev2 is not the complete automotive product. It does not include protected
vehicle 12V power input or the high-current battery-disconnect contactor.

## 2. Board Specification

| Item | Specification |
|---|---|
| Board size | 80 mm x 60 mm |
| Layers | 2 |
| Material | FR-4 |
| Thickness | 1.6 mm |
| Copper | 1 oz |
| Surface finish | Lead-free HASL or ENIG |
| Solder mask | Green, both sides |
| Silkscreen | White, top side |
| Assembly side | Top |
| Input power | USB-C 5V |
| Controller | ESP32-WROOM-32 |
| USB interface | CP2102N USB-UART |
| Output | 5V relay dry contacts through J2 |

### Manufacturing Rules

| Item | Specification |
|---|---|
| Typical signal trace | 0.20 mm |
| Minimum signal trace | 0.15 mm |
| Power trace | 0.50 mm |
| Typical via | 0.60 mm pad / 0.30 mm drill |
| Power via | 0.80 mm pad / 0.40 mm drill |
| Small J1 escape via | 0.40 mm pad / 0.20 mm drill |

## 3. Authoritative Order Files

Only use these files for the Rev2 order:

| File | Purpose |
|---|---|
| `production/Sarlls_IoT_Switch_Rev2_JLCPCB.zip` | PCB fabrication Gerbers and drill files |
| `production/ESP32_Simple_IoT_BOM.csv` | Bill of materials |
| `production/ESP32_Simple_IoT_CPL.csv` | Component placement list |
| `production/FABRICATION_SPEC.txt` | Fabrication notes |
| `production/drc_report.json` | Latest design-rule report |

The Gerber ZIP must contain exactly these 11 files:

- `ESP32_Simple_IoT-F_Cu.gtl`
- `ESP32_Simple_IoT-B_Cu.gbl`
- `ESP32_Simple_IoT-F_Mask.gts`
- `ESP32_Simple_IoT-B_Mask.gbs`
- `ESP32_Simple_IoT-F_Paste.gtp`
- `ESP32_Simple_IoT-F_Silkscreen.gto`
- `ESP32_Simple_IoT-B_Silkscreen.gbo`
- `ESP32_Simple_IoT-Edge_Cuts.gm1`
- `ESP32_Simple_IoT-PTH.drl`
- `ESP32_Simple_IoT-NPTH.drl`
- `ESP32_Simple_IoT-job.gbrjob`

Do not use older Rev1, v1.2, PCBWay, MacroFab, or patch-generated ZIP files.

## 4. Internal Release Validation

Complete this before uploading files to a manufacturer.

### Required DRC Result

```text
DRC gate: 0 blocking, 26 approved J1 edge errors, 11 warnings
```

The 26 approved errors are caused by the USB-C connector intentionally sitting
at the board edge. All other errors block the order.

### Blocking Findings

Do not order if the report contains any:

- Unconnected electrical connections
- Shorts between electrical connections
- Crossing traces
- Ordinary copper-clearance errors
- Hole-clearance errors
- Ground-plane connection errors

### Run the Release Check

```powershell
& "C:\Users\james\AppData\Local\Programs\KiCad\9.0\bin\python.exe" `
  scripts\validate_drc.py production\drc_report.json
```

### Internal Validation Checklist

- [ ] DRC gate reports zero blocking findings.
- [ ] Gerber ZIP contains exactly the 11 expected files.
- [ ] BOM opens correctly and contains 20 line items.
- [ ] CPL opens correctly and contains 28 placements.
- [ ] Board size is shown as 80 mm x 60 mm.
- [ ] No older design files are being used.

## 5. Step One: Manufacturer Review of USB-C Area

### Reason

The USB-C connector is mounted at the board edge. Two USB power connections use
small via-in-pad escapes. These must be reviewed because solder can potentially
flow into the holes during assembly.

### Send the Manufacturer

- Rev2 Gerber ZIP
- BOM
- CPL
- Fabrication specification
- The following question:

> Please review the USB-C connector J1. It uses two 0.40 mm pad / 0.20 mm drill
> via-in-pad VBUS escapes. Can you reliably fabricate and assemble this area?
> Is via filling, plugging, or another process required to prevent solder
> wicking? Please identify any required cost or design change before production.

### Required Manufacturer Answers

- Can the 0.20 mm drill holes be manufactured?
- Can the USB-C connector be assembled reliably?
- Is via filling or plugging required?
- Will the USB-C connector sit at the board edge correctly?
- Is additional cost or special processing required?
- Does the manufacturer recommend any design change?

### Pass Condition

The manufacturer confirms the USB-C area is manufacturable and provides any
required process settings or costs.

### Fail Condition

Stop the order if the manufacturer:

- Rejects the small vias
- Warns that solder wicking may cause unreliable joints
- Requires an unapproved design change
- Cannot assemble the edge-mounted connector
- Does not provide a clear answer

## 6. Step Two: Confirm SW1, SW2, and J2 Fit

### Reason

Rev1 arrived without SW1, SW2, and J2 because the selected components did not
match the board footprints. Rev2 must not be ordered until the exact parts are
confirmed.

### Components Requiring Confirmation

| Reference | Function | Required Check |
|---|---|---|
| SW1 | Boot button | Exact part matches footprint, pin layout, size, and rotation |
| SW2 | Reset button | Exact part matches footprint, pin layout, size, and rotation |
| J2 | Relay-output wire connector | Exact part matches hole spacing, pin spacing, size, and orientation |

### Ask the Manufacturer

> Please confirm the selected part numbers for SW1, SW2, and J2 physically and
> electrically match the PCB footprints. Confirm whether each part will be
> installed during assembly or must be installed manually.

### Required Confirmation

For each component, record:

| Item | SW1 | SW2 | J2 |
|---|---|---|---|
| Manufacturer part number confirmed |  |  |  |
| Package/footprint confirmed |  |  |  |
| Pin layout confirmed |  |  |  |
| Orientation confirmed |  |  |  |
| In stock |  |  |  |
| Assembly method confirmed |  |  |  |

### Pass Condition

All three components have confirmed matching part numbers, footprints,
orientation, availability, and assembly method.

### Fail Condition

Stop the order if any component:

- Does not match its footprint
- Is unavailable without an approved substitute
- Has uncertain pin layout or orientation
- Is omitted from the assembly quote or preview
- Requires manual assembly that has not been planned

## 7. Step Three: Manufacturer DFM and Preview Review

### Reason

The manufacturer's Design for Manufacturing review and visual placement preview
are the final opportunity to catch missing, rotated, or incorrectly placed
parts before payment.

### PCB Fabrication Preview Checks

- [ ] Board dimensions are 80 mm x 60 mm.
- [ ] Board outline is complete and not distorted.
- [ ] USB-C connector opening is at the board edge.
- [ ] No board material blocks the USB-C opening.
- [ ] All mounting holes are visible.
- [ ] Plated and non-plated drill files were recognized separately.
- [ ] Copper layers appear complete.
- [ ] Solder-mask openings appear reasonable.
- [ ] No unexpected internal slots, cutouts, or extra boards appear.

### Assembly Preview Checks

- [ ] J1 USB-C connector is present and correctly oriented.
- [ ] D1 is away from the USB-C connector.
- [ ] SW1 is present.
- [ ] SW2 is present.
- [ ] J2 is present.
- [ ] ESP32 module U1 faces the expected direction.
- [ ] USB-UART chip U3 is present.
- [ ] Relay K1 and diode D1 assembly method is confirmed.
- [ ] No component is marked missing, unidentified, or unconfirmed.
- [ ] No unexpected component substitutions were made.
- [ ] Every substitution has been reviewed and approved.

### DFM Report Checks

- [ ] Manufacturer reports no unresolved fabrication errors.
- [ ] USB-C edge placement is accepted.
- [ ] USB-C via-in-pad process is accepted.
- [ ] Minimum drill and trace sizes are accepted.
- [ ] Board thickness, copper weight, finish, and colors are correct.
- [ ] Quantity and assembly quantity are correct.

### Pass Condition

The fabrication preview, assembly preview, and DFM report are correct, and all
manufacturer warnings are resolved or explicitly approved.

### Fail Condition

Stop the order if:

- A component is missing, misplaced, or rotated incorrectly
- The USB-C port is blocked or not at the edge
- SW1, SW2, or J2 is missing
- The wrong board dimensions or specifications are shown
- The manufacturer reports an unresolved production issue
- An unapproved substitution is present

## 8. Order Configuration

Use these order settings unless the manufacturer provides an approved reason
to change them:

| Setting | Required Value |
|---|---|
| Quantity | Prototype quantity, normally 5 |
| Layers | 2 |
| Dimensions | 80 mm x 60 mm |
| Thickness | 1.6 mm |
| Copper weight | 1 oz |
| Material | FR-4 |
| Surface finish | Lead-free HASL or approved ENIG upgrade |
| Solder mask | Green |
| Silkscreen | White |
| Assembly | Top-side assembly |
| Electrical test | Yes |
| Flying-probe test | Yes, if offered |

Confirm whether through-hole parts K1, D1, and J2 will be installed by the
manufacturer or manually after delivery.

## 9. Final Approval Gate

The person approving the order must complete every blocking item:

### Files and Design

- [ ] Correct Rev2 Gerber ZIP selected.
- [ ] Correct Rev2 BOM selected.
- [ ] Correct Rev2 CPL selected.
- [ ] DRC gate reports zero blocking findings.
- [ ] Gerber ZIP contains exactly the expected 11 files.

### Manufacturer Review

- [ ] Manufacturer approved J1 USB-C via-in-pad construction.
- [ ] Required USB-C special processing and cost are understood.
- [ ] SW1 exact part and footprint are confirmed.
- [ ] SW2 exact part and footprint are confirmed.
- [ ] J2 exact part and footprint are confirmed.

### Preview and Quote

- [ ] Fabrication preview reviewed.
- [ ] Assembly preview reviewed.
- [ ] DFM report reviewed.
- [ ] Every substitution reviewed.
- [ ] Through-hole assembly plan confirmed.
- [ ] Quantity, specifications, price, and delivery address confirmed.
- [ ] No unresolved manufacturer warning remains.

**Do not pay for or approve production until every item above is checked.**

## 10. Records to Save After Ordering

Save the following in the project:

- Final uploaded Gerber ZIP
- Final uploaded BOM and CPL
- Screenshots of fabrication and assembly previews
- Manufacturer DFM report
- Manufacturer written approval of USB-C via-in-pad construction
- Confirmed SW1, SW2, and J2 part numbers
- Approved substitutions
- Final quote and order confirmation
- Order number
- Tracking number when available

Record:

| Item | Value |
|---|---|
| Manufacturer |  |
| Order number |  |
| Order date |  |
| Quantity |  |
| Total cost |  |
| USB-C review contact |  |
| SW1 part number |  |
| SW2 part number |  |
| J2 part number |  |
| Expected delivery date |  |
| Tracking number |  |

## 11. After the Boards Arrive

Do not install Rev2 in a vehicle immediately.

Complete controlled bench testing first:

1. Inspect the board for damage, missing parts, and solder defects.
2. Confirm the USB-C cable inserts fully.
3. Confirm USB enumeration.
4. Flash the hardware test firmware using the `huge_app` partition.
5. Test 5V and 3.3V power rails.
6. Test WiFi and serial communication.
7. Test relay and LEDs.
8. Test J2 output with a low-risk bench load.
9. Document all results before automotive integration.

