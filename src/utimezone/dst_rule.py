import re  # type: ignore

class _DSTRule:
    """
    Compact, MicroPython-friendly representation of a POSIX TZ 'Mm.w.d[/time]' rule.

    Stored fields:
      month: 1..12
      week:  1..5 (5 means "last")
      weekday: 0..6 (0=Sunday)
      seconds: transition time in seconds from 00:00 (can be negative or >86400)
    """

    def __init__(self, posix_rule: str) -> None:
        if posix_rule is None:
            raise ValueError("posix_rule must not be None")

        self.posix_rule: str = posix_rule.strip()
        if not self.posix_rule:
            raise ValueError("posix_rule must not be empty")

        self.month: int = 0
        self.week: int = 0
        self.weekday: int = 0
        self.seconds: int = 0

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

        time_s = m.group(5)
        self.seconds = 2 * 3600 if time_s is None else self._parse_time_to_seconds(time_s)

    def __repr__(self) -> str:
        return f"_DSTRule(month={self.month}, week={self.week}, weekday={self.weekday}, seconds={self.seconds})"