"""Station statistics loading."""

import os

import pandas as pd

from src.models import StationStats


def resolve_station_stats_path(preferred_path: str, fallback_path: str) -> str:
    """Return preferred_path if it exists, else fallback_path.

    Lets the app use real aggregated data (data/station_stats.csv) when present
    while always degrading to the committed sample dataset if it is missing, so
    the app never fails to load its station data.
    """
    return preferred_path if os.path.exists(preferred_path) else fallback_path


def load_station_stats(path: str) -> dict[str, StationStats]:
    df = pd.read_csv(path)
    stats = {}
    for _, row in df.iterrows():
        stats[row["station_name"]] = StationStats(
            station_name=row["station_name"],
            sample_size=int(row["sample_size"]),
            late_rate=float(row["late_rate"]),
            cancellation_rate=float(row["cancellation_rate"]),
            avg_delay_minutes=float(row["avg_delay_minutes"]),
            p80_delay_minutes=float(row["p80_delay_minutes"]),
        )
    return stats


def get_station_stats(
    destination_station: str, stats: dict[str, StationStats]
) -> StationStats | None:
    return stats.get(destination_station)
