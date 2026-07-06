from datetime import time

import pytest

from src.models import BufferRecommendation, StationStats, TripInput


def test_valid_trip_input_can_be_created():
    trip = TripInput(
        origin_station="Berlin Hbf",
        destination_station="Hamburg Hbf",
        planned_arrival_time=time(9, 40),
        arrival_deadline=time(10, 0),
        trip_type="normal",
    )
    assert trip.origin_station == "Berlin Hbf"
    assert trip.trip_type == "normal"


def test_invalid_trip_type_is_rejected():
    with pytest.raises(ValueError):
        TripInput(
            origin_station="Berlin Hbf",
            destination_station="Hamburg Hbf",
            planned_arrival_time=time(9, 40),
            arrival_deadline=time(10, 0),
            trip_type="bogus",
        )


def test_empty_station_name_is_rejected():
    with pytest.raises(ValueError):
        TripInput(
            origin_station="",
            destination_station="Hamburg Hbf",
            planned_arrival_time=time(9, 40),
            arrival_deadline=time(10, 0),
            trip_type="normal",
        )


def test_station_stats_accepts_valid_rates():
    stats = StationStats(
        station_name="Hamburg Hbf",
        sample_size=250,
        late_rate=0.28,
        cancellation_rate=0.03,
        avg_delay_minutes=7,
        p80_delay_minutes=15,
    )
    assert stats.sample_size == 250
    assert stats.late_rate == 0.28


def test_station_stats_rejects_invalid_late_rate():
    with pytest.raises(ValueError):
        StationStats(
            station_name="Hamburg Hbf",
            sample_size=250,
            late_rate=1.5,
            cancellation_rate=0.03,
            avg_delay_minutes=7,
            p80_delay_minutes=15,
        )


def test_buffer_recommendation_contains_required_fields():
    rec = BufferRecommendation(
        risk_level="Low",
        recommended_buffer_minutes=10,
        latest_safe_planned_arrival=time(9, 25),
        is_planned_arrival_safe=True,
        confidence_level="high",
        reasons=["low late rate"],
        warnings=[],
        data_sources=["Hamburg Hbf historical stats"],
    )
    assert rec.risk_level == "Low"
    assert rec.recommended_buffer_minutes == 10
    assert rec.is_planned_arrival_safe is True
    assert rec.reasons == ["low late rate"]
