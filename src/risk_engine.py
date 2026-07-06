"""Risk and buffer calculation engine."""

from src.models import BufferRecommendation, StationStats, TripInput

RISK_LEVELS = ["Low", "Medium", "High"]

BASE_BUFFER_MINUTES = {
    "Low": 10,
    "Medium": 20,
    "High": 35,
}

TRIP_TYPE_MODIFIER_MINUTES = {
    "normal": 0,
    "airport": 20,
    "interview_exam": 15,
    "government_visa_medical": 15,
    "transfer": 0,
}

AIRPORT_WARNING = (
    "Airport buffer does not include security, baggage drop, or walking time "
    "inside the airport."
)

TRANSFER_WARNING = (
    "Transfer mode is not fully supported in TrainBuffer v1. Use this result "
    "only as a rough warning."
)

WEATHER_MODIFIER_MINUTES = {
    "strong_wind": 5,
    "heat": 5,
    "snow_ice": 10,
}

MAX_WEATHER_MODIFIER_MINUTES = 15


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


def apply_trip_type_modifier(
    base_buffer_minutes: int, trip_type: str
) -> tuple[int, list[str]]:
    warnings: list[str] = []
    modifier = TRIP_TYPE_MODIFIER_MINUTES.get(trip_type, 0)

    if trip_type == "airport":
        warnings.append(AIRPORT_WARNING)
    if trip_type == "transfer":
        warnings.append(TRANSFER_WARNING)

    return base_buffer_minutes + modifier, warnings


def apply_weather_modifier(
    strong_wind: bool = False, heat: bool = False, snow_ice: bool = False
) -> tuple[int, list[str]]:
    reasons: list[str] = []
    minutes = 0

    if strong_wind:
        minutes += WEATHER_MODIFIER_MINUTES["strong_wind"]
        reasons.append("Strong wind may affect this trip.")
    if heat:
        minutes += WEATHER_MODIFIER_MINUTES["heat"]
        reasons.append("Heat may affect this trip.")
    if snow_ice:
        minutes += WEATHER_MODIFIER_MINUTES["snow_ice"]
        reasons.append("Snow or ice may affect this trip.")

    minutes = min(minutes, MAX_WEATHER_MODIFIER_MINUTES)

    return minutes, reasons


def calculate_buffer(
    trip_input: TripInput,
    station_stats: StationStats,
    strong_wind: bool = False,
    heat: bool = False,
    snow_ice: bool = False,
) -> BufferRecommendation:
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
    base_buffer_minutes = calculate_base_buffer(risk_level)
    recommended_buffer_minutes, trip_type_warnings = apply_trip_type_modifier(
        base_buffer_minutes, trip_input.trip_type
    )
    weather_minutes, weather_reasons = apply_weather_modifier(strong_wind, heat, snow_ice)
    recommended_buffer_minutes += weather_minutes

    reasons = [
        f"Historical late rate at {station_stats.station_name} is "
        f"{station_stats.late_rate:.0%}."
    ]
    if station_stats.cancellation_rate >= 0.08:
        reasons.append(
            f"Cancellation rate at {station_stats.station_name} is "
            f"{station_stats.cancellation_rate:.0%}, increasing risk."
        )
    reasons.extend(weather_reasons)

    return BufferRecommendation(
        risk_level=risk_level,
        recommended_buffer_minutes=recommended_buffer_minutes,
        latest_safe_planned_arrival=None,
        is_planned_arrival_safe=None,
        confidence_level=confidence_level,
        reasons=reasons,
        warnings=trip_type_warnings,
        data_sources=[station_stats.station_name],
    )
