from datetime import time

from src.time_utils import calculate_latest_safe_arrival, is_planned_arrival_safe


# --- Feature 4.1 — calculate latest safe planned arrival ---

def test_latest_safe_arrival_10_00_minus_35():
    assert calculate_latest_safe_arrival(time(10, 0), 35) == time(9, 25)


def test_latest_safe_arrival_09_00_minus_20():
    assert calculate_latest_safe_arrival(time(9, 0), 20) == time(8, 40)


def test_latest_safe_arrival_midnight_edge_case():
    assert calculate_latest_safe_arrival(time(0, 30), 45) == time(23, 45)


# --- Feature 4.2 — compare planned arrival with latest safe arrival ---

def test_planned_arrival_before_safe_time_is_safe():
    assert is_planned_arrival_safe(time(9, 20), time(9, 25)) is True


def test_planned_arrival_exactly_at_safe_time_is_safe():
    assert is_planned_arrival_safe(time(9, 25), time(9, 25)) is True


def test_planned_arrival_after_safe_time_is_risky():
    assert is_planned_arrival_safe(time(9, 30), time(9, 25)) is False
