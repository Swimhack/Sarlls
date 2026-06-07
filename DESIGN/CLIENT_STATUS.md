# Client Status — Eric Sarlls

## Last Updated: 2026-06-06

## Engineering Status
- Rev 1 boards arrived, but hardware bring-up is incomplete.
- USB enumeration, firmware flashing, and relay operation are not confirmed.
- Rev 2 controller PCB is a verified pre-fabrication candidate with zero
  blocking DRC findings.
- The mobile app remains a UI prototype and is not integrated with the ESP32.
- The current controller board is USB-C powered and is not yet a complete
  automotive battery-disconnect product.

## Communication Timeline
- **2026-05-11:** Invoice ES-05112026 sent for $3,700 (120-day milestone payment)
- **2026-05-11 to 05-17:** No response from Eric
- **2026-05-18 ~7:40pm:** James texted board photos to Eric — "Hey Eric, Boards came in today"
- **2026-05-18 8:44pm:** Eric replied — "Thank you James. Very Excited"
- **Invoice status:** Sent, not yet paid. Eric has not acknowledged invoice directly.

## Contract Summary
- **Total contract:** $17,321
- **Paid to date:** $13,535.50
- **Outstanding invoice:** $3,700 (120-day milestone — overdue by contract terms)
- **Final payment:** $5,785.50 (due upon project completion)
- **Monthly maintenance:** $100/month post-delivery
- **Scope:** Mobile app + smart switch prototype for 12V car battery disconnect + monitoring

## Strategy
- Do NOT chase invoice directly
- Lead with project progress — working demo is the best collection tool
- After firmware is flashed and relay is clicking over WiFi, send demo video
- Mention invoice casually after progress update: "Also just making sure that invoice didn't end up in spam"
- $3,700 covers work already completed — boards in hand justify this payment regardless of prototype status
- Wait for working prototype before invoicing the $5,785.50 final payment

## What Eric Expects
- A working prototype that disconnects his car battery remotely from his phone
- Mobile app (SafeSwitch) that actually communicates with the hardware
- Real-time monitoring of connection status
- He does NOT know this is the first PCB attempt — maintain confidence

## Prototype Delivery Plan
1. Attempt Rev 1 USB and relay bring-up, or document Rev 1 as superseded.
2. Complete Rev 2 assembler DFM and part-footprint review.
3. Order and bring up Rev 2.
4. Integrate SafeSwitch app control with the ESP32 API.
5. Design and validate protected 12V power and the external contactor system.
6. Demonstrate remote battery disconnect only after the complete system passes
   bench and vehicle-safety testing.
