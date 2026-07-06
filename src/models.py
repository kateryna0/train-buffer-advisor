"""Domain models for TrainBuffer."""

from dataclasses import dataclass, field
from datetime import time

ALLOWED_TRIP_TYPES = {
    "normal",
    "airport",
    "interview_exam",
    "government_visa_medical",
    "transfer",
}


@dataclass
class TripInput:
    origin_station: str
    destination_station: str
    planned_arrival_time: time
    arrival_deadline: time
    trip_type: str

    def __post_init__(self):
        if not self.origin_station:
            raise ValueError("origin_station must not be empty")
        if not self.destination_station:
            raise ValueError("destination_station must not be empty")
        if self.trip_type not in ALLOWED_TRIP_TYPES:
            raise ValueError(
                f"invalid trip_type: {self.trip_type!r}, "
                f"must be one of {sorted(ALLOWED_TRIP_TYPES)}"
            )


@dataclass
class StationStats:
    station_name: str
    sample_size: int
    late_rate: float
    cancellation_rate: float
    avg_delay_minutes: float
    p80_delay_minutes: float

    def __post_init__(self):
        if not self.station_name:
            raise ValueError("station_name must not be empty")
        if self.sample_size < 0:
            raise ValueError("sample_size must not be negative")
        if not 0.0 <= self.late_rate <= 1.0:
            raise ValueError("late_rate must be between 0 and 1")
        if not 0.0 <= self.cancellation_rate <= 1.0:
            raise ValueError("cancellation_rate must be between 0 and 1")


@dataclass
class BufferRecommendation:
    risk_level: str
    recommended_buffer_minutes: int | None
    latest_safe_planned_arrival: time | None
    is_planned_arrival_safe: bool | None
    confidence_level: str
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    data_sources: list[str] = field(default_factory=list)
