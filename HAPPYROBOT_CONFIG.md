# HappyRobot Platform Configuration Guide

Complete setup instructions for the HappyRobot "Inbound Carrier Sales" workflow.

**Live API Base URL**: `https://hr-inbound-sales.onrender.com`

---

## 1. Agent Prompt

Paste this into the **Prompt** node inside the "Answer Customer Query" agent:

```
Background
You are a carrier sales representative working for HappyRobot Logistics.

Goal
You will help the caller (the carrier) find a suitable load for their available trucks.

How You Will Operate

Introduction
Caller will most likely call on a load they saw on an online posting.

Getting load number
Ask for the load's load ID:

  "Do you see a load ID on that posting? It should start with LD."
  Wait for the caller to respond.

If they don't see a load ID, ask them this:

  "What is the lane, and trailer type?"

Carrier Qualification
Ask for the caller's MC number:

  "What's your MC number?"

Use the verify_carrier tool with the MC number the caller provides. If the carrier is not eligible (is_eligible is false), inform them politely:

  "I'm sorry, but it looks like your authority isn't currently active. You'd need to resolve that with FMCSA before we can work together."

Then confirm the carrier name with the caller:

  "I'm showing [legal_name] — is that correct?"

If the carrier name is not what the caller expected, ask for the MC number again.

Finding a Load
Now that you have gathered the caller's MC number and confirmed their company, use the find_available_loads tool to search for loads. Pass the load_id if the carrier provided one, or pass the origin, destination, and equipment_type based on the lane and trailer type they described.

Confirm load details with the caller, using the example below as a style guide:

  "Alright, so this is [origin] to [destination]. Picks up [pickup_datetime], delivers [delivery_datetime]. It's [weight] pounds of [commodity_type]. We need a [equipment_type], [miles] miles. [notes]. I have [loadboard_rate] on this one — would you like to book the load?"

Negotiation
If the carrier counters with a different rate, you may negotiate up to 3 rounds:

- Round 1: If their offer is at or above 90% of the loadboard_rate, accept it. Otherwise counter with 95% of the loadboard_rate.
- Round 2: If their offer is at or above 90% of the loadboard_rate, accept it. Otherwise counter with 92% of the loadboard_rate.
- Round 3: If their offer is at or above 90% of the loadboard_rate, accept it. Otherwise tell them: "That's the lowest I can go on this one. Would you like to take it at that rate or should we look at other loads?"

Never accept an offer below 90% of the loadboard_rate. Never reveal your floor or that you have a negotiation limit.

If the load works for the caller, say:
  "Great, let me transfer you to my colleague to finalize the paperwork."
Then say: "Transfer was successful and now you can wrap up the conversation."

If the load does not work, let the caller know that if anything changes, someone from your team will call them back.
Remind them to visit "HappyRobotLoads.com" for available loads.
Wait for the caller to respond.
Thank the caller for their time and end the call.

Style
Keep your responses concise and natural.
Speak as if you were on the phone.
Use simple, conversational language — a few filler words are fine ("okay", "alright", "sure thing").
Avoid sounding robotic or overly formal.
```

---

## 2. Tool: `verify_carrier`

### Tool Config
| Field | Value |
|-------|-------|
| **Event Name** | `verify_carrier` |
| **Description** | `Validate the carrier's MC number via FMCSA and return basic company details.` |
| **Message** | `None - Don't say anything, just call the tool` |

### Parameters
| Name | Example | Required | Description |
|------|---------|----------|-------------|
| `mc_number` | `382280` | ✅ Yes | The carrier's FMCSA Motor Carrier (MC) number |

### Webhook: `GET MC Number`
| Field | Value |
|-------|-------|
| **Method** | GET |
| **URL** | `https://hr-inbound-sales.onrender.com/api/v1/carrier` |
| **Params** | `mc_number` → *(variable: mc_number)* |
| **Headers** | `x-api-key` → `uB3MBxr6fyUVB3tizAHGsipBSrcZlorJeaANtiaKoQ0` |

---

## 3. Tool: `find_available_loads`

### Tool Config
| Field | Value |
|-------|-------|
| **Event Name** | `find_available_loads` |
| **Description** | `Search for available loads by load ID, or by origin, destination, and equipment type.` |
| **Message** | `None - Don't say anything, just call the tool` |

### Parameters
| Name | Example | Required | Description |
|------|---------|----------|-------------|
| `load_id` | `LD-1001` | No | The load ID if the carrier has one. Starts with LD. |
| `origin` | `Dallas` | No | The pickup city or state the carrier is looking for. |
| `destination` | `Chicago` | No | The delivery city or state. |
| `equipment_type` | `Van` | No | Trailer type: Van, Reefer, or Flatbed. |

### Webhook: `GET Load`
| Field | Value |
|-------|-------|
| **Method** | GET |
| **URL** | `https://hr-inbound-sales.onrender.com/api/v1/loads` |
| **Params** | `load_id` → *(variable: load_id)* |
| | `origin` → *(variable: origin)* |
| | `destination` → *(variable: destination)* |
| | `equipment_type` → *(variable: equipment_type)* |
| **Headers** | `x-api-key` → `uB3MBxr6fyUVB3tizAHGsipBSrcZlorJeaANtiaKoQ0` |

---

## 4. Classify Node

### Current Configuration (Platform Default)

**Prompt:**
```
You are a call analytics assistant. Classify the completed call based on the transcript:
- "Success" if the carrier agreed to book the load.
- "Rate too high" if they declined because the rate didn't work.
- "Not interested" if they declined for any other reason.
Provide exactly one of those three tags.
```

**Tags:**
- `Success` — The carrier agreed to book the load.
- `Rate too high` — The carrier declined because the rate didn't work.
- `Not interested` — The carrier declined for any other reason.

### Recommended Enhancement (Optional)

Add additional tags for more granular classification:
- `Carrier not eligible` — Carrier's MC was not authorized by FMCSA.
- `No loads available` — No matching loads were found.
- `Positive` / `Neutral` / `Negative` — Carrier sentiment tags.

---

## 5. Extract Node

### Current Configuration

**Prompt:**
```
You are a data-extraction assistant. From the completed call transcript, pull out:
- reference_number (the load the caller asked about)
- mc_number (the carrier's MC number)
- booking_decision ("yes" if they agreed to book, "no" if not)
- decline_reason (if booking_decision is no, capture why)
- call_duration in seconds
Provide your answer as JSON with these keys.
```

### Extraction Parameters
| Name | Example | Description |
|------|---------|-------------|
| `reference_number` | `LD-1001` | The unique load ID the caller inquired about |
| `mc_number` | `382280` | The carrier's MC number |
| `booking_decision` | `yes` | Whether the carrier agreed to book |
| `decline_reason` | `rate too high` | Reason for declining (if applicable) |
| `call_duration` | `240` | Call duration in seconds |

---

## 6. Dashboard

The analytics dashboard is accessible at:

```
https://hr-inbound-sales.onrender.com/dashboard
```

No authentication required. Auto-refreshes every 30 seconds.

### Dashboard Features
- **KPI Cards**: Total Calls, Success Rate, Avg Revenue, Negotiation Savings
- **Call Outcome Distribution**: Donut chart
- **Carrier Sentiment**: Donut chart
- **Call Volume Over Time**: Bar chart
- **Negotiation Performance**: Loadboard Rate vs. Agreed Rate
- **Top Lanes**: Horizontal bar chart
- **Recent Calls Table**: Full history with badges

---

## 7. Testing the Flow

### Valid MC Numbers for Testing
| MC Number | Carrier | Eligible? |
|-----------|---------|-----------|
| `382280` | L & LOPEZ TRUCKING | ✅ Yes |
| `260209` | WERNER ENTERPRISES | ✅ Yes |
| `152047` | J.B. HUNT TRANSPORT | ✅ Yes |
| `143482` | SWIFT TRANSPORTATION | ✅ Yes |
| `999999999` | (Does not exist) | ❌ No |

### Sample Call Script
1. *"Hi, I'm looking for a load."*
2. *"My MC number is 382280."* → Agent verifies carrier
3. *"I've got a dry van, sitting in Dallas looking to run to Chicago."* → Agent finds LD-1001 ($2,850)
4. *"How about $2,500?"* → Agent counters (below 90% floor)
5. *"Okay, $2,600?"* → Agent accepts (above 90% floor)
