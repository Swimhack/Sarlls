# Quote Comparison Template - Sarlls IoT Switch Project

## **QUOTE TRACKING SPREADSHEET STRUCTURE**

Create a spreadsheet with these columns to track all incoming quotes:

### **Column Headers:**

| A | B | C | D | E | F | G | H | I | J | K | L |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Vendor | Contact Email | Total Quote | PCB Cost | Assembly | Components | Shipping | Delivery Date | Payment Terms | Response Time | Quality Score | TOTAL SCORE |

### **Sample Data Structure:**

| Vendor | Contact Email | Total Quote | PCB Cost | Assembly | Components | Shipping | Delivery Date | Payment Terms | Response Time | Quality Score | TOTAL SCORE |
|--------|---------------|-------------|----------|-----------|-------------|-----------|---------------|---------------|---------------|---------------|-------------|
| PCBWay | onlinepcb@pcbway.com | $XXX | $XX | $XX | $XX | $XX | Friday | PayPal | 2 hrs | 8/10 | XX/40 |
| JLCPCB | support@jlcpcb.com | $XXX | $XX | $XX | $XX | $XX | Friday | CC | 1 hr | 9/10 | XX/40 |
| 4PCB | sales@4pcb.com | $XXX | $XX | $XX | $XX | $XX | Thursday | NET30 | 4 hrs | 9/10 | XX/40 |
| Sunstone | quotes@sunstone.com | $XXX | $XX | $XX | $XX | $XX | Friday | CC | 3 hrs | 8/10 | XX/40 |
| Sierra | sales@protoexpress.com | $XXX | $XX | $XX | $XX | $XX | Saturday | NET15 | 6 hrs | 8/10 | XX/40 |

---

## **SCORING SYSTEM**

### **1. Delivery Score (1-10 points)**
- **10 points**: Friday delivery GUARANTEED
- **8 points**: Thursday delivery (early!)
- **6 points**: Friday delivery "likely"
- **4 points**: Saturday delivery
- **2 points**: Monday delivery
- **0 points**: Cannot commit to specific date

### **2. Price Score (1-10 points)**
- **10 points**: Lowest total quote
- **8 points**: Within 10% of lowest
- **6 points**: Within 20% of lowest
- **4 points**: Within 30% of lowest
- **2 points**: Within 50% of lowest
- **0 points**: More than 50% above lowest

### **3. Quality/Reputation Score (1-10 points)**
- **10 points**: Excellent reputation, IPC certified
- **8 points**: Good reputation, quality focus
- **6 points**: Average reputation
- **4 points**: Mixed reviews
- **2 points**: Unknown reputation
- **0 points**: Poor reputation

### **4. Response Score (1-10 points)**
- **10 points**: Response within 1 hour
- **8 points**: Response within 2 hours
- **6 points**: Response within 4 hours
- **4 points**: Response within 8 hours
- **2 points**: Response within 24 hours
- **0 points**: No response after 24 hours

### **TOTAL SCORE: /40 points maximum**

---

## **DECISION MATRIX**

### **Qualification Criteria (Must Meet ALL):**
- ✅ Can deliver by Friday OR Thursday
- ✅ Provides complete turnkey service
- ✅ Responds within 8 hours
- ✅ Quote includes all costs
- ✅ Accepts standard payment methods

### **Evaluation Priority:**
1. **MUST deliver Friday** (eliminates non-qualifiers)
2. **Highest total score** wins
3. **Best value** (quality vs cost)

---

## **QUOTE EVALUATION CHECKLIST**

### **For Each Quote, Verify:**
- [ ] Total cost is clearly stated
- [ ] Delivery date is firm commitment
- [ ] All services included (design, fab, assembly, test)
- [ ] Shipping cost included
- [ ] Payment terms acceptable
- [ ] Company has good reputation
- [ ] Contact information is complete

---

## **SAMPLE EVALUATION**

### **Example Scoring:**

**PCBWay Quote Example:**
- **Delivery**: Friday guaranteed = 10 points
- **Price**: $350 total (lowest) = 10 points  
- **Quality**: Good reputation = 8 points
- **Response**: 2 hours = 8 points
- **TOTAL**: 36/40 points

**JLCPCB Quote Example:**
- **Delivery**: Friday likely = 6 points
- **Price**: $385 total (+10%) = 8 points
- **Quality**: Excellent reputation = 10 points
- **Response**: 1 hour = 10 points
- **TOTAL**: 34/40 points

**Winner**: PCBWay (36 points)

---

## **FOLLOW-UP EMAIL TEMPLATES**

### **If Quote is Too High:**
```
Subject: Quote Review - ESP32 IoT Switch Project

Thank you for your quote of $XXX for the ESP32 IoT switch project.

I've received several competitive quotes and yours is currently above our target range. Would you be able to:

1. Review the specifications for any cost savings
2. Provide alternative options or reduced quantities  
3. Offer your best final pricing

We're making a decision by [TIME] today and would like to include your company in the final evaluation.

Best regards,
[Name]
```

### **Final Clarification Email:**
```
Subject: Final Questions - ESP32 PCB Project Award

Your quote is being strongly considered for the ESP32 IoT switch project.

Final questions:
1. Can you GUARANTEE Friday delivery to Houston, TX?
2. What are your payment terms?
3. Is this your best pricing for potential repeat orders?
4. What is your order confirmation process?

Award decision will be made within 2 hours of your response.

Thank you,
[Name]
```

---

## **CONTRACT AWARD EMAIL**

```
Subject: PROJECT AWARDED - ESP32 IoT Switch Manufacturing

Congratulations! Your company has been selected for the ESP32 IoT switch manufacturing project.

**Project Details:**
- Quote accepted: $XXX total
- Delivery commitment: Friday to Houston, TX 77493
- Payment terms: [As agreed]

**Next Steps:**
1. Please send purchase order template
2. Confirm final specifications
3. Provide payment instructions
4. Schedule production kickoff

I am ready to proceed immediately. Please respond with next steps.

Best regards,
[Name]
[Phone for urgent contact]
```

---

## **BACKUP PLAN**

### **If Primary Vendor Fails:**
- **Contact #2 vendor** immediately
- **Explain situation**: "Our selected vendor had an issue"
- **Ask for expedited service**: "Can you help us out?"
- **Be willing to pay premium**: For emergency service

### **Emergency Contacts:**
Keep phone numbers handy for quick backup activation:
- PCBWay: +86 571 8531 7532
- JLCPCB: +86 755 2391 9769  
- Advanced Circuits: 1-800-979-4722

This template ensures systematic evaluation and quick decision-making to meet your Friday deadline.