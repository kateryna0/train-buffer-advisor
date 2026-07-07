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
class TripLeg:
    """A single train leg within a multi-leg (connecting) trip."""

    origin_station: str
    destination_station: str
    planned_departure_time: time
    planned_arrival_time: time

    def __post_init__(self):
        if not self.origin_station:
            raise ValueError("origin_station must not be empty")
        if not self.destination_station:
            raise ValueError("destination_station must not be empty")
        if self.origin_station == self.destination_station:
            raise ValueError(
                "leg origin_station and destination_station must differ"
            )


@dataclass
class MultiLegTripInput:
    """A connecting trip: two or more legs plus a final deadline.

    v3 connection mode. Adjacent legs must connect (the destination of one leg
    is the origin of the next), which is where the transfer happens.
    """

    legs: list["TripLeg"]
    arrival_deadline: time
    trip_type: str

    def __post_init__(self):
        if len(self.legs) < 2:
            raise ValueError(
                "a multi-leg trip must have at least 2 legs; use TripInput "
                "for a single-leg trip"
            )
        for earlier, later in zip(self.legs, self.legs[1:]):
            if earlier.destination_station != later.origin_station:
                raise ValueError(
                    "legs must connect: leg destination "
                    f"{earlier.destination_station!r} does not match next "
                    f"leg origin {later.origin_station!r}"
                )
        if self.trip_type not in ALLOWED_TRIP_TYPES:
            raise ValueError(
                f"invalid trip_type: {self.trip_type!r}, "
                f"must be one of {sorted(ALLOWED_TRIP_TYPES)}"
            )

    @property
    def transfer_stations(self) -> list[str]:
        """Stations where the traveler changes trains (between legs)."""
        return [leg.destination_station for leg in self.legs[:-1]]

    @property
    def final_destination(self) -> str:
        return self.legs[-1].destination_station


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
