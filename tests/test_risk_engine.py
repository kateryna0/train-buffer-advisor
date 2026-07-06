from datetime import time

from src.models import StationStats, TripInput
from src.risk_engine import (
    calculate_base_buffer,
    calculate_buffer,
    calculate_confidence,
    calculate_historical_risk,
)


def _trip_input(trip_type="normal"):
    return TripInput(
        origin_station="Berlin Hbf",
        destination_station="Hamburg Hbf",
        planned_arrival_time=time(9, 40),
        arrival_deadline=time(10, 0),
        trip_type=trip_type,
    )


# --- Feature 3.1 — confidence calculation ---

def test_confidence_no_data():
    assert calculate_confidence(5) == "no_data"


def test_confidence_low():
    assert calculate_confidence(25) == "low"


def test_confidence_medium():
    assert calculate_confidence(100) == "medium"


def test_confidence_high():
    assert calculate_confidence(250) == "high"


# --- Feature 3.2 — historical risk level ---

def test_historical_risk_low():
    assert calculate_historical_risk(0.10, 0.02) == "Low"


def test_historical_risk_medium():
    assert calculate_historical_risk(0.22, 0.02) == "Medium"


def test_historical_risk_high():
    assert calculate_historical_risk(0.40, 0.02) == "High"


def test_high_cancellation_increases_low_to_medium():
    assert calculate_historical_risk(0.10, 0.09) == "Medium"


def test_high_cancellation_increases_medium_to_high():
    assert calculate_historical_risk(0.22, 0.09) == "High"


def test_high_remains_high_with_cancellation_modifier():
    assert calculate_historical_risk(0.40, 0.09) == "High"


# --- Feature 3.3 — base buffer calculation ---

def test_base_buffer_low():
    assert calculate_base_buffer("Low") == 10


def test_base_buffer_medium():
    assert calculate_base_buffer("Medium") == 20


def test_base_buffer_high():
    assert calculate_base_buffer("High") == 35


def test_base_buffer_no_data_returns_none():
    assert calculate_base_buffer("no_data") is None


# --- Feature 3.4 — main calculation function ---

def test_calculate_buffer_no_data_station():
    stats = StationStats(
        station_name="Small Station",
        sample_size=12,
        late_rate=0.20,
        cancellation_rate=0.00,
        avg_delay_minutes=4,
        p80_delay_minutes=8,
    )
    result = calculate_buffer(_trip_input(), stats)
    assert result.confidence_level == "no_data"
    assert result.recommended_buffer_minutes is None
    assert len(result.warnings) > 0


def test_calculate_buffer_low_risk_station():
    stats = StationStats(
        station_name="Berlin Hbf",
        sample_size=300,
        late_rate=0.18,
        cancellation_rate=0.02,
        avg_delay_minutes=5,
        p80_delay_minutes=10,
    )
    result = calculate_buffer(_trip_input(), stats)
    assert result.risk_level == "Medium"
    assert result.recommended_buffer_minutes == 20
    assert result.confidence_level == "high"


def test_calculate_buffer_high_cancellation_station():
    stats = StationStats(
        station_name="Köln Hbf",
        sample_size=90,
        late_rate=0.31,
        cancellation_rate=0.09,
        avg_delay_minutes=10,
        p80_delay_minutes=25,
    )
    result = calculate_buffer(_trip_input(), stats)
    assert result.risk_level == "High"
    assert result.recommended_buffer_minutes == 35
