# 09 — Roadmap and Definition of Done

## Product principle

Ship a focused v1 before adding intelligence.

The main risk is not that the idea is too small. The main risk is that it becomes too large and never ships.

## Version roadmap

| Version | Goal | Main value | Status |
|---|---|---|---|
| v0 | Product/spec documentation | Clarify what to build | Current |
| v1 | Historical reliability + weather + deadline-based buffer advice | Demoable decision-support app | Next |
| v1.5 | Live upstream delay + simple construction/disruption check | Biggest accuracy improvement | Later |
| v2 | Full construction/disruption overlay and analytics board | Deeper reliability context | Later |
| v3 | Connection mode | “Will I make my transfer?” | Later |

## v0 — Documentation pack

### Goal

Create enough product and technical documentation to guide implementation with Claude Code.

### Done when

- product description exists;
- market/competitor research exists;
- user questions/JTBD are defined;
- four-role audit exists;
- v1 spec is written;
- data sources are assessed;
- risk rule is defined;
- legal/privacy notes exist;
- roadmap and DoD are defined;
- prompt-engineering workflow is defined.

## v1 — Historical + weather + deadline buffer advisor

### Goal

Build a working Streamlit demo that answers:

> I need to arrive by a specific time. What is the latest safe planned arrival, and should I take one earlier?

### Must-have features

| Feature | Required |
|---|---:|
| Input form | Yes |
| Destination station reliability lookup | Yes |
| Risk level | Yes |
| Buffer recommendation | Yes |
| Arrival deadline input | Yes |
| Latest safe planned arrival time | Yes |
| Planned arrival assessment | Yes |
| Trip type modifier | Yes |
| Weather modifier | Yes |
| Confidence badge | Yes |
| Explanation card | Yes |
| No-data state | Yes |
| App disclaimer | Yes |
| README | Yes |
| Unit tests for risk engine | Yes |

### Not in v1

- live train status;
- transfer prediction;
- heavy construction overlay;
- accounts;
- favorites;
- notifications;
- mobile app;
- ML model;
- passenger rights assistant.

Simple construction/disruption data is **P1 optional** in v1 if it is low-complexity and does not block shipping.

### v1 Definition of Done

v1 is done when:

1. app runs locally with `streamlit run app.py`;
2. risk engine is separate from UI;
3. core engine has unit tests;
4. sample/precomputed station stats are included;
5. weather data works or has a graceful fallback;
6. UI shows risk, buffer, latest safe planned arrival, confidence, reasons, limitations;
7. README explains how to run the app;
8. GitHub repo is public or ready to share;
9. deployed demo exists or deployment instructions are complete;
10. project has a short CV/interview description.

## v1.5 — Live upstream check

### Goal

Add a live signal for a specific train if the user provides a train number.

### Why this matters

Historical reliability is useful for planning, but the biggest practical accuracy gain comes from checking whether the train is already delayed at earlier stops.

### Candidate features

- optional train number lookup;
- current delay at previous stops;
- live risk adjustment;
- “already delayed” warning;
- fallback if live API fails.

### Risks

- API fragility;
- rate limits;
- terms of use;
- matching train numbers correctly;
- live data disappearing after arrival.

## v2 — Disruption and reliability board

### Goal

Add broader context:

- full construction/disruption overlays;
- worst stations/routes/times;
- reliability dashboard;
- data freshness indicators.

### Why not v1

This adds data complexity and can distract from the core app.

## v3 — Connection mode

### Goal

Answer:

> Will I make my transfer?

### Requirements

This requires:

- multi-leg journey parsing;
- arrival delay prediction for first leg;
- transfer time and station layout assumptions;
- downstream connection risk;
- live data;
- missed-connection handling.

This is valuable but too complex for v1.

## Project management guardrails

### Rule 1 — No new feature before v1 runs

If the app cannot run locally, do not add new features.

### Rule 2 — No UI before risk engine tests

The result card should be driven by tested logic, not hardcoded UI text.

### Rule 3 — No ML before baseline works

A simple transparent rule is better than an unfinished ML model.

### Rule 4 — No live API dependency in v1

v1 should still work if all live APIs are unavailable.

### Rule 5 — Every feature must improve the core decision

If it does not help answer “what is my latest safe planned arrival and should I take one earlier?”, it is not v1.

## Suggested implementation milestones

| Milestone | Deliverable |
|---|---|
| M1 | Repository structure and docs committed |
| M2 | Risk rule with deadline calculation implemented as pure function |
| M3 | Unit tests passing |
| M4 | Sample station stats loaded |
| M5 | Weather modifier integrated |
| M6 | Streamlit input/result UI working |
| M7 | README polished |
| M8 | Demo deployed |
| M9 | CV bullet and interview story written |

## Interview story

This project should be explainable as:

> I started with product discovery and market research, identified that existing tools solve live journey management but not transparent deadline-based pre-trip buffer decisions, wrote a v1 specification, designed a testable rule-based risk engine, and used Claude Code as an AI-assisted development partner to implement and iterate toward a deployed Streamlit demo.
