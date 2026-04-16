import pytest

from utimezone.utils import datetime_to_epoch, epoch_to_ymdhms
from utimezone.timezone import TimeZone


@pytest.mark.parametrize(
    "y,m,d,h,mi,s",
    [
        (1970, 1, 1, 0, 0, 0),
        (1971, 3, 1, 12, 34, 56),
        (1999, 12, 31, 23, 59, 59),
        (2000, 2, 29, 23, 59, 59),
        (2004, 2, 29, 6, 7, 8),
        (2100, 3, 1, 0, 0, 0),  # 2100 is not a leap year
        (2400, 2, 29, 12, 0, 0),  # 2400 is a leap year
        (2030, 11, 30, 23, 0, 1),
    ],
)
def test_epoch_to_ymdhms_roundtrip(y, m, d, h, mi, s):
    """datetime_to_epoch -> epoch_to_ymdhms should round-trip for sample dates."""
    epoch = datetime_to_epoch(y, m, d, h, mi, s)
    y2, m2, d2, h2, mi2, s2 = epoch_to_ymdhms(epoch)
    assert (y, m, d, h, mi, s) == (y2, m2, d2, h2, mi2, s2)


def test_utc_epoch_to_local_and_name_and_offset_for_fixed_zone():
    tz = TimeZone("Asia/Kolkata")

    epoch = datetime_to_epoch(2026, 1, 15, 12, 0, 0)  # UTC
    local = tz.utc_epoch_to_local(epoch)

    # UTC 12:00 -> IST 17:30
    assert local == (2026, 1, 15, 17, 30, 0)
    assert tz.name_for_epoch(epoch) == "IST"
    assert tz.offset_for_epoch(epoch) == 5 * 3600 + 30 * 60


def test_utc_epoch_to_local_and_name_and_offset_for_dst_zone():
    tz = TimeZone("Europe/London")

    epoch_winter = datetime_to_epoch(2026, 1, 15, 12, 0, 0)
    assert tz.utc_epoch_to_local(epoch_winter) == (2026, 1, 15, 12, 0, 0)
    assert tz.name_for_epoch(epoch_winter) == "GMT"
    assert tz.offset_for_epoch(epoch_winter) == 0

    epoch_summer = datetime_to_epoch(2026, 6, 15, 12, 0, 0)
    assert tz.utc_epoch_to_local(epoch_summer) == (2026, 6, 15, 13, 0, 0)
    assert tz.name_for_epoch(epoch_summer) == "BST"
    assert tz.offset_for_epoch(epoch_summer) == 3600


def test_local_to_utc_epoch_roundtrip_for_fixed_zone():
    tz = TimeZone("Asia/Kolkata")

    local = (2026, 1, 15, 17, 30, 0)
    utc_epoch = tz.local_to_utc_epoch(*local)
    assert utc_epoch == datetime_to_epoch(2026, 1, 15, 12, 0, 0)


def test_local_to_utc_epoch_roundtrip_for_dst_zone():
    tz = TimeZone("Europe/London")

    # Start from a UTC epoch, convert to local, then back to UTC
    epoch = datetime_to_epoch(2026, 6, 15, 12, 0, 0)
    local = tz.utc_epoch_to_local(epoch)
    epoch_back = tz.local_to_utc_epoch(*local)
    assert epoch_back == epoch


@pytest.mark.parametrize(
    "tz_name, local",
    [
        ("Asia/Kathmandu", (2026, 1, 15, 12, 0, 0)),
        ("Asia/Kolkata", (2026, 1, 15, 12, 0, 0)),
        ("Pacific/Chatham", (2026, 6, 15, 12, 0, 0)),
        ("Australia/Lord_Howe", (2026, 6, 15, 12, 0, 0)),
    ],
)
def test_local_roundtrip_quarter_and_half_hour_offsets(tz_name, local):
    """Ensure zones with quarter/half-hour offsets round-trip local->utc->local."""
    tz = TimeZone(tz_name)
    utc_epoch = tz.local_to_utc_epoch(*local)
    local_back = tz.utc_epoch_to_local(utc_epoch)
    assert local_back == local


def test_from_posix_timezone_string_roundtrip():
    tz = TimeZone.from_posix_timezone_string("EST5EDT,M3.2.0,M11.1.0")
    # Basic properties
    assert tz._std_tz_name == "EST"
    assert tz._dst_tz_name == "EDT"

    # Round-trip a summer time
    epoch = datetime_to_epoch(2026, 6, 15, 12, 0, 0)
    local = tz.utc_epoch_to_local(epoch)
    epoch_back = tz.local_to_utc_epoch(*local)
    assert epoch_back == epoch


