import pytest

from utimezone.timezone import TimeZone
from utimezone.utils import datetime_to_epoch


@pytest.fixture(scope="module")
def tz_strange():
    """
    A hypothetical "StrangeZone" with:
    - STD offset: -827s
    - DST offset: 2713s
    - DST Start: M2.5.1/-1:30:15 (Feb 22, 22:29:45 Standard Time)
    - DST End: 300/25:45:10
      Day 300 of 2026 (non-leap) is Oct 28.
      + 25h 45m 10s = Oct 29, 01:45:10 Local Time (DST).
    """
    return TimeZone.from_posix_timezone_string(
        "<STRANGE++>0:13:47<DST--1>-0:45:13,M2.5.1/-1:30:15,300/25:45:10"
    )


def test_strange_timezone_parsing(tz_strange: TimeZone):
    """Ensure complex but valid POSIX strings are parsed correctly."""
    assert tz_strange._std_tz_name == "<STRANGE++>"
    assert tz_strange._std_offset == -(13 * 60 + 47)

    assert tz_strange._has_dst is True
    assert tz_strange._dst_tz_name == "<DST--1>"
    assert tz_strange._dst_offset == 45 * 60 + 13

    assert tz_strange._dst_start_rule is not None
    assert tz_strange._dst_end_rule is not None

    # DST Start rule M2.5.1/-1:30:15 -> month=2, week=5 (last), weekday=1, seconds=-5415
    assert tz_strange._dst_start_rule.month == 2
    assert tz_strange._dst_start_rule.week == 5
    assert tz_strange._dst_start_rule.weekday == 1
    assert tz_strange._dst_start_rule.seconds == -5415

    # DST End rule 300/25:45:10 -> rule_type='N', day=300, seconds=92710
    assert tz_strange._dst_end_rule.rule_type == "N"
    assert tz_strange._dst_end_rule.day == 300
    assert tz_strange._dst_end_rule.seconds == 92710


def test_strange_timezone_transitions(tz_strange: TimeZone):
    """
    Verify DST transitions for the strange timezone:
    """
    # Quick transition checks for 2026 (non-leap):
    # DST starts around Feb 22 and ends around Oct 28.
    # Before transition (Standard)
    assert tz_strange.is_dst_at(2026, 2, 22, 22, 0, 0) is False
    # After transition (DST)
    assert tz_strange.is_dst_at(2026, 2, 22, 23, 0, 0) is True

    # End rule is unusual (day-of-year plus >24h).
    # We perform simple checks for dates before/after the expected transition.

    # Oct 1 (DST)
    assert tz_strange.is_dst_at(2026, 10, 1, 12, 0, 0) is True
    # Nov 1 (Standard)
    assert tz_strange.is_dst_at(2026, 11, 1, 12, 0, 0) is False

    # Transition happens on Oct 28 approx.
    assert tz_strange.is_dst_at(2026, 10, 27, 12, 0, 0) is True
    assert tz_strange.is_dst_at(2026, 10, 29, 12, 0, 0) is False


def test_strange_timezone_offsets(tz_strange: TimeZone):
    # Jan 1 (Standard)
    assert tz_strange.offset_at(2026, 1, 1, 12, 0, 0) == -827
    assert tz_strange.name_at(2026, 1, 1, 12, 0, 0) == "<STRANGE++>"

    # June 1 (DST)
    assert tz_strange.offset_at(2026, 6, 1, 12, 0, 0) == 2713
    assert tz_strange.name_at(2026, 6, 1, 12, 0, 0) == "<DST--1>"


def test_strange_timezone_fold(tz_strange: TimeZone):
    """
    Test fold behavior in the strange timezone.
    DST End: 300/25:45:10
    In 2026 (non-leap), day 301 is Oct 28.
    Rule 300/25:45:10 -> Oct 28 00:00:00 + 25h 45m 10s = Oct 29 01:45:10.

    STD offset: -827, DST offset: 2713
    Transition at 01:45:10 local DST (01:00:00 - 3s UTC).
    At 01:00:00 UTC (Oct 29), local becomes 01:00:00 + (-827) = 00:46:13.
    It jumps from 01:45:10 local DST back to 00:46:10 local STD.
    The overlapped interval is [00:46:13, 01:45:10].
    """
    # 01:00:00 on Oct 29 is ambiguous.
    t1 = tz_strange.local_to_utc_epoch(2026, 10, 29, 1, 0, 0, fold=False)
    t2 = tz_strange.local_to_utc_epoch(2026, 10, 29, 1, 0, 0, fold=True)

    assert t1 == datetime_to_epoch(2026, 10, 29, 0, 14, 47)
    assert t2 == datetime_to_epoch(2026, 10, 29, 1, 13, 47)


def test_strange_timezone_negative_epoch(tz_strange: TimeZone):
    """Test negative epoch (pre-1970) for the strange timezone."""
    # 1900-01-01 (Standard Time)
    epoch = datetime_to_epoch(1900, 1, 1, 12, 0, 0)
    assert epoch < 0
    assert tz_strange.is_dst(epoch) is False
    assert tz_strange.offset_for_epoch(epoch) == -827

    local = tz_strange.utc_epoch_to_local(epoch)
    # 12:00:00 UTC + (-827s) = 11:46:13
    assert local == (1900, 1, 1, 11, 46, 13)
