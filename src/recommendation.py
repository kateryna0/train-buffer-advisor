"""Customer-native recommendation text."""

from datetime import time

from src.models import BufferRecommendation, TripInput

TRIP_TYPE_LABELS = {
    "normal": "trip",
    "airport": "airport trip",
    "interview_exam": "interview/exam",
    "government_visa_medical": "government/visa/medical appointment",
    "transfer": "transfer trip",
}

NO_DATA_TEXT = (
    "There is not enough historical data for this destination station to make "
    "a reliable recommendation. Please check DB Navigator before departure and "
    "plan conservatively."
)

TRANSFER_TEXT = (
    "Transfer trips are not fully supported in TrainBuffer v1. Use this result "
    "as a rough warning only and check your connection in DB Navigator."
)


def build_recommendation_text(trip_input: TripInput, result: BufferRecommendation) -> str:
    if result.confidence_level == "no_data":
        return NO_DATA_TEXT

    if trip_input.trip_type == "transfer":
        return TRANSFER_TEXT

    trip_label = TRIP_TYPE_LABELS.get(trip_input.trip_type, "trip")
    article = "an" if trip_label[0] in "aeiou" else "a"

    if result.is_planned_arrival_safe is False:
        text = (
            f"Your planned arrival is risky for {article} {trip_label}. "
            f"Aim to arrive at least {result.recommended_buffer_minutes} minutes "
            "before your deadline. If possible, choose a train that arrives one "
            "connection earlier than planned."
        )
    else:
        text = (
            f"Your planned arrival looks acceptable for {article} {trip_label}. "
            f"A {result.recommended_buffer_minutes}-minute buffer is recommended "
            "based on the available station reliability data."
        )

    if trip_input.trip_type == "airport":
        text += (
            " Note: this buffer does not include security, baggage drop, or "
            "walking time inside the airport."
        )

    return text


CONNECTION_NO_DATA_CAVEAT = (
    " This is based on the schedule only — there is no historical delay data "
    "for the first leg, so treat it as a rough guide and check DB Navigator."
)


def build_connection_message(
    connection_risk: dict, next_departure_time: time | None = None
) -> str:
    """Customer-facing message for a transfer, incl. next-train fallback (20e).

    Args:
        connection_risk: the dict returned by
            src.connection_engine.compute_connection_risk.
        next_departure_time: optional planned departure of the next train after
            the connection; used to phrase the fallback for a likely miss.

    Returns:
        A plain-language message tuned to the connection_risk_level. A High/
        likely-missed connection gets explicit next-train fallback guidance;
        Medium warns to have a fallback in mind; Low reassures. When the leg-1
        estimate had no data, a caveat is appended.
    """
    station = connection_risk["transfer_station"]
    level = connection_risk["connection_risk_level"]
    minimum = connection_risk["minimum_transfer_minutes"]
    expected_delay = connection_risk["expected_leg1_delay_minutes"]
    p80_delay = connection_risk["p80_leg1_delay_minutes"]
    expected_slack = connection_risk["expected_transfer_slack_minutes"]

    if level == "High":
        fallback = (
            f" Plan for the next departure at {next_departure_time.strftime('%H:%M')}"
            if next_departure_time is not None
            else " Take an earlier first train, or plan for the next departure."
        )
        text = (
            f"High risk of missing your transfer at {station}. A typical delay "
            f"(~{expected_delay} min) would leave less than the {minimum} min "
            f"needed to change trains.{fallback}"
        )
    elif level == "Medium":
        text = (
            f"Your transfer at {station} is tight. It should work if the first "
            f"leg is roughly on time, but a bad delay (~{p80_delay} min) would "
            "make you miss it — have a fallback connection in mind."
        )
    else:
        text = (
            f"Your transfer at {station} looks safe, with about {expected_slack} "
            "min of slack after the minimum change time, even allowing for a "
            "typical delay."
        )

    if not connection_risk.get("has_data", True):
        text += CONNECTION_NO_DATA_CAVEAT

    return text
