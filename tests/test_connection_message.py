"""Tests for Phase 20e: missed-connection / next-train fallback messaging."""

from datetime import time

from src.recommendation import CONNECTION_NO_DATA_CAVEAT, build_connection_message


def _risk(level, has_data=True, expected=5, p80=15, slack=10):
    return {
        "transfer_station": "Hannover Hbf",
        "connection_risk_level": level,
        "minimum_transfer_minutes": 7,
        "expected_leg1_delay_minutes": expected,
        "p80_leg1_delay_minutes": p80,
        "expected_transfer_slack_minutes": slack,
        "has_data": has_data,
    }


def test_high_risk_message_mentions_missing_and_generic_fallback():
    msg = build_connection_message(_risk("High"))
    assert "High risk" in msg
    assert "Hannover Hbf" in msg
    assert "earlier first train" in msg


def test_high_risk_message_uses_next_departure_when_given():
    msg = build_connection_message(_risk("High"), next_departure_time=time(9, 45))
    assert "next departure at 09:45" in msg


def test_medium_risk_message_warns_to_have_fallback():
    msg = build_connection_message(_risk("Medium"))
    assert "tight" in msg
    assert "fallback" in msg


def test_low_risk_message_is_reassuring():
    msg = build_connection_message(_risk("Low", slack=25))
    assert "looks safe" in msg
    assert "25" in msg


def test_no_data_appends_caveat():
    msg = build_connection_message(_risk("Low", has_data=False))
    assert msg.endswith(CONNECTION_NO_DATA_CAVEAT)


def test_has_data_does_not_append_caveat():
    msg = build_connection_message(_risk("Low", has_data=True))
    assert CONNECTION_NO_DATA_CAVEAT not in msg
