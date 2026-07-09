"""Tests for the data-source transparency copy (UX/trust polish)."""

from src.ui_helpers import data_source_notes


def test_notes_cover_all_four_sources():
    notes = data_source_notes(using_real_data=True)
    joined = " ".join(notes).lower()
    assert "piebro" in joined and "cc by 4.0" in joined  # historical reliability
    assert "open-meteo" in joined  # weather
    assert "db.transport.rest" in joined  # live delay
    assert "manual prototype flag" in joined  # construction


def test_live_delay_and_weather_state_fallback():
    joined = " ".join(data_source_notes(True)).lower()
    assert "fail-closed" in joined
    assert "fallback" in joined


def test_real_vs_sample_reliability_line_differs():
    real = data_source_notes(using_real_data=True)[0]
    sample = data_source_notes(using_real_data=False)[0]
    assert "real aggregated" in real.lower()
    assert "sample dataset" in sample.lower()
    assert real != sample


def test_returns_four_bullets():
    assert len(data_source_notes(True)) == 4
    assert len(data_source_notes(False)) == 4
