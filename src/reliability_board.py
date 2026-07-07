"""Reliability board: aggregate views over station statistics (v2).

Pure functions only — the Streamlit page renders whatever these return, so the
rankings stay testable and are never hardcoded in the UI.
"""

from src.models import StationStats

DEFAULT_TOP_N = 3


def compute_reliability_rankings(
    stats_by_station: dict[str, StationStats], top_n: int = DEFAULT_TOP_N
) -> dict:
    """Return the worst-N stations by late_rate and by cancellation_rate.

    Args:
        stats_by_station: mapping of station_name -> StationStats
            (as produced by src.data_loader.load_station_stats).
        top_n: how many stations to include in each ranking.

    Returns:
        {
            "worst_by_late_rate": [(station_name, late_rate), ...],
            "worst_by_cancellation_rate": [(station_name, cancellation_rate), ...],
        }

    Ordering is highest-rate-first. Ties are broken deterministically by
    station_name (ascending), so the same input always yields the same output.
    An empty input yields empty rankings without error.
    """

    def ranked(rate_attr: str) -> list[tuple[str, float]]:
        pairs = [
            (stats.station_name, getattr(stats, rate_attr))
            for stats in stats_by_station.values()
        ]
        # Sort by rate descending, then station name ascending for tie-breaking.
        pairs.sort(key=lambda pair: (-pair[1], pair[0]))
        return pairs[:top_n]

    return {
        "worst_by_late_rate": ranked("late_rate"),
        "worst_by_cancellation_rate": ranked("cancellation_rate"),
    }
