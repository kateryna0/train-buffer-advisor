from datetime import time

from src.models import BufferRecommendation, TripInput
from src.recommendation import build_recommendation_text


def _trip_input(trip_type="normal"):
    return TripInput(
        origin_station="Berlin Hbf",
        destination_station="Hamburg Hbf",
        planned_arrival_time=time(9, 40),
        arrival_deadline=time(10, 0),
        trip_type=trip_type,
    )


def test_high_risk_text_includes_risky():
    trip = _trip_input(trip_type="interview_exam")
    result = BufferRecommendation(
        risk_level="High",
        recommended_buffer_minutes=35,
        latest_safe_planned_arrival=time(9, 25),
        is_planned_arrival_safe=False,
        confidence_level="high",
    )
    text = build_recommendation_text(trip, result)
    assert "risky" in text


def test_safe_text_includes_acceptable():
    trip = _trip_input(trip_type="normal")
    result = BufferRecommendation(
        risk_level="Low",
        recommended_buffer_minutes=10,
        latest_safe_planned_arrival=time(9, 50),
        is_planned_arrival_safe=True,
        confidence_level="high",
    )
    text = build_recommendation_text(trip, result)
    assert "acceptable" in text


def test_no_data_text_includes_not_enough_historical_data():
    trip = _trip_input(trip_type="normal")
    result = BufferRecommendation(
        risk_level="no_data",
        recommended_buffer_minutes=None,
        latest_safe_planned_arrival=None,
        is_planned_arrival_safe=None,
        confidence_level="no_data",
    )
    text = build_recommendation_text(trip, result)
    assert "not enough historical data" in text


def test_airport_text_includes_conservative_wording():
    trip = _trip_input(trip_type="airport")
    result = BufferRecommendation(
        risk_level="Low",
        recommended_buffer_minutes=30,
        latest_safe_planned_arrival=time(9, 30),
        is_planned_arrival_safe=True,
        confidence_level="high",
    )
    text = build_recommendation_text(trip, result)
    assert "security" in text


def test_transfer_text_includes_out_of_scope_warning():
    trip = _trip_input(trip_type="transfer")
    result = BufferRecommendation(
        risk_level="Low",
        recommended_buffer_minutes=10,
        latest_safe_planned_arrival=time(9, 50),
        is_planned_arrival_safe=True,
        confidence_level="high",
    )
    text = build_recommendation_text(trip, result)
    assert "not fully supported" in text
