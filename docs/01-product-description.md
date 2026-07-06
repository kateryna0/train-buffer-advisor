# 01 — Product Description

## Product name

**TrainBuffer**

Previous working name: Bahn Buffer Advisor.

## One-sentence description

**TrainBuffer helps travelers in Germany decide how early they should plan to arrive for an important train trip, using transparent historical reliability, weather-based reasoning, trip type, and a deadline-based buffer calculation.**

## Tagline

> Transparent deadline-based buffer advice for German train trips.

## Problem

German train travelers often do not know how much extra time they should plan before an important arrival deadline. DB Navigator shows real-time information and alternative connections, but it mostly helps once the trip is planned or a disruption is already visible.

Before the trip, users still ask themselves:

- I need to be there by 10:00 — which train arrival time is safe?
- Should I take one train earlier?
- How much buffer do I need before a flight, interview, exam, visa appointment, or medical appointment?
- Can I trust this connection if being late would be expensive or stressful?

Existing tools usually show timetable information, live delays, or a score. TrainBuffer focuses on turning risk into a practical planning decision.

## Product idea

TrainBuffer is a **buffer advisor, not a delay predictor**.

It does not claim to know the exact delay of one specific train. Instead, it gives a conservative and explainable recommendation:

- how much buffer to plan;
- what the latest safe planned arrival time is;
- whether the currently planned arrival is safe enough;
- whether the user should choose a train that arrives one connection earlier;
- why the recommendation was made;
- how much confidence the app has in the data.

## Core user question

> **When do I absolutely need to arrive — and what is the latest safe train arrival time?**

This is stronger than a generic “risk score” because users care about their deadline, not abstract probability.

## Example result

```text
Trip type: Interview/exam
Deadline: 10:00
Recommended buffer: 45 minutes
Latest safe planned arrival: 09:15

Recommendation:
Your planned arrival is risky for an important trip.
Aim to arrive at least 45 minutes before your deadline.
If possible, choose a train that arrives one connection earlier than planned.

Why:
- 27% of historical arrivals at the destination station were late.
- Data confidence is medium, based on 86 performed arrivals.
- Strong wind is forecast near the destination.
- v1 does not include live disruption status, so check DB Navigator before departure.
```

## Target users

| Persona | Situation | Pain | Product value |
|---|---|---|---|
| Airport traveler | Train to airport | Missing a flight is expensive; security and baggage need extra time | Conservative buffer and “arrive before X” advice |
| Interview/exam traveler | Must arrive calm and on time | High emotional cost of lateness | Stronger recommendation to take one earlier train |
| Government/visa/medical appointment traveler | Appointment is hard to reschedule | Rescheduling may be slow or costly | Conservative latest safe arrival time |
| Transfer traveler | Needs to catch another train | Transfer prediction is complex | v1 warns that transfer mode is out of scope |
| Normal traveler | Flexible trip | Delay is annoying but manageable | Less conservative buffer |

## Trip types

| Trip type | Why it matters | v1 treatment |
|---|---|---|
| Normal trip | Lower cost of lateness | Standard buffer |
| Airport | Needs conservative buffer; security/baggage are not included | Critical conservatism |
| Interview/exam | Emotional cost; lateness can damage outcome | Important/Critical conservatism |
| Government/visa/medical appointment | Hard to reschedule | Critical conservatism |
| Transfer to another train | Complex because actual connection reliability matters | Warning: transfer mode is not supported in v1 |

## Core outputs

- Risk level: Low / Medium / High / Not enough data.
- Recommended buffer in minutes.
- Latest safe planned arrival time.
- Customer-native recommendation.
- Confidence level.
- Explanation with reasons and sources.
- Weather risk flags.
- Optional construction/disruption flag if feasible.
- Clear v1 limitations.

## What TrainBuffer is not

TrainBuffer is not:

- a DB Navigator replacement;
- a ticket booking tool;
- a live train tracker;
- a legal/passenger-rights assistant;
- a black-box ML delay predictor;
- a full routing engine.

## Product positioning

> TrainBuffer gives a transparent, deadline-based buffer recommendation for important train trips in Germany, based on historical reliability, weather signals, trip type, and confidence in the available data.

## Why this is portfolio-relevant

This project demonstrates:

- product discovery and market positioning;
- competitor analysis;
- requirements engineering;
- public-data/API reasoning;
- explainable rule design;
- risk and compliance thinking;
- Python/Streamlit implementation potential;
- AI-assisted development using Claude Code and prompt engineering.

## Main limitation

The strongest version of this product eventually needs live disruption and connection data. v1 is intentionally smaller: it proves the transparent buffer logic and user experience before adding live complexity.
