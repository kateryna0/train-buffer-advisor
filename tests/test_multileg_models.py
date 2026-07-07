"""Tests for the v3 multi-leg trip input model (Phase 20a)."""

from datetime import time

import pytest

from src.models import MultiLegTripInput, TripLeg


def _leg(origin, dest, dep=time(8, 0), arr=time(9, 0)):
    return TripLeg(
        origin_station=origin,
        destination_station=dest,
        planned_departure_time=dep,
        planned_arrival_time=arr,
    )


def test_valid_two_leg_trip():
    trip = MultiLegTripInput(
        legs=[
            _leg("Berlin Hbf", "Hannover Hbf"),
            _leg("Hannover Hbf", "Köln Hbf", dep=time(9, 20), arr=time(11, 0)),
        ],
        arrival_deadline=time(11, 30),
        trip_type="normal",
    )
    assert trip.transfer_stations == ["Hannover Hbf"]
    assert trip.final_destination == "Köln Hbf"


def test_three_leg_trip_lists_all_transfer_stations():
    trip = MultiLegTripInput(
        legs=[
            _leg("A", "B"),
            _leg("B", "C"),
            _leg("C", "D"),
        ],
        arrival_deadline=time(12, 0),
        trip_type="normal",
    )
    assert trip.transfer_stations == ["B", "C"]
    assert trip.final_destination == "D"


def test_single_leg_is_rejected():
    with pytest.raises(ValueError):
        MultiLegTripInput(
            legs=[_leg("A", "B")],
            arrival_deadline=time(10, 0),
            trip_type="normal",
        )


def test_non_connecting_legs_are_rejected():
    with pytest.raises(ValueError):
        MultiLegTripInput(
            legs=[_leg("A", "B"), _leg("X", "C")],
            arrival_deadline=time(10, 0),
            trip_type="normal",
        )


def test_invalid_trip_type_is_rejected():
    with pytest.raises(ValueError):
        MultiLegTripInput(
            legs=[_leg("A", "B"), _leg("B", "C")],
            arrival_deadline=time(10, 0),
            trip_type="teleport",
        )


def test_leg_with_same_origin_and_destination_is_rejected():
    with pytest.raises(ValueError):
        _leg("A", "A")


def test_leg_with_empty_station_is_rejected():
    with pytest.raises(ValueError):
        _leg("", "B")
