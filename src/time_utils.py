"""Deadline/time calculations."""

from datetime import datetime, time, timedelta


def calculate_latest_safe_arrival(arrival_deadline: time, recommended_buffer_minutes: int) -> time:
    reference = datetime(
        2000, 1, 1, arrival_deadline.hour, arrival_deadline.minute, arrival_deadline.second
    )
    result = reference - timedelta(minutes=recommended_buffer_minutes)
    return result.time()


def is_planned_arrival_safe(planned_arrival_time: time, latest_safe_planned_arrival: time) -> bool:
    return planned_arrival_time <= latest_safe_planned_arrival
