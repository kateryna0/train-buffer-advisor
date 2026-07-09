# 14 — Real Historical Data Source Decision (Phase 23a)

**Project:** TrainBuffer
**Phase:** 23a (research + recommendation only — no ingestion code)
**Goal:** choose a real-world source of Deutsche Bahn historical reliability data to replace the 5-row sample `data/sample_station_stats.csv`, feeding the existing `StationStats` model unchanged.
**Status:** awaiting approval before Phase 23b (ingestion).

---

## Constraints (from the task, restated)

```text
- Prefer free and legally usable sources.
- Do NOT make an unofficial or fragile source a hard dependency.
- Do NOT remove the existing sample CSV fallback.
- The pipeline must output the same StationStats shape so the risk engine
  does not change:
    station_name, sample_size, late_rate, cancellation_rate,
    avg_delay_minutes, p80_delay_minutes
- Runtime must not depend on a live feed being up (offline/batch ingest → CSV).
- Phase 23a is research + recommendation only.
```

## How the target model maps (applies to every candidate)

To produce one `StationStats` row per station we need per-stop records that we can group by station and aggregate:

```text
sample_size          = number of observed stops at the station
late_rate            = share of stops with arrival delay >= 6 min (DB's own
                       punctuality threshold) — must be tunable/documented
cancellation_rate    = share of stops flagged cancelled
avg_delay_minutes    = mean arrival delay (minutes)
p80_delay_minutes    = 80th percentile of arrival delay (minutes)
```

So a source is a strong fit only if it exposes, per stop: a **station identifier**, a **delay value (or planned vs actual time)**, and a **cancellation flag**.

---

## Candidate 1 — piebro `deutsche-bahn-data` (Hugging Face)  ✅ RECOMMEND

1. **Source & URL:** `https://github.com/piebro/deutsche-bahn-data` → dataset at `https://huggingface.co/datasets/piebro/deutsche-bahn-data`
2. **What it provides:** per-stop records collected 4×/day from DB's public Station Data + Timetables APIs, published as cleaned monthly **parquet** files (plus raw XML/JSON).
3. **Delays & cancellations:** Yes — `delay in minutes` and a `cancellation flag` per stop, with planned and actual arrival/departure times.
4. **Station names / IDs:** Yes — station name, XML name, and **EVA number** (stable station ID).
5. **License / terms:** Code MIT; **data CC BY 4.0 (attributed to Deutsche Bahn)** — attribution required, commercial use allowed.
6. **Free / key:** Free, **no account or API key**; downloaded as static files.
7. **Size & ingestion complexity:** Moderate. Monthly parquet; ~100 biggest stations from 2024-07, all stations more recently (through late 2025). Ingestion = read parquet with pandas → group by station → aggregate. Low complexity, and it's **batch/offline**, so no runtime coupling.
8. **Fit with StationStats:** Excellent — every field is directly derivable (see mapping above). `station_name` from the name field; `sample_size`/rates/percentiles from grouping stops.
9. **Main risks:** (a) It's a **third-party mirror**, not DB itself — could stop being updated; mitigated because we snapshot a fixed parquet into `data/` and don't depend on it at runtime. (b) Coverage is stops *observed at polled stations*, not a complete census — fine for reliability estimates but must be documented. (c) Attribution obligation (CC BY) — add a credit line.
10. **Recommendation:** **USE** as the primary source. It is free, legally clean, already aggregated to per-stop rows with exactly our fields, and fits a batch-ingest-to-CSV pipeline with zero runtime dependency.

---

## Candidate 2 — DB Timetables API (official, DB API Marketplace)  🟡 MAYBE (later, for freshness)

1. **Source & URL:** `https://developers.deutschebahn.com/db-api-marketplace/apis/product/timetables`
2. **What it provides:** planned timetable per station per hour + known real-time changes (delays, cancellations). The authoritative live source.
3. **Delays & cancellations:** Yes (this is DB's own real-time feed).
4. **Station names / IDs:** Yes (EVA numbers / station data API).
5. **License / terms:** Data **CC BY 4.0**; API usage governed by DB Marketplace terms.
6. **Free / key:** Free tier, but **requires an account + API key/subscription**.
7. **Size & ingestion complexity:** **High to build history ourselves** — it's a *live* API (changes are removed once obsolete), rate-limited (~20 req/min), so we'd have to run a poller for weeks/months to accumulate history. That is essentially what Candidate 1 already did for us.
8. **Fit with StationStats:** Good *once aggregated*, but only after we build and run our own collection pipeline.
9. **Main risks:** Rate limits; operational burden of continuous polling; key management; live-dependency temptation (violates our guardrail if used at runtime).
10. **Recommendation:** **MAYBE — defer.** Not for 23b. Good future option to *refresh* the dataset or add live freshness, but too heavy to bootstrap history now and risks a live dependency.

---

## Candidate 3 — Bahn-Vorhersage dataset (Uni Augsburg OPUS archive)  🟡 MAYBE (fallback)

1. **Source & URL:** `https://opus.bibliothek.uni-augsburg.de/opus4/frontdoor/index/index/docId/127213`
2. **What it provides:** an open research archive of most German train delays since **September 2021** (collected via the DB Timetable API).
3. **Delays & cancellations:** Yes (delay records; cancellations expected — needs confirmation).
4. **Station names / IDs:** Yes (station-level records).
5. **License / terms:** Academic open archive (needs exact license confirmation before use).
6. **Free / key:** Free download; no key.
7. **Size & ingestion complexity:** **Large** (multi-year, national). Higher storage/processing cost; format/schema needs verification.
8. **Fit with StationStats:** Likely good after aggregation, but schema and license must be verified first.
9. **Main risks:** Size/handling; unverified exact license and schema; heavier than we need for a prototype.
10. **Recommendation:** **MAYBE — hold as fallback.** Use only if Candidate 1 becomes unavailable or we need multi-year depth. Verify license/schema before adopting.

---

## Candidate 4 — gtfs.de GTFS + GTFS-Realtime  ❌ REJECT (wrong shape)

1. **Source & URL:** `https://gtfs.de/en/` (realtime: `https://realtime.gtfs.de/realtime-free.pb`)
2. **What it provides:** static GTFS timetables + a GTFS-Realtime stream (TripUpdates, ServiceAlerts) from the DELFI national dataset.
3. **Delays & cancellations:** Real-time only (via TripUpdates/alerts) — **no historical aggregates**.
4. **Station names / IDs:** Yes (GTFS stops).
5. **License / terms:** **CC BY-SA 4.0** (share-alike — copyleft obligation on derived data).
6. **Free / key:** Free.
7. **Size & ingestion complexity:** High — we'd have to continuously capture the RT stream to build history (same problem as Candidate 2), plus share-alike compliance.
8. **Fit with StationStats:** Poor without our own long-running collection.
9. **Main risks:** Share-alike license; no ready-made history; live-dependency temptation.
10. **Recommendation:** **REJECT** for historical reliability. (Fine as a future *live* signal, not as our historical dataset.)

---

## Candidate 5 — `v6.db.transport.rest` (unofficial REST wrapper)  ❌ REJECT (as data source)

1. **Source & URL:** `https://v6.db.transport.rest/`
2. **What it provides:** a friendly live wrapper over DB APIs (departures, trips, delays). Already used by TrainBuffer for the Phase 18 live delay check.
3. **Delays & cancellations:** Live only; **no historical aggregates**.
4. **Station names / IDs:** Yes.
5. **License / terms:** Unofficial community project; terms/uptime not guaranteed.
6. **Free / key:** Free, no key.
7. **Size & ingestion complexity:** N/A for history (would require self-polling).
8. **Fit with StationStats:** Poor (live, not historical).
9. **Main risks:** **Fragile / unofficial** — explicitly must not be a hard dependency per our guardrail.
10. **Recommendation:** **REJECT** as the historical data source. Keep it only where it already lives (optional live delay check, fail-closed).

---

## Candidate 6 — Statista / national monthly punctuality figures  ❌ REJECT

1. **Source & URL:** `https://www.statista.com/statistics/935040/deutsche-bahn-train-punctuality-germany/`
2. **What it provides:** national, monthly aggregate punctuality percentages.
3. **Delays:** Only a single national punctuality %, **not per-station**; no cancellation breakdown per station.
4. **Station names / IDs:** No.
5. **License / terms:** Proprietary / paywalled.
6. **Free / key:** Largely paywalled.
7. **Size & ingestion complexity:** Trivial but useless for our per-station model.
8. **Fit with StationStats:** **None** (no station dimension).
9. **Main risks:** Paywall; wrong granularity.
10. **Recommendation:** **REJECT.**

---

## Summary table

| # | Source | Delays | Cancel | Station ID | License | Free/no key | History ready | Fit | Verdict |
|---|--------|:---:|:---:|:---:|--------|:---:|:---:|:---:|--------|
| 1 | piebro deutsche-bahn-data (HF) | ✓ | ✓ | ✓ (EVA) | CC BY 4.0 | ✓ | ✓ | Excellent | **USE** |
| 2 | DB Timetables API (official) | ✓ | ✓ | ✓ | CC BY 4.0 | key needed | build yourself | Good later | MAYBE |
| 3 | Bahn-Vorhersage (OPUS) | ✓ | ? | ✓ | academic (verify) | ✓ | ✓ (large) | Good | MAYBE |
| 4 | gtfs.de GTFS-RT | RT only | RT only | ✓ | CC BY-SA | ✓ | build yourself | Poor | REJECT |
| 5 | v6.db.transport.rest | live | live | ✓ | unofficial | ✓ | ✗ | Poor | REJECT |
| 6 | Statista national | national % | ✗ | ✗ | paywall | ✗ | n/a | None | REJECT |

---

## Recommendation

**Adopt Candidate 1 (piebro `deutsche-bahn-data`, Hugging Face) as the primary historical source**, used strictly as an **offline batch input**:

```text
1. Download a fixed monthly parquet snapshot into data/ (committed or documented,
   with CC BY 4.0 attribution to Deutsche Bahn).
2. Phase 23b: a tested pure ingestion function reads the snapshot, groups by
   station, and writes data/station_stats.csv in the exact StationStats shape
   (late_rate threshold = arrival delay >= 6 min, documented and configurable).
3. Phase 23c: point STATION_STATS_PATH at the real CSV; if it is missing, fall
   back to the existing sample_station_stats.csv (fallback is NOT removed).
```

This satisfies every constraint: free, CC BY 4.0 (legally usable with attribution), not a live/fragile runtime dependency, sample-CSV fallback preserved, and output identical to today's `StationStats` so the risk engine, recommendation text, reliability board, and connection engine all stay unchanged.

**Deferred options:** DB Timetables API (Candidate 2) later for freshness/refresh; Bahn-Vorhersage OPUS (Candidate 3) as a fallback if Candidate 1 disappears or multi-year depth is needed.

---

## Open questions for approval

```text
- OK to adopt Candidate 1 as the primary source?
- Preferred scope for the first real dataset: the ~100 biggest stations, or all
  stations? (Biggest-100 is smaller and simpler for a first pass.)
- late_rate threshold: confirm 6 minutes (DB's punctuality definition), or set
  a different cutoff?
- Commit the parquet snapshot into the repo, or keep it out of git (in .gitignore)
  and document the download step? (Affects repo size.)
```

**Stop point:** no ingestion code until this source is approved (Phase 23b).
