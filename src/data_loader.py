"""Station statistics loading."""

import pandas as pd

from src.models import StationStats


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
