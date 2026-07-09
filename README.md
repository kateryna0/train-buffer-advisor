# TrainBuffer

[![CI](https://github.com/kateryna0/train-buffer-advisor/actions/workflows/ci.yml/badge.svg)](https://github.com/kateryna0/train-buffer-advisor/actions/workflows/ci.yml)

**Transparent deadline-based buffer advice for important train trips in Germany.**

**Live demo:** https://train-buffer-advisor.streamlit.app

> Runtime: Python 3.12 (pinned in `.python-version`); set the same version in the Streamlit Cloud app's Advanced settings so local, CI, and deploy match.

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
4. The base buffer is adjusted for trip type (airport, interview/exam, government/visa/medical, transfer), a live weather signal (with manual override fallback), a manual construction/disruption flag, and — if a train number is given — a live upstream delay check.
5. The buffer is subtracted from the deadline to get the latest safe planned arrival, which is compared against the planned arrival to flag the trip as safe or risky.
6. A customer-native (non-technical) recommendation is generated, along with reasons, warnings, and the confidence level.

Business logic is fully separated from the UI:

```text
app.py                     # Streamlit UI only (Trip advisor / Connection mode / Reliability board tabs)
src/models.py              # input/output models (incl. multi-leg TripLeg / MultiLegTripInput)
src/risk_engine.py         # risk, buffer, trip type, weather, construction calculations
src/recommendation.py      # customer-native advice text (incl. connection messaging)
src/data_loader.py         # station statistics loading
src/time_utils.py          # deadline/time calculations
src/logging_utils.py       # optional anonymous advice logging
src/ui_helpers.py          # pure presentation helpers (risk badge colors/icons)
src/weather_client.py      # live weather signal (Open-Meteo) with graceful fallback
src/live_delay_client.py   # live upstream delay check for a specific train
src/reliability_board.py   # worst-station reliability rankings
src/connection_engine.py   # v3 connection mode: per-leg delay, transfer time, connection risk
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

## Real historical data (offline ingestion)

The app loads real aggregated statistics from `data/station_stats.csv` when present, and automatically falls back to the hand-curated `data/sample_station_stats.csv` if it is missing. The committed `data/station_stats.csv` was generated offline from the [piebro/deutsche-bahn-data](https://huggingface.co/datasets/piebro/deutsche-bahn-data) Hugging Face dataset — the top 100 busiest stations from the October 2025 snapshot (see [docs/14-real-historical-data-source-decision.md](docs/14-real-historical-data-source-decision.md) for the source evaluation). To regenerate or refresh it:

The ingestion is a **batch/offline step** in `src/data_ingest.py` — it is not imported by the app, so there is no runtime dependency on the dataset or a parquet engine:

```python
from src.data_ingest import build_station_stats_csv

# Download a monthly parquet snapshot into data/raw/ first (kept out of git):
#   huggingface.co/datasets/piebro/deutsche-bahn-data/.../monthly_processed_data
build_station_stats_csv(
    "data/raw/data-2025-10.parquet",  # per-stop records
    "data/station_stats.csv",         # StationStats-shaped output
    station_col="station_name",
    delay_col="delay_in_min",
    cancelled_col="is_canceled",
    late_threshold_minutes=6,          # DB punctuality definition
    top_n=100,                        # busiest stations first
)
```

Reading the real parquet locally requires a parquet engine (e.g. `pip install pyarrow`); the test suite uses tiny CSV fixtures and needs neither. Raw `*.parquet` snapshots and `data/raw/` are git-ignored; only the small generated CSV is intended for commit.

**Data attribution:** historical data is derived from Deutsche Bahn timetable data via the piebro/deutsche-bahn-data project, licensed **CC BY 4.0** — attributed to Deutsche Bahn.

## Project status

**V1, v1.5, v2, v3, and the v2.1 production-readiness milestone are implemented and passing tests (151 tests).** See [docs/progress.md](docs/progress.md) for phase-by-phase delivery status. Completed:

- **v1 core:** domain models, risk engine, deadline logic, trip type modifiers, recommendation text, sample station data layer (5 stations), Streamlit UI, privacy-safe anonymous advice logging, manual weather/construction modifiers, and end-to-end backend tests. Deployed to Streamlit Community Cloud and tagged `v1.0`.
- **Better UI design (P1-4):** color-coded risk badge, grouped result card, "Advanced conditions" section, and a "How TrainBuffer works" sidebar.
- **Live weather API (P1-5):** automatic weather lookup via Open-Meteo with graceful fallback to a manual override when the source is unavailable.
- **v1.5 — live upstream delay check:** optional per-train live delay signal that increases the buffer when the train is already delayed, failing closed to v1 behavior when unavailable.
- **v2 — reliability board:** worst-station rankings (by late rate and cancellation rate) with a data-freshness indicator.
- **v3 — connection mode:** multi-leg trips with transfer-time modeling and a "will I make my transfer?" connection-risk assessment plus next-train fallback messaging.
- **v2.1 — production readiness:** CI (pytest + import smoke check) with a pinned Python version, cached/hardened live API calls, and **real aggregated Deutsche Bahn statistics for the top 100 stations** (with the sample dataset kept as an automatic fallback). Tagged `v2.1`.

## Limitations

- Ships with real aggregated Deutsche Bahn statistics for the ~100 busiest stations (one monthly snapshot); a smaller station or an older month is not covered, and unknown stations return "no data". The 5-station sample dataset remains as an automatic fallback.
- Weather is now looked up live (Open-Meteo) for a small set of known stations; outside that set, or when the source is down, it falls back to no adjustment / a manual override.
- The live upstream delay check depends on an unofficial public endpoint; when it is unavailable the app degrades to static-reliability behavior (fails closed, never blocks).
- Construction/disruption remains a manual yes/no/unknown flag — no low-complexity, stable free data source was adopted (see [docs/progress.md](docs/progress.md)).
- Connection mode uses a manual minimum-transfer-time table and static reliability data; it does not yet use live leg times.
- No user accounts, notifications, route optimization, or mobile/PWA build.

## Roadmap

Delivered (see Project status above): better UI design, live weather API, live upstream delay check (v1.5), reliability board (v2), connection mode (v3), and the v2.1 production-readiness milestone (CI, hardening, real historical data — P2-1 done).

Remaining:

- **Real construction/disruption data (P2-3, plan Phase 24):** deferred, to be revisited — kept as a manual flag until a stable, low-complexity, free source is confirmed feasible.
- **Mobile/PWA (P2-5):** out of scope; not planned.

See `docs/12-v2-technical-delivery-plan.md`, `trainbuffer_technical_delivery_plan.md`, and `docs/09-roadmap-definition-of-done.md` for the full backlog.

## AI-assisted development workflow

Claude Code was used as an AI-assisted development partner for implementation support, debugging, and test scaffolding. Product decisions, scope control, risk logic, and documentation were defined through a structured prompt-engineering workflow, delivered one small feature at a time with tests required before moving to the next feature. See `docs/10-prompt-engineering-workflow.md` and `docs/progress.md` for details.

This app does not use GenAI to predict train delays.
