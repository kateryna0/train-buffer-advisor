"""Phase 22: caching behavior for the live weather and delay clients.

No real network calls — the *uncached* raw network functions are monkeypatched.
"""

import pytest

from src import live_delay_client, weather_client

COORDS = {"Testville": {"latitude": 1.0, "longitude": 2.0}}


@pytest.fixture(autouse=True)
def _clear_caches():
    weather_client._weather_cache.clear()
    live_delay_client._delay_cache.clear()
    yield
    weather_client._weather_cache.clear()
    live_delay_client._delay_cache.clear()


# --- weather ----------------------------------------------------------------

def test_repeated_weather_lookup_hits_network_once(monkeypatch):
    calls = []

    def fake_raw(lat, lon):
        calls.append((lat, lon))
        return {
            "wind_speed_10m": 10,
            "temperature_2m": 18,
            "snowfall": 0,
            "weather_code": 1,
        }

    monkeypatch.setattr(weather_client, "_fetch_current_weather_uncached", fake_raw)
    weather_client.fetch_weather_signal("Testville", COORDS)
    weather_client.fetch_weather_signal("Testville", COORDS)
    assert len(calls) == 1  # second call served from cache


def test_weather_failure_not_cached_as_success(monkeypatch):
    state = {"fail": True}

    def fake_raw(lat, lon):
        if state["fail"]:
            raise ConnectionError("down")
        return {
            "wind_speed_10m": 70,
            "temperature_2m": 18,
            "snowfall": 0,
            "weather_code": 1,
        }

    monkeypatch.setattr(weather_client, "_fetch_current_weather_uncached", fake_raw)
    first = weather_client.get_weather_flags_with_fallback("Testville", COORDS)
    assert first["source"] == "unavailable"
    # Recovery: next call succeeds instead of returning a cached failure.
    state["fail"] = False
    second = weather_client.get_weather_flags_with_fallback("Testville", COORDS)
    assert second["source"] == "live"
    assert second["strong_wind"] is True


# --- delay ------------------------------------------------------------------

def test_repeated_delay_lookup_hits_network_once(monkeypatch):
    calls = []

    def fake_raw(train_number):
        calls.append(train_number)
        return {"delay_minutes": 9}

    monkeypatch.setattr(
        live_delay_client, "_request_train_status_uncached", fake_raw
    )
    live_delay_client.fetch_live_delay("ICE 123")
    live_delay_client.fetch_live_delay("ICE 123")
    assert len(calls) == 1


def test_delay_failure_not_cached_as_success(monkeypatch):
    state = {"fail": True}

    def fake_raw(train_number):
        if state["fail"]:
            raise TimeoutError("timeout")
        return {"delay_minutes": 12}

    monkeypatch.setattr(
        live_delay_client, "_request_train_status_uncached", fake_raw
    )
    assert live_delay_client.fetch_live_delay("ICE 123") is None
    state["fail"] = False
    assert live_delay_client.fetch_live_delay("ICE 123") == {
        "currently_delayed": True,
        "delay_minutes": 12,
    }
