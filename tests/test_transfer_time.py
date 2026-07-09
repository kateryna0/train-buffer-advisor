"""Tests for Phase 20c: minimum transfer time modeling."""

from src.connection_engine import (
    DEFAULT_MINIMUM_TRANSFER_MINUTES,
    MINIMUM_TRANSFER_MINUTES,
    minimum_transfer_minutes,
)


def test_known_station_uses_table_value():
    assert minimum_transfer_minutes("Frankfurt Hbf") == 12
    assert minimum_transfer_minutes("Hannover Hbf") == 7


def test_unknown_station_uses_default():
    assert (
        minimum_transfer_minutes("Nowhere Bahnhof")
        == DEFAULT_MINIMUM_TRANSFER_MINUTES
    )


def test_default_is_overridable():
    assert minimum_transfer_minutes("Nowhere Bahnhof", default=15) == 15


def test_table_values_are_positive_ints():
    for minutes in MINIMUM_TRANSFER_MINUTES.values():
        assert isinstance(minutes, int)
        assert minutes > 0
