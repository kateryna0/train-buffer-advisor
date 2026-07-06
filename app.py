"""TrainBuffer Streamlit UI."""

from datetime import time

import streamlit as st

from src.data_loader import get_station_stats, load_station_stats
from src.logging_utils import log_advice
from src.models import ALLOWED_TRIP_TYPES, TripInput
from src.recommendation import build_recommendation_text
from src.risk_engine import calculate_buffer
from src.time_utils import calculate_latest_safe_arrival, is_planned_arrival_safe

STATION_STATS_PATH = "data/sample_station_stats.csv"
ADVICE_LOG_PATH = "data/advice_log.csv"

st.set_page_config(page_title="TrainBuffer", page_icon="🚆")

st.title("TrainBuffer")
st.caption(
    "TrainBuffer v1 uses destination station reliability as the main "
    "historical signal. It does not predict exact train delays."
)
st.caption(
    "This prototype may log anonymous query inputs locally for evaluation. "
    "No account or personal profile is used."
)

station_stats = load_station_stats(STATION_STATS_PATH)

with st.form("trip_form"):
    origin_station = st.text_input("Origin station", value="Berlin Hbf")
    destination_station = st.text_input("Destination station", value="Hamburg Hbf")
    planned_arrival_time = st.time_input("Planned arrival time", value=time(9, 40))
    arrival_deadline = st.time_input("Arrival deadline", value=time(10, 0))
    trip_type = st.selectbox("Trip type", sorted(ALLOWED_TRIP_TYPES))
    st.write("Weather conditions (optional)")
    strong_wind = st.checkbox("Strong wind?")
    heat = st.checkbox("Heat?")
    snow_ice = st.checkbox("Snow or ice?")
    construction = st.selectbox(
        "Known construction/disruption on route?", ["no", "yes", "unknown"]
    )
    submitted = st.form_submit_button("Get advice")

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
            st.subheader("No data")
            st.warning(
                "There is not enough historical data for this destination "
                "station to make a reliable recommendation. Please check DB "
                "Navigator before departure and plan conservatively."
            )
        else:
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

            st.subheader("Result")
            st.metric("Risk level", result.risk_level)
            st.metric("Recommended buffer", f"{result.recommended_buffer_minutes} min")
            st.metric(
                "Latest safe planned arrival",
                result.latest_safe_planned_arrival.strftime("%H:%M"),
            )
            st.metric(
                "Is planned arrival safe?",
                "Yes" if result.is_planned_arrival_safe else "No",
            )
            st.metric("Confidence level", result.confidence_level)

            st.write(build_recommendation_text(trip_input, result))

            if result.reasons:
                st.write("**Reasons:**")
                for reason in result.reasons:
                    st.write(f"- {reason}")

            if result.warnings:
                st.write("**Warnings:**")
                for warning in result.warnings:
                    st.warning(warning)

            st.write("**Data sources:**")
            for source in result.data_sources:
                st.caption(source)
