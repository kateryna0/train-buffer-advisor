# 03 — User Questions and Jobs To Be Done

This document translates common user questions around Deutsche Bahn delays into product requirements. The goal is to avoid building a generic train-data app and instead build around real decisions users make.

## Core insight after feedback

Users do not primarily care about abstract buffer minutes. They care about a deadline:

> **I need to be there by a certain time. What train arrival time is safe enough?**

Therefore, TrainBuffer should be deadline-based.

## Main user question

> When do I absolutely need to arrive — and should I choose a train that arrives earlier?

## Question cluster A — before the trip

| User question | Underlying need | Product implication |
|---|---|---|
| “I need to be there by 10:00. Which train arrival time is safe?” | Deadline planning | Core v1 flow: deadline → latest safe planned arrival |
| “Should I take one train earlier?” | Reduce risk | Main action output |
| “How much buffer should I plan before a flight?” | Avoid high-cost lateness | Airport trip type with conservative buffer |
| “Can I trust this connection for an interview/exam?” | Avoid emotional/professional cost | Interview/exam trip type |
| “Is this enough time before a visa/medical appointment?” | Hard-to-reschedule event | Government/visa/medical trip type |
| “Is this station/route usually delayed?” | Historical reliability | Destination-station stats and confidence badge |

## Question cluster B — during the trip

| User question | Underlying need | Product implication |
|---|---|---|
| “My train is already delayed. What now?” | Live recovery | Out of scope for v1; v1.5 live check |
| “Will I still catch the next train?” | Connection reliability | v3 connection mode |
| “Can I take another train?” | Passenger rights / ticket rules | Later info link only, not v1 core |
| “Is there construction on this route?” | Disruption context | Optional construction flag if feasible; otherwise v1.5/v2 |

## Question cluster C — after disruption

| User question | Underlying need | Product implication |
|---|---|---|
| “Can I get compensation?” | Passenger rights | Not core; add official DB link later |
| “Can I use a taxi/hotel?” | Emergency support | Not core for v1 |
| “How do I file a passenger-rights claim?” | Post-trip process | Not core for v1 |

## Jobs To Be Done

### JTBD 1 — Deadline-safe arrival

**When** I have a fixed appointment time,  
**I want** to know the latest safe planned train arrival time,  
**so that** I can choose a connection with enough buffer.

**Priority:** v1 core

### JTBD 2 — Airport trip buffer

**When** I travel to the airport by train,  
**I want** a conservative buffer recommendation,  
**so that** I do not miss my flight.

**Priority:** v1 core as Airport trip type

### JTBD 3 — Interview/exam/appointment buffer

**When** I travel to an interview, exam, visa appointment, government appointment, or medical appointment,  
**I want** a recommendation that reflects the high cost of being late,  
**so that** I can plan conservatively.

**Priority:** v1 core

### JTBD 4 — Normal trip

**When** my trip is flexible,  
**I want** a less conservative recommendation,  
**so that** I do not over-buffer unnecessarily.

**Priority:** v1 core

### JTBD 5 — Transfer trip

**When** I need to catch another train,  
**I want** to know if the transfer is safe,  
**so that** I do not get stranded.

**Priority:** out of scope for v1. v1 should warn: “Transfer reliability is not supported yet.”

## Product decision: primary v1 question

The v1 product should be designed around one screen and one question:

```text
When do you absolutely need to arrive?
```

Then calculate:

```text
latest_safe_planned_arrival = arrival_deadline - recommended_buffer
```

## Required v1 inputs from JTBD

| Input | Why needed |
|---|---|
| Origin station | User context and future route logic |
| Destination station | Anchor for historical reliability |
| Travel date | Weather/disruption context |
| Arrival deadline | Core of the deadline-based flow |
| Planned arrival time | Allows the app to judge whether the selected connection is safe |
| Trip type | Converts risk into the right level of conservatism |
| Optional train number | Future v1.5 live lookup |

## Required v1 outputs from JTBD

| Output | Why needed |
|---|---|
| Latest safe planned arrival time | Most actionable output |
| Recommended buffer | Explains how conservative the recommendation is |
| Action recommendation | Tells user what to do |
| Risk level | Communicates severity |
| Confidence | Prevents false precision |
| Explanation | Differentiates from black-box scores |
| Limitation note | Builds trust |

## Example customer-native outputs

### Normal trip

```text
Your planned arrival looks acceptable for a normal trip.
Recommended buffer: 15 minutes.
Latest safe planned arrival for your deadline: 09:45.
```

### Interview/exam

```text
Your planned arrival is risky for an interview/exam.
Aim to arrive at least 45 minutes before your deadline.
If possible, choose a train that arrives one connection earlier than planned.
```

### Airport

```text
This is a critical trip type. TrainBuffer only estimates rail buffer, not airport security or baggage time.
Plan to arrive at the airport station at least 60 minutes before your own airport-processing buffer begins.
```

### Transfer

```text
Transfer reliability is not supported in v1.
Use this result only as a general risk signal and check DB Navigator live before departure.
```
