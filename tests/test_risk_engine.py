from datetime import time

from src.models import StationStats, TripInput
from src.risk_engine import (
    apply_trip_type_modifier,
    apply_weather_modifier,
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


# --- Phase 5 — trip type conservatism ---

def test_normal_trip_keeps_base_buffer():
    minutes, warnings = apply_trip_type_modifier(10, "normal")
    assert minutes == 10
    assert warnings == []


def test_airport_adds_20_minutes_and_warning():
    minutes, warnings = apply_trip_type_modifier(10, "airport")
    assert minutes == 30
    assert any("security" in w for w in warnings)


def test_interview_exam_adds_15_minutes():
    minutes, warnings = apply_trip_type_modifier(10, "interview_exam")
    assert minutes == 25
    assert warnings == []


def test_government_visa_medical_adds_15_minutes():
    minutes, warnings = apply_trip_type_modifier(10, "government_visa_medical")
    assert minutes == 25
    assert warnings == []


def test_transfer_returns_warning():
    minutes, warnings = apply_trip_type_modifier(10, "transfer")
    assert minutes == 10
    assert any("not fully supported" in w for w in warnings)


def test_calculate_buffer_applies_airport_modifier():
    stats = StationStats(
        station_name="München Hbf",
        sample_size=180,
        late_rate=0.34,
        cancellation_rate=0.04,
        avg_delay_minutes=9,
        p80_delay_minutes=20,
    )
    result = calculate_buffer(_trip_input(trip_type="airport"), stats)
    assert result.risk_level == "High"
    assert result.recommended_buffer_minutes == 55
    assert any("security" in w for w in result.warnings)


# --- Phase 10 — weather signal modifiers ---

def test_strong_wind_adds_5_minutes_and_reason():
    minutes, reasons = apply_weather_modifier(strong_wind=True)
    assert minutes == 5
    assert any("wind" in r for r in reasons)


def test_heat_adds_5_minutes_and_reason():
    minutes, reasons = apply_weather_modifier(heat=True)
    assert minutes == 5
    assert any("Heat" in r for r in reasons)


def test_snow_adds_10_minutes_and_reason():
    minutes, reasons = apply_weather_modifier(snow_ice=True)
    assert minutes == 10
    assert any("Snow" in r for r in reasons)


def test_multiple_weather_flags_are_capped_at_15():
    minutes, reasons = apply_weather_modifier(strong_wind=True, heat=True, snow_ice=True)
    assert minutes == 15
    assert len(reasons) == 3


def test_no_weather_flags_keep_buffer_unchanged():
    minutes, reasons = apply_weather_modifier()
    assert minutes == 0
    assert reasons == []


def test_calculate_buffer_applies_weather_modifier():
    stats = StationStats(
        station_name="Berlin Hbf",
        sample_size=300,
        late_rate=0.10,
        cancellation_rate=0.02,
        avg_delay_minutes=5,
        p80_delay_minutes=10,
    )
    result = calculate_buffer(_trip_input(), stats, snow_ice=True)
    assert result.recommended_buffer_minutes == 20
    assert any("Snow" in r for r in result.reasons)
