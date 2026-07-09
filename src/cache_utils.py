"""A tiny time-based cache for live API calls.

Kept dependency-free and testable (injectable clock). Only *successful*
producer results are cached: if the producer raises, the exception propagates
and nothing is stored, so a transient failure is never remembered as a
permanent one and the caller's fail-closed fallback still works.
"""

import time as _time


class TimedCache:
    """Caches values by key for `ttl_seconds`; caches successes only."""

    def __init__(self, ttl_seconds: float, clock=_time.monotonic):
        self.ttl_seconds = ttl_seconds
        self._clock = clock
        self._store: dict = {}

    def get_or_call(self, key, producer):
        """Return the cached value for `key`, or call `producer()` and cache it.

        A fresh (non-expired) cached value is returned without calling
        `producer`. Otherwise `producer()` is called; its return value is cached
        and returned. If `producer()` raises, the error propagates and nothing
        is cached.
        """
        now = self._clock()
        entry = self._store.get(key)
        if entry is not None and entry[0] > now:
            return entry[1]

        value = producer()  # exceptions propagate; not cached
        self._store[key] = (now + self.ttl_seconds, value)
        return value

    def clear(self) -> None:
        self._store.clear()
