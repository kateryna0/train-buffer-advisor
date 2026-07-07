"""Tests for the pure presentation helpers in src/ui_helpers.py."""

from src.ui_helpers import risk_badge


def test_low_risk_badge_is_green():
    badge = risk_badge("Low")
    assert badge["color"] == "#1a7f37"
    assert badge["emoji"] == "🟢"
    assert badge["label"] == "Low risk"


def test_medium_risk_badge_is_amber():
    badge = risk_badge("Medium")
    assert badge["color"] == "#bf8700"
    assert badge["emoji"] == "🟡"
    assert badge["label"] == "Medium risk"


def test_high_risk_badge_is_red():
    badge = risk_badge("High")
    assert badge["color"] == "#cf222e"
    assert badge["emoji"] == "🔴"
    assert badge["label"] == "High risk"


def test_no_data_badge_is_neutral_grey():
    badge = risk_badge("no_data")
    assert badge["color"] == "#6e7781"
    assert badge["label"] == "No data"


def test_unknown_risk_level_returns_neutral_fallback_without_raising():
    badge = risk_badge("something_unexpected")
    assert badge["label"] == "Unknown"
    assert badge["color"] == "#6e7781"


def test_every_badge_has_required_keys():
    for level in ("Low", "Medium", "High", "no_data"):
        badge = risk_badge(level)
        assert set(badge.keys()) == {"color", "emoji", "label"}
