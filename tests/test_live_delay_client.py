"""Tests for src/live_delay_client.py. No real network calls are made."""

from src import live_delay_client
from src.live_delay_client import (
    apply_live_delay_modifier,
    fetch_live_delay,
    validate_train_number,
)
from src.models import BufferRecommendation


def _recommendation(buffer_minutes):
    return BufferRecommendation(
        risk_level="Low",
        recommended_buffer_minutes=buffer_minutes,
        latest_safe_planned_arrival=None,
        is_planned_arrival_safe=None,
        confidence_level="high",
        reasons=[],
        warnings=[],
        data_sources=["Test"],
    )


def test_validate_train_number_accepts_common_formats():
    assert validate_train_number("ICE 123")
    assert validate_train_number("IC2043")
    assert validate_train_number("RE 4")


def test_validate_train_number_rejects_garbage():
    assert not validate_train_number("")
    assert not validate_train_number("not a train")
    assert not validate_train_number("123456789")


def test_fetch_live_delay_returns_info_for_delayed_response(monkeypatch):
    monkeypatch.setattr(
        live_delay_client, "_request_train_status", lambda tn: {"delay_minutes": 12}
    )
    assert fetch_live_delay("ICE 123") == {
        "currently_delayed": True,
        "delay_minutes": 12,
    }


def test_fetch_live_delay_returns_not_delayed_for_zero(monkeypatch):
    monkeypatch.setattr(
        live_delay_client, "_request_train_status", lambda tn: {"delay_minutes": 0}
    )
    assert fetch_live_delay("ICE 123") == {
        "currently_delayed": False,
        "delay_minutes": 0,
    }


def test_fetch_live_delay_returns_none_on_timeout(monkeypatch):
    def boom(tn):
        raise TimeoutError("timed out")

    monkeypatch.setattr(live_delay_client, "_request_train_status", boom)
    assert fetch_live_delay("ICE 123") is None


def test_fetch_live_delay_returns_none_for_invalid_number(monkeypatch):
    # Must not even attempt the network call for a bad format.
    def fail(tn):
        raise AssertionError("network should not be called")

    monkeypatch.setattr(live_delay_client, "_request_train_status", fail)
    assert fetch_live_delay("not a train") is None


def test_apply_modifier_increases_buffer_and_warns_when_delayed():
    rec = _recommendation(20)
    result = apply_live_delay_modifier(
        rec, {"currently_delayed": True, "delay_minutes": 12}
    )
    assert result.recommended_buffer_minutes == 32
    assert any("delayed by 12 min" in w for w in result.warnings)


def test_apply_modifier_is_noop_when_no_live_data():
    rec = _recommendation(20)
    result = apply_live_delay_modifier(rec, None)
    assert result.recommended_buffer_minutes == 20
    assert result.warnings == []


def test_apply_modifier_is_noop_when_not_delayed():
    rec = _recommendation(20)
    result = apply_live_delay_modifier(
        rec, {"currently_delayed": False, "delay_minutes": 0}
    )
    assert result.recommended_buffer_minutes == 20
    assert result.warnings == []


def test_apply_modifier_is_noop_for_no_data_recommendation():
    rec = _recommendation(None)
    result = apply_live_delay_modifier(
        rec, {"currently_delayed": True, "delay_minutes": 12}
    )
    assert result.recommended_buffer_minutes is None
    assert result.warnings == []
