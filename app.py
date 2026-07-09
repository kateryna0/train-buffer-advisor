"""TrainBuffer Streamlit UI.

Presentation and orchestration only. All calculations live in src/*.
"""

import os
from datetime import datetime, time

import streamlit as st

from src.connection_engine import compute_connection_risk, estimate_leg_arrival_delay
from src.data_loader import (
    get_station_stats,
    load_station_stats,
    resolve_station_stats_path,
)
from src.live_delay_client import apply_live_delay_modifier, fetch_live_delay
from src.logging_utils import log_advice
from src.models import ALLOWED_TRIP_TYPES, MultiLegTripInput, TripInput, TripLeg
from src.recommendation import (
    NO_DATA_TEXT,
    build_connection_message,
    build_recommendation_text,
)
from src.reliability_board import compute_reliability_rankings
from src.risk_engine import calculate_buffer
from src.time_utils import calculate_latest_safe_arrival, is_planned_arrival_safe
from src.ui_helpers import risk_badge
from src.weather_client import STATION_COORDINATES, get_weather_flags_with_fallback

REAL_STATION_STATS_PATH = "data/station_stats.csv"
SAMPLE_STATION_STATS_PATH = "data/sample_station_stats.csv"
# Prefer real aggregated data; fall back to the committed sample if absent.
STATION_STATS_PATH = resolve_station_stats_path(
    REAL_STATION_STATS_PATH, SAMPLE_STATION_STATS_PATH
)
USING_REAL_DATA = STATION_STATS_PATH == REAL_STATION_STATS_PATH
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

advisor_tab, connection_tab, board_tab = st.tabs(
    ["Trip advisor", "Connection mode", "Reliability board"]
)

# --- Trip advisor -----------------------------------------------------------
with advisor_tab:
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
            train_number = st.text_input(
                "Train number (optional, e.g. ICE 123)", value=""
            )

        with st.expander("Advanced conditions (optional)"):
            st.caption(
                "Set these only if you already know the conditions on your "
                "route. Leaving them untouched keeps the base recommendation."
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

                # Optional live upstream delay check. Fails closed to v1
                # behavior: a blank/invalid number or an unavailable API yields
                # None (no-op).
                live_delay_info = None
                live_status_caption = None
                if train_number.strip():
                    live_delay_info = fetch_live_delay(train_number)
                    result = apply_live_delay_modifier(result, live_delay_info)
                    if live_delay_info is None:
                        live_status_caption = "Live status: unavailable"
                    elif live_delay_info["currently_delayed"]:
                        live_status_caption = (
                            f"Live status: delayed by "
                            f"{live_delay_info['delay_minutes']} min"
                        )
                    else:
                        live_status_caption = "Live status: on time"

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
                if live_status_caption:
                    st.caption(live_status_caption)

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

# --- Connection mode (v3) ---------------------------------------------------
with connection_tab:
    st.subheader("Will I make my transfer?")
    st.caption(
        "Estimates the risk of missing a transfer by combining the first leg's "
        "historical arrival delay with the scheduled transfer time. Uses static "
        "reliability data; check DB Navigator for live times."
    )

    with st.form("connection_form"):
        st.write("**Leg 1**")
        c1, c2 = st.columns(2)
        with c1:
            leg1_origin = st.text_input("Leg 1 origin", value="Berlin Hbf")
            leg1_departure = st.time_input("Leg 1 departure", value=time(8, 0))
        with c2:
            leg1_destination = st.text_input(
                "Transfer station (leg 1 destination)", value="Hamburg Hbf"
            )
            leg1_arrival = st.time_input("Leg 1 arrival", value=time(9, 40))

        st.write("**Leg 2**")
        c3, c4 = st.columns(2)
        with c3:
            leg2_destination = st.text_input(
                "Final destination (leg 2)", value="Köln Hbf"
            )
            leg2_departure = st.time_input("Leg 2 departure", value=time(9, 55))
        with c4:
            conn_trip_type = st.selectbox(
                "Trip type", sorted(ALLOWED_TRIP_TYPES), key="conn_trip_type"
            )
            leg2_arrival = st.time_input("Leg 2 arrival", value=time(11, 30))

        conn_submitted = st.form_submit_button("Check connection")

    if conn_submitted:
        try:
            leg1 = TripLeg(
                origin_station=leg1_origin,
                destination_station=leg1_destination,
                planned_departure_time=leg1_departure,
                planned_arrival_time=leg1_arrival,
            )
            leg2 = TripLeg(
                origin_station=leg1_destination,
                destination_station=leg2_destination,
                planned_departure_time=leg2_departure,
                planned_arrival_time=leg2_arrival,
            )
            trip = MultiLegTripInput(
                legs=[leg1, leg2],
                arrival_deadline=leg2_arrival,
                trip_type=conn_trip_type,
            )
        except ValueError as exc:
            st.error(f"Invalid connecting trip: {exc}")
        else:
            transfer_stats = get_station_stats(
                leg1.destination_station, station_stats
            )
            leg1_delay = estimate_leg_arrival_delay(leg1, transfer_stats)
            connection_risk = compute_connection_risk(leg1, leg2, leg1_delay)

            badge = risk_badge(connection_risk["connection_risk_level"])
            st.markdown(
                f"<span style='background:{badge['color']};color:white;"
                f"padding:4px 12px;border-radius:12px;font-weight:600;'>"
                f"{badge['emoji']} Connection: {badge['label']}</span>",
                unsafe_allow_html=True,
            )

            mcol1, mcol2 = st.columns(2)
            with mcol1:
                st.metric(
                    "Scheduled transfer",
                    f"{connection_risk['scheduled_transfer_minutes']} min",
                )
                st.metric(
                    "Minimum needed",
                    f"{connection_risk['minimum_transfer_minutes']} min",
                )
            with mcol2:
                st.metric(
                    "Expected leg-1 delay",
                    f"{connection_risk['expected_leg1_delay_minutes']} min",
                )
                st.metric(
                    "Slack (typical)",
                    f"{connection_risk['expected_transfer_slack_minutes']} min",
                )

            message = build_connection_message(connection_risk)
            if connection_risk["connection_risk_level"] == "High":
                st.error(message)
            elif connection_risk["connection_risk_level"] == "Medium":
                st.warning(message)
            else:
                st.success(message)

            if not connection_risk["has_data"]:
                st.caption(
                    "No historical delay data for the transfer station; result "
                    "is schedule-only and low-confidence."
                )

# --- Reliability board ------------------------------------------------------
with board_tab:
    st.subheader("Reliability board")
    st.caption(
        "Aggregate view of the least reliable stations in the current dataset. "
        "Higher rates are worse."
    )

    rankings = compute_reliability_rankings(station_stats)

    bcol1, bcol2 = st.columns(2)
    with bcol1:
        st.write("**Worst by late rate**")
        if rankings["worst_by_late_rate"]:
            for name, rate in rankings["worst_by_late_rate"]:
                st.write(f"- {name}: {rate:.0%}")
        else:
            st.caption("No stations in dataset.")
    with bcol2:
        st.write("**Worst by cancellation rate**")
        if rankings["worst_by_cancellation_rate"]:
            for name, rate in rankings["worst_by_cancellation_rate"]:
                st.write(f"- {name}: {rate:.0%}")
        else:
            st.caption("No stations in dataset.")

    # Data source + freshness indicator.
    if USING_REAL_DATA:
        st.caption(
            "Data source: real aggregated Deutsche Bahn statistics "
            "(CC BY 4.0, via piebro/deutsche-bahn-data)."
        )
    else:
        st.caption("Data source: built-in sample dataset (5 stations).")
    try:
        updated_at = datetime.fromtimestamp(
            os.path.getmtime(STATION_STATS_PATH)
        ).strftime("%Y-%m-%d %H:%M")
        st.caption(f"Dataset file last updated: {updated_at}")
    except OSError:
        st.caption("Dataset file last updated: unknown")

    st.caption(
        "Construction/disruption remains a manual per-trip flag in the advisor: "
        "no low-complexity, stable free source was confirmed feasible for v2, "
        "so the manual flag is kept and this decision is documented in "
        "docs/progress.md."
    )
