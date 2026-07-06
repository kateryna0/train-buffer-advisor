# 12 — TrainBuffer v1.5+ Technical Delivery Plan

**Project:** TrainBuffer
**Repo:** `train-buffer-advisor`
**Status:** v1.0 released (all P0 backlog items done; P1-1, P1-2, P1-3 done)
**This document covers:** remaining P1 backlog (P1-4, P1-5) and the v1.5 / v2 / v3 roadmap from `docs/09-roadmap-definition-of-done.md`

---

## 0. How to use this document

Follow the same developer lifecycle rule as v1 (`trainbuffer_technical_delivery_plan.md` section 5):

```text
1. Define
2. Design
3. Implement
4. Test
5. Review
6. Commit
7. Move to next feature
```

Rule: **no next feature before the current feature passes tests.** Implement one phase at a time, add tests, run `pytest`, fix failures, commit, then continue. Update `docs/progress.md` after each phase, same as v1.

Do not ask an AI coding agent to "build v1.5." Ask it to implement one phase, add tests, run tests, stop.

---

## 1. Phase 16 — Better UI design (P1-4)

### Goal

Polish the Streamlit UI now that the core engine works. This is presentation only — no business logic changes.

### Scope

```text
- Improve visual layout of the result card (columns, grouping, icons)
- Add color-coded risk level (e.g. green/amber/red badge for Low/Medium/High)
- Group weather and construction inputs under an expandable "Advanced conditions" section
- Add a sidebar with a short "How TrainBuffer works" explainer
- Keep app.py thin: layout/styling changes only, no new calculations in app.py
```

### Out of scope for this phase

```text
- New calculation logic
- New data sources
- Any change to src/risk_engine.py, src/time_utils.py, src/recommendation.py business rules
```

### Manual UI checklist

```text
Risk level badge shows correct color for Low/Medium/High/no_data
Advanced conditions section collapses/expands correctly
Sidebar explainer renders
No regression in existing manual QA checklist from Phase 8
pytest still passes (no test changes expected since no logic changed)
```

### Done when

```text
- UI redesign implemented
- Manual QA checklist passes
- pytest passes (unchanged suite)
```

### Commit

```bash
git commit -m "Improve Streamlit UI design and layout"
```

---

## 2. Phase 17 — Real weather API (P1-5)

### Goal

Replace the manual strong-wind/heat/snow-ice checkboxes with a live weather signal, while preserving a graceful fallback if the API is unavailable (per v1.5 roadmap rule: "v1 should still work if all live APIs are unavailable").

### Candidate data source

```text
Open-Meteo (free, no API key required) — https://open-meteo.com
```

### New file

```text
src/weather_client.py
```

### Functions

```python
def fetch_weather_signal(station_name: str, station_coordinates: dict) -> dict:
    """Returns {"strong_wind": bool, "heat": bool, "snow_ice": bool} or raises on failure."""
    ...


def get_weather_flags_with_fallback(station_name: str, station_coordinates: dict) -> dict:
    """Calls fetch_weather_signal; on any failure, returns all-False flags and a fallback warning."""
    ...
```

### Design notes

```text
- Add a small lookup table of station_name -> (latitude, longitude) for the sample stations
- Wind threshold, heat threshold, and snow/ice detection rules must be explicit and testable
  (e.g. wind_speed_kmh > 50 -> strong_wind, temperature_c > 30 -> heat, snowfall/precip type -> snow_ice)
- Reuse the existing apply_weather_modifier(strong_wind, heat, snow_ice) from src/risk_engine.py unchanged —
  only the flag source changes, not the modifier rule
- Network calls must be isolated in src/weather_client.py so they can be mocked in tests
```

### Tests

```text
- fetch_weather_signal returns expected flags for mocked API responses (wind/heat/snow/none)
- get_weather_flags_with_fallback returns all-False + warning when the API call raises
- get_weather_flags_with_fallback returns correct flags when the API call succeeds
- existing apply_weather_modifier tests remain unchanged and passing
```

### UI change

```text
Replace the three weather checkboxes with an automatic lookup + a "Weather source: live / unavailable" caption.
Keep a manual override checkbox group visible but collapsed, in case the live source is down.
```

### Done when

```text
- src/weather_client.py implemented with mockable network calls
- fallback behavior tested and confirmed non-blocking
- app.py uses live weather with manual override fallback
- pytest passes
```

### Commit

```bash
git commit -m "Add live weather API with graceful fallback"
```

---

## 3. Phase 18 — v1.5: Live upstream delay check

### Goal

Add a live signal for a specific train if the user provides a train number, per `docs/09-roadmap-definition-of-done.md` v1.5 section: check whether the train is already delayed at earlier stops, since this is "the biggest practical accuracy gain."

### New file

```text
src/live_delay_client.py
```

### Functions

```python
def fetch_live_delay(train_number: str) -> dict | None:
    """Returns {"currently_delayed": bool, "delay_minutes": int} or None if unavailable/not found."""
    ...


def apply_live_delay_modifier(base_recommendation, live_delay_info: dict | None):
    """If the train is already delayed, add a warning and increase buffer; if unavailable, no-op."""
    ...
```

### Candidate data source

```text
DB Timetables API or db.transport.rest (public, unofficial) — confirm current terms of use before integrating
```

### Design notes / risks (from roadmap doc, must be respected)

```text
- Train number input becomes meaningful for the first time (v1 collected it as optional, unused)
- API fragility and rate limits: wrap all calls with a timeout and fail closed (treat failure as "no live data", not an error)
- Matching train numbers correctly is nontrivial — validate format before calling the API
- Live data disappearing after arrival must not crash the app — treat missing data as neutral, not negative
- This must not become a hard dependency: if the API is down, v1.5 behavior must degrade to v1 behavior exactly
```

### Tests

```text
- fetch_live_delay returns delay info for a mocked "delayed" response
- fetch_live_delay returns None for a mocked "not found" or timeout response
- apply_live_delay_modifier increases buffer and adds warning when train is delayed
- apply_live_delay_modifier is a no-op when live data is unavailable
- full app behavior is unchanged when no train number is provided
```

### UI change

```text
Add optional "Train number" input (already present in TripInput per v1 spec, currently unused)
Show "Live status: delayed by X min" or "Live status: unavailable" badge
```

### Done when

```text
- src/live_delay_client.py implemented with mocked tests (no real network calls in test suite)
- fallback to v1 behavior confirmed when API unavailable
- pytest passes
- manual QA: app still works with airplane-mode / API blocked
```

### Commit

```bash
git commit -m "Add live upstream delay check for v1.5"
```

---

## 4. Phase 19 — v2: Disruption and reliability board

### Goal

Add broader context beyond a single-trip recommendation, per the v2 roadmap goal: full construction/disruption overlays, a reliability dashboard (worst stations/routes/times), and data freshness indicators.

### Scope

```text
- New Streamlit page/tab: "Reliability board"
- Aggregate view: worst stations by late_rate, worst by cancellation_rate, from data/sample_station_stats.csv
  (or real aggregated data once P2-1 is done)
- Data freshness indicator: show when the underlying dataset was last updated
- Replace the P1 manual construction yes/no/unknown flag with a real construction/disruption data source
  (only if a low-complexity, stable source is confirmed feasible — otherwise keep the manual flag and document why)
```

### New file

```text
src/reliability_board.py
```

### Functions

```python
def compute_reliability_rankings(stats_by_station: dict) -> dict:
    """Returns worst-N stations by late_rate and by cancellation_rate."""
    ...
```

### Tests

```text
- compute_reliability_rankings returns correct ordering for a known small dataset
- ties are handled deterministically
- empty dataset returns empty rankings without error
```

### Done when

```text
- reliability board renders in the UI as a separate view
- rankings are computed by tested pure functions, not hardcoded in the UI
- construction/disruption data source decision is documented (real source adopted, or manual flag kept with reason)
- pytest passes
```

### Commit

```bash
git commit -m "Add v2 reliability board and disruption context"
```

---

## 5. Phase 20 — v3: Connection mode

### Goal

Answer the harder question: **"Will I make my transfer?"** This is explicitly called out in the roadmap as too complex for v1 — treat it as its own multi-phase effort, not a single commit.

### Sub-phases (do not combine into one task)

```text
20a. Multi-leg trip input model (extend TripInput or add a new MultiLegTripInput)
20b. Arrival delay estimation for the first leg (reuse existing risk engine per leg)
20c. Transfer time modeling (minimum realistic transfer time per station, manual table first)
20d. Downstream connection risk calculation (combine leg 1 delay distribution with leg 2 buffer)
20e. Missed-connection handling and next-train fallback messaging
20f. UI for multi-leg input and connection-risk result card
```

### Design notes

```text
- Do not attempt live data integration until 20a-20e work with static/sample data
- Each sub-phase must have its own tests before starting the next (same one-feature-at-a-time rule)
- This is the largest and riskiest phase in the roadmap; expect it to take longer than all prior phases combined
```

### Done when (for the full v3 milestone)

```text
- all sub-phases 20a-20f implemented and tested independently
- end-to-end test scenario: "connecting trip with tight transfer" produces a correct risk warning
- pytest passes
```

### Commit

```bash
git commit -m "Add v3 connection mode: <sub-phase name>"
```
(one commit per sub-phase, not one commit for all of v3)

---

## 6. Guardrails carried over from the v1 plan

These still apply (from `docs/09-roadmap-definition-of-done.md`):

```text
Rule 1 — No new feature before the app runs locally on the current phase's changes
Rule 2 — No UI before the underlying logic has tests
Rule 3 — No ML before the current rule-based baseline is proven insufficient
Rule 4 — No live API dependency that breaks v1 behavior when the API is unavailable
Rule 5 — Every feature must improve the core decision: "what is my latest safe planned arrival, and should I take one earlier?"
```

---

## 7. Updated technical backlog after this plan

| ID | Feature | Phase | Status after this plan |
|---|---|---|---|
| P1-4 | Better UI design | 16 | To do |
| P1-5 | Real weather API | 17 | To do |
| P2-2 | Live DB delay API (v1.5) | 18 | To do |
| P2-3 | Real construction/disruption data | 19 (partial) | To do or documented as deferred |
| P2-1 | Real DB historical aggregation | 19 (prerequisite for full board) | To do |
| P2-4 | Connection mode (v3) | 20a-20f | To do |
| P2-5 | Mobile/PWA | — | Still out of scope; not planned in this document |

---

## 8. Definition of Done for this document's scope

This delivery plan's scope (Phases 16-20) is done when:

```text
- Phases 16 and 17 (P1 backlog) are complete, tested, and committed
- Phase 18 (v1.5) is complete with confirmed graceful degradation when live APIs are unavailable
- Phase 19 (v2) reliability board is live and its data source decision is documented
- Phase 20 (v3) sub-phases are complete and independently tested
- docs/progress.md is updated after every phase, same as v1
- README.md roadmap section is updated to move completed items from "Roadmap" to "Project status"
```
