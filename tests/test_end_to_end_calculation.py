from datetime import time

from src.data_loader import get_station_stats, load_station_stats
from src.models import TripInput
from src.recommendation import build_recommendation_text
from src.risk_engine import calculate_buffer
from src.time_utils import calculate_latest_safe_arrival, is_planned_arrival_safe

CSV_PATH = "data/sample_station_stats.csv"


def _run_pipeline(destination, trip_type, deadline, planned_arrival):
    stats_by_station = load_station_stats(CSV_PATH)
    trip_input = TripInput(
        origin_station="Berlin Hbf",
        destination_station=destination,
        planned_arrival_time=planned_arrival,
        arrival_deadline=deadline,
        trip_type=trip_type,
    )
    stats = get_station_stats(destination, stats_by_station)

    if stats is None:
        return trip_input, None, None

    result = calculate_buffer(trip_input, stats)
    result.latest_safe_planned_arrival = calculate_latest_safe_arrival(
        deadline, result.recommended_buffer_minutes
    )
    result.is_planned_arrival_safe = is_planned_arrival_safe(
        planned_arrival, result.latest_safe_planned_arrival
    )
    text = build_recommendation_text(trip_input, result)
    return trip_input, result, text


def test_scenario_1_normal_low_risk_trip():
    _, result, text = _run_pipeline(
        destination="Berlin Hbf",
        trip_type="normal",
        deadline=time(10, 0),
        planned_arrival=time(9, 40),
    )
    assert result.confidence_level == "high"
    assert result.risk_level in {"Low", "Medium", "High"}
    assert isinstance(text, str) and text


def test_scenario_2_airport_trip():
    _, result, text = _run_pipeline(
        destination="München Hbf",
        trip_type="airport",
        deadline=time(12, 0),
        planned_arrival=time(11, 40),
    )
    assert result.recommended_buffer_minutes >= 20
    assert result.is_planned_arrival_safe is False
    assert "security" in text


def test_scenario_3_interview_exam():
    _, result, text = _run_pipeline(
        destination="Berlin Hbf",
        trip_type="interview_exam",
        deadline=time(10, 0),
        planned_arrival=time(9, 40),
    )
    assert result.recommended_buffer_minutes >= 15
    assert isinstance(text, str) and text


def test_scenario_4_unknown_station():
    _, result, text = _run_pipeline(
        destination="Unknown Station",
        trip_type="normal",
        deadline=time(10, 0),
        planned_arrival=time(9, 40),
    )
    assert result is None
    assert text is None


def test_scenario_5_transfer():
    _, result, text = _run_pipeline(
        destination="Berlin Hbf",
        trip_type="transfer",
        deadline=time(10, 0),
        planned_arrival=time(9, 40),
    )
    assert any("not fully supported" in w for w in result.warnings)
    assert "not fully supported" in text
