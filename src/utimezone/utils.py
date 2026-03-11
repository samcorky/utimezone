import re


def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def days_in_month(year: int, month: int) -> int:
    return 28 + int(is_leap_year(year)) if month == 2 else 31 - month % 7 % 2

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

    h = (day + (13*(month+1)) // 5 + k + k // 4 + j // 4 + 5 * j) % 7

    # Zeller's returns 0=Saturday … 6=Friday, convert to Sunday=0
    return (h + 6) % 7

def datetime_to_epoch(year: int, month: int, day: int, hour: int, minute: int, second: int) -> int:
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
