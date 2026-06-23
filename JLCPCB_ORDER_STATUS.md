# JLCPCB Order Status — 2026-06-23

**Order:** W2026050802124660 | PCB: Y5-10434062A | PCBA: SMT026050763002
**Total:** $205.68 | Placed: 2026-05-07

## Current Phase: MONITORING COMPLETE — 34 days past delivery window

Delivery was expected May 18–20 via DHL Express to Katy TX 77493.

## Action for James Today
- **If boards have NOT arrived:** Contact JLCPCB support — this is critically overdue (4+ weeks late).
  DHL tracking: https://www.dhl.com/ | Order: https://jlcpcb.com/user-center/orders/
- **If boards DID arrive:** See firmware steps below — you're all set.

## When Boards Arrive
1. Flash `production/firmware/wifi_switch.ino` via Arduino IDE (USB data cable needed).
2. Connect to AP `Sarlls-Switch-XXXX` (password: `sarlls1234`), configure WiFi.
3. Demo for Eric at http://sarlls-switch.local
