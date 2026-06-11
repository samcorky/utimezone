import gc
import sys

from utimezone.db import (
    _CACHE,
    _MAX_CACHE_SIZE,
    _get_all_iana_names,
    get_posix_rule_for_iana_name,
)


def test_cache_memory_eviction():
    """Cache does not grow without bound."""
    _CACHE.clear()

    iana_names = _get_all_iana_names()
    test_names = iana_names[: _MAX_CACHE_SIZE + 5]

    for name in test_names:
        get_posix_rule_for_iana_name(name)

    assert 0 < len(_CACHE) <= _MAX_CACHE_SIZE


def test_memory_usage_basic():
    """Create and drop many TimeZone objects; ensure no large leak."""
    gc.collect()

    from utimezone.timezone import TimeZone

    iana_names = _get_all_iana_names()
    if not iana_names:
        return

    initial_objects = len(gc.get_objects())

    zones = [TimeZone(iana_names[i % len(iana_names)]) for i in range(100)]

    assert len(gc.get_objects()) > initial_objects

    del zones
    gc.collect()

    after_cleanup = len(gc.get_objects())
    assert after_cleanup <= initial_objects + 10


def test_size_of_cache_entries():
    """Cache keys/values are reasonably small strings."""
    _CACHE.clear()
    get_posix_rule_for_iana_name("America/New_York")

    for key, value in _CACHE.items():
        if hasattr(sys, "getsizeof"):
            assert sys.getsizeof(key) < 128
            assert sys.getsizeof(value) < 128

        assert len(key) < 64
        assert len(value) < 128


def test_memory_usage_iteration():
    """Iterate a timezone across 1 hour and ensure no obvious leak."""
    gc.collect()
    initial_objects = len(gc.get_objects())

    from utimezone.timezone import TimeZone
    from utimezone.utils import datetime_to_epoch

    zone = TimeZone("Europe/London")
    start_epoch = datetime_to_epoch(2023, 1, 1, 0, 0, 0)

    for i in range(3600):
        iso_str = zone.to_iso8601(start_epoch + i)
        assert iso_str.startswith("2023-01-01T")

    del zone
    gc.collect()

    after_cleanup = len(gc.get_objects())
    assert after_cleanup <= initial_objects + 20
