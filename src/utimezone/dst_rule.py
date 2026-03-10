import re  # type: ignore
import time

from .utils import day_of_week, days_in_month, datetime_to_epoch


class _DSTRule:
    """
    Compact, MicroPython-friendly representation of a POSIX TZ 'Mm.w.d[/time]' rule.

    Stored fields:
      month: 1..12
      week:  1..5 (5 means "last")
      weekday: 0..6 (0=Sunday)
      seconds: transition time in seconds from 00:00 (can be negative or >86400)
    """

    def __init__(self, posix_rule: str, transition_offset_seconds: int = 0) -> None:
        if posix_rule is None:
            raise ValueError("posix_rule must not be None")

        self.posix_rule: str = posix_rule.strip()
        if not self.posix_rule:
            raise ValueError("posix_rule must not be empty")

        self.month: int = 0
        self.week: int = 0
        self.weekday: int = 0
        self.seconds: int = 0

        self.transition_offset_seconds = transition_offset_seconds
        self._parse_posix_rule()

    @staticmethod
    def _parse_time_to_seconds(t: str) -> int:
        """
        Parse POSIX rule time (after '/') into seconds.
        Accepts: HH, HH:MM, HH:MM:SS with optional leading +/-.
        """
        t = t.strip()
        if not t:
            raise ValueError(f"Empty rule time")

        m = re.match("^([+-])?([0-9]+)(:([0-9]+)(:([0-9]+))?)?$", t)
        if m is None:
            raise ValueError(f"Bad rule time: {t!r}")

        sign_s = m.group(1)
        sign = -1 if sign_s == "-" else 1

        h = int(m.group(2))
        mm = int(m.group(4) or "0")
        ss = int(m.group(6) or "0")

        if mm >= 60 or ss >= 60:
            raise ValueError(f"Bad rule time (minute/second out of range): {t!r}")

        return sign * (h * 3600 + mm * 60 + ss)

    def _parse_posix_rule(self) -> None:
        """
        Currently supports the 'M' rule form used in your db:
          Mm.w.d[/time]
        If /time omitted, POSIX default is 02:00.
        """
        rule = self.posix_rule

        m = re.match("^M([0-9]+)\\.([0-9]+)\\.([0-9]+)(/(.+))?$", rule)
        if m is None:
            raise ValueError(f"Unsupported DST rule: {rule!r}")

        self.month = int(m.group(1))
        self.week = int(m.group(2))
        self.weekday = int(m.group(3))

        if not (0 <= self.weekday <= 6):
            raise ValueError(f"Bad weekday: {self.weekday}")
        if not (1 <= self.week <= 5):
            raise ValueError(f"Bad week: {self.week}")
        if not (1 <= self.month <= 12):
            raise ValueError(f"Bad month: {self.month}")

        time_s = m.group(5)
        self.seconds = 2 * 3600 if time_s is None else self._parse_time_to_seconds(time_s)

    def _resolve_day_of_month(self, year: int) -> int:
        first_weekday = day_of_week(year, self.month, 1)
        days_total = days_in_month(year, self.month)

        first_match = 1 + (self.weekday - first_weekday) % 7

        if self.week < 5:
            return first_match + (self.week - 1) * 7

        candidate = first_match + 28
        if candidate <= days_total:
            return candidate
        return candidate - 7

    @staticmethod
    def _shift_date(year: int, month: int, day: int, day_shift: int) -> tuple[int, int, int]:
        day += day_shift

        while day < 1:
            month -= 1
            if month < 1:
                month = 12
                year -= 1
            day += days_in_month(year, month)

        while day > days_in_month(year, month):
            day -= days_in_month(year, month)
            month += 1
            if month > 12:
                month = 1
                year += 1

        return year, month, day

    def get_transition(self, year: int) -> int:
        day = self._resolve_day_of_month(year)

        day_shift = self.seconds // 86400
        second_of_day = self.seconds % 86400

        hour = second_of_day // 3600
        minute = (second_of_day % 3600) // 60
        second = second_of_day % 60

        trans_year, trans_month, trans_day = self._shift_date(year, self.month, day, day_shift)

        naive_epoch = datetime_to_epoch(trans_year, trans_month, trans_day, hour, minute, second)
        return int(naive_epoch) - self.transition_offset_seconds

    def __repr__(self) -> str:
        return f"_DSTRule(month={self.month}, week={self.week}, weekday={self.weekday}, seconds={self.seconds})"