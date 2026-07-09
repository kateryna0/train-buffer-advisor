"""Tests for src/cache_utils.TimedCache (Phase 22)."""

import pytest

from src.cache_utils import TimedCache


class _Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def test_value_cached_within_ttl_producer_called_once():
    calls = []

    def producer():
        calls.append(1)
        return "v"

    cache = TimedCache(ttl_seconds=100, clock=_Clock())
    assert cache.get_or_call("k", producer) == "v"
    assert cache.get_or_call("k", producer) == "v"
    assert len(calls) == 1


def test_value_recomputed_after_ttl_expires():
    clock = _Clock()
    calls = []

    def producer():
        calls.append(1)
        return len(calls)

    cache = TimedCache(ttl_seconds=10, clock=clock)
    assert cache.get_or_call("k", producer) == 1
    clock.now = 11  # past TTL
    assert cache.get_or_call("k", producer) == 2
    assert len(calls) == 2


def test_exception_is_not_cached():
    state = {"fail": True}

    def producer():
        if state["fail"]:
            raise ConnectionError("boom")
        return "ok"

    cache = TimedCache(ttl_seconds=100, clock=_Clock())
    with pytest.raises(ConnectionError):
        cache.get_or_call("k", producer)
    # Failure was not stored, so a later success is returned, not a cached error.
    state["fail"] = False
    assert cache.get_or_call("k", producer) == "ok"


def test_different_keys_cached_separately():
    cache = TimedCache(ttl_seconds=100, clock=_Clock())
    assert cache.get_or_call("a", lambda: 1) == 1
    assert cache.get_or_call("b", lambda: 2) == 2
    assert cache.get_or_call("a", lambda: 99) == 1  # still cached


def test_clear_forces_recompute():
    calls = []
    cache = TimedCache(ttl_seconds=100, clock=_Clock())
    cache.get_or_call("k", lambda: calls.append(1))
    cache.clear()
    cache.get_or_call("k", lambda: calls.append(1))
    assert len(calls) == 2
