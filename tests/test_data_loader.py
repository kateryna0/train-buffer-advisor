from src.data_loader import get_station_stats, load_station_stats
from src.models import StationStats
from src.risk_engine import calculate_confidence

CSV_PATH = "data/sample_station_stats.csv"


def test_csv_loads_correctly():
    stats = load_station_stats(CSV_PATH)
    assert "Hamburg Hbf" in stats
    assert isinstance(stats["Hamburg Hbf"], StationStats)
    assert len(stats) == 5


def test_known_station_returns_station_stats():
    stats = load_station_stats(CSV_PATH)
    result = get_station_stats("Berlin Hbf", stats)
    assert result is not None
    assert result.station_name == "Berlin Hbf"
    assert result.sample_size == 300


def test_unknown_station_returns_none():
    stats = load_station_stats(CSV_PATH)
    result = get_station_stats("Nonexistent Station", stats)
    assert result is None


def test_small_station_triggers_no_data_through_risk_engine():
    stats = load_station_stats(CSV_PATH)
    small_station = get_station_stats("Small Station", stats)
    assert small_station.sample_size < 20
    assert calculate_confidence(small_station.sample_size) == "no_data"
