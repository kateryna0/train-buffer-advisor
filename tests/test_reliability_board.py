"""Tests for src/reliability_board.py."""

from src.models import StationStats
from src.reliability_board import compute_reliability_rankings


def _stats(name, late_rate, cancellation_rate):
    return StationStats(
        station_name=name,
        sample_size=100,
        late_rate=late_rate,
        cancellation_rate=cancellation_rate,
        avg_delay_minutes=5,
        p80_delay_minutes=10,
    )


def test_rankings_ordered_worst_first():
    data = {
        "A": _stats("A", 0.10, 0.01),
        "B": _stats("B", 0.40, 0.02),
        "C": _stats("C", 0.25, 0.09),
    }
    rankings = compute_reliability_rankings(data, top_n=3)
    assert rankings["worst_by_late_rate"] == [
        ("B", 0.40),
        ("C", 0.25),
        ("A", 0.10),
    ]
    assert rankings["worst_by_cancellation_rate"] == [
        ("C", 0.09),
        ("B", 0.02),
        ("A", 0.01),
    ]


def test_top_n_limits_results():
    data = {
        "A": _stats("A", 0.10, 0.01),
        "B": _stats("B", 0.40, 0.02),
        "C": _stats("C", 0.25, 0.03),
    }
    rankings = compute_reliability_rankings(data, top_n=2)
    assert rankings["worst_by_late_rate"] == [("B", 0.40), ("C", 0.25)]


def test_ties_broken_deterministically_by_station_name():
    data = {
        "Zeta": _stats("Zeta", 0.30, 0.05),
        "Alpha": _stats("Alpha", 0.30, 0.05),
    }
    rankings = compute_reliability_rankings(data, top_n=2)
    # Equal rates -> alphabetical station name first.
    assert rankings["worst_by_late_rate"] == [("Alpha", 0.30), ("Zeta", 0.30)]
    assert rankings["worst_by_cancellation_rate"] == [
        ("Alpha", 0.05),
        ("Zeta", 0.05),
    ]


def test_empty_dataset_returns_empty_rankings():
    rankings = compute_reliability_rankings({})
    assert rankings["worst_by_late_rate"] == []
    assert rankings["worst_by_cancellation_rate"] == []
