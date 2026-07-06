"""Optional advice logging."""

import csv
import os
from datetime import datetime

from src.models import BufferRecommendation, TripInput

LOG_COLUMNS = [
    "timestamp",
    "origin_station",
    "destination_station",
    "planned_arrival_time",
    "arrival_deadline",
    "trip_type",
    "risk_level",
    "recommended_buffer_minutes",
    "latest_safe_planned_arrival",
    "is_planned_arrival_safe",
    "confidence_level",
]


def log_advice(trip_input: TripInput, result: BufferRecommendation, path: str) -> None:
    file_exists = os.path.exists(path)

    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "origin_station": trip_input.origin_station,
        "destination_station": trip_input.destination_station,
        "planned_arrival_time": trip_input.planned_arrival_time.isoformat(),
        "arrival_deadline": trip_input.arrival_deadline.isoformat(),
        "trip_type": trip_input.trip_type,
        "risk_level": result.risk_level,
        "recommended_buffer_minutes": result.recommended_buffer_minutes,
        "latest_safe_planned_arrival": (
            result.latest_safe_planned_arrival.isoformat()
            if result.latest_safe_planned_arrival
            else None
        ),
        "is_planned_arrival_safe": result.is_planned_arrival_safe,
        "confidence_level": result.confidence_level,
    }

    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
