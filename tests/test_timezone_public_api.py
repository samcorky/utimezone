from utimezone.timezone import TimeZone
from utimezone.utils import datetime_to_epoch, epoch_to_ymdhms


def test_is_dst_false_for_non_dst_zone() -> None:
    """Ensure fixed-offset zones never report DST."""
    timezone = TimeZone("Africa/Bamako")

    assert timezone.is_dst_at(2026, 1, 15, 12, 0, 0) is False
    assert timezone.is_dst_at(2026, 6, 15, 12, 0, 0) is False


def test_is_dst_at_works_for_northern_hemisphere_zone() -> None:
    """Ensure DST state is correct for zones with start and end in the same year."""
    timezone = TimeZone("Europe/London")

    assert timezone.is_dst_at(2026, 1, 15, 12, 0, 0) is False
    assert timezone.is_dst_at(2026, 6, 15, 12, 0, 0) is True
    assert timezone.is_dst_at(2026, 12, 15, 12, 0, 0) is False


def test_is_dst_at_works_for_southern_hemisphere_zone() -> None:
    """Ensure DST state is correct for zones whose DST season crosses new year."""
    timezone = TimeZone("Pacific/Auckland")

    assert timezone.is_dst_at(2026, 1, 15, 12, 0, 0) is True
    assert timezone.is_dst_at(2026, 6, 15, 12, 0, 0) is False
    assert timezone.is_dst_at(2026, 12, 15, 12, 0, 0) is True


def test_offset_and_name_at_works_for_southern_hemisphere_zone() -> None:
    """Ensure offset and abbreviation switch correctly for southern hemisphere DST."""
    timezone = TimeZone("Pacific/Auckland")

    assert timezone.offset_at(2026, 1, 15, 12, 0, 0) == 13 * 3600
    assert timezone.name_at(2026, 1, 15, 12, 0, 0) == "NZDT"

    assert timezone.offset_at(2026, 6, 15, 12, 0, 0) == 12 * 3600
    assert timezone.name_at(2026, 6, 15, 12, 0, 0) == "NZST"

    assert timezone.offset_at(2026, 12, 15, 12, 0, 0) == 13 * 3600
    assert timezone.name_at(2026, 12, 15, 12, 0, 0) == "NZDT"


def test_is_dst_at_works_for_custom_posix_zone() -> None:
    """Ensure custom POSIX-created zones support DST state queries."""
    timezone = TimeZone.from_posix_timezone_string("EST5EDT,M3.2.0,M11.1.0")

    assert timezone.is_dst_at(2026, 1, 15, 12, 0, 0) is False
    assert timezone.is_dst_at(2026, 6, 15, 12, 0, 0) is True


def test_offset_at_returns_standard_and_dst_offsets() -> None:
    """Ensure tuple-based offset lookup returns the active UTC offset."""
    timezone = TimeZone("Europe/London")

    assert timezone.offset_at(2026, 1, 15, 12, 0, 0) == 0
    assert timezone.offset_at(2026, 6, 15, 12, 0, 0) == 3600


def test_offset_at_for_non_dst_zone_is_always_standard_offset() -> None:
    """Ensure fixed-offset zones always return their standard offset."""
    timezone = TimeZone("Asia/Kolkata")

    assert timezone.offset_at(2026, 1, 15, 12, 0, 0) == 5 * 3600 + 30 * 60
    assert timezone.offset_at(2026, 6, 15, 12, 0, 0) == 5 * 3600 + 30 * 60


def test_name_at_returns_standard_and_dst_names() -> None:
    """Ensure tuple-based name lookup returns the active timezone abbreviation."""
    timezone = TimeZone("Europe/London")

    assert timezone.name_at(2026, 1, 15, 12, 0, 0) == "GMT"
    assert timezone.name_at(2026, 6, 15, 12, 0, 0) == "BST"


def test_name_at_for_non_dst_zone_returns_standard_name() -> None:
    """Ensure fixed-offset zones always return the standard abbreviation."""
    timezone = TimeZone("Africa/Bamako")

    assert timezone.name_at(2026, 1, 15, 12, 0, 0) == "GMT"
    assert timezone.name_at(2026, 6, 15, 12, 0, 0) == "GMT"


def test_repr_contains_iana_name() -> None:
    """Ensure the debug representation includes the IANA timezone name."""
    timezone = TimeZone("Europe/London")

    assert repr(timezone) == "<TimeZone Europe/London>"


def test_utc_datetime_to_local_basic():
    # A straightforward UTC -> local conversion (tuple helpers)
    utc = (2026, 6, 15, 12, 0, 0)
    epoch = datetime_to_epoch(*utc)
    tz = TimeZone("Europe/London")
    expected = tz.utc_epoch_to_local(epoch)
    assert tz.utc_datetime_to_local(utc) == expected


def test_local_datetime_to_utc_basic():
    # A straightforward local -> UTC conversion (tuple helpers)
    local = (2026, 1, 15, 12, 0, 0)
    tz = TimeZone("Europe/London")
    utc_epoch = tz.local_to_utc_epoch(*local)
    expected = epoch_to_ymdhms(int(utc_epoch))
    assert tz.local_datetime_to_utc(local) == expected


def test_local_to_utc_and_back_roundtrip():
    # Non-DST local time should round-trip through UTC (tuple helpers)
    local = (2026, 1, 15, 8, 30, 0)
    tz = TimeZone("Europe/London")
    utc_tuple = tz.local_datetime_to_utc(local)
    back = tz.utc_datetime_to_local(utc_tuple)
    assert back == local


if __name__ == "__main__":
    # This module can be executed directly under MicroPython or CPython.
    # It prints a summary similar to pytest.
    total = 0
    passed = 0
    failed = 0
    failures = []

    # Collect test callables in definition order where possible
    items = list(globals().items())
    for name, obj in items:
        if name.startswith("test_") and callable(obj):
            total += 1
            print("RUN", name)
            try:
                obj()
                passed += 1
                print("  OK")
            except Exception as e:
                failed += 1
                failures.append((name, e))
                print("  FAIL:", name, "->", e)

    print("\n========================")
    print(f"Total: {total}, Passed: {passed}, Failed: {failed}")
    if failed:
        print("\nFailures:")
        for name, exc in failures:
            print(f"- {name}: {exc}")
            try:
                import sys as _sys

                if hasattr(_sys, "print_exception"):
                    # MicroPython: print a full traceback-like message
                    _sys.print_exception(exc)
                else:
                    # Fallback: print repr of exception
                    print(repr(exc))
            except Exception:
                # best-effort, ignore errors printing exception
                pass
        raise SystemExit(1)
    else:
        print("All tests passed.")


