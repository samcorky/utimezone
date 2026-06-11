import pytest

from utimezone import TimeZone
from utimezone.utils import format_iso8601


def test_format_iso8601():
    # Basic positive offset
    assert format_iso8601(2026, 4, 16, 13, 41, 0, 3600) == "2026-04-16T13:41:00+01:00"
    # Basic negative offset
    assert format_iso8601(2026, 4, 16, 13, 41, 0, -18000) == "2026-04-16T13:41:00-05:00"
    # Zero offset (Z handling)
    assert format_iso8601(2026, 4, 16, 13, 41, 0, 0) == "2026-04-16T13:41:00Z"
    # Offset with minutes
    assert format_iso8601(2026, 4, 16, 13, 41, 0, 12600) == "2026-04-16T13:41:00+03:30"


def test_timezone_to_iso8601():
    tz = TimeZone("Europe/London")

    # Winter time (UTC+0)
    # 1736942400 is 2025-01-15 12:00:00 UTC
    epoch_winter = 1736942400
    assert tz.to_iso8601(epoch_winter) == "2025-01-15T12:00:00Z"

    # Summer time (BST, UTC+1)
    # 1752667200 is 2025-07-16 12:00:00 UTC
    epoch_summer = 1752667200
    assert tz.to_iso8601(epoch_summer) == "2025-07-16T13:00:00+01:00"

    # Test components signature
    assert tz.to_iso8601(2025, 1, 15, 12, 0, 0) == "2025-01-15T12:00:00Z"
    assert tz.to_iso8601((2025, 7, 16, 12, 0, 0)) == "2025-07-16T13:00:00+01:00"


def test_timezone_to_iso8601_is_local():
    tz = TimeZone("Europe/London")

    # Local epoch for 2025-07-16 13:00:00
    # UTC epoch was 1752667200, so local epoch is 1752667200 + 3600 = 1752670800
    local_epoch = 1752670800
    assert tz.to_iso8601(local_epoch, is_local=True) == "2025-07-16T13:00:00+01:00"

    # Local components
    assert (
        tz.to_iso8601(2025, 7, 16, 13, 0, 0, is_local=True)
        == "2025-07-16T13:00:00+01:00"
    )
    assert (
        tz.to_iso8601((2025, 7, 16, 13, 0, 0), is_local=True)
        == "2025-07-16T13:00:00+01:00"
    )

    # Positional is_local (not recommended but supported for consistency)
    assert tz.to_iso8601(2025, 7, 16, 13, 0, 0, True) == "2025-07-16T13:00:00+01:00"


@pytest.fixture
def tz_strange():
    return TimeZone.from_posix_timezone_string(
        "<STRANGE++>0:13:47<DST--1>-0:45:13,M2.5.1/-1:30:15,300/25:45:10"
    )


def test_strange_timezone_iso8601(tz_strange):
    # <STRANGE++>0:13:47<DST--1>-0:45:13,M2.5.1/-1:30:15,300/25:45:10
    # Standard offset: -0:13:47 = -827s
    # DST offset: -(-0:45:13) = +2713s

    # A time in standard time
    epoch_std = 1767225600  # 2026-01-01 00:00:00 UTC
    # local = UTC + (-827) = 2025-12-31 23:46:13
    assert tz_strange.to_iso8601(epoch_std) == "2025-12-31T23:46:13-00:13"

    # 1782820800 is 2026-06-30 12:00:00 UTC
    epoch_dst = 1782820800
    # local = UTC + 2713 = 2026-06-30 12:45:13

    iso_dst = tz_strange.to_iso8601(epoch_dst)
    # 2713s = 45m 13s -> +00:45
    assert iso_dst == "2026-06-30T12:45:13+00:45"
