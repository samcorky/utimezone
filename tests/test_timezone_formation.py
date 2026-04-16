import pytest

from utimezone.timezone import TimeZone


def test_timezone_parses_fixed_offset_zone() -> None:
    """Ensure a timezone without DST is parsed into standard-only fields."""
    timezone = TimeZone("Africa/Bamako")

    assert timezone.iana_timezone_name == "Africa/Bamako"
    assert timezone._posix_timezone_string == "GMT0"

    assert timezone._std_tz_name == "GMT"
    assert timezone._std_offset == 0

    assert timezone._has_dst is False
    assert timezone._dst_tz_name is None
    assert timezone._dst_offset is None
    assert timezone._dst_start_rule is None
    assert timezone._dst_end_rule is None


def test_timezone_parses_dst_zone() -> None:
    """Ensure a timezone with DST populates DST-related fields and rules."""
    timezone = TimeZone("Europe/London")

    assert timezone.iana_timezone_name == "Europe/London"
    assert timezone._std_tz_name == "GMT"
    assert timezone._std_offset == 0

    assert timezone._has_dst is True
    assert timezone._dst_tz_name == "BST"
    assert timezone._dst_offset == 3600
    assert timezone._dst_start_rule is not None
    assert timezone._dst_end_rule is not None


def test_timezone_parses_non_hour_offset() -> None:
    """Ensure offsets with minutes are parsed correctly."""
    timezone = TimeZone("Asia/Kolkata")

    assert timezone._std_tz_name == "IST"
    assert timezone._std_offset == 5 * 3600 + 30 * 60
    assert timezone._has_dst is False


def test_from_posix_timezone_string_creates_custom_dst_timezone() -> None:
    """Ensure a custom POSIX timezone string can build a DST-aware timezone."""
    timezone = TimeZone.from_posix_timezone_string("EST5EDT,M3.2.0,M11.1.0")

    assert timezone._posix_timezone_string == "EST5EDT,M3.2.0,M11.1.0"
    assert timezone._std_tz_name == "EST"
    assert timezone._std_offset == -5 * 3600

    assert timezone._has_dst is True
    assert timezone._dst_tz_name == "EDT"
    assert timezone._dst_offset == -4 * 3600
    assert timezone._dst_start_rule is not None
    assert timezone._dst_end_rule is not None


def test_from_posix_timezone_string_uses_default_dst_offset_when_omitted() -> None:
    """Ensure DST offset defaults to standard offset plus one hour when omitted."""
    timezone = TimeZone.from_posix_timezone_string("GMT0BST,M3.5.0/1,M10.5.0")

    assert timezone._std_tz_name == "GMT"
    assert timezone._std_offset == 0
    assert timezone._dst_tz_name == "BST"
    assert timezone._dst_offset == 3600


def test_from_posix_timezone_string_accepts_bracketed_names_and_weird_times() -> None:
    """Ensure bracketed names and unusual transition times are preserved correctly."""
    timezone = TimeZone.from_posix_timezone_string(
        "<+0330>-3:30<+0430>,M3.5.4/-1,M10.5.4/24"
    )

    assert timezone._std_tz_name == "<+0330>"
    assert timezone._std_offset == 3 * 3600 + 30 * 60

    assert timezone._has_dst is True
    assert timezone._dst_tz_name == "<+0430>"
    assert timezone._dst_offset == 4 * 3600 + 30 * 60

    assert timezone._dst_start_rule is not None
    assert timezone._dst_end_rule is not None
    assert timezone._dst_start_rule.seconds == -3600
    assert timezone._dst_end_rule.seconds == 24 * 3600


def test_from_posix_timezone_string_accepts_quarter_hour_offset() -> None:
    """Ensure custom fixed-offset zones support quarter-hour offsets."""
    timezone = TimeZone.from_posix_timezone_string("<+0845>-8:45")

    assert timezone._std_tz_name == "<+0845>"
    assert timezone._std_offset == 8 * 3600 + 45 * 60
    assert timezone._has_dst is False
    assert timezone._dst_tz_name is None
    assert timezone._dst_offset is None


def test_from_posix_timezone_string_accepts_custom_julian_rules() -> None:
    """Ensure DST rules using Julian day syntax are parsed into transition rules."""
    timezone = TimeZone.from_posix_timezone_string("XST-2XDT-3,J59/1:30,J300/2:45")

    assert timezone._std_tz_name == "XST"
    assert timezone._std_offset == 2 * 3600
    assert timezone._dst_tz_name == "XDT"
    assert timezone._dst_offset == 3 * 3600

    assert timezone._dst_start_rule is not None
    assert timezone._dst_end_rule is not None
    assert timezone._dst_start_rule.rule_type == "J"
    assert timezone._dst_end_rule.rule_type == "J"
    assert timezone._dst_start_rule.day == 59
    assert timezone._dst_end_rule.day == 300
    assert timezone._dst_start_rule.seconds == 5400
    assert timezone._dst_end_rule.seconds == 9900


def test_from_posix_timezone_string_accepts_custom_numeric_day_rules() -> None:
    """Ensure DST rules using numeric day-of-year syntax are parsed correctly."""
    timezone = TimeZone.from_posix_timezone_string("NST3:30NDT4:15,59/0,300/23:30")

    assert timezone._std_tz_name == "NST"
    assert timezone._std_offset == -(3 * 3600 + 30 * 60)
    assert timezone._dst_tz_name == "NDT"
    assert timezone._dst_offset == -(4 * 3600 + 15 * 60)

    assert timezone._dst_start_rule is not None
    assert timezone._dst_end_rule is not None
    assert timezone._dst_start_rule.rule_type == "N"
    assert timezone._dst_end_rule.rule_type == "N"
    assert timezone._dst_start_rule.day == 59
    assert timezone._dst_end_rule.day == 300
    assert timezone._dst_start_rule.seconds == 0
    assert timezone._dst_end_rule.seconds == 23 * 3600 + 30 * 60


def test_from_posix_timezone_string_rejects_invalid_string() -> None:
    """Ensure malformed POSIX timezone strings are rejected."""
    with pytest.raises(ValueError):
        TimeZone.from_posix_timezone_string("not a valid posix timezone string")


def test_ensure_cache_for_non_dst_timezone_sets_empty_cache() -> None:
    """Ensure cache generation for non-DST zones stores the year and no transitions."""
    timezone = TimeZone("Africa/Bamako")

    timezone._ensure_cache(2026)

    assert timezone._cache_year == 2026
    assert timezone._cache_dst_start is None
    assert timezone._cache_dst_end is None


def test_ensure_cache_for_dst_timezone_populates_transition_cache() -> None:
    """Ensure DST zones compute and cache start and end transitions for a year."""
    timezone = TimeZone("Europe/London")

    timezone._ensure_cache(2026)

    assert timezone._cache_year == 2026
    assert timezone._cache_dst_start is not None
    assert timezone._cache_dst_end is not None
    assert isinstance(timezone._cache_dst_start, int)
    assert isinstance(timezone._cache_dst_end, int)


def test_ensure_cache_for_custom_funky_timezone_populates_transition_cache() -> None:
    """Ensure custom POSIX-created DST zones also compute transition caches."""
    timezone = TimeZone.from_posix_timezone_string(
        "<+0330>-3:30<+0430>,M3.5.4/-1,M10.5.4/24"
    )

    timezone._ensure_cache(2026)

    assert timezone._cache_year == 2026
    assert timezone._cache_dst_start is not None
    assert timezone._cache_dst_end is not None
    assert isinstance(timezone._cache_dst_start, int)
    assert isinstance(timezone._cache_dst_end, int)


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


def test_repr_contains_posix_string_for_custom_timezone() -> None:
    """Ensure custom POSIX-created zones still have a useful debug representation."""
    timezone = TimeZone.from_posix_timezone_string("EST5EDT,M3.2.0,M11.1.0")

    assert repr(timezone) == "<TimeZone EST5EDT,M3.2.0,M11.1.0>"
