# TrainBuffer — Delivery Progress

Tracks phase completion per `trainbuffer_technical_delivery_plan.md`.

| Phase | Description | Status |
|---|---|---|
| 1 | Project setup | Done |
| 2 | Domain models | Done |
| 3 | Core risk engine | Done |
| 4 | Deadline-based flow | Done |
| 5 | Trip type conservatism | Done |
| 6 | Customer-native recommendation text | Done |
| 7 | Sample data layer | Done |
| 8 | Streamlit UI skeleton | Done |
| 9 | Advice logging | Done |
| 10 | Weather signal (P1) | Done |
| 11 | Construction/disruption signal (P1) | Done |
| 12 | End-to-end backend tests | Done |
| 13 | Documentation update | Done |
| 14 | Deployment | Done |
| 15 | V1 release | Done |
| 16 | Better UI design (P1-4) | Done |
| 17 | Real weather API (P1-5) | Done |
| 18 | Live upstream delay check (v1.5) | Done |
| 19 | Reliability board (v2) | Done |
| 20a | Multi-leg trip input model (v3) | Done |
| 20b | First-leg arrival delay estimation (v3) | Done |
| 20c | Transfer time modeling (v3) | Done |
| 20d | Downstream connection risk calculation (v3) | Done |
| 20e | Missed-connection / next-train messaging (v3) | Done |
| 20f | Multi-leg UI + connection-risk result card (v3) | Done |
| 21 | CI + Python version pin (v2.1) | Done |
| 22 | Cache + harden live API calls (v2.1) | Done |
| 23a | Real historical data source decision (research) | Done |
| 23b | Offline data ingestion pipeline | Done |
| 23c | Wire real data into app with fallback | Done |

## Log

- Phase 1: git repo initialized, full scaffold created (`app.py`, `src/`, `tests/`, `data/`, `docs/`), import test passing, committed.
- Phase 2: `TripInput`, `StationStats`, `BufferRecommendation` implemented in `src/models.py` with validation; 6 tests added; committed.
- Phase 3: `calculate_confidence`, `calculate_historical_risk`, `calculate_base_buffer`, `calculate_buffer` implemented in `src/risk_engine.py`; tests added; committed.
- Phase 4: `calculate_latest_safe_arrival`, `is_planned_arrival_safe` implemented in `src/time_utils.py` (incl. midnight wraparound); tests added; committed.
- Phase 5: `apply_trip_type_modifier` added to `src/risk_engine.py` (airport/interview_exam/government_visa_medical/transfer modifiers + warnings), wired into `calculate_buffer`; tests added; committed.
- Phase 6: `build_recommendation_text` implemented in `src/recommendation.py` (risky/acceptable/no-data/airport/transfer wording); tests added; committed.
- Phase 7: `data/sample_station_stats.csv` populated with 5 sample stations; `load_station_stats`/`get_station_stats` implemented in `src/data_loader.py`; tests added; committed.
- Phase 8: Streamlit UI built in `app.py` (thin wrapper over `src/*`); manually verified locally (known station, unknown station no-data, airport modifier + warning, deadline calc, transfer warning); committed.
- Phase 9: `log_advice` implemented in `src/logging_utils.py` (no personal fields), wired into `app.py` with privacy note; tests added; committed.
- Phase 10: `apply_weather_modifier` added to `src/risk_engine.py` (strong wind/heat/snow-ice, capped at +15 min), wired into `calculate_buffer` and `app.py` as optional checkboxes; tests added; committed.
- Phase 11: `apply_construction_modifier` added to `src/risk_engine.py` (manual yes/no/unknown flag, +10 min for yes, limitation warning for unknown), wired into `calculate_buffer` and `app.py`; tests added; committed. Option B (real construction data) deferred to v1.5/v2 per plan.
- Phase 12: `tests/test_end_to_end_calculation.py` added covering the 5 scenarios (normal, airport, interview/exam, unknown station, transfer) through the full pipeline (data_loader → risk_engine → time_utils → recommendation); committed.
- Phase 13: README.md rewritten to reflect implemented v1 (what/why/how it works, tech stack, setup/test instructions verified to work, project status, limitations, roadmap, AI-assisted workflow note); committed.
- Phase 14: Repo pushed to github.com/kateryna0/train-buffer-advisor; deployed to Streamlit Community Cloud at https://train-buffer-advisor.streamlit.app (public); live link added to README; committed.
- Phase 15: All 64 tests passing; v1.0 tag created and pushed.

- Phase 16: Streamlit UI redesign (P1-4, presentation only) — color-coded risk badge (green/amber/red/grey), two-column result card with icons, weather + construction grouped under an "Advanced conditions" expander, and a "How TrainBuffer works" sidebar explainer. Badge color/emoji mapping extracted to a pure `src/ui_helpers.py:risk_badge` (keeps `app.py` thin); 6 tests added. No business-logic changes; 70/70 tests passing.

- Phase 17: `src/weather_client.py` added — live weather via Open-Meteo (stdlib `urllib`, no new dependency), with explicit testable thresholds (wind > 50 km/h, temp > 30 °C, snowfall > 0 or WMO snow code). `fetch_weather_signal` maps a reading to strong_wind/heat/snow_ice flags; `get_weather_flags_with_fallback` degrades to all-False + warning on any failure so behavior matches v1 when the API is down. Network call isolated in `_fetch_current_weather` and mocked in tests (8 tests, no real network). `apply_weather_modifier` unchanged — only the flag source changed. `app.py` now looks up weather automatically for the destination station with a "Weather source: live/unavailable" caption and a collapsed manual-override group. 78/78 tests passing.

- Phase 18: `src/live_delay_client.py` added — optional live upstream delay check for a specific train (v1.5). `validate_train_number` guards format before any network call; `fetch_live_delay` returns `{currently_delayed, delay_minutes}` or `None`, failing closed (invalid format, timeout, not found, malformed data all → `None`, never raises); `apply_live_delay_modifier` increases the buffer and adds a warning when delayed, and is a strict no-op when live data is absent, not delayed, or the recommendation is no_data. Network call isolated in `_request_train_status` (db.transport.rest, 5s timeout) and mocked in tests (10 tests, no real network). `app.py` adds an optional "Train number" input and a "Live status: delayed by X min / on time / unavailable" caption; app degrades exactly to v1 when the field is blank or the API is down. 88/88 tests passing.

- Phase 19: `src/reliability_board.py` added — `compute_reliability_rankings(stats_by_station, top_n=3)` returns worst-N stations by `late_rate` and by `cancellation_rate` as a pure, tested function (ordering highest-rate-first, ties broken deterministically by station name, empty input → empty rankings). `app.py` split into two tabs ("Trip advisor" / "Reliability board"); the board renders the rankings and a data-freshness indicator (mtime of `data/sample_station_stats.csv`). 4 tests added; 92/92 passing.
  - **Construction/disruption data-source decision (required by plan):** the P1 manual per-trip construction flag (`no`/`yes`/`unknown`) is **kept**. No low-complexity, stable, free construction/disruption source was confirmed feasible for v2 (DB disruption feeds require auth/terms review and route-matching complexity out of scope here, and must not become a hard dependency per guardrail rule 4). Documented and surfaced in the reliability board UI. Real construction data (P2-3) remains deferred.

- Phase 20a: `TripLeg` and `MultiLegTripInput` added to `src/models.py` for v3 connection mode (input model only — no calculation yet). `TripLeg` holds origin/destination and planned departure/arrival times with validation; `MultiLegTripInput` requires ≥2 legs, enforces that adjacent legs connect (destination of one = origin of next), validates trip_type, and exposes `transfer_stations` and `final_destination` helpers. 7 tests added; 99/99 passing. No changes to existing models or the advisor flow.

- Phase 20b: `src/connection_engine.py` added — `estimate_leg_arrival_delay(leg, destination_stats)` estimates a leg's arrival delay from its destination station stats, reusing the existing risk engine (`calculate_confidence`, `calculate_historical_risk`) rather than a new model. Returns risk_level, confidence_level, expected (avg) and p80 delay minutes, and `has_data`; no data / too-thin samples report 0-minute delays and `has_data=False` so downstream connection logic treats them neutrally. Static data only (no live integration yet). NOTE: the engine file was already present uncommitted from an earlier interrupted session; it matched the plan and was adopted as-is with tests added. 4 tests; 103/103 passing.

- Phase 20c: transfer time modeling added to `src/connection_engine.py` — `MINIMUM_TRANSFER_MINUTES` manual per-station table (large hubs need more; extend as real data confirmed) plus `DEFAULT_MINIMUM_TRANSFER_MINUTES` fallback, and `minimum_transfer_minutes(station_name, default=...)`. This is the transfer time before any delay is applied; 20d compares it against the leg-1 delay estimate. 4 tests; 107/107 passing.

- Phase 20d: `compute_connection_risk(arrival_leg, departure_leg, leg1_delay_estimate, transfer_station=None)` added to `src/connection_engine.py`. Combines the scheduled transfer buffer (`departure - arrival`), the leg-1 delay estimate (expected + p80 from 20b), and the minimum transfer time (20c) into slack = buffer − delay − minimum. Classifies Low (conservative/p80 slack ≥ 0), Medium (expected slack ≥ 0 only), High (expected slack < 0), and exposes `likely_missed` and all intermediates. No-data leg-1 estimates use 0-minute delays (neutral) with `has_data=False` so the UI can mark low confidence. Helper `_minutes_between` added. 6 tests; 113/113 passing.

- Phase 20e: `build_connection_message(connection_risk, next_departure_time=None)` added to `src/recommendation.py`. Turns a 20d connection-risk dict into customer-facing text: High → explicit next-train fallback ("plan for the next departure at HH:MM" when a time is given, else "take an earlier first train"); Medium → tight, keep a fallback in mind; Low → reassuring with slack minutes. Appends `CONNECTION_NO_DATA_CAVEAT` when the leg-1 estimate had no data. 6 tests; 119/119 passing.

- Phase 20f: connection mode wired into the UI. `app.py` gains a third tab ("Connection mode") with a two-leg input form (origin/transfer/final stations, per-leg departure/arrival, trip type) that builds `TripLeg`/`MultiLegTripInput`, estimates the leg-1 delay from the transfer station's stats, computes connection risk (20d), and renders a color-coded connection-risk card with metrics and the 20e message (error/warning/success by level, low-confidence caption when no data). Invalid connecting trips surface the model's ValueError. app.py stays thin (orchestration only). End-to-end test added (`tests/test_end_to_end_connection.py`): a tight transfer at München Hbf yields a correct High-risk warning with next-train fallback, and a comfortable transfer yields Low — through the full pipeline. 2 tests; 121/121 passing. **v3 connection mode (Phase 20a-20f) complete.**

- Phase 21: continuous integration added (`.github/workflows/ci.yml`) — on every push/PR to main it installs `requirements.txt`, runs `pytest`, and runs an `import app` smoke check (the check that would have caught the v2.0 stale-deploy ImportError). Python pinned to 3.12 via `.python-version` (consumed by actions/setup-python; README notes to set the same version in Streamlit Cloud). CI badge added to README. 6 tests guard the config itself; 127/127 passing. First v2.1 phase, per `docs/13-v2.1-technical-delivery-plan.md`.

- Phase 22: `src/cache_utils.py` added — `TimedCache` (injectable clock) caches successful producer results for a TTL and never caches exceptions. Wired into the live clients: the raw network calls were split into `_..._uncached` plus a cached front (`_fetch_current_weather` keyed by coordinates, TTL 600s; `_request_train_status` keyed by train number, TTL 60s), so repeated submits hit the API at most once per TTL. Failures are not cached, so the fail-closed fallback still works and can recover. Existing weather/delay tests unchanged (they patch the cached front); new tests patch the uncached raw fns. 9 tests added (5 cache_utils + 4 caching); 136/136 passing. `app.py` unchanged (caching lives in `src/*`).

- Phase 23a: research + recommendation only (no code, so no tests). `docs/14-real-historical-data-source-decision.md` evaluates 6 candidate real-world DB historical data sources against a 10-point rubric and the StationStats mapping. Recommendation: adopt piebro `deutsche-bahn-data` (Hugging Face, CC BY 4.0, per-stop delay + cancellation + EVA station id, downloadable parquet) as an offline batch input; DB Timetables API and Bahn-Vorhersage/OPUS deferred as later/fallback; gtfs.de, v6.db.transport.rest, and Statista rejected. Awaiting source approval before Phase 23b (ingestion). Sample CSV fallback to be preserved.

- Phase 23b: `src/data_ingest.py` added — offline batch pipeline turning per-stop DB records into StationStats-shaped output. `aggregate_station_stats` groups by station and computes sample_size, cancellation_rate (cancelled/all stops), late_rate (share of non-cancelled stops with arrival delay >= 6 min, tunable), avg_delay_minutes, and p80_delay_minutes; cancelled stops are excluded from delay metrics. `read_stops` dispatches parquet (real snapshot) or CSV (fixture); `build_station_stats_csv` runs read→aggregate→write, and the output loads through the unchanged `data_loader`/`StationStats` (proven by a round-trip test). `min_sample_size` and `top_n` support the busiest-stations-first scope. NOT wired into the app (that is 23c); risk engine unchanged. Raw `*.parquet`/`data/raw/` git-ignored; README documents the download step and CC BY 4.0 attribution to Deutsche Bahn (via piebro/deutsche-bahn-data). 11 tests using a tiny fixture (no real parquet, no pyarrow); 147/147 passing.

- Phase 23c: real data wired into the app with fallback. Generated `data/station_stats.csv` (top 100 busiest stations, Oct 2025 snapshot, ≥6 min threshold) via the Phase 23b pipeline from the piebro parquet (schema: station_name / delay_in_min / is_canceled; 1.99M stops → 100 stations, 4.2 KB CSV, committed). `resolve_station_stats_path(preferred, fallback)` added to `data_loader` (tested); `app.py` now prefers `data/station_stats.csv` and falls back to `data/sample_station_stats.csv` if absent — sample fallback NOT removed. Reliability board shows the active data source (real vs sample) + file freshness. Risk engine unchanged; raw parquet kept out of git. README limitations/status updated. 4 tests added; 151/151 passing. **v2.1 real-data milestone (23a–23c) complete.**

## Post-release audit (2026-07-06)

Two independent audits verified all 15 phases against `trainbuffer_technical_delivery_plan.md`'s exact numeric thresholds, function signatures, and named test scenarios — all passed. One cosmetic finding: `app.py`'s "no data" branch hardcoded its own copy of the no-data message instead of reusing `src/recommendation.py`'s `NO_DATA_TEXT`. Fixed by importing and reusing `NO_DATA_TEXT` directly, removing the duplicated string. No functional or business-rule discrepancies found. 64/64 tests still passing after the fix.
