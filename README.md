# TrainBuffer

**Transparent deadline-based buffer advice for important train trips in Germany.**

TrainBuffer is a portfolio product concept and technical specification for a small Python/Streamlit app. It helps travelers decide **how early they should plan to arrive** for an important train trip in Germany.

The core product question is now deadline-based:

> **I need to be at my destination by a specific time. What is the latest safe planned train arrival time — and should I take one earlier?**

The product is intentionally positioned as a **buffer advisor, not a delay predictor**. It does not claim to predict the exact delay of one train. Instead, it combines historical reliability, weather risk signals, trip type, confidence level, and clear decision rules to produce an explainable recommendation.

Working name before feedback: **Bahn Buffer Advisor**. Final product name: **TrainBuffer**.

## Current stage

This is the **concept and specification stage**. There is no production app yet. The documentation is designed to become the blueprint for implementation with Claude Code and/or other AI coding tools.

## Core user flow

The user enters:

- origin station;
- destination station;
- date;
- **arrival deadline** — when they absolutely need to be at the destination;
- planned train arrival time, if they already selected a connection in DB Navigator;
- trip type: Normal, Airport, Interview/exam, Government/visa/medical appointment, Transfer to another train;
- optional train number.

TrainBuffer returns:

- risk level: Low / Medium / High;
- recommended buffer in minutes;
- **latest safe planned arrival time**: `deadline - recommended buffer`;
- action recommendation: planned arrival is fine / choose an earlier arrival / take one connection earlier;
- confidence level based on historical sample size;
- plain-language explanation;
- weather risk flags;
- optional construction/disruption warning if a low-complexity data source is available;
- honest “not enough data” when the data is too thin.

## Target user

The first version is aimed at travelers who have a high cost of arriving late:

- airport trips;
- job interviews or exams;
- visa, government, or medical appointments;
- long-distance trips with strict arrival times;
- transfers where missing the next train would be expensive or stressful.

Daily commuters are **not** the primary v1 persona because a daily-use product would require live disruption monitoring, saved routes, and notifications.

## Differentiation

Existing tools such as DB Navigator, Bahn-Vorhersage, Zugfinder, and Bahn Experte already cover journey planning, real-time information, connection scoring, and train tracking. TrainBuffer should not try to replace them.

The niche is:

> **A deadline-based, explainable pre-trip decision memo for important train journeys.**

The product differentiator is not “more data”. The differentiator is a transparent recommendation that translates risk into a concrete planning decision.

Example output:

```text
Your planned arrival is risky for a critical trip.
Aim to arrive at least 45 minutes before your deadline.
Your latest safe planned arrival time is 09:15.
If possible, choose a train that arrives one connection earlier than planned.
```

## Documentation map

| File | Purpose |
|---|---|
| `docs/01-product-description.md` | Product concept, problem, target user, value proposition |
| `docs/02-market-and-competitor-research.md` | Market context, competitors, positioning gap |
| `docs/03-user-questions-and-jobs-to-be-done.md` | Common user questions and JTBD translation |
| `docs/04-four-role-product-audit.md` | Audit from Staff Engineer, Engineering Manager, Product Owner, Business Analyst |
| `docs/05-v1-product-spec.md` | Concrete v1 scope, inputs, outputs, requirements |
| `docs/06-data-sources-and-feasibility.md` | Data sources, access, licensing, risks |
| `docs/07-risk-rule-spec.md` | Transparent rule-based scoring and buffer logic |
| `docs/08-legal-privacy-compliance.md` | GDPR, attribution, licensing, API terms, disclaimers |
| `docs/09-roadmap-definition-of-done.md` | Version plan, scope control, DoD |
| `docs/10-prompt-engineering-workflow.md` | How Claude Code / GenAI-assisted development will be documented |
| `docs/11-feedback-and-decisions.md` | External feedback, decisions, and scope changes |

## Portfolio positioning

Until a working demo exists, this project should be described as:

> Designed TrainBuffer, a product concept and technical specification for an AI-assisted decision-support app for German rail travel, focused on deadline-based buffer recommendations using historical delay data, weather signals, and explainable rule-based logic.

After v1 is implemented and deployed, the stronger CV line becomes:

> Built and deployed TrainBuffer, an AI-assisted Python/Streamlit decision-support app for German rail travel, using public rail-delay data, weather APIs, transparent rule-based risk scoring, and prompt-engineered development workflows with Claude Code.

## Next implementation step

Do **not** start with Streamlit UI. Start with the core decision engine:

1. implement `calculate_buffer()` as a pure Python function;
2. include deadline logic: `latest_safe_planned_arrival = deadline - recommended_buffer`;
3. write unit tests for risk bands, trip types, confidence levels, cancellation handling, weather modifiers, no-data cases, and deadline outputs;
4. only then connect the engine to a Streamlit interface.
