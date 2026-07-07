"""Live weather signal via Open-Meteo, with a graceful fallback.

This module is the ONLY place that performs network calls for weather. It
translates a live current-weather reading into the same three boolean flags
the manual checkboxes used to produce (strong_wind / heat / snow_ice), which
are then fed unchanged into src.risk_engine.apply_weather_modifier.

Guardrail (v1.5 rule 4): if the live source is unavailable for any reason,
get_weather_flags_with_fallback returns all-False flags plus a warning, so the
app degrades to exactly the v1 "no weather adjustment" behavior rather than
raising.
"""

import json
import urllib.request

# Open-Meteo: free, no API key required. https://open-meteo.com
_OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
_REQUEST_TIMEOUT_SECONDS = 5

# Coordinates for the sample destination stations. Kept explicit and small;
# extend alongside data/sample_station_stats.csv.
STATION_COORDINATES = {
    "Hamburg Hbf": {"latitude": 53.5528, "longitude": 10.0067},
    "Berlin Hbf": {"latitude": 52.5251, "longitude": 13.3694},
    "München Hbf": {"latitude": 48.1401, "longitude": 11.5583},
    "Köln Hbf": {"latitude": 50.9430, "longitude": 6.9587},
    "Small Station": {"latitude": 51.0000, "longitude": 10.0000},
}

# Explicit, testable thresholds (see plan Phase 17 design notes).
WIND_THRESHOLD_KMH = 50
HEAT_THRESHOLD_C = 30
# WMO weather codes that indicate snow / ice pellets / snow showers.
SNOW_WEATHER_CODES = {71, 73, 75, 77, 85, 86}

FALLBACK_WARNING = (
    "Live weather source unavailable; no weather adjustment applied. "
    "Use the manual override if you know the conditions."
)


def _fetch_current_weather(latitude: float, longitude: float) -> dict:
    """Perform the raw network call and return Open-Meteo's `current` block.

    Isolated so tests can monkeypatch it without touching the network.
    Raises on any network/parse failure.
    """
    query = (
        f"?latitude={latitude}&longitude={longitude}"
        "&current=temperature_2m,wind_speed_10m,snowfall,weather_code"
        "&wind_speed_unit=kmh"
    )
    request = urllib.request.Request(
        _OPEN_METEO_URL + query, headers={"User-Agent": "TrainBuffer/1.5"}
    )
    with urllib.request.urlopen(request, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload["current"]


def fetch_weather_signal(station_name: str, station_coordinates: dict) -> dict:
    """Return {"strong_wind": bool, "heat": bool, "snow_ice": bool}.

    Raises on any failure (unknown station, network error, malformed data).
    """
    coordinates = station_coordinates.get(station_name)
    if coordinates is None:
        raise ValueError(f"No coordinates known for station {station_name!r}.")

    current = _fetch_current_weather(
        coordinates["latitude"], coordinates["longitude"]
    )

    wind_kmh = float(current["wind_speed_10m"])
    temperature_c = float(current["temperature_2m"])
    snowfall = float(current.get("snowfall", 0) or 0)
    weather_code = int(current.get("weather_code", 0) or 0)

    return {
        "strong_wind": wind_kmh > WIND_THRESHOLD_KMH,
        "heat": temperature_c > HEAT_THRESHOLD_C,
        "snow_ice": snowfall > 0 or weather_code in SNOW_WEATHER_CODES,
    }


def get_weather_flags_with_fallback(
    station_name: str, station_coordinates: dict
) -> dict:
    """Live weather flags, degrading safely if the source is unavailable.

    Returns a dict with the three boolean flags plus:
      - "source": "live" or "unavailable"
      - "warning": None on success, or FALLBACK_WARNING on failure.

    Never raises — on any failure it returns all-False flags so the app
    behaves exactly as v1 did with no weather adjustment.
    """
    try:
        flags = fetch_weather_signal(station_name, station_coordinates)
        return {**flags, "source": "live", "warning": None}
    except Exception:
        return {
            "strong_wind": False,
            "heat": False,
            "snow_ice": False,
            "source": "unavailable",
            "warning": FALLBACK_WARNING,
        }
