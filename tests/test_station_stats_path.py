"""Phase 23c: real-data preference with sample fallback."""

from src.data_loader import load_station_stats, resolve_station_stats_path


def test_prefers_real_path_when_it_exists(tmp_path):
    real = tmp_path / "station_stats.csv"
    sample = tmp_path / "sample.csv"
    real.write_text("x")
    sample.write_text("x")
    assert resolve_station_stats_path(str(real), str(sample)) == str(real)


def test_falls_back_to_sample_when_real_missing(tmp_path):
    real = tmp_path / "does_not_exist.csv"
    sample = tmp_path / "sample.csv"
    sample.write_text("x")
    assert resolve_station_stats_path(str(real), str(sample)) == str(sample)


def test_real_dataset_loads_as_valid_stationstats():
    # The generated real dataset must load through the unchanged loader/model.
    stats = load_station_stats("data/station_stats.csv")
    assert len(stats) >= 50
    assert "München Hbf" in stats
    munich = stats["München Hbf"]
    assert munich.sample_size > 1000
    assert 0.0 <= munich.late_rate <= 1.0
    assert 0.0 <= munich.cancellation_rate <= 1.0


def test_sample_dataset_still_present_as_fallback():
    stats = load_station_stats("data/sample_station_stats.csv")
    assert len(stats) == 5
