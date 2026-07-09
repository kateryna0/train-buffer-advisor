"""Pure presentation helpers for the Streamlit UI.

These functions contain no business logic — they only translate engine
outputs (e.g. risk_level strings) into display attributes such as colors
and icons. Keeping them here (instead of inline in app.py) keeps app.py
thin and lets the presentation mapping be unit-tested.
"""

# Maps a risk_level produced by src/risk_engine.py to a display badge.
# color is a hex string suitable for inline HTML styling; emoji and label
# are for at-a-glance reading. "no_data" is a distinct, neutral grey badge.
_RISK_BADGES = {
    "Low": {"color": "#1a7f37", "emoji": "🟢", "label": "Low risk"},
    "Medium": {"color": "#bf8700", "emoji": "🟡", "label": "Medium risk"},
    "High": {"color": "#cf222e", "emoji": "🔴", "label": "High risk"},
    "no_data": {"color": "#6e7781", "emoji": "⚪", "label": "No data"},
}

# Fallback badge for any unexpected/unknown risk_level value.
_UNKNOWN_BADGE = {"color": "#6e7781", "emoji": "⚪", "label": "Unknown"}


def risk_badge(risk_level: str) -> dict:
    """Return display attributes for a risk_level.

    Args:
        risk_level: one of "Low", "Medium", "High", "no_data".

    Returns:
        A dict with keys "color" (hex string), "emoji", and "label".
        Unknown inputs return a neutral grey "Unknown" badge rather than
        raising, so the UI never crashes on an unexpected value.
    """
    return _RISK_BADGES.get(risk_level, _UNKNOWN_BADGE)


def data_source_notes(using_real_data: bool) -> list[str]:
    """Return short markdown bullets describing what the recommendation uses.

    Presentation-only transparency copy for the "What this uses" info box. The
    historical-reliability line reflects whether the real dataset or the sample
    fallback is currently loaded.
    """
    if using_real_data:
        reliability = (
            "**Historical reliability:** real aggregated Deutsche Bahn statistics "
            "(piebro/deutsche-bahn-data, CC BY 4.0)."
        )
    else:
        reliability = (
            "**Historical reliability:** built-in sample dataset (5 stations) — the "
            "real Deutsche Bahn statistics (piebro/deutsche-bahn-data, CC BY 4.0) "
            "are not currently loaded."
        )
    return [
        reliability,
        "**Weather:** Open-Meteo live lookup, with fallback to no adjustment / "
        "manual override if unavailable.",
        "**Live delay:** optional train-number check via db.transport.rest, "
        "fail-closed if unavailable.",
        "**Construction/disruption:** manual prototype flag only — not an "
        "automatic live source yet.",
    ]
