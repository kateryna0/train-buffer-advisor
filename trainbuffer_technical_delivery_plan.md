# TrainBuffer — Technical Delivery Plan

**Project:** TrainBuffer  
**Repo name:** `train-buffer-advisor`  
**Product type:** Python/Streamlit web app  
**Current stage:** pre-build planning → implementation with Claude Code  
**Core positioning:** deadline-based buffer advisor, not a delay predictor  

---

## 1. Product summary

TrainBuffer is a web app that helps users plan important train trips in Germany. Instead of trying to predict the exact delay of a single Deutsche Bahn train, it gives a transparent buffer recommendation based on historical station reliability, trip type, deadline, confidence level, and later optional weather/construction signals.

The main user question is:

> “I need to arrive by a specific time. Is my planned train arrival safe enough, or should I take an earlier train?”

The product should not feel like a technical risk calculator. It should feel like a practical travel advisor.

---

## 2. Product decision after feedback

Friend feedback changed the product focus from generic buffer minutes to a deadline-based flow.

### Before

```text
Recommended buffer: 30 minutes
```

### Now

```text
When do you absolutely need to arrive?
```

Then the app calculates:

```text
latest_safe_planned_arrival = arrival_deadline - recommended_buffer
```

Example:

```text
Arrival deadline: 10:00
Recommended buffer: 35 minutes
Latest safe planned arrival: 09:25
```

If the user’s planned arrival is later than 09:25, the app warns that the trip is risky.

---

## 3. V1 scope

### V1 must do

```text
- User enters origin station
- User enters destination station
- User enters planned arrival time
- User enters absolute arrival deadline
- User selects trip type
- App calculates risk level: Low / Medium / High / No data
- App calculates recommended buffer in minutes
- App calculates latest safe planned arrival
- App compares planned arrival with latest safe planned arrival
- App gives customer-native recommendation text
- App shows confidence level
- App shows reasons and warnings
- App handles unknown / low-data stations honestly
- App runs locally
- App is deployed as a Streamlit web app
- Core logic is covered with tests
```

### V1 must not do

```text
- No mobile app
- No native iOS/Android
- No complex ML model
- No exact train delay prediction
- No live DB API in first sprint
- No full construction/disruption integration in first sprint
- No connection prediction in v1
- No user accounts
- No notifications
- No route optimization
```

### Optional V1 / P1

```text
- Manual weather risk flags
- Manual construction/disruption flag
- Privacy-safe local advice logging
```

---

## 4. Technical architecture principle

The most important technical rule:

```text
Business logic must be separate from Streamlit UI.
```

Bad structure:

```text
app.py contains UI + formulas + data loading + recommendation text + logging
```

Good structure:

```text
app.py                 # Streamlit UI only
src/models.py          # input/output models
src/risk_engine.py     # risk and buffer calculation
src/recommendation.py  # customer-native advice text
src/data_loader.py     # station statistics loading
src/time_utils.py      # deadline/time calculations
src/logging_utils.py   # optional advice logging
```

This makes the project testable and reusable. Later, the same core logic could be reused in a FastAPI backend, React frontend, PWA, or mobile app.

---

## 5. Developer lifecycle rule

Every feature follows the same lifecycle:

```text
1. Define
2. Design
3. Implement
4. Test
5. Review
6. Commit
7. Move to next feature
```

The project rule:

```text
No next feature before current feature passes tests.
```

For every feature:

```text
- Implement one small feature only
- Add tests for that feature
- Run pytest
- Fix failing tests
- Commit only when tests pass
- Then move to the next feature
```

Core command:

```bash
pytest
```

Later optional quality command:

```bash
ruff check .
```

---

## 6. Definition of Done

A feature is done only when:

```text
- Code works locally
- Unit tests exist
- Tests pass
- No unrelated changes are included
- Documentation is updated if needed
- Git commit is made with a clear message
```

TrainBuffer v1 is done only when:

```text
- User can enter destination, planned arrival, deadline, and trip type
- App calculates risk level
- App calculates recommended buffer
- App calculates latest safe planned arrival
- App compares planned arrival with latest safe planned arrival
- App gives customer-native recommendation
- App shows confidence
- App handles no-data cases honestly
- App has tests for risk engine, deadline logic, trip type modifiers, recommendation text, and data loading
- pytest passes
- App runs locally
- App is deployed
- README explains project, setup, limitations, and roadmap
```

---

# 7. Delivery phases

---

## Phase 1 — Project setup

### Goal

Create a clean project structure so Claude Code does not generate a messy app.

### Tasks

Create GitHub repo:

```text
train-buffer-advisor
```

Create files:

```text
train-buffer-advisor/
  README.md
  app.py
  requirements.txt
  pytest.ini

  src/
    __init__.py
    models.py
    risk_engine.py
    recommendation.py
    data_loader.py
    time_utils.py
    logging_utils.py

  data/
    sample_station_stats.csv

  tests/
    test_project_imports.py
    test_models.py
    test_risk_engine.py
    test_recommendation.py
    test_data_loader.py
    test_time_utils.py
    test_logging_utils.py

  docs/
    01-product-description.md
    02-market-and-competitor-research.md
    03-user-questions-and-jobs-to-be-done.md
    04-four-role-product-audit.md
    05-v1-product-spec.md
    06-data-sources-and-feasibility.md
    07-risk-rule-spec.md
    08-legal-privacy-compliance.md
    09-roadmap-definition-of-done.md
    10-prompt-engineering-workflow.md
    11-feedback-and-decisions.md
```

### Dependencies

Start with:

```text
streamlit
pandas
pytest
```

Optional later:

```text
ruff
```

### Test

Create `tests/test_project_imports.py`:

```python
def test_project_imports():
    import src.models
    import src.risk_engine
    import src.recommendation
    import src.data_loader
    import src.time_utils
```

### Done when

```text
- Project structure exists
- Import test exists
- pytest passes
```

### Commit

```bash
git commit -m "Initialize TrainBuffer project structure"
```

---

## Phase 2 — Domain models

### Goal

Define clean input/output models before implementing calculations.

### File

```text
src/models.py
```

### Models

#### TripInput

Fields:

```text
origin_station: str
destination_station: str
planned_arrival_time: datetime or time
arrival_deadline: datetime or time
trip_type: str
```

Allowed trip types:

```text
normal
airport
interview_exam
government_visa_medical
transfer
```

#### StationStats

Fields:

```text
station_name: str
sample_size: int
late_rate: float
cancellation_rate: float
avg_delay_minutes: float
p80_delay_minutes: float
```

#### BufferRecommendation

Fields:

```text
risk_level: str
recommended_buffer_minutes: int | None
latest_safe_planned_arrival: datetime/time | None
is_planned_arrival_safe: bool | None
confidence_level: str
reasons: list[str]
warnings: list[str]
data_sources: list[str]
```

### Tests

File:

```text
tests/test_models.py
```

Test cases:

```text
- valid TripInput can be created
- invalid trip type is rejected or handled
- empty station name is rejected or handled
- StationStats accepts valid rates
- BufferRecommendation contains required fields
```

### Done when

```text
- models.py exists
- tests exist
- pytest passes
```

### Commit

```bash
git commit -m "Add domain models for TrainBuffer"
```

---

## Phase 3 — Core risk engine

### Goal

Build the main calculation engine without UI, APIs, weather, or live data.

### File

```text
src/risk_engine.py
```

---

### Feature 3.1 — Confidence calculation

Rule:

```text
sample_size < 20       -> no_data
20–49                  -> low
50–199                 -> medium
>= 200                 -> high
```

Function example:

```python
def calculate_confidence(sample_size: int) -> str:
    ...
```

Tests:

```text
sample_size = 5   -> no_data
sample_size = 25  -> low
sample_size = 100 -> medium
sample_size = 250 -> high
```

---

### Feature 3.2 — Historical risk level

Rule:

```text
late_rate < 0.15       -> Low
0.15–0.30              -> Medium
> 0.30                 -> High
```

Cancellation modifier:

```text
cancellation_rate >= 0.08 -> increase risk by one level
```

Risk level order:

```text
Low -> Medium -> High
```

Tests:

```text
late_rate 0.10 -> Low
late_rate 0.22 -> Medium
late_rate 0.40 -> High
high cancellation increases Low to Medium
high cancellation increases Medium to High
High remains High
```

---

### Feature 3.3 — Base buffer calculation

Base rule:

```text
Low risk      -> 10 minutes
Medium risk   -> 20 minutes
High risk     -> 35 minutes
No data       -> no recommendation, show warning
```

Tests:

```text
Low -> 10
Medium -> 20
High -> 35
No data -> recommended_buffer_minutes is None
No data -> warning is present
```

---

### Feature 3.4 — Main calculation function

Function:

```python
def calculate_buffer(trip_input: TripInput, station_stats: StationStats) -> BufferRecommendation:
    ...
```

### Done when

```text
- confidence calculation works
- risk level calculation works
- buffer calculation works
- no-data behavior works
- tests pass
```

### Commit

```bash
git commit -m "Implement core risk engine with tests"
```

---

## Phase 4 — Deadline-based flow

### Goal

Implement the most important product improvement from feedback.

### File

```text
src/time_utils.py
```

### Feature 4.1 — Calculate latest safe planned arrival

Formula:

```text
latest_safe_planned_arrival = arrival_deadline - recommended_buffer
```

Example:

```text
deadline = 10:00
buffer = 35 minutes
latest safe planned arrival = 09:25
```

Tests:

```text
10:00 - 35 min -> 09:25
09:00 - 20 min -> 08:40
00:30 - 45 min -> previous day / handled correctly
```

---

### Feature 4.2 — Compare planned arrival with latest safe arrival

Rule:

```text
if planned_arrival_time <= latest_safe_planned_arrival:
    is_planned_arrival_safe = True
else:
    is_planned_arrival_safe = False
```

Tests:

```text
planned arrival before safe time -> safe
planned arrival exactly safe time -> safe
planned arrival after safe time -> risky
```

### Done when

```text
- latest safe planned arrival is calculated
- planned arrival safety is calculated
- tests pass
```

### Commit

```bash
git commit -m "Add deadline-based safe arrival logic"
```

---

## Phase 5 — Trip type conservatism

### Goal

Tailor the buffer recommendation without adding heavy complexity.

### File

```text
src/risk_engine.py
```

### Trip type modifiers

| Trip type | Modifier | Product meaning |
|---|---:|---|
| normal | +0 min | Less conservative |
| airport | +20 min | Conservative buffer; airport security/baggage not included |
| interview_exam | +15 min | High emotional cost |
| government_visa_medical | +15 min | Hard to reschedule |
| transfer | +0 or +10 min + warning | Transfer mode not fully supported in v1 |

### Important warning for airport

```text
Airport buffer does not include security, baggage drop, or walking time inside the airport.
```

### Important warning for transfer

```text
Transfer mode is not fully supported in v1. Use this result only as a rough warning.
```

### Tests

```text
normal trip keeps base buffer
airport adds 20 minutes
interview_exam adds 15 minutes
government_visa_medical adds 15 minutes
transfer returns warning
airport returns airport-specific warning
```

### Done when

```text
- trip type modifies buffer correctly
- warnings work
- tests pass
```

### Commit

```bash
git commit -m "Add trip type buffer modifiers"
```

---

## Phase 6 — Customer-native recommendation text

### Goal

Make the output sound like a useful travel advisor, not a calculator.

### File

```text
src/recommendation.py
```

### Function

```python
def build_recommendation_text(trip_input: TripInput, result: BufferRecommendation) -> str:
    ...
```

### Example outputs

#### Risky important trip

```text
Your planned arrival is risky for an interview/exam.
Aim to arrive at least 35 minutes before your deadline.
If possible, choose a train that arrives one connection earlier than planned.
```

#### Safe normal trip

```text
Your planned arrival looks acceptable for a normal trip.
A 10-minute buffer is recommended based on the available station reliability data.
```

#### No data

```text
There is not enough historical data for this destination station to make a reliable recommendation.
Please check DB Navigator before departure and plan conservatively.
```

#### Transfer

```text
Transfer trips are not fully supported in TrainBuffer v1.
Use this result as a rough warning only and check your connection in DB Navigator.
```

### Tests

```text
High risk text includes "risky"
Safe text includes "acceptable"
No data text includes "not enough historical data"
Airport text includes conservative wording
Transfer text includes out-of-scope warning
```

### Done when

```text
- recommendation.py implemented
- text tests pass
- pytest passes
```

### Commit

```bash
git commit -m "Add customer-native recommendation text"
```

---

## Phase 7 — Sample data layer

### Goal

Use simple local sample data before working with the real large DB dataset.

Do not start with millions of rows. That is a scope trap.

### File

```text
data/sample_station_stats.csv
```

### Example data

```csv
station_name,sample_size,late_rate,cancellation_rate,avg_delay_minutes,p80_delay_minutes
Hamburg Hbf,250,0.28,0.03,7,15
Berlin Hbf,300,0.18,0.02,5,10
München Hbf,180,0.34,0.04,9,20
Köln Hbf,90,0.31,0.09,10,25
Small Station,12,0.20,0.00,4,8
```

### File

```text
src/data_loader.py
```

### Functions

```python
def load_station_stats(path: str) -> dict[str, StationStats]:
    ...


def get_station_stats(destination_station: str, stats: dict[str, StationStats]) -> StationStats | None:
    ...
```

### Tests

```text
CSV loads correctly
known station returns StationStats
unknown station returns None
Small Station triggers no_data through risk engine
```

### Done when

```text
- sample CSV exists
- loader works
- tests pass
```

### Commit

```bash
git commit -m "Add sample station statistics data layer"
```

---

## Phase 8 — Streamlit UI skeleton

### Goal

Build the first web UI only after the core logic works.

### File

```text
app.py
```

### Inputs

```text
Origin station
Destination station
Planned arrival time
Arrival deadline
Trip type
```

### UI honesty note

```text
TrainBuffer v1 uses destination station reliability as the main historical signal. It does not predict exact train delays.
```

### Result card

Show:

```text
Risk level
Recommended buffer
Latest safe planned arrival
Is planned arrival safe?
Customer-native recommendation
Confidence level
Reasons
Warnings
Data sources / limitations
```

### Manual UI checklist

```text
streamlit run app.py
Hamburg Hbf works
Unknown station shows no data
Airport increases buffer
Deadline calculation appears correctly
Transfer warning appears
No crash when fields are empty
```

### Automated testing rule

Streamlit UI itself can be tested manually in v1, but all logic must stay outside `app.py` and remain covered by unit tests.

### Done when

```text
- app runs locally
- manual UI checklist passes
- pytest still passes
```

### Commit

```bash
git commit -m "Add Streamlit UI for TrainBuffer prototype"
```

---

## Phase 9 — Advice logging

### Goal

Show that the product can be evaluated later.

This supports the product claim that TrainBuffer is transparent and measurable.

### File

```text
src/logging_utils.py
```

### Local log file

```text
data/advice_log.csv
```

### Fields

```text
timestamp
origin_station
destination_station
planned_arrival_time
arrival_deadline
trip_type
risk_level
recommended_buffer_minutes
latest_safe_planned_arrival
is_planned_arrival_safe
confidence_level
```

### Privacy rule

Do not log:

```text
- user name
- user email
- account id
- IP address
- precise personal profile
```

### UI note

```text
This prototype may log anonymous query inputs locally for evaluation. No account or personal profile is used.
```

### Tests

```text
log row is created
log contains expected columns
no personal profile fields are logged
```

### Done when

```text
- logging works locally
- privacy note exists
- tests pass
```

### Commit

```bash
git commit -m "Add privacy-safe advice logging"
```

---

## Phase 10 — Weather signal, optional P1

### Goal

Add a small weather modifier without building a complex weather system.

Start with manual flags, not API.

### Manual weather inputs

```text
Strong wind? yes/no
Heat? yes/no
Snow or ice? yes/no
```

### Weather modifier rule

```text
strong wind -> +5 min and reason
heat -> +5 min and reason
snow/ice -> +10 min and reason
max weather modifier -> +15 min
```

### Tests

```text
strong wind adds +5 and reason
heat adds +5 and reason
snow adds +10 and reason
multiple flags are capped at +15
no weather flags keep buffer unchanged
```

### Done when

```text
- manual weather flags work
- reasons are shown
- tests pass
```

### Commit

```bash
git commit -m "Add simple weather risk modifiers"
```

### Later replacement

After this works, manual flags can be replaced by Open-Meteo API.

---

## Phase 11 — Construction/disruption signal, optional P1

### Product note

Friend feedback suggested construction/disruption data because Germany has many rail construction works. This is valid, but it can easily become a data-integration trap.

### PM decision

Construction/disruption is P1 optional, not a blocker for v1.

### Option A — Simple manual flag for v1

Input:

```text
Known construction/disruption on route? yes/no/unknown
```

Rule:

```text
yes -> +10 min and reason
unknown -> no modifier, show limitation
no -> no modifier
```

### Tests

```text
construction yes adds +10
construction yes adds reason
construction unknown adds limitation
construction no does nothing
```

### Done when

```text
- simple flag works
- tests pass
```

### Commit

```bash
git commit -m "Add optional construction risk flag"
```

### Option B — Real construction/disruption data

Later only. Do not start with this.

---

## Phase 12 — End-to-end backend tests

### Goal

Test the full calculation path without Streamlit UI.

### File

```text
tests/test_end_to_end_calculation.py
```

### Scenario 1 — Normal low-risk trip

```text
Destination: Berlin Hbf
Trip type: normal
Deadline: 10:00
Planned arrival: 09:40
Expected: acceptable or low/medium risk depending on sample data
```

### Scenario 2 — Airport trip

```text
Destination: München Hbf
Trip type: airport
Deadline: 12:00
Planned arrival: 11:40
Expected: risky or conservative advice due to airport modifier
```

### Scenario 3 — Interview/exam

```text
Trip type: interview_exam
Expected: conservative recommendation text
```

### Scenario 4 — Unknown station

```text
Destination: Unknown Station
Expected: no_data, no fake recommendation
```

### Scenario 5 — Transfer

```text
Trip type: transfer
Expected: warning that transfer mode is out of scope in v1
```

### Done when

```text
- integration tests pass
- pytest passes
```

### Commit

```bash
git commit -m "Add end-to-end calculation tests"
```

---

## Phase 13 — Documentation update

### Goal

Make the GitHub repo understandable for recruiters and interviewers.

### README must include

```text
What TrainBuffer is
Problem statement
Why it is a buffer advisor, not a delay predictor
How it works
Tech stack
How to run locally
How to run tests
Project status
Limitations
Roadmap
AI-assisted development workflow
```

### Add screenshots later

```text
docs/screenshots/
```

### AI-assisted development section

Recommended wording:

```text
Claude Code was used as an AI-assisted development partner for implementation support, debugging, and test scaffolding. Product decisions, scope control, risk logic, and documentation were defined through a structured prompt-engineering workflow.
```

Do not claim:

```text
This app uses GenAI to predict train delays.
```

### Done when

```text
- README is clear
- setup instructions work
- test instructions work
- limitations are honest
```

### Commit

```bash
git commit -m "Update documentation for TrainBuffer v1"
```

---

## Phase 14 — Deployment

### Goal

Create a live demo.

### Platform

```text
Streamlit Community Cloud
```

### Tasks

```text
Push repo to GitHub
Check requirements.txt
Deploy app.py
Open live app
Test sample station
Test unknown station
Add live link to README
```

### Deployment checklist

```text
App opens
Sample stations work
Unknown station works
No secrets exposed
README has live demo link
pytest passes locally
```

### Done when

```text
- live URL works
- GitHub repo looks clean
- README has demo link
```

### Commit

```bash
git commit -m "Prepare TrainBuffer for Streamlit deployment"
```

---

## Phase 15 — V1 release

### Release checklist

```text
All P0 features complete
pytest passes
Streamlit app runs locally
Live deployment works
README is updated
Limitations are clear
No-data state works
Deadline flow works
Trip type modifiers work
Customer-native recommendations work
```

### Tag release

```bash
git tag v1.0
git push origin v1.0
```

---

# 8. Technical backlog

## P0 — Must have for v1

| ID | Feature | Test required |
|---|---|---|
| P0-1 | Project structure | Import test |
| P0-2 | Domain models | Model tests |
| P0-3 | Risk engine | Unit tests |
| P0-4 | Deadline logic | Time calculation tests |
| P0-5 | Trip type modifiers | Unit tests |
| P0-6 | Recommendation text | Text output tests |
| P0-7 | Sample data loader | CSV/data tests |
| P0-8 | Streamlit UI | Manual QA + backend tests |
| P0-9 | README | Manual review |
| P0-10 | Deploy | Live smoke test |

## P1 — Nice but not first

| ID | Feature | Comment |
|---|---|---|
| P1-1 | Weather modifier | Start with manual flags |
| P1-2 | Construction flag | Start with manual yes/no/unknown |
| P1-3 | Advice logging | Useful for evaluation and portfolio credibility |
| P1-4 | Better design | After core app works |
| P1-5 | Real weather API | After manual weather logic works |

## P2 — Later

| ID | Feature | Comment |
|---|---|---|
| P2-1 | Real DB historical aggregation | Hard data engineering task |
| P2-2 | Live DB delay API | v1.5 |
| P2-3 | Real construction/disruption data | v1.5/v2 |
| P2-4 | Connection mode | v3 |
| P2-5 | Mobile/PWA | Only after web app works |

---

# 9. Claude Code workflow

## Rule

Do not ask Claude Code:

```text
Build the whole app.
```

Ask Claude Code:

```text
Implement one feature.
Add tests.
Run tests.
Fix failing tests only.
Stop.
```

---

## Prompt 1 — Project setup

```text
We are building TrainBuffer, a Python/Streamlit web app that gives transparent buffer advice for German train trips.

Important rules:
- Do not build the full app yet.
- Do not add external APIs.
- Do not add live DB data.
- Keep business logic separate from Streamlit UI.
- After each feature, add pytest tests.
- We only move to the next feature when tests pass.

First task:
Create the initial project structure:
- app.py
- requirements.txt
- pytest.ini
- src/__init__.py
- src/models.py
- src/risk_engine.py
- src/recommendation.py
- src/data_loader.py
- src/time_utils.py
- src/logging_utils.py
- tests/test_project_imports.py

Add a simple import test to confirm the modules can be imported.
Do not implement business logic yet.
After creating files, tell me how to run the tests.
```

---

## Prompt 2 — Domain models

Use only after Prompt 1 tests pass.

```text
Now implement the domain models in src/models.py.

Create models for:
- TripInput
- StationStats
- BufferRecommendation

Fields:
TripInput:
- origin_station: str
- destination_station: str
- planned_arrival_time
- arrival_deadline
- trip_type

Allowed trip types:
- normal
- airport
- interview_exam
- government_visa_medical
- transfer

StationStats:
- station_name
- sample_size
- late_rate
- cancellation_rate
- avg_delay_minutes
- p80_delay_minutes

BufferRecommendation:
- risk_level
- recommended_buffer_minutes
- latest_safe_planned_arrival
- is_planned_arrival_safe
- confidence_level
- reasons
- warnings
- data_sources

Add pytest tests for valid and invalid model cases.
Do not implement Streamlit UI yet.
After implementation, tell me exactly how to run the tests.
```

---

## Prompt 3 — Risk engine

Use only after model tests pass.

```text
Now implement the core risk engine in src/risk_engine.py.

Rules:
Confidence:
- sample_size < 20 -> no_data
- 20 to 49 -> low
- 50 to 199 -> medium
- >= 200 -> high

Historical risk:
- late_rate < 0.15 -> Low
- 0.15 to 0.30 -> Medium
- > 0.30 -> High

Cancellation modifier:
- cancellation_rate >= 0.08 increases risk by one level
- High remains High

Base buffer:
- Low -> 10 minutes
- Medium -> 20 minutes
- High -> 35 minutes
- no_data -> no recommendation and warning

Implement:
- calculate_confidence(sample_size)
- calculate_historical_risk(late_rate, cancellation_rate)
- calculate_base_buffer(risk_level)
- calculate_buffer(trip_input, station_stats)

Add pytest tests for all rules.
Do not implement UI, API, weather, or construction yet.
```

---

## Prompt 4 — Deadline logic

Use only after risk engine tests pass.

```text
Now implement deadline-based safe arrival logic.

In src/time_utils.py implement:
- calculate_latest_safe_arrival(arrival_deadline, recommended_buffer_minutes)
- is_planned_arrival_safe(planned_arrival_time, latest_safe_planned_arrival)

Rule:
latest_safe_planned_arrival = arrival_deadline - recommended_buffer

Safe rule:
planned arrival is safe if planned_arrival_time <= latest_safe_planned_arrival.

Add pytest tests:
- 10:00 minus 35 min = 09:25
- planned arrival before safe time is safe
- planned arrival exactly at safe time is safe
- planned arrival after safe time is risky
- edge case around midnight is handled

Do not implement UI yet.
```

---

## Prompt 5 — Trip type modifiers

Use only after deadline tests pass.

```text
Now add trip type buffer modifiers.

Rules:
- normal -> +0 minutes
- airport -> +20 minutes and airport warning
- interview_exam -> +15 minutes
- government_visa_medical -> +15 minutes
- transfer -> add warning that transfer mode is not fully supported in v1

Airport warning:
Airport buffer does not include security, baggage drop, or walking time inside the airport.

Transfer warning:
Transfer mode is not fully supported in TrainBuffer v1. Use this result only as a rough warning.

Update calculate_buffer so the final recommended buffer includes the trip type modifier.
Add tests for each trip type.
Do not implement UI yet.
```

---

## Prompt 6 — Recommendation text

Use only after trip type tests pass.

```text
Now implement customer-native recommendation text in src/recommendation.py.

Create:
build_recommendation_text(trip_input, result) -> str

The text should be practical and human-readable.

Examples:
- Risky important trip: "Your planned arrival is risky for an interview/exam. Aim to arrive at least X minutes before your deadline. If possible, choose a train that arrives one connection earlier than planned."
- Safe normal trip: "Your planned arrival looks acceptable for a normal trip. A X-minute buffer is recommended based on the available station reliability data."
- No data: "There is not enough historical data for this destination station to make a reliable recommendation. Please check DB Navigator before departure and plan conservatively."
- Transfer: include that transfer mode is not fully supported in v1.

Add pytest tests for risky, safe, no-data, airport, and transfer cases.
Do not implement UI yet.
```

---

## Prompt 7 — Sample data layer

Use only after recommendation tests pass.

```text
Now add a simple sample data layer.

Create data/sample_station_stats.csv with these columns:
station_name,sample_size,late_rate,cancellation_rate,avg_delay_minutes,p80_delay_minutes

Add sample rows for:
- Hamburg Hbf
- Berlin Hbf
- München Hbf
- Köln Hbf
- Small Station

In src/data_loader.py implement:
- load_station_stats(path)
- get_station_stats(destination_station, stats)

Add tests:
- CSV loads
- known station returns StationStats
- unknown station returns None
- Small Station has sample_size < 20 and triggers no_data through the risk engine

Do not implement UI yet.
```

---

## Prompt 8 — Streamlit UI

Use only after data loader tests pass.

```text
Now build the first Streamlit UI in app.py.

Important:
- Keep app.py thin.
- Do not put business logic directly into app.py.
- Use functions from src/models.py, src/data_loader.py, src/risk_engine.py, src/time_utils.py, and src/recommendation.py.

Inputs:
- Origin station
- Destination station
- Planned arrival time
- Arrival deadline
- Trip type

Output:
- Risk level
- Recommended buffer
- Latest safe planned arrival
- Whether planned arrival is safe
- Customer-native recommendation text
- Confidence level
- Reasons
- Warnings
- Limitations

Add an honesty note:
"TrainBuffer v1 uses destination station reliability as the main historical signal. It does not predict exact train delays."

After implementation, tell me how to run:
streamlit run app.py

Do not add external APIs.
```

---

# 10. Final implementation order

Do not skip.

```text
1. Repo setup
2. Import tests
3. Domain models
4. Model tests
5. Risk engine
6. Risk engine tests
7. Deadline logic
8. Deadline tests
9. Trip type modifiers
10. Trip type tests
11. Recommendation text
12. Recommendation tests
13. Sample data loader
14. Data loader tests
15. Streamlit UI
16. Manual UI test
17. Optional advice logging
18. Optional weather flag
19. Optional construction flag
20. README update
21. Deployment
22. v1 release
```

---

# 11. What to avoid

Avoid these traps:

```text
- Starting with UI before core logic
- Asking Claude Code to build the whole app at once
- Adding live DB API too early
- Adding real construction data too early
- Working with the full DB dataset before sample data works
- Adding mobile app scope
- Adding ML before baseline rules are working
- Writing app.py as one huge file
- Moving to next feature while tests fail
```

---

# 12. Current PM decision

The first implementation sprint is:

```text
Sprint 1:
- Project setup
- Import tests
- Domain models
- Model tests
- Core risk engine
- Risk engine tests
```

Do not build the UI in Sprint 1.

The first working milestone is not a pretty app. It is a tested calculation engine.

