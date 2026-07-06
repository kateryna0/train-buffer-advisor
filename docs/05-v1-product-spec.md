# 05 — v1 Product Specification

## Version

v1 pre-build specification, updated after external feedback, 2026-07-06.

## Product goal

Build a small Streamlit web app that gives an explainable, deadline-based buffer recommendation for important train trips in Germany.

## Primary user question

> I need to be at my destination by a specific time. What is the latest safe planned train arrival time, and should I take one earlier?

## Scope statement

v1 uses historical destination-station reliability, weather risk signals, trip type, and a deadline-based buffer calculation to recommend a safe planned arrival time and action.

v1 does **not** include a full routing engine, live train status, true transfer prediction, user accounts, or notifications.

Construction/disruption data is treated as **P1 optional for v1**: include only if a low-complexity, stable data source is available. If not, clearly state that live construction/disruption status is not included and move it to v1.5/v2.

## In scope

| Feature | Description | Priority |
|---|---|---|
| Trip input form | User enters origin, destination, date, deadline, planned arrival, trip type | P0 |
| Destination reliability lookup | App looks up precomputed reliability for destination station | P0 |
| Weather risk check | App checks weather around travel date/time and route endpoints | P0 |
| Trip type modifier | Normal / Airport / Interview-exam / Government-visa-medical / Transfer | P0 |
| Deadline calculation | App computes latest safe planned arrival time | P0 |
| Risk level | Low / Medium / High / Not enough data | P0 |
| Buffer minutes | Recommended buffer before the deadline | P0 |
| Customer-native recommendation | Plain-language action, not only a number | P0 |
| Confidence badge | Based on data sample size | P0 |
| Explanation card | Plain-language reasons and data sources | P0 |
| No-data state | Honest message if station data is too thin | P0 |
| Limitations note | v1 does not include live status; check DB Navigator | P0 |
| Construction/disruption flag | Simple warning if feasible without heavy integration | P1 optional |
| Recommendation logging | Save input/output for later validation | P1 |

## Out of scope

| Feature | Reason |
|---|---|
| Full DB routing engine | DB Navigator already does route planning |
| Live train delay API | v1.5 |
| True connection / transfer prediction | v3 |
| Heavy construction overlay | v1.5/v2 unless simple P1 source exists |
| User accounts | Not needed for v1 |
| Push notifications | Requires saved routes and background jobs |
| ML prediction | Not required; would overcomplicate v1 |
| Passenger rights/legal assistant | Not core to buffer decision |

## User inputs

| Field | Type | Required | Notes |
|---|---|---:|---|
| Origin station | text/select | yes | Used for display and future route logic |
| Destination station | text/select | yes | Main anchor for historical reliability |
| Travel date | date | yes | Used for weather and optional construction context |
| Arrival deadline | datetime/time | yes | When user absolutely needs to arrive |
| Planned arrival time | datetime/time | optional but recommended | If user already selected a connection in DB Navigator |
| Trip type | enum | yes | Normal / Airport / Interview-exam / Government-visa-medical / Transfer |
| Train number | text | no | Not used in v1 rule, saved for future v1.5 |

## Trip type options

| Trip type | Meaning | Product behavior |
|---|---|---|
| Normal trip | Being late is annoying but manageable | Standard buffer |
| Airport | Missing flight is expensive; security/baggage not included | Critical rail buffer + airport disclaimer |
| Interview/exam | High emotional or professional cost | Conservative buffer |
| Government/visa/medical appointment | Hard to reschedule | Conservative-to-critical buffer |
| Transfer to another train | User needs to catch another train | Warning: transfer reliability is out of scope for v1 |

## User outputs

| Output | Example |
|---|---|
| Risk level | Medium |
| Numeric risk | 27% late arrivals historically |
| Recommended buffer | 45 minutes |
| Latest safe planned arrival | 09:15 for a 10:00 deadline |
| Planned arrival assessment | Your planned arrival at 09:40 is risky |
| Recommended action | Choose a train that arrives one connection earlier |
| Confidence | Medium confidence, based on 86 observations |
| Reasons | Historical delay rate, weather flag, sample size, trip type |
| Data sources | Historical DB data, weather API |
| Limitation | Live disruptions are not included in v1 |

## Primary UI layout

### Screen 1 — Input

```text
Plan your train buffer

From: [Hamburg Hbf]
To: [Berlin Hbf]
Date: [2026-07-15]
When do you absolutely need to arrive? [10:00]
Planned train arrival time, if known: [09:40]
Trip type: [Normal | Airport | Interview/exam | Government/visa/medical | Transfer]
Optional train: [ICE 597]

[Check buffer]
```

### Screen 2 — Result card

```text
Risk: Medium
Recommended rail buffer: 45 min
Latest safe planned arrival: 09:15

Recommendation:
Your planned arrival at 09:40 is risky for an interview/exam.
Aim to arrive at least 45 minutes before your deadline.
If possible, choose a train that arrives one connection earlier than planned.

Why:
- 27% of historical arrivals at Berlin Hbf were late.
- Strong wind is forecast near the destination.
- Interview/exam trips use a more conservative buffer.
- Data confidence is medium: 86 historical arrivals.

Limitations:
- v1 does not include live disruption status.
- Always check DB Navigator before departure.
```

## Functional requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-001 | User can enter origin, destination, travel date, deadline, planned arrival, trip type | P0 |
| FR-002 | App validates required fields | P0 |
| FR-003 | App matches destination station to stats table | P0 |
| FR-004 | App computes historical late rate | P0 |
| FR-005 | App computes confidence from sample size | P0 |
| FR-006 | App checks weather risk flags | P0 |
| FR-007 | App maps risk to buffer minutes | P0 |
| FR-008 | App modifies conservatism by trip type | P0 |
| FR-009 | App computes latest safe planned arrival time | P0 |
| FR-010 | App compares planned arrival time against latest safe planned arrival | P0 |
| FR-011 | App generates customer-native recommendation text | P0 |
| FR-012 | App shows no-data state if sample too small | P0 |
| FR-013 | App shows limitations and source notes | P0 |
| FR-014 | App logs recommendation input/output | P1 |
| FR-015 | App includes simple construction/disruption flag if feasible | P1 optional |
| FR-016 | App allows optional train number | P2 |

## Non-functional requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-001 | Fast response | Result in <3 seconds for normal query |
| NFR-002 | Simple deployment | Streamlit Community Cloud |
| NFR-003 | Low cost | Free hosting and free APIs for demo usage |
| NFR-004 | Testability | Risk engine tested without UI |
| NFR-005 | Explainability | Every output must include reasons |
| NFR-006 | Privacy-light | No login, no user profiles, no sensitive storage |
| NFR-007 | Maintainability | Business logic separated from Streamlit |
| NFR-008 | Scope control | Construction/disruption is optional, not a v1 blocker |

## Acceptance criteria

A v1 query is successful if:

1. the user enters valid trip data;
2. the app finds destination stats or shows no-data state;
3. the app computes risk, buffer, confidence, reasons, and latest safe planned arrival;
4. the app compares the planned arrival time to the safe arrival threshold if provided;
5. the app shows a readable recommendation card;
6. the app states the v1 limitations;
7. the app does not pretend to know live disruptions.

## Example recommendations

### Low risk, normal trip

```text
Risk: Low
Recommended rail buffer: 10 min
Latest safe planned arrival: 09:50
Action: Your planned arrival looks acceptable for a normal trip.
```

### Medium risk, interview/exam

```text
Risk: Medium
Recommended rail buffer: 45 min
Latest safe planned arrival: 09:15
Action: Your planned arrival is risky for an interview/exam. Choose an earlier arrival if possible.
```

### High risk, airport

```text
Risk: High
Recommended rail buffer: 60 min
Latest safe planned arrival: 09:00
Action: Strongly choose a train that arrives one connection earlier.
Note: airport security and baggage time are not included.
```

### Transfer trip

```text
Transfer reliability is not supported in v1.
Use this result only as a general risk signal and check DB Navigator live before departure.
```

### No data

```text
Not enough historical data for this station.
We cannot give a reliable buffer estimate. Check DB Navigator live and plan conservatively.
```

## Definition of Done for v1

v1 is done when:

- the app runs locally;
- the risk engine has tests;
- sample/precomputed station stats are included;
- deadline calculation works;
- planned arrival assessment works;
- trip type modifier works;
- weather modifier works or is mocked if API unavailable;
- construction/disruption is either implemented as a simple flag or explicitly excluded with a limitation note;
- Streamlit result card works;
- README explains concept and limitations;
- project is pushed to GitHub;
- demo is deployed or has clear run instructions.
