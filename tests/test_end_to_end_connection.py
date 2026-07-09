"""End-to-end connection-mode scenario (Phase 20f).

Runs a connecting trip with a tight transfer through the full pipeline:
data_loader -> connection_engine.estimate_leg_arrival_delay ->
compute_connection_risk -> recommendation.build_connection_message, and
asserts it produces a correct high-risk warning.
"""

from datetime import time

from src.connection_engine import (
    compute_connection_risk,
    estimate_leg_arrival_delay,
)
from src.data_loader import get_station_stats, load_station_stats
from src.models import MultiLegTripInput, TripLeg
from src.recommendation import build_connection_message

STATION_STATS_PATH = "data/sample_station_stats.csv"


def test_tight_transfer_produces_high_risk_warning():
    station_stats = load_station_stats(STATION_STATS_PATH)

    # Transfer at München Hbf: sample data has avg 9 / p80 20 min delay,
    # late_rate 0.34 -> High historical risk.
    leg1 = TripLeg(
        origin_station="Berlin Hbf",
        destination_station="München Hbf",
        planned_departure_time=time(8, 0),
        planned_arrival_time=time(10, 0),
    )
    # Only 12 scheduled minutes to change trains at a hub needing 10.
    leg2 = TripLeg(
        origin_station="München Hbf",
        destination_station="Köln Hbf",
        planned_departure_time=time(10, 12),
        planned_arrival_time=time(14, 0),
    )
    trip = MultiLegTripInput(
        legs=[leg1, leg2], arrival_deadline=time(14, 0), trip_type="normal"
    )
    assert trip.transfer_stations == ["München Hbf"]

    transfer_stats = get_station_stats(leg1.destination_station, station_stats)
    leg1_delay = estimate_leg_arrival_delay(leg1, transfer_stats)
    assert leg1_delay["has_data"] is True

    connection_risk = compute_connection_risk(leg1, leg2, leg1_delay)
    # scheduled 12, minimum 10 (München Hbf), expected delay 9 ->
    # expected slack 12 - 9 - 10 = -7 < 0 -> High, likely missed.
    assert connection_risk["connection_risk_level"] == "High"
    assert connection_risk["likely_missed"] is True

    message = build_connection_message(
        connection_risk, next_departure_time=time(10, 42)
    )
    assert "High risk" in message
    assert "München Hbf" in message
    assert "next departure at 10:42" in message


def test_comfortable_transfer_is_low_risk_end_to_end():
    station_stats = load_station_stats(STATION_STATS_PATH)
    leg1 = TripLeg(
        origin_station="Berlin Hbf",
        destination_station="Hamburg Hbf",
        planned_departure_time=time(8, 0),
        planned_arrival_time=time(9, 40),
    )
    # 45-minute scheduled transfer at Hamburg Hbf (min 8, p80 delay 15).
    leg2 = TripLeg(
        origin_station="Hamburg Hbf",
        destination_station="Köln Hbf",
        planned_departure_time=time(10, 25),
        planned_arrival_time=time(13, 0),
    )
    MultiLegTripInput(
        legs=[leg1, leg2], arrival_deadline=time(13, 0), trip_type="normal"
    )
    transfer_stats = get_station_stats(leg1.destination_station, station_stats)
    leg1_delay = estimate_leg_arrival_delay(leg1, transfer_stats)
    connection_risk = compute_connection_risk(leg1, leg2, leg1_delay)
    # 45 - 15 - 8 = 22 >= 0 -> Low even in the conservative case.
    assert connection_risk["connection_risk_level"] == "Low"
    assert "looks safe" in build_connection_message(connection_risk)
