"""Connection-mode calculations for v3 (Phase 20b onward).

Phase 20b: estimate the arrival delay of a single leg at its destination
station, reusing the existing historical risk engine per leg rather than
introducing a new risk model.
"""

from src.models import StationStats, TripLeg
from src.risk_engine import calculate_confidence, calculate_historical_risk


def estimate_leg_arrival_delay(
    leg: TripLeg, destination_stats: StationStats | None
) -> dict:
    """Estimate how late a leg is likely to arrive at its destination.

    Reuses the historical risk engine: the leg's destination station stats give
    a risk_level (via calculate_historical_risk) and a confidence_level (via
    calculate_confidence). The point and p80 delay estimates come from the
    station's historical avg / p80 delay minutes.

    Returns:
        {
            "station_name": str,          # the leg destination
            "has_data": bool,             # False when stats missing or too thin
            "risk_level": str,            # "Low"/"Medium"/"High" or "no_data"
            "confidence_level": str,
            "expected_delay_minutes": int,
            "p80_delay_minutes": int,
        }

    When there is no usable data (stats missing, or sample too small so
    confidence is "no_data"), delays are reported as 0 and has_data is False,
    so downstream connection logic can treat it neutrally rather than negative.
    """
    if destination_stats is None:
        return {
            "station_name": leg.destination_station,
            "has_data": False,
            "risk_level": "no_data",
            "confidence_level": "no_data",
            "expected_delay_minutes": 0,
            "p80_delay_minutes": 0,
        }

    confidence_level = calculate_confidence(destination_stats.sample_size)

    if confidence_level == "no_data":
        return {
            "station_name": leg.destination_station,
            "has_data": False,
            "risk_level": "no_data",
            "confidence_level": confidence_level,
            "expected_delay_minutes": 0,
            "p80_delay_minutes": 0,
        }

    risk_level = calculate_historical_risk(
        destination_stats.late_rate, destination_stats.cancellation_rate
    )

    return {
        "station_name": leg.destination_station,
        "has_data": True,
        "risk_level": risk_level,
        "confidence_level": confidence_level,
        "expected_delay_minutes": round(destination_stats.avg_delay_minutes),
        "p80_delay_minutes": round(destination_stats.p80_delay_minutes),
    }
