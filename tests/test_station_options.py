"""Tests for the station-picker helpers (UX polish)."""

from src.data_loader import (
    default_option_index,
    load_station_stats,
    station_names,
)
from src.models import StationStats


def _stats(names):
    return {
        n: StationStats(
            station_name=n,
            sample_size=100,
            late_rate=0.1,
            cancellation_rate=0.0,
            avg_delay_minutes=3,
            p80_delay_minutes=6,
        )
        for n in names
    }


def test_station_names_sorted():
    stats = _stats(["Köln Hbf", "Aachen Hbf", "Berlin Hauptbahnhof"])
    assert station_names(stats) == [
        "Aachen Hbf",
        "Berlin Hauptbahnhof",
        "Köln Hbf",
    ]


def test_station_names_empty():
    assert station_names({}) == []


def test_default_option_index_found():
    options = ["Aachen Hbf", "Berlin Hauptbahnhof", "Köln Hbf"]
    assert default_option_index(options, "Köln Hbf") == 2


def test_default_option_index_missing_returns_zero():
    options = ["Aachen Hbf", "Köln Hbf"]
    assert default_option_index(options, "Berlin Hbf") == 0


def test_default_option_index_empty_options_returns_zero():
    assert default_option_index([], "anything") == 0


def test_real_dataset_station_options_include_known_stations():
    stats = load_station_stats("data/station_stats.csv")
    options = station_names(stats)
    assert len(options) == 100
    # The real dataset uses "Berlin Hauptbahnhof", not "Berlin Hbf".
    assert "Berlin Hauptbahnhof" in options
    assert "Köln Hbf" in options
    assert options == sorted(options)
