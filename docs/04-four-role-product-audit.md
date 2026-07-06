# 04 — Four-Role Product Audit

## Purpose

This document evaluates TrainBuffer from four professional perspectives:

1. Staff Engineer;
2. Engineering Manager;
3. Product Owner;
4. Business Analyst.

The goal is to identify whether the concept is relevant, buildable, useful, and measurable before implementation starts.

## Overall verdict

The idea is relevant and portfolio-strong, but it must be scoped tightly.

The strongest version is not a broad “AI delay predictor”. The strongest version is:

> **A transparent deadline-based pre-trip buffer advisor for important train journeys in Germany.**

The product is useful if it helps users translate a fixed arrival deadline into a latest safe planned train arrival time. It becomes much weaker if it only displays abstract delay probabilities or generic buffer minutes.

## Evaluation table

| Role | Main question | Current score | What is strong | What is missing | First improvement |
|---|---|---:|---|---|---|
| Staff Engineer | Can this be built, tested, and maintained? | 6/10 | Clear concept, public data, good fit for Python/Streamlit, explainable rule possible | No exact rule spec, no test cases, cancellation handling unclear, data aggregation risk | Write pure `risk_engine.py` spec and tests first |
| Engineering Manager | Can a beginner finish this into a demo? | 7/10 | Can be broken into v1/v1.5/v2, portfolio-friendly | Scope easily explodes into live APIs, ML, connections, legal FAQ | Freeze v1 DoD and reject extra features |
| Product Owner | Will users open this instead of existing tools? | 6/10 v1, 8/10 v1.5 | Real pain, strong “take earlier?” use case | DB Navigator and Bahn-Vorhersage already strong; value must be sharper | Focus on deadline-based important-trip buffer decision |
| Business Analyst | Can we prove it works and creates value? | 6/10 | Good KPI potential, measurable outcomes possible | No forecast→actual validation, no calibration metrics, no North Star | Log advice vs actual outcome from day one |

## Staff Engineer audit

### What works

- Python and Streamlit are appropriate for a small portfolio demo.
- A transparent rule-based engine is easier to test than ML.
- Precomputed station aggregates avoid loading a huge dataset at request time.
- Separating the decision engine from UI will make the project interview-ready.

### Critical gaps

1. **No exact rule specification**

   Without thresholds and formulas, Claude Code will invent logic. The app needs explicit Low/Medium/High thresholds, buffer mapping, confidence levels, weather modifiers, and fallback behavior.

2. **Cancellations must be separate**

   A canceled train is not “a very long delay”. It is a different event type. The model should track delay risk and cancellation risk separately.

3. **Confidence must be statistical, not decorative**

   A station with 8 observations must not receive the same confidence as a station with 500 observations.

4. **Engine must be separated from Streamlit**

   Core function should be testable without UI:

   ```python
   calculate_recommendation(input, station_stats, weather_flags) -> Recommendation
   ```

5. **Data versioning needed**

   Historical aggregates should include generation date, source version, row count, coverage, and assumptions.

### Staff Engineer recommendation

Build order:

1. define schemas;
2. build risk engine;
3. write tests;
4. connect to small sample data;
5. add Streamlit UI.

## Engineering Manager audit

### What works

The project is strong as a portfolio build because it combines:

- product discovery;
- data sourcing;
- API usage;
- rule logic;
- UX explanation;
- deployment;
- prompt-engineered AI-assisted development.

### Critical gaps

1. **Scope is too large if not controlled**

   Historical data + weather + live train API + construction data + transfer mode + notifications is too much for v1.

2. **v1 has to be demoable, not complete**

   The goal is a working public demo, not a production-grade rail platform.

3. **Dependencies are fragile**

   Unofficial APIs and community datasets can break. The project needs fallback behavior and documented assumptions.

4. **Definition of Done missing**

   Without DoD, the project will never feel finished.

### Engineering Manager recommendation

v1 must include only:

- station reliability lookup;
- weather modifier;
- risk level;
- buffer recommendation;
- explanation card;
- confidence badge;
- no-data state;
- README and deployment.

Everything else goes to roadmap.

## Product Owner audit

### What works

The problem is emotionally meaningful. Users care about train delays when the cost of being late is high. “What is my latest safe planned arrival?” is a better product question than “Will my train be delayed?”

### Critical gaps

1. **Moment of use must be sharper**

   The product is not for all train journeys. It is for pre-trip planning before important journeys.

2. **DB Navigator cannot be ignored**

   Users already use DB Navigator for tickets and live status. The app must complement, not compete directly.

3. **Bahn-Vorhersage is a direct competitor**

   The product must differentiate from reliability scoring by offering an explanation and buffer recommendation.

4. **Action must be concrete**

   “Risk is 27%” is not enough. The output must say:

   - normal connection OK;
   - add 15 minutes;
   - take one earlier train;
   - not enough data, check official live info.

### Product Owner recommendation

Product promise:

> “Before an important train trip, know whether your planned connection is safe enough or whether to take one earlier.”

## Business Analyst audit

### What works

The product can be measured well if designed correctly.

Potential metrics:

- recommendation accuracy;
- calibration error;
- coverage rate;
- no-data rate;
- over-buffer rate;
- under-buffer rate;
- user action taken.

### Critical gaps

1. **No validation loop**

   If the app claims transparency, it must log recommendations and compare them with actual outcomes later.

2. **No North Star metric**

   Recommended:

   > Percentage of trips where actual delay was covered by the recommended buffer.

3. **No defined success threshold**

   Example: v1 alpha success could be “80% of evaluated recommendations did not under-buffer the actual delay.”

4. **No cost/benefit framing**

   The product should balance two bad outcomes:

   - too little buffer → user is late;
   - too much buffer → user wastes time.

### Business Analyst recommendation

Add `advice_log.csv` or similar from the first build, even if actual outcomes are added manually in v1.

## Cross-role critical issues

| Issue | Staff Engineer | Engineering Manager | Product Owner | Business Analyst | Priority |
|---|---|---|---|---|---|
| No exact scoring rule | Critical | Critical | Medium | High | P0 |
| No advice-vs-actual validation | High | High | Critical | Critical | P0 |
| Undefined user decision | Medium | Medium | Critical | High | P0 |
| Cancellations not separate | Critical | Medium | High | Critical | P0 |
| Scope too broad | High | Critical | High | Medium | P0 |
| No confidence/min-sample logic | Critical | Medium | Medium | Critical | P0 |
| No legal/privacy note | Medium | High | Medium | Critical | P1 |
| No competitor positioning | Low | Medium | Critical | High | P1 |
| No test strategy | Critical | High | Low | Medium | P1 |
| No prompt-engineering proof | Medium | Medium | Medium | Medium | P1 |

## Final recommendation

Do the project, but keep v1 brutally focused.

Do not build:

- ML prediction;
- live disruption check;
- transfer mode;
- construction overlay;
- accounts;
- notifications;
- full legal assistant.

Build:

> A clear, explainable, deployed demo that answers one important question: should I take an earlier train?
