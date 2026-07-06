# 07 — Risk Rule Specification

## Purpose

This document defines the transparent v1 rule for converting historical reliability, weather signals, trip type, and deadline information into a risk level, buffer recommendation, latest safe planned arrival time, confidence level, and explanation.

This is intentionally **not** machine learning. The goal of v1 is a readable, testable baseline.

## Core design principle

> The rule must be simple enough to explain in the UI and test in unit tests.

## Core formula

```text
latest_safe_planned_arrival = arrival_deadline - recommended_buffer
```

This is the most important output. Users care about their deadline, not only abstract buffer minutes.

## Definitions

### Late arrival

A train arrival is considered late if:

```text
delay_in_min >= 6
```

This follows the common DB punctuality convention where trains delayed by less than six minutes are considered punctual.

### Performed arrival

A performed arrival is an arrival that was not canceled.

### Cancellation

A cancellation is counted separately and never converted into delay minutes.

### Planned arrival assessment

If the user provides a planned train arrival time:

```text
planned_arrival_is_safe = planned_arrival_time <= latest_safe_planned_arrival
```

If the planned arrival time is later than the latest safe planned arrival, the app recommends choosing an earlier arrival.

## Input data

The rule receives:

```text
station_stats = {
  destination_station,
  n_observations,
  n_performed,
  late_count,
  late_rate,
  cancel_count,
  cancel_rate,
  median_delay,
  p80_delay,
  p90_delay,
  data_start,
  data_end
}

weather_flags = {
  strong_wind,
  extreme_heat,
  snow_or_ice,
  heavy_precipitation
}

optional_disruption_flags = {
  known_construction_or_disruption
}

trip_context = {
  origin_station,
  destination_station,
  travel_date,
  arrival_deadline,
  planned_arrival_time,
  trip_type
}
```

## Confidence levels

| Confidence | Condition | UI wording |
|---|---:|---|
| High | `n_performed >= 200` | Strong historical base |
| Medium | `50 <= n_performed < 200` | Moderate historical base |
| Low | `20 <= n_performed < 50` | Thin historical base |
| No data | `n_performed < 20` | Not enough historical data |

If confidence is “No data”, the app must not produce a numeric risk recommendation.

## Base risk bands

Based on historical late rate:

| Risk | Late rate | Meaning |
|---|---:|---|
| Low | `< 15%` | Most arrivals were punctual |
| Medium | `15%–30%` | Noticeable delay risk |
| High | `> 30%` | Delay risk is meaningfully elevated |

## Cancellation override

Cancellation risk is separate from late risk.

| Cancel rate | Treatment |
|---|---|
| `< 2%` | Mention only if relevant |
| `2%–5%` | Add reason: elevated cancellation signal |
| `> 5%` | Upgrade risk by one level, max High |

Rationale: a canceled train breaks the trip more severely than a small delay.

## Weather modifier

Weather is a modifier, not the main predictor.

| Weather flag | Buffer addition | Reason text |
|---|---:|---|
| Strong wind | +10 min | Strong wind may increase operational disruption risk |
| Extreme heat | +5 min | Extreme heat can affect rail infrastructure |
| Snow or ice | +10 min | Winter conditions may increase disruption risk |
| Heavy precipitation | +5 min | Heavy precipitation may add minor operational risk |

Maximum weather addition in v1:

```text
max_weather_buffer = 15 minutes
```

## Optional construction/disruption modifier

Construction and disruption data can improve relevance, but it must not block v1.

| Flag | Treatment |
|---|---|
| No source available | Do not include; show limitation |
| Simple known construction/disruption flag available | Add reason and +10 min buffer |
| Detailed live disruption source available | Move to v1.5/v2, not v1 core |

Suggested v1 rule if implemented:

```text
construction_buffer = 10 if known_construction_or_disruption else 0
max_construction_buffer = 10
```

## Base buffer by risk

| Risk | Base buffer |
|---|---:|
| Low | 10 min |
| Medium | 20 min |
| High | 35 min |

## Trip type modifier

Trip type replaces the previous generic “trip importance” field. It makes the recommendation feel tailored without heavy complexity.

| Trip type | Buffer adjustment | Action sensitivity |
|---|---:|---|
| Normal trip | +0 min | Less conservative |
| Airport | +25 min | Strongly conservative; airport processing not included |
| Interview/exam | +20 min | Conservative |
| Government/visa/medical appointment | +20 min | Conservative |
| Transfer to another train | +15 min | Warn: transfer reliability unsupported in v1 |

## Final buffer calculation

```text
base_buffer = buffer_from_risk(late_rate)
weather_buffer = min(sum(weather_modifiers), 15)
construction_buffer = 10 if known_construction_or_disruption else 0
trip_type_buffer = trip_type_modifier(trip_type)
raw_buffer = base_buffer + weather_buffer + construction_buffer + trip_type_buffer
final_buffer = min(round_to_nearest_5(raw_buffer), max_final_buffer)
latest_safe_planned_arrival = arrival_deadline - final_buffer
```

Suggested v1 cap:

```text
max_final_buffer = 75 minutes
```

If the rule would exceed the cap, the UI should recommend taking an earlier train rather than showing an exaggerated exact number.

## Action mapping

| Risk | Normal trip | Airport | Interview/exam | Government/visa/medical | Transfer |
|---|---|---|---|---|---|
| Low | Planned arrival likely okay if before safe threshold | Add conservative airport rail buffer | Add buffer | Add buffer | Warn: transfer mode unsupported |
| Medium | Add buffer | Take one earlier train if possible | Take one earlier train if possible | Take one earlier train if possible | Warn and check DB Navigator |
| High | Take one earlier train | Strongly take one earlier train | Strongly take one earlier train | Strongly take one earlier train | Avoid tight transfer |
| No data | Plan conservatively | Plan very conservatively | Plan conservatively | Plan conservatively | Do not rely on estimate |

## Output schema

```python
Recommendation = {
    "risk_level": "Low | Medium | High | No data",
    "late_rate": float | None,
    "cancel_rate": float | None,
    "buffer_minutes": int | None,
    "arrival_deadline": datetime,
    "latest_safe_planned_arrival": datetime | None,
    "planned_arrival_time": datetime | None,
    "planned_arrival_is_safe": bool | None,
    "trip_type": str,
    "action": str,
    "confidence": "High | Medium | Low | No data",
    "reasons": list[str],
    "limitations": list[str],
    "sources": list[str]
}
```

## Explanation generation rules

The explanation should always include:

1. historical late rate reason;
2. sample size/confidence reason;
3. cancellation note if elevated;
4. weather note if any flag is active;
5. trip type reason;
6. deadline reason;
7. construction/disruption note if implemented or limitation if not;
8. v1 limitation note.

Example:

```text
Your planned arrival at 09:40 is risky for an interview/exam. For a 10:00 deadline, TrainBuffer recommends a 45-minute rail buffer, so your latest safe planned arrival is 09:15. This is based mainly on historical arrivals at Berlin Hbf: 27% of performed arrivals were at least 6 minutes late. The estimate has medium confidence because it is based on 86 historical arrivals. Strong wind is forecast near the destination, so the buffer was increased. v1 does not include live disruptions, so check DB Navigator before departure.
```

## No-data rule

If `n_performed < 20`, output:

```text
Risk: Not enough data
Buffer: none
Latest safe planned arrival: cannot calculate reliably
Action: Plan conservatively and check official live information.
```

The app must not invent a percentage.

## Unit test cases

| Test | Input | Expected |
|---|---|---|
| Low risk normal | late_rate 0.10, n 250, normal, no weather, deadline 10:00 | Low, 10 min, latest safe 09:50 |
| Medium interview | late_rate 0.22, n 120, interview/exam, no weather, deadline 10:00 | Medium, 40 min, latest safe 09:20 |
| Medium interview + wind | late_rate 0.22, n 120, interview/exam, wind, deadline 10:00 | Medium, 50 min, latest safe 09:10 |
| High airport | late_rate 0.35, n 300, airport, wind, deadline 10:00 | High, conservative buffer, latest safe calculated |
| Planned arrival unsafe | latest safe 09:15, planned arrival 09:40 | planned_arrival_is_safe = False |
| Planned arrival safe | latest safe 09:15, planned arrival 09:05 | planned_arrival_is_safe = True |
| No data | n 8 | No data, no numeric late rate displayed |
| Cancellation upgrade | late_rate 0.12, cancel_rate 0.06 | upgraded risk |
| Weather cap | multiple weather flags | weather addition <= 15 |
| Transfer trip | trip_type transfer | warning that transfer reliability is unsupported |

## Open decision before implementation

Decide whether the first prototype asks for:

1. only deadline, then gives “latest safe planned arrival”; or
2. deadline + planned arrival time, then judges whether the chosen connection is safe.

Recommended v1 choice: use both. Planned arrival time should be optional but strongly encouraged.
