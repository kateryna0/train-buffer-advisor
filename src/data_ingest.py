"""Offline ingestion of real DB historical per-stop data into StationStats.

Turns per-stop records (from the piebro/deutsche-bahn-data Hugging Face dataset
— DB Timetables data, CC BY 4.0) into the exact StationStats shape the risk
engine already consumes. See docs/14-real-historical-data-source-decision.md.

This module is a BATCH / OFFLINE step. It is intentionally NOT imported by
app.py: the app reads the generated CSV, never this pipeline, so there is no
runtime dependency on the dataset or a parquet engine. Wiring the generated CSV
into the app is Phase 23c.

Aggregation per station (documented, tunable):
    sample_size        = number of observed stops for the station
    cancellation_rate  = cancelled stops / all stops
    late_rate          = share of NON-cancelled stops (with a delay value)
                         whose arrival delay >= late_threshold_minutes
    avg_delay_minutes  = mean arrival delay over those stops
    p80_delay_minutes  = 80th percentile of arrival delay over those stops

Delay metrics use non-cancelled stops only (a cancelled train has no meaningful
arrival delay); cancellations are captured separately via cancellation_rate.
"""

import pandas as pd

from src.models import StationStats

# DB's own punctuality definition: an arrival is "late" at >= 6 minutes.
DEFAULT_LATE_THRESHOLD_MINUTES = 6

# Default column names. The exact piebro schema is confirmed when the real
# snapshot is downloaded (Phase 23c); override via the *_col arguments.
DEFAULT_STATION_COL = "station_name"
DEFAULT_DELAY_COL = "arrival_delay_minutes"
DEFAULT_CANCELLED_COL = "cancelled"

STATION_STATS_COLUMNS = [
    "station_name",
    "sample_size",
    "late_rate",
    "cancellation_rate",
    "avg_delay_minutes",
    "p80_delay_minutes",
]


def read_stops(path) -> pd.DataFrame:
    """Read per-stop records from a .parquet (real snapshot) or .csv (fixture).

    Parquet reading needs a parquet engine (e.g. pyarrow) installed locally for
    the offline run; the test suite uses CSV fixtures so it needs neither.
    """
    text_path = str(path)
    if text_path.endswith(".parquet"):
        return pd.read_parquet(path)
    if text_path.endswith(".csv"):
        return pd.read_csv(path)
    raise ValueError(f"Unsupported input format for {text_path!r}; use .parquet or .csv")


def aggregate_station_stats(
    stops: pd.DataFrame,
    *,
    station_col: str = DEFAULT_STATION_COL,
    delay_col: str = DEFAULT_DELAY_COL,
    cancelled_col: str = DEFAULT_CANCELLED_COL,
    late_threshold_minutes: int = DEFAULT_LATE_THRESHOLD_MINUTES,
    min_sample_size: int = 1,
    top_n: int | None = None,
) -> list[StationStats]:
    """Aggregate per-stop records into one StationStats per station.

    Stations with fewer than `min_sample_size` observed stops are dropped.
    Results are sorted by sample_size descending (then station name), so
    `top_n` keeps the busiest stations first.
    """
    results: list[StationStats] = []

    for station_name, group in stops.groupby(station_col):
        sample_size = int(len(group))
        if sample_size < min_sample_size:
            continue

        cancelled = group[cancelled_col].fillna(False).astype(bool)
        cancellation_rate = round(float(cancelled.mean()), 4)

        delays = group.loc[~cancelled, delay_col].dropna().astype(float)
        if len(delays) > 0:
            late_rate = round(float((delays >= late_threshold_minutes).mean()), 4)
            avg_delay = round(float(delays.mean()), 1)
            p80_delay = float(round(float(delays.quantile(0.8))))
        else:
            late_rate = 0.0
            avg_delay = 0.0
            p80_delay = 0.0

        results.append(
            StationStats(
                station_name=str(station_name),
                sample_size=sample_size,
                late_rate=late_rate,
                cancellation_rate=cancellation_rate,
                avg_delay_minutes=avg_delay,
                p80_delay_minutes=p80_delay,
            )
        )

    results.sort(key=lambda s: (-s.sample_size, s.station_name))
    if top_n is not None:
        results = results[:top_n]
    return results


def write_station_stats_csv(stats: list[StationStats], path) -> None:
    """Write StationStats rows to CSV in the same shape as the sample data."""
    frame = pd.DataFrame(
        [
            {
                "station_name": s.station_name,
                "sample_size": s.sample_size,
                "late_rate": s.late_rate,
                "cancellation_rate": s.cancellation_rate,
                "avg_delay_minutes": s.avg_delay_minutes,
                "p80_delay_minutes": s.p80_delay_minutes,
            }
            for s in stats
        ],
        columns=STATION_STATS_COLUMNS,
    )
    frame.to_csv(path, index=False)


def build_station_stats_csv(
    input_path, output_path, **aggregate_kwargs
) -> list[StationStats]:
    """End-to-end offline step: read stops -> aggregate -> write StationStats CSV."""
    stops = read_stops(input_path)
    stats = aggregate_station_stats(stops, **aggregate_kwargs)
    write_station_stats_csv(stats, output_path)
    return stats
