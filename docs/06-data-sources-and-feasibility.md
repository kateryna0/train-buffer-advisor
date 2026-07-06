# 06 — Data Sources and Feasibility

## Purpose

This document evaluates whether the product can be built with free/public data and identifies the risks of each data source.

## Data need overview

| Need | Required for v1? | Candidate source |
|---|---:|---|
| Historical delay data | Yes | Public DB delay datasets, HuggingFace/Kaggle/Bahn-Vorhersage data |
| Station names and identifiers | Yes | DB station metadata / dataset fields |
| Weather forecast | Yes | Open-Meteo or Bright Sky/DWD |
| Live train status | No, v1.5 | DB Timetables API or db.transport.rest |
| Construction/disruption data | P1 optional for v1, otherwise v1.5/v2 | DB/strecken-info/other public sources |
| Passenger rights information | No, optional | Official DB FAQ |

## Historical delay data

### Candidate source: HuggingFace DB delay dataset

The previously selected dataset includes useful fields such as station names, EVA identifiers, train name, final destination, timestamp, delay minutes, and cancellation flag.

### Why it fits v1

v1 does not need raw live records at runtime. It can use precomputed station-level statistics:

- destination station;
- total observations;
- late arrivals;
- late rate;
- cancellation count/rate;
- median delay;
- p80/p90 delay;
- last updated date.

### Main risk

The raw dataset can be very large. It should not be loaded directly in Streamlit.

### Mitigation

Precompute a compact table offline:

```text
station_id
station_name
n_observations
late_count
late_rate
cancel_count
cancel_rate
median_delay
p80_delay
p90_delay
data_start
data_end
generated_at
source_version
```

## Weather data

### Option A: Open-Meteo

Open-Meteo offers a free API with no key required. Non-commercial use has free limits and attribution is required under CC BY 4.0.

### Option B: Bright Sky / DWD

Bright Sky is a free JSON API for DWD open weather data. No API key is required, but DWD terms apply.

### Weather fields needed for v1

| Field | Why it matters |
|---|---|
| Wind gusts | Storm/wind can affect rail operations |
| Temperature | Extreme heat can affect infrastructure |
| Snow / precipitation | Winter conditions can add risk |
| Weather warnings | Later improvement |

### Recommended v1 approach

Use weather only as a **modifier**, not as the core predictor.

Weather should add a small buffer or reason flag. It should not dominate historical reliability in v1.

## Live train data

### Not required for v1

Live data is valuable, but it would increase complexity significantly. It belongs to v1.5.

### Candidate source: db.transport.rest

This API can provide real-time data from upstream DB mobile app sources, without authentication, with documented rate limits.

### Candidate source: DB Timetables API

The official DB API Marketplace offers timetable APIs for stations and dynamic changes. Terms and limits must be checked before use.

### Risk

Live APIs can change, rate-limit, or fail. If v1 depends on live data, the app becomes more fragile.

### Recommendation

Use live data only in v1.5 after v1 is shipped.

## Construction / disruption data

External feedback highlighted that construction and disruption data could be an important risk factor in Germany because rail construction is frequent and can materially affect punctuality.

Product decision for v1:

```text
P1 optional if simple and stable. Not a v1 blocker.
```

Implementation rule:

- If a low-complexity data source can provide a simple construction/disruption flag, include it as a warning and small buffer modifier.
- If it requires complex live integration, scraping, uncertain terms, or unreliable parsing, keep it out of v1 and show a limitation note.

TrainBuffer must not become a construction-data integration project before the basic deadline-based buffer advisor works.

## Feasibility assessment

| Layer | Feasible for v1? | Complexity | Risk | Recommendation |
|---|---:|---:|---:|---|
| Historical station reliability | Yes | Medium | Medium | Core v1 |
| Weather forecast | Yes | Low/Medium | Low | Core v1 modifier |
| Live train delay | Later | Medium/High | High | v1.5 |
| Construction/disruption flag | Optional | Medium/High | High | P1 optional v1; otherwise v1.5/v2 |
| Transfer prediction | Later | High | High | v3 |

## Data quality risks

| Risk | Impact | Mitigation |
|---|---|---|
| Low sample size for small stations | False precision | Confidence badge and no-data threshold |
| Dataset not fully current | Outdated recommendations | Show data date and version |
| Cancellations mixed with delays | Wrong risk estimate | Separate cancellation rate |
| Station name mismatches | Failed lookup | Use station IDs where possible |
| Weather forecast unavailable | Missing modifier | Continue with historical data only |
| API rate limit | App failure | Cache weather requests or degrade gracefully |
| Construction/disruption source too complex | Scope creep | Keep as P1 optional or move to v1.5/v2 |

## Data governance requirements

Each aggregate dataset should include metadata:

```text
dataset_name
source_url
generated_at
data_start
data_end
row_count_raw
row_count_used
transformation_script_version
known_limitations
```

## Sources

- HuggingFace Deutsche Bahn dataset: https://huggingface.co/datasets/piebro/deutsche-bahn-data
- Bahn-Vorhersage open data: https://bahnvorhersage.de/open-data/raw-data/
- Open-Meteo API: https://open-meteo.com/
- Open-Meteo terms: https://open-meteo.com/en/terms
- Bright Sky API docs: https://brightsky.dev/docs/
- db.transport.rest v6 docs: https://v6.db.transport.rest/
- DB API Marketplace Timetables: https://developers.deutschebahn.com/db-api-marketplace/apis/product/timetables
