"""Tests for src/weather_client.py. No real network calls are made."""

import pytest

from src import weather_client
from src.weather_client import (
    FALLBACK_WARNING,
    fetch_weather_signal,
    get_weather_flags_with_fallback,
)

COORDS = {"Testville": {"latitude": 1.0, "longitude": 2.0}}


def _patch_current(monkeypatch, current):
    """Make _fetch_current_weather return a fixed `current` block."""
    monkeypatch.setattr(
        weather_client, "_fetch_current_weather", lambda lat, lon: current
    )


def test_fetch_weather_signal_detects_strong_wind(monkeypatch):
    _patch_current(
        monkeypatch,
        {"wind_speed_10m": 65, "temperature_2m": 15, "snowfall": 0, "weather_code": 3},
    )
    flags = fetch_weather_signal("Testville", COORDS)
    assert flags == {"strong_wind": True, "heat": False, "snow_ice": False}


def test_fetch_weather_signal_detects_heat(monkeypatch):
    _patch_current(
        monkeypatch,
        {"wind_speed_10m": 10, "temperature_2m": 33, "snowfall": 0, "weather_code": 0},
    )
    flags = fetch_weather_signal("Testville", COORDS)
    assert flags == {"strong_wind": False, "heat": True, "snow_ice": False}


def test_fetch_weather_signal_detects_snow_from_snowfall(monkeypatch):
    _patch_current(
        monkeypatch,
        {"wind_speed_10m": 10, "temperature_2m": -2, "snowfall": 1.5, "weather_code": 3},
    )
    flags = fetch_weather_signal("Testville", COORDS)
    assert flags["snow_ice"] is True


def test_fetch_weather_signal_detects_snow_from_weather_code(monkeypatch):
    _patch_current(
        monkeypatch,
        {"wind_speed_10m": 10, "temperature_2m": -2, "snowfall": 0, "weather_code": 75},
    )
    flags = fetch_weather_signal("Testville", COORDS)
    assert flags["snow_ice"] is True


def test_fetch_weather_signal_no_adverse_conditions(monkeypatch):
    _patch_current(
        monkeypatch,
        {"wind_speed_10m": 12, "temperature_2m": 18, "snowfall": 0, "weather_code": 1},
    )
    flags = fetch_weather_signal("Testville", COORDS)
    assert flags == {"strong_wind": False, "heat": False, "snow_ice": False}


def test_fetch_weather_signal_raises_for_unknown_station():
    with pytest.raises(ValueError):
        fetch_weather_signal("Nowhere", COORDS)


def test_fallback_returns_all_false_and_warning_when_api_raises(monkeypatch):
    def boom(lat, lon):
        raise ConnectionError("network down")

    monkeypatch.setattr(weather_client, "_fetch_current_weather", boom)
    result = get_weather_flags_with_fallback("Testville", COORDS)
    assert result["strong_wind"] is False
    assert result["heat"] is False
    assert result["snow_ice"] is False
    assert result["source"] == "unavailable"
    assert result["warning"] == FALLBACK_WARNING


def test_fallback_returns_live_flags_on_success(monkeypatch):
    _patch_current(
        monkeypatch,
        {"wind_speed_10m": 70, "temperature_2m": 31, "snowfall": 0, "weather_code": 0},
    )
    result = get_weather_flags_with_fallback("Testville", COORDS)
    assert result["strong_wind"] is True
    assert result["heat"] is True
    assert result["snow_ice"] is False
    assert result["source"] == "live"
    assert result["warning"] is None
