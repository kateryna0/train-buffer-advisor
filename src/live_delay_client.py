"""Live upstream delay check for a specific train (v1.5).

Guardrails (from docs/09 roadmap, restated in the v2 plan Phase 18):
- This must never become a hard dependency. Any failure — bad train number,
  timeout, not found, malformed data, missing data after arrival — is treated
  as "no live data" (return None), never as an error. When None, the app's
  behavior is exactly v1.
- All network access is isolated in _request_train_status so tests mock it
  without touching the network.
"""

import json
import re
import urllib.parse
import urllib.request

# Public, unofficial DB endpoint. Terms of use must be confirmed before any
# production use; kept behind a mockable isolation function and fail-closed.
_DB_REST_URL = "https://v6.db.transport.rest/trips"
_REQUEST_TIMEOUT_SECONDS = 5

# A DB train number is a line label like "ICE 123", "IC 2043", "RE4", "S 7".
# Letters (1-4) optionally followed by whitespace and 1-5 digits.
_TRAIN_NUMBER_PATTERN = re.compile(r"^[A-Za-z]{1,4}\s?\d{1,5}$")


def validate_train_number(train_number: str) -> bool:
    """True if train_number looks like a DB line label (e.g. 'ICE 123')."""
    if not train_number:
        return False
    return bool(_TRAIN_NUMBER_PATTERN.match(train_number.strip()))


def _request_train_status(train_number: str) -> dict:
    """Raw network call returning the parsed status payload for a train.

    Isolated so tests can monkeypatch it. Raises on any network/parse error.
    """
    query = f"?lineName={urllib.parse.quote(train_number)}"
    request = urllib.request.Request(
        _DB_REST_URL + query, headers={"User-Agent": "TrainBuffer/1.5"}
    )
    with urllib.request.urlopen(request, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_live_delay(train_number: str) -> dict | None:
    """Return {"currently_delayed": bool, "delay_minutes": int} or None.

    None means "no usable live data" (invalid format, network failure, train
    not found, or malformed response). Never raises.
    """
    if not validate_train_number(train_number):
        return None

    try:
        payload = _request_train_status(train_number)
        delay_minutes = int(payload["delay_minutes"])
    except Exception:
        return None

    if delay_minutes < 0:
        delay_minutes = 0

    return {
        "currently_delayed": delay_minutes > 0,
        "delay_minutes": delay_minutes,
    }


def apply_live_delay_modifier(base_recommendation, live_delay_info: dict | None):
    """Increase the buffer and warn if the train is already delayed.

    No-op (returns the recommendation unchanged) when live_delay_info is None,
    when the train is not currently delayed, or when there is no numeric buffer
    to adjust (e.g. a no_data recommendation). Mutates and returns the passed
    recommendation.
    """
    if live_delay_info is None:
        return base_recommendation
    if not live_delay_info.get("currently_delayed"):
        return base_recommendation
    if base_recommendation.recommended_buffer_minutes is None:
        return base_recommendation

    delay_minutes = int(live_delay_info["delay_minutes"])
    base_recommendation.recommended_buffer_minutes += delay_minutes
    base_recommendation.warnings.append(
        f"Live status: this train is already delayed by {delay_minutes} min "
        "at an earlier stop; buffer increased accordingly."
    )
    return base_recommendation
