# 11 — Feedback and Decisions

## Purpose

This document records external feedback and the resulting product decisions. It shows that TrainBuffer is being developed through product discovery, not just coding.

## Feedback source

External reviewer familiar with the initial project idea.

Date: 2026-07-06

## High-level feedback summary

The reviewer understood the concept and liked the v1 scope. The main recommendation was to make the product more customer-native and deadline-based.

Instead of centering the product around:

```text
Recommended buffer: 30 minutes
```

TrainBuffer should center around:

```text
When do you absolutely need to arrive?
```

Then calculate:

```text
latest_safe_planned_arrival_time = deadline - recommended_buffer
```

## Feedback → decision log

| Feedback | Decision | Reason |
|---|---|---|
| Add a deadline-based flow: “I need to be there by 10:00. How early should I plan to arrive?” | **Accepted** | This makes the product more useful and more customer-native than a generic risk score. |
| Add input: “When do you absolutely need to arrive?” | **Accepted** | This becomes the central v1 input. |
| Calculate latest safe planned arrival time as deadline minus buffer | **Accepted** | This turns buffer minutes into a concrete planning action. |
| Add trip type: Airport, Interview/exam, Government/visa/medical appointment, Transfer, Normal | **Accepted** | This improves personalization without heavy technical complexity. |
| Make recommendation text more concrete and human | **Accepted** | Output should say what to do, not only show a number. |
| Consider construction/disruption data in v1 | **Partially accepted** | Valuable, but could create scope risk. It becomes P1 optional for v1 if simple; otherwise v1.5/v2. |
| Watch overlap with DB Vorhersage | **Accepted as positioning risk** | TrainBuffer must differentiate as a deadline-based buffer advisor, not a reliability score/prediction app. |
| Consider alternative project idea if overlap is too high | **Deferred** | The current project remains active. Alternative ideas are stored in a separate backlog for later. |

## Product changes made

### 1. Product name finalized

Old working name:

```text
TrainBuffer
```

Final name:

```text
TrainBuffer
```

### 2. Core question changed

Previous core question:

```text
Should I trust this train connection for an important trip, or should I take one earlier?
```

New core question:

```text
I need to be at my destination by a specific time. What is the latest safe planned train arrival time, and should I take one earlier?
```

### 3. v1 inputs changed

Added:

- arrival deadline;
- planned train arrival time;
- trip type.

Trip type options:

- Normal trip;
- Airport;
- Interview/exam;
- Government/visa/medical appointment;
- Transfer to another train.

### 4. v1 outputs changed

Added:

- latest safe planned arrival time;
- planned arrival assessment;
- customer-native recommendation text;
- trip-type-specific warning/logic.

### 5. Construction/disruption data decision

Construction/disruption data is useful but not allowed to block v1.

Decision:

```text
P1 optional in v1 if simple, stable, and low-complexity.
Otherwise move to v1.5/v2 and show a clear limitation note.
```

## Updated positioning

TrainBuffer is not:

```text
another delay prediction app
```

TrainBuffer is:

```text
a deadline-based buffer advisor for important train trips in Germany
```

## New v1 success definition

v1 is successful if a user can answer:

```text
I need to arrive by 10:00. What is the latest safe train arrival I should choose?
```

and receive:

- a buffer recommendation;
- latest safe planned arrival time;
- action recommendation;
- explanation;
- confidence level;
- clear limitations.
