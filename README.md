# TrainBuffer

**Transparent deadline-based buffer advice for important train trips in Germany.**

**Live demo:** https://train-buffer-advisor.streamlit.app

## What TrainBuffer is

TrainBuffer is a Python/Streamlit web app that helps travelers decide **how early they should plan to arrive** for an important train trip in Germany. Instead of trying to predict the exact delay of a single Deutsche Bahn train, it gives a transparent buffer recommendation based on historical station reliability, trip type, deadline, confidence level, and optional manual weather/construction signals.

## Problem statement

Travelers with an important deadline — a flight, an interview, a visa appointment — have no simple way to translate "how reliable is this station historically?" into "how much earlier should I plan to arrive?" Existing tools (DB Navigator, Bahn-Vorhersage, Zugfinder) cover journey planning and live tracking, but not this pre-trip planning decision.

The core user question:

> **I need to arrive by a specific time. Is my planned train arrival safe enough, or should I take an earlier train?**

## Why a buffer advisor, not a delay predictor

TrainBuffer does not claim to predict the exact delay of one train. It combines historical station reliability, trip type, and confidence level into an explainable buffer recommendation, then compares that against the user's deadline:

```text
latest_safe_planned_arrival = arrival_deadline - recommended_buffer
```

Example:

```text
Arrival deadline: 10:00
Recommended buffer: 35 minutes
Latest safe planned arrival: 09:25
```

If the planned arrival is later than 09:25, the app flags the trip as risky.

## How it works

1. User enters origin, destination, planned arrival time, arrival deadline, and trip type.
2. TrainBuffer looks up historical reliability stats for the destination station (late rate, cancellation rate, sample size).
3. It calculates a confidence level from the sample size, a historical risk level from the late/cancellation rates, and a base buffer from that risk level.
4. The base buffer is adjusted for trip type (airport, interview/exam, government/visa/medical, transfer) and, optionally, manual weather and construction/disruption flags.
5. The buffer is subtracted from the deadline to get the latest safe planned arrival, which is compared against the planned arrival to flag the trip as safe or risky.
6. A customer-native (non-technical) recommendation is generated, along with reasons, warnings, and the confidence level.

Business logic is fully separated from the UI:

```text
app.py                 # Streamlit UI only
src/models.py          # input/output models
src/risk_engine.py     # risk, buffer, trip type, weather, construction calculations
src/recommendation.py  # customer-native advice text
src/data_loader.py     # station statistics loading
src/time_utils.py      # deadline/time calculations
src/logging_utils.py   # optional anonymous advice logging
```

## Tech stack

- Python
- Streamlit (UI)
- pandas (station data loading)
- pytest (testing)

## How to run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## How to run tests

```bash
source .venv/bin/activate
pytest
```

## Project status

**V1 core is implemented and passing tests.** See [docs/progress.md](docs/progress.md) for phase-by-phase delivery status. Completed:

- Domain models, risk engine, deadline logic, trip type modifiers, recommendation text
- Sample station data layer (5 stations) and Streamlit UI
- Privacy-safe anonymous advice logging
- Optional manual weather and construction/disruption modifiers
- End-to-end backend test coverage across normal, airport, interview/exam, unknown-station, and transfer scenarios

Remaining: deployment to Streamlit Community Cloud and v1 release tagging.

## Limitations

- Uses a small hand-curated sample dataset (5 stations), not real Deutsche Bahn historical statistics.
- No live DB delay API — recommendations are based on static historical reliability, not real-time data.
- Weather and construction/disruption signals are manual yes/no/unknown flags, not live API data.
- Transfer trips are not fully supported — treated as a rough warning only.
- No user accounts, notifications, or route optimization in v1.

## Roadmap

- **P1 (near-term):** better UI design, real weather API (replacing manual flags)
- **P2 (later):** real DB historical data aggregation, live DB delay API, real construction/disruption data, connection-mode support, mobile/PWA

See `trainbuffer_technical_delivery_plan.md` and `docs/09-roadmap-definition-of-done.md` for the full backlog.

## AI-assisted development workflow

Claude Code was used as an AI-assisted development partner for implementation support, debugging, and test scaffolding. Product decisions, scope control, risk logic, and documentation were defined through a structured prompt-engineering workflow, delivered one small feature at a time with tests required before moving to the next feature. See `docs/10-prompt-engineering-workflow.md` and `docs/progress.md` for details.

This app does not use GenAI to predict train delays.
