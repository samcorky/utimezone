import pytest

from utimezone.transition_rule import _TransitionRule
from utimezone.utils import (
    datetime_to_epoch,
    epoch_to_utc_year,
    parse_signed_hms_to_seconds,
    shift_date,
)


@pytest.mark.parametrize(
    (
        "rule",
        "expected_type",
        "expected_month",
        "expected_week",
        "expected_weekday",
        "expected_day",
        "expected_seconds",
    ),
    [
        ("M3.2.0", "M", 3, 2, 0, 0, 2 * 3600),
        ("M10.5.0/3", "M", 10, 5, 0, 0, 3 * 3600),
        ("M9.1.6/22", "M", 9, 1, 6, 0, 22 * 3600),
        ("J59", "J", 0, 0, 0, 59, 2 * 3600),
        ("J60/1:30", "J", 0, 0, 0, 60, 5400),
        ("0", "N", 0, 0, 0, 0, 2 * 3600),
        ("365/24", "N", 0, 0, 0, 365, 24 * 3600),
    ],
)
def test_transition_rule_parses_supported_formats(
    rule: str,
    expected_type: str,
    expected_month: int,
    expected_week: int,
    expected_weekday: int,
    expected_day: int,
    expected_seconds: int,
) -> None:
    """Ensure each supported POSIX rule format is parsed into the expected fields."""
    transition_rule = _TransitionRule(rule)

    assert transition_rule.posix_rule == rule
    assert transition_rule.rule_type == expected_type
    assert transition_rule.month == expected_month
    assert transition_rule.week == expected_week
    assert transition_rule.weekday == expected_weekday
    assert transition_rule.day == expected_day
    assert transition_rule.seconds == expected_seconds


@pytest.mark.parametrize(
    "rule",
    [
        None,
        "",
        " ",
    ],
)
def test_transition_rule_rejects_empty_or_none(rule: str | None) -> None:
    """Ensure missing or blank rules are rejected early."""
    with pytest.raises(ValueError):
        _TransitionRule(rule)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "rule",
    [
        "M13.2.0",
        "M3.0.0",
        "M3.6.0",
        "M3.2.7",
        "J0",
        "J366",
        "366",
        "M3.2",
        "J59/",
        "abc",
    ],
)
def test_transition_rule_rejects_invalid_rules(rule: str) -> None:
    """Ensure malformed or out-of-range rule values raise ValueError."""
    with pytest.raises(ValueError):
        _TransitionRule(rule)


@pytest.mark.parametrize(
    ("rule", "year", "expected_month", "expected_day"),
    [
        ("M3.2.0", 2023, 3, 12),
        ("M10.5.0", 2023, 10, 29),
        ("J59", 2023, 2, 28),
        ("J60", 2023, 3, 1),
        ("J60", 2024, 3, 1),
        ("59", 2023, 3, 1),
        ("59", 2024, 2, 29),
        ("60", 2024, 3, 1),
        ("364", 2023, 12, 31),
        ("365", 2024, 12, 31),
    ],
)
def test_resolve_month_day(
    rule: str, year: int, expected_month: int, expected_day: int
) -> None:
    """Ensure parsed rules resolve to the expected calendar date for a given year."""
    transition_rule = _TransitionRule(rule)

    # This verifies the rule-to-date conversion independent of epoch math.
    month, day = transition_rule._resolve_month_day(year)

    assert (month, day) == (expected_month, expected_day)


def test_repr_contains_useful_fields() -> None:
    """Ensure the debug representation includes the most useful parsed fields."""
    transition_rule = _TransitionRule("M3.2.0/1:23:45")
    rendered = repr(transition_rule)

    assert "_TransitionRule(" in rendered
    assert "posix_rule=M3.2.0/1:23:45" in rendered
    assert "rule_type=M" in rendered
    assert "month=3" in rendered
    assert "week=2" in rendered
    assert "weekday=0" in rendered
    assert "seconds=5025" in rendered


def test_parse_signed_hms_errors_and_signs() -> None:
    with pytest.raises(ValueError):
        parse_signed_hms_to_seconds(None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        parse_signed_hms_to_seconds("")

    with pytest.raises(ValueError):
        parse_signed_hms_to_seconds("1:60")

    with pytest.raises(ValueError):
        parse_signed_hms_to_seconds("1:59:60")

    with pytest.raises(ValueError):
        parse_signed_hms_to_seconds("not-a-time")

    assert parse_signed_hms_to_seconds("-1:30") == -(1 * 3600 + 30 * 60)
    assert parse_signed_hms_to_seconds("+2:00") == 2 * 3600


def test_transition_get_transition_applies_offset() -> None:
    # Second Sunday in March at 02:00, with a transition offset of 3600s
    rule = _TransitionRule("M3.2.0/2", transition_offset_seconds=3600)
    month, day = rule._resolve_month_day(2026)

    expected_epoch = datetime_to_epoch(2026, month, day, 2, 0, 0) - 3600
    assert rule.get_transition(2026) == expected_epoch


def test_shift_date_year_boundaries() -> None:
    assert shift_date(2023, 1, 1, -1) == (2022, 12, 31)
    assert shift_date(2023, 12, 31, 1) == (2024, 1, 1)
    # Multi-month negative shift (March 1, 2023 minus 31 days -> Jan 29, 2023)
    assert shift_date(2023, 3, 1, -31) == (2023, 1, 29)


def test_epoch_to_utc_year_negative_works() -> None:
    # No longer raises ValueError
    assert epoch_to_utc_year(-1) == 1969
