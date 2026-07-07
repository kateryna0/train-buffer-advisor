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

## Post-release audit (2026-07-06)

Two independent audits verified all 15 phases against `trainbuffer_technical_delivery_plan.md`'s exact numeric thresholds, function signatures, and named test scenarios — all passed. One cosmetic finding: `app.py`'s "no data" branch hardcoded its own copy of the no-data message instead of reusing `src/recommendation.py`'s `NO_DATA_TEXT`. Fixed by importing and reusing `NO_DATA_TEXT` directly, removing the duplicated string. No functional or business-rule discrepancies found. 64/64 tests still passing after the fix.
