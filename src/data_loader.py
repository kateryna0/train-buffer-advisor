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


def station_names(stats: dict[str, StationStats]) -> list[str]:
    """Sorted list of station names available in the loaded stats.

    Used to populate searchable station pickers in the UI so the user chooses
    from valid stations instead of typing exact names.
    """
    return sorted(stats.keys())


def default_option_index(options: list[str], preferred: str) -> int:
    """Index of `preferred` in `options`, or 0 if it is not present.

    Lets the UI request a sensible default station without crashing when that
    station is absent from the current dataset (e.g. sample vs real data).
    """
    return options.index(preferred) if preferred in options else 0
