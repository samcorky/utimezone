import re


def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError(f"Bad month: {month}")

    if month == 2:
        return 29 if is_leap_year(year) else 28

    if month in (4, 6, 9, 11):
        return 30

    return 31


def is_valid_date(year: int, month: int, day: int) -> bool:
    return 1 <= month <= 12 and 1 <= day <= days_in_month(year, month)


def day_of_week(year: int, month: int, day: int) -> int:
    """
    Zeller's Congruence for the Gregorian calendar.
    Returns 0=Sunday, 1=Monday, ..., 6=Saturday.
    """
    if month < 3:
        month += 12
        year -= 1

    k = year % 100
    j = year // 100

    h = (day + (13 * (month + 1)) // 5 + k + k // 4 + j // 4 + 5 * j) % 7

    # Zeller's returns 0=Saturday … 6=Friday, convert to Sunday=0
    return (h + 6) % 7


def day_of_year_to_month_day(year: int, day_of_year: int) -> tuple[int, int]:
    month = 1

    while True:
        month_days = days_in_month(year, month)
        if day_of_year <= month_days:
            return month, day_of_year
        day_of_year -= month_days
        month += 1


def datetime_to_epoch(
    year: int, month: int, day: int, hour: int, minute: int, second: int
) -> int:
    y = year
    m = month

    if m <= 2:
        y -= 1
        m += 12

    era = y // 400
    yoe = y - era * 400
    doy = (153 * (m - 3) + 2) // 5 + day - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    days_since_epoch = era * 146097 + doe - 719468

    return days_since_epoch * 86400 + hour * 3600 + minute * 60 + second


def epoch_to_utc_year(epoch_seconds: int) -> int:
    if epoch_seconds < 0:
        raise ValueError("Negative epoch values are not supported")

    year = 1970
    days_remaining = epoch_seconds // 86400

    while True:
        year_days = 366 if is_leap_year(year) else 365
        if days_remaining < year_days:
            return year
        days_remaining -= year_days
        year += 1


_TIME_PART_RE = re.compile("^([+-])?([0-9]+)(:([0-9]+)(:([0-9]+))?)?$")


def parse_signed_hms_to_seconds(value: str) -> int:
    if value is None:
        raise ValueError("Value must be a string, not None")

    value = value.strip()
    if not value:
        raise ValueError("Value must not be empty")

    m = _TIME_PART_RE.match(value)
    if m is None:
        raise ValueError(f"Bad time value: {value!r}")

    sign_s = m.group(1)
    sign = -1 if sign_s == "-" else 1

    h = int(m.group(2))
    mm = int(m.group(4) or "0")
    ss = int(m.group(6) or "0")

    if mm >= 60 or ss >= 60:
        raise ValueError(f"Bad time value (minute/second out of range): {value!r}")

    return sign * (h * 3600 + mm * 60 + ss)
