"""Customer-native recommendation text."""

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
