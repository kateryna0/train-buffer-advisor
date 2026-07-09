"""Tests for Phase 20d: downstream connection risk calculation."""

from datetime import time

from src.connection_engine import compute_connection_risk
from src.models import TripLeg


def _leg(origin, dest, dep, arr):
    return TripLeg(
        origin_station=origin,
        destination_station=dest,
        planned_departure_time=dep,
        planned_arrival_time=arr,
    )


def _estimate(expected, p80, has_data=True):
    return {
        "expected_delay_minutes": expected,
        "p80_delay_minutes": p80,
        "has_data": has_data,
    }


# Transfer at "Hannover Hbf" -> minimum_transfer_minutes = 7 (from 20c table).
LEG1 = _leg("Berlin Hbf", "Hannover Hbf", dep=time(8, 0), arr=time(9, 0))


def test_generous_buffer_is_low_risk():
    # 40-min scheduled transfer, small delays, 7-min minimum -> holds even at p80.
    leg2 = _leg("Hannover Hbf", "Köln Hbf", dep=time(9, 40), arr=time(11, 0))
    risk = compute_connection_risk(LEG1, leg2, _estimate(5, 10))
    assert risk["scheduled_transfer_minutes"] == 40
    assert risk["minimum_transfer_minutes"] == 7
    assert risk["conservative_transfer_slack_minutes"] == 40 - 10 - 7
    assert risk["connection_risk_level"] == "Low"
    assert risk["likely_missed"] is False


def test_tight_buffer_is_medium_when_only_expected_holds():
    # 20-min transfer; expected 5 -> slack 8 (ok); p80 15 -> slack -2 (fails).
    leg2 = _leg("Hannover Hbf", "Köln Hbf", dep=time(9, 20), arr=time(11, 0))
    risk = compute_connection_risk(LEG1, leg2, _estimate(5, 15))
    assert risk["expected_transfer_slack_minutes"] == 20 - 5 - 7
    assert risk["conservative_transfer_slack_minutes"] == 20 - 15 - 7
    assert risk["connection_risk_level"] == "Medium"
    assert risk["likely_missed"] is False


def test_short_buffer_is_high_risk():
    # 10-min transfer; expected delay 8 -> slack 10-8-7 = -5 -> High.
    leg2 = _leg("Hannover Hbf", "Köln Hbf", dep=time(9, 10), arr=time(11, 0))
    risk = compute_connection_risk(LEG1, leg2, _estimate(8, 20))
    assert risk["connection_risk_level"] == "High"
    assert risk["likely_missed"] is True


def test_transfer_station_defaults_to_arrival_leg_destination():
    leg2 = _leg("Hannover Hbf", "Köln Hbf", dep=time(9, 30), arr=time(11, 0))
    risk = compute_connection_risk(LEG1, leg2, _estimate(0, 0))
    assert risk["transfer_station"] == "Hannover Hbf"


def test_no_data_estimate_uses_zero_delays_neutrally():
    # No leg-1 data -> delays 0; risk reflects only buffer vs minimum transfer.
    leg2 = _leg("Hannover Hbf", "Köln Hbf", dep=time(9, 30), arr=time(11, 0))
    risk = compute_connection_risk(LEG1, leg2, _estimate(0, 0, has_data=False))
    assert risk["has_data"] is False
    # 30 - 0 - 7 = 23 >= 0 -> Low
    assert risk["connection_risk_level"] == "Low"


def test_unknown_transfer_station_uses_default_minimum():
    leg1 = _leg("A", "B", dep=time(8, 0), arr=time(9, 0))
    leg2 = _leg("B", "C", dep=time(9, 30), arr=time(11, 0))
    risk = compute_connection_risk(leg1, leg2, _estimate(0, 0))
    assert risk["minimum_transfer_minutes"] == 8  # DEFAULT
