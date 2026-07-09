"""Tests for src/data_ingest.py (Phase 23b) using a tiny fixture, not real data."""

import pandas as pd

from src.data_ingest import (
    aggregate_station_stats,
    build_station_stats_csv,
    read_stops,
    write_station_stats_csv,
)
from src.data_loader import load_station_stats
from src.models import StationStats


def _fixture_frame():
    """Per-stop records with known, hand-computed aggregates.

    Berlin Hbf: 6 non-cancelled delays [0,2,4,6,8,20] + 2 cancelled (8 stops).
    Small Halt: 2 non-cancelled delays [1,2], no cancellations (2 stops).
    """
    rows = [
        ("Berlin Hbf", 0, False),
        ("Berlin Hbf", 2, False),
        ("Berlin Hbf", 4, False),
        ("Berlin Hbf", 6, False),
        ("Berlin Hbf", 8, False),
        ("Berlin Hbf", 20, False),
        ("Berlin Hbf", None, True),
        ("Berlin Hbf", None, True),
        ("Small Halt", 1, False),
        ("Small Halt", 2, False),
    ]
    return pd.DataFrame(
        rows, columns=["station_name", "arrival_delay_minutes", "cancelled"]
    )


def _by_name(stats):
    return {s.station_name: s for s in stats}


def test_aggregate_computes_expected_values():
    stats = aggregate_station_stats(_fixture_frame())
    by_name = _by_name(stats)

    berlin = by_name["Berlin Hbf"]
    assert berlin.sample_size == 8
    assert berlin.cancellation_rate == 0.25  # 2 / 8
    assert berlin.late_rate == 0.5  # 3 of 6 (6, 8, 20) >= 6
    assert berlin.avg_delay_minutes == 6.7  # mean of [0,2,4,6,8,20] = 6.667
    assert berlin.p80_delay_minutes == 8.0

    small = by_name["Small Halt"]
    assert small.sample_size == 2
    assert small.cancellation_rate == 0.0
    assert small.late_rate == 0.0
    assert small.avg_delay_minutes == 1.5
    assert small.p80_delay_minutes == 2.0


def test_results_are_valid_stationstats_in_model_ranges():
    for s in aggregate_station_stats(_fixture_frame()):
        assert isinstance(s, StationStats)
        assert 0.0 <= s.late_rate <= 1.0
        assert 0.0 <= s.cancellation_rate <= 1.0
        assert s.sample_size >= 0


def test_late_threshold_boundary_is_inclusive():
    frame = pd.DataFrame(
        [("X", 5, False), ("X", 6, False)],
        columns=["station_name", "arrival_delay_minutes", "cancelled"],
    )
    stats = aggregate_station_stats(frame, late_threshold_minutes=6)
    assert stats[0].late_rate == 0.5  # 6 counts as late, 5 does not


def test_cancelled_stops_excluded_from_delay_metrics():
    # The cancelled row carries a huge delay value that must be ignored.
    frame = pd.DataFrame(
        [("X", 2, False), ("X", 4, False), ("X", 999, True)],
        columns=["station_name", "arrival_delay_minutes", "cancelled"],
    )
    stats = aggregate_station_stats(frame)
    assert stats[0].avg_delay_minutes == 3.0  # (2+4)/2, 999 excluded
    assert stats[0].sample_size == 3
    assert round(stats[0].cancellation_rate, 4) == round(1 / 3, 4)


def test_all_cancelled_station_has_zero_delay_metrics():
    frame = pd.DataFrame(
        [("X", None, True), ("X", None, True)],
        columns=["station_name", "arrival_delay_minutes", "cancelled"],
    )
    stats = aggregate_station_stats(frame)
    s = stats[0]
    assert s.cancellation_rate == 1.0
    assert s.late_rate == 0.0
    assert s.avg_delay_minutes == 0.0
    assert s.p80_delay_minutes == 0.0


def test_min_sample_size_filters_small_stations():
    stats = aggregate_station_stats(_fixture_frame(), min_sample_size=3)
    names = {s.station_name for s in stats}
    assert "Berlin Hbf" in names
    assert "Small Halt" not in names  # only 2 stops


def test_top_n_keeps_busiest_first():
    stats = aggregate_station_stats(_fixture_frame(), top_n=1)
    assert len(stats) == 1
    assert stats[0].station_name == "Berlin Hbf"  # 8 stops > 2


def test_empty_input_returns_empty():
    frame = pd.DataFrame(
        columns=["station_name", "arrival_delay_minutes", "cancelled"]
    )
    assert aggregate_station_stats(frame) == []


def test_read_stops_reads_csv_fixture(tmp_path):
    csv_path = tmp_path / "stops.csv"
    _fixture_frame().to_csv(csv_path, index=False)
    frame = read_stops(csv_path)
    assert len(frame) == 10
    assert "station_name" in frame.columns


def test_build_csv_roundtrips_into_loadable_stationstats(tmp_path):
    input_csv = tmp_path / "stops.csv"
    output_csv = tmp_path / "station_stats.csv"
    _fixture_frame().to_csv(input_csv, index=False)

    build_station_stats_csv(input_csv, output_csv)

    # The generated CSV must load through the unchanged data_loader/model.
    loaded = load_station_stats(str(output_csv))
    assert "Berlin Hbf" in loaded
    berlin = loaded["Berlin Hbf"]
    assert isinstance(berlin, StationStats)
    assert berlin.sample_size == 8
    assert berlin.late_rate == 0.5


def test_write_then_read_preserves_columns(tmp_path):
    stats = aggregate_station_stats(_fixture_frame())
    out = tmp_path / "s.csv"
    write_station_stats_csv(stats, out)
    header = out.read_text().splitlines()[0]
    assert header == (
        "station_name,sample_size,late_rate,cancellation_rate,"
        "avg_delay_minutes,p80_delay_minutes"
    )
