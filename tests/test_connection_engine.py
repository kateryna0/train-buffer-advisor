"""Tests for src/connection_engine.py (Phase 20b: first-leg delay estimate)."""

from datetime import time

from src.connection_engine import estimate_leg_arrival_delay
from src.models import StationStats, TripLeg


def _leg(dest="Hamburg Hbf"):
    return TripLeg(
        origin_station="Berlin Hbf",
        destination_station=dest,
        planned_departure_time=time(8, 0),
        planned_arrival_time=time(9, 0),
    )


def _stats(name, sample_size, late_rate, cancellation_rate, avg, p80):
    return StationStats(
        station_name=name,
        sample_size=sample_size,
        late_rate=late_rate,
        cancellation_rate=cancellation_rate,
        avg_delay_minutes=avg,
        p80_delay_minutes=p80,
    )


def test_estimate_uses_station_stats_and_risk_engine():
    stats = _stats("Hamburg Hbf", 250, 0.28, 0.03, 7, 15)
    estimate = estimate_leg_arrival_delay(_leg("Hamburg Hbf"), stats)
    assert estimate["has_data"] is True
    assert estimate["station_name"] == "Hamburg Hbf"
    assert estimate["risk_level"] == "Medium"  # 0.15 < 0.28 <= 0.30
    assert estimate["confidence_level"] == "high"  # sample_size >= 200
    assert estimate["expected_delay_minutes"] == 7
    assert estimate["p80_delay_minutes"] == 15


def test_estimate_returns_no_data_when_stats_missing():
    estimate = estimate_leg_arrival_delay(_leg("Nowhere"), None)
    assert estimate["has_data"] is False
    assert estimate["risk_level"] == "no_data"
    assert estimate["expected_delay_minutes"] == 0
    assert estimate["p80_delay_minutes"] == 0


def test_estimate_returns_no_data_when_sample_too_small():
    stats = _stats("Small Station", 12, 0.20, 0.0, 4, 8)
    estimate = estimate_leg_arrival_delay(_leg("Small Station"), stats)
    assert estimate["has_data"] is False
    assert estimate["confidence_level"] == "no_data"
    assert estimate["expected_delay_minutes"] == 0


def test_high_late_rate_yields_high_risk():
    stats = _stats("München Hbf", 180, 0.34, 0.04, 9, 20)
    estimate = estimate_leg_arrival_delay(_leg("München Hbf"), stats)
    assert estimate["has_data"] is True
    assert estimate["risk_level"] == "High"  # late_rate > 0.30
    assert estimate["p80_delay_minutes"] == 20
