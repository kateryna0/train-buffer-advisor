"""TrainBuffer Streamlit UI.

Presentation and orchestration only. All calculations live in src/*.
"""

from datetime import time

import streamlit as st

from src.data_loader import get_station_stats, load_station_stats
from src.logging_utils import log_advice
from src.models import ALLOWED_TRIP_TYPES, TripInput
from src.recommendation import NO_DATA_TEXT, build_recommendation_text
from src.risk_engine import calculate_buffer
from src.time_utils import calculate_latest_safe_arrival, is_planned_arrival_safe
from src.ui_helpers import risk_badge
from src.weather_client import STATION_COORDINATES, get_weather_flags_with_fallback

STATION_STATS_PATH = "data/sample_station_stats.csv"
ADVICE_LOG_PATH = "data/advice_log.csv"

st.set_page_config(page_title="TrainBuffer", page_icon="🚆")

# --- Sidebar explainer ------------------------------------------------------
with st.sidebar:
    st.header("How TrainBuffer works")
    st.markdown(
        "TrainBuffer answers one question: **what is my latest safe planned "
        "arrival, and should I take an earlier train?**"
    )
    st.markdown(
        "- It uses **destination station reliability** as the main historical "
        "signal — it does **not** predict a specific train's delay.\n"
        "- It turns that reliability into a **recommended time buffer** before "
        "your deadline.\n"
        "- Trip type (e.g. airport, interview) and optional weather / "
        "construction conditions make the buffer more conservative.\n"
        "- The result tells you the **latest safe planned arrival** and whether "
        "your planned arrival clears it."
    )
    st.caption(
        "This prototype may log anonymous query inputs locally for evaluation. "
        "No account or personal profile is used."
    )

# --- Header -----------------------------------------------------------------
st.title("🚆 TrainBuffer")
st.caption(
    "Deadline-based buffer advisor for German train trips. "
    "It does not predict exact train delays."
)

station_stats = load_station_stats(STATION_STATS_PATH)

# --- Input form -------------------------------------------------------------
with st.form("trip_form"):
    col1, col2 = st.columns(2)
    with col1:
        origin_station = st.text_input("Origin station", value="Berlin Hbf")
        planned_arrival_time = st.time_input(
            "Planned arrival time", value=time(9, 40)
        )
        trip_type = st.selectbox("Trip type", sorted(ALLOWED_TRIP_TYPES))
    with col2:
        destination_station = st.text_input(
            "Destination station", value="Hamburg Hbf"
        )
        arrival_deadline = st.time_input("Arrival deadline", value=time(10, 0))

    with st.expander("Advanced conditions (optional)"):
        st.caption(
            "Set these only if you already know the conditions on your route. "
            "Leaving them untouched keeps the base recommendation."
        )
        st.write("**Weather**")
        st.caption(
            "Weather is looked up automatically from a live source for the "
            "destination station. Enable manual override only if the live "
            "source is down or you know the conditions."
        )
        manual_weather_override = st.checkbox("Override weather manually")
        wcol1, wcol2, wcol3 = st.columns(3)
        with wcol1:
            manual_strong_wind = st.checkbox("💨 Strong wind")
        with wcol2:
            manual_heat = st.checkbox("🌡️ Heat")
        with wcol3:
            manual_snow_ice = st.checkbox("❄️ Snow or ice")
        construction = st.selectbox(
            "🚧 Known construction/disruption on route?",
            ["no", "yes", "unknown"],
        )

    submitted = st.form_submit_button("Get advice")

# --- Result -----------------------------------------------------------------
if submitted:
    if not origin_station or not destination_station:
        st.error("Please enter both an origin and a destination station.")
    else:
        trip_input = TripInput(
            origin_station=origin_station,
            destination_station=destination_station,
            planned_arrival_time=planned_arrival_time,
            arrival_deadline=arrival_deadline,
            trip_type=trip_type,
        )

        stats = get_station_stats(destination_station, station_stats)

        if stats is None:
            badge = risk_badge("no_data")
            st.subheader("Result")
            st.markdown(
                f"<span style='background:{badge['color']};color:white;"
                f"padding:4px 12px;border-radius:12px;font-weight:600;'>"
                f"{badge['emoji']} {badge['label']}</span>",
                unsafe_allow_html=True,
            )
            st.warning(NO_DATA_TEXT)
        else:
            # Resolve weather flags: manual override wins; otherwise use the
            # live source, which degrades to all-False if unavailable.
            if manual_weather_override:
                strong_wind = manual_strong_wind
                heat = manual_heat
                snow_ice = manual_snow_ice
                weather_caption = "Weather source: manual override"
            else:
                weather = get_weather_flags_with_fallback(
                    destination_station, STATION_COORDINATES
                )
                strong_wind = weather["strong_wind"]
                heat = weather["heat"]
                snow_ice = weather["snow_ice"]
                weather_caption = (
                    "Weather source: live"
                    if weather["source"] == "live"
                    else "Weather source: unavailable"
                )

            result = calculate_buffer(
                trip_input,
                stats,
                strong_wind=strong_wind,
                heat=heat,
                snow_ice=snow_ice,
                construction=construction,
            )
            result.latest_safe_planned_arrival = calculate_latest_safe_arrival(
                arrival_deadline, result.recommended_buffer_minutes
            )
            result.is_planned_arrival_safe = is_planned_arrival_safe(
                planned_arrival_time, result.latest_safe_planned_arrival
            )

            log_advice(trip_input, result, ADVICE_LOG_PATH)

            badge = risk_badge(result.risk_level)

            st.subheader("Result")
            st.markdown(
                f"<span style='background:{badge['color']};color:white;"
                f"padding:4px 12px;border-radius:12px;font-weight:600;'>"
                f"{badge['emoji']} {badge['label']}</span>",
                unsafe_allow_html=True,
            )

            safe = result.is_planned_arrival_safe
            rcol1, rcol2 = st.columns(2)
            with rcol1:
                st.metric(
                    "Recommended buffer",
                    f"{result.recommended_buffer_minutes} min",
                )
                st.metric(
                    "Latest safe planned arrival",
                    result.latest_safe_planned_arrival.strftime("%H:%M"),
                )
            with rcol2:
                st.metric(
                    "Planned arrival safe?",
                    "✅ Yes" if safe else "⚠️ No",
                )
                st.metric("Confidence level", result.confidence_level)

            st.caption(weather_caption)

            if safe:
                st.success(build_recommendation_text(trip_input, result))
            else:
                st.error(build_recommendation_text(trip_input, result))

            if result.reasons:
                with st.expander("Reasons", expanded=True):
                    for reason in result.reasons:
                        st.write(f"- {reason}")

            if result.warnings:
                for warning in result.warnings:
                    st.warning(warning)

            with st.expander("Data sources"):
                for source in result.data_sources:
                    st.caption(source)
