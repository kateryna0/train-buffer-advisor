# 08 — Legal, Privacy, and Compliance Notes

## Purpose

This document identifies legal/privacy/compliance risks for a portfolio version of TrainBuffer. It is not legal advice. The goal is to make the project professional enough for GitHub and DACH job applications.

## Scope of v1

v1 should be privacy-light:

- no login;
- no user accounts;
- no saved personal profiles;
- no push notifications;
- no exact user tracking;
- no sale or sharing of user data;
- no sensitive personal data collection.

## GDPR risk

Even simple trip queries can become personal data if they are linked to an identifiable person. A route plus date/time plus IP address or persistent identifier can reveal patterns about someone’s movement.

### v1 mitigation

| Risk | Mitigation |
|---|---|
| Route query and arrival deadline could reveal travel behavior | Do not store user-identifiable logs |
| IP address in custom logs | Do not log IP at app level |
| User profiles | Do not create accounts in v1 |
| Analytics cookies | Avoid analytics or use privacy-friendly/no-cookie approach |
| Saved favorites | Out of scope for v1 |

## Recommended privacy note for app footer

```text
Privacy note: This demo does not require login and does not create user profiles. Route queries are used only to generate the current recommendation. If recommendation logging is enabled, logs should be anonymized and stored without personal identifiers.
```

## Recommendation logging

The product should eventually log advice vs actual outcome for validation, but this should be designed carefully.

### Safe v1 logging schema

```text
timestamp_rounded_to_day
origin_station_id
destination_station_id
travel_date
travel_hour_bucket
arrival_deadline_hour_bucket
risk_level
recommended_buffer
latest_safe_planned_arrival_bucket
trip_type
confidence
weather_flags
actual_delay_optional
was_canceled_optional
```

Avoid:

- exact timestamp of query;
- exact arrival deadline if logging is not needed;
- user ID;
- IP address;
- browser fingerprint;
- email;
- free-text notes that may contain personal info.

## Data attribution

### Open-Meteo

Open-Meteo requires attribution under CC BY 4.0 for free/non-commercial use. Add attribution in README and app footer.

Suggested wording:

```text
Weather data by Open-Meteo.com, used under CC BY 4.0 attribution requirements.
```

### Bright Sky / DWD

Bright Sky provides access to DWD open weather data and notes that DWD terms apply.

Suggested wording:

```text
Weather data may be sourced from Bright Sky / Deutscher Wetterdienst open data. DWD terms of use apply.
```

### Deutsche Bahn / rail data

For any DB-related dataset or API, check the source license and terms. If using a community dataset, attribute the dataset and link to its source.

Suggested wording:

```text
Historical rail-delay aggregates are derived from publicly available Deutsche Bahn-related datasets. This project is an independent portfolio demo and is not affiliated with Deutsche Bahn.
```

## API terms and fragility

### Unofficial APIs

If using db.transport.rest or another unofficial wrapper, clearly state:

- it may change;
- it may have rate limits;
- it has no SLA;
- it should not be treated as official DB infrastructure.

### Official DB APIs

If using DB API Marketplace, check:

- API access requirements;
- terms of use;
- rate limits;
- allowed use cases;
- whether public deployment is allowed.

## Disclaimer

The app should not promise arrival certainty.

Recommended disclaimer:

```text
This app provides a planning recommendation based on historical data and weather signals. It does not guarantee punctual arrival and does not replace official Deutsche Bahn travel information. Always check DB Navigator or official station information before departure.
```

## Passenger rights boundary

The app should avoid giving legal advice about compensation, Zugbindung, refunds, taxi, or hotel reimbursement.

If included later, use only official links and neutral wording:

```text
For passenger rights and ticket validity, check the official Deutsche Bahn Fahrgastrechte information.
```

## Compliance checklist before public deployment

| Item | Required for v1? | Status |
|---|---:|---|
| Privacy note in README | Yes | To do |
| App footer disclaimer | Yes | To do |
| Open-Meteo attribution | If used | To do |
| DWD/Bright Sky attribution | If used | To do |
| DB dataset attribution | Yes | To do |
| No user login | Yes | Planned |
| No personal profiles | Yes | Planned |
| No raw IP logging | Yes | Planned |
| No legal advice claims | Yes | Planned |
| API terms reviewed | Yes | To do |

## Sources

- EU GDPR personal data explanation: https://commission.europa.eu/law/law-topic/data-protection/data-protection-explained_en
- Open-Meteo terms: https://open-meteo.com/en/terms
- Open-Meteo licence: https://open-meteo.com/en/licence
- Bright Sky docs: https://brightsky.dev/docs/
- DB API Marketplace: https://developers.deutschebahn.com/db-api-marketplace/apis/frontpage
- DB passenger rights FAQ: https://www.bahn.de/faq/pk/service/buchung/fahrgastrechte
