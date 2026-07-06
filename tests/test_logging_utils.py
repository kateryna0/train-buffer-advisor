import csv
from datetime import time

from src.logging_utils import LOG_COLUMNS, log_advice
from src.models import BufferRecommendation, TripInput

PERSONAL_FIELDS = {"name", "email", "account_id", "user_id", "ip_address"}


def _trip_input():
    return TripInput(
        origin_station="Berlin Hbf",
        destination_station="Hamburg Hbf",
        planned_arrival_time=time(9, 40),
        arrival_deadline=time(10, 0),
        trip_type="normal",
    )


def _result():
    return BufferRecommendation(
        risk_level="Medium",
        recommended_buffer_minutes=20,
        latest_safe_planned_arrival=time(9, 40),
        is_planned_arrival_safe=True,
        confidence_level="high",
    )


def test_log_row_is_created(tmp_path):
    log_path = tmp_path / "advice_log.csv"
    log_advice(_trip_input(), _result(), str(log_path))

    with open(log_path) as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 1
    assert rows[0]["destination_station"] == "Hamburg Hbf"


def test_log_contains_expected_columns(tmp_path):
    log_path = tmp_path / "advice_log.csv"
    log_advice(_trip_input(), _result(), str(log_path))

    with open(log_path) as f:
        header = next(csv.reader(f))

    assert header == LOG_COLUMNS


def test_no_personal_profile_fields_are_logged():
    assert not (set(LOG_COLUMNS) & PERSONAL_FIELDS)
