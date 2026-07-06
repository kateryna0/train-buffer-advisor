"""Risk and buffer calculation engine."""

from src.models import BufferRecommendation, StationStats, TripInput

RISK_LEVELS = ["Low", "Medium", "High"]

BASE_BUFFER_MINUTES = {
    "Low": 10,
    "Medium": 20,
    "High": 35,
}


def calculate_confidence(sample_size: int) -> str:
    if sample_size < 20:
        return "no_data"
    if sample_size < 50:
        return "low"
    if sample_size < 200:
        return "medium"
    return "high"


def calculate_historical_risk(late_rate: float, cancellation_rate: float) -> str:
    if late_rate < 0.15:
        risk_level = "Low"
    elif late_rate <= 0.30:
        risk_level = "Medium"
    else:
        risk_level = "High"

    if cancellation_rate >= 0.08:
        index = min(RISK_LEVELS.index(risk_level) + 1, len(RISK_LEVELS) - 1)
        risk_level = RISK_LEVELS[index]

    return risk_level


def calculate_base_buffer(risk_level: str) -> int | None:
    return BASE_BUFFER_MINUTES.get(risk_level)


def calculate_buffer(trip_input: TripInput, station_stats: StationStats) -> BufferRecommendation:
    confidence_level = calculate_confidence(station_stats.sample_size)

    if confidence_level == "no_data":
        return BufferRecommendation(
            risk_level="no_data",
            recommended_buffer_minutes=None,
            latest_safe_planned_arrival=None,
            is_planned_arrival_safe=None,
            confidence_level=confidence_level,
            reasons=[],
            warnings=[
                "Not enough historical data for this station to make a reliable recommendation."
            ],
            data_sources=[station_stats.station_name],
        )

    risk_level = calculate_historical_risk(
        station_stats.late_rate, station_stats.cancellation_rate
    )
    recommended_buffer_minutes = calculate_base_buffer(risk_level)

    reasons = [
        f"Historical late rate at {station_stats.station_name} is "
        f"{station_stats.late_rate:.0%}."
    ]
    if station_stats.cancellation_rate >= 0.08:
        reasons.append(
            f"Cancellation rate at {station_stats.station_name} is "
            f"{station_stats.cancellation_rate:.0%}, increasing risk."
        )

    return BufferRecommendation(
        risk_level=risk_level,
        recommended_buffer_minutes=recommended_buffer_minutes,
        latest_safe_planned_arrival=None,
        is_planned_arrival_safe=None,
        confidence_level=confidence_level,
        reasons=reasons,
        warnings=[],
        data_sources=[station_stats.station_name],
    )
