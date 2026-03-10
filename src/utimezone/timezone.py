import re

from utimezone.dst_rule import _DSTRule
from utimezone.db import IANA_TO_POSIX_MAP

_POSIX_TZ_RE: re.Pattern = re.compile(r"^(<[^>]+>|[A-Za-z]+)([+-]?[0-9]+(:[0-9]+(:[0-9]+)?)?)((<[^>]+>|[A-Za-z]+)([+-]?[0-9]+(:[0-9]+(:[0-9]+)?)?)?)?(,([^,]+),([^,]+))?$")

class TimeZone:
    def __init__(self, iana_timezone_name: str) -> None:
        self.iana_timezone_name: str = iana_timezone_name
        if iana_timezone_name not in IANA_TO_POSIX_MAP:
            raise ValueError(f"Unknown IANA timezone name: {iana_timezone_name}")

        self._posix_timezone_string: str = IANA_TO_POSIX_MAP[iana_timezone_name]

        self._std_offset: int = 0
        self._std_tz_name: str | None = None

        # DST Stuff
        self._has_dst: bool = False
        self._dst_tz_name: str | None = None
        self._dst_offset: int | None = None

        # Parsed rule (not absolute timestamps)
        self._dst_start_rule: _DSTRule | None = None
        self._dst_end_rule: _DSTRule | None = None

        # Per-year computed cache (epoch seconds)
        self._cache_year: int | None = None
        self._cache_dst_start: int | None = None
        self._cache_dst_end: int | None = None

        self._parse_posix_timezone_string()

    def _parse_posix_timezone_string(self) -> None:
        s: str = self._posix_timezone_string.strip()

        m = re.match(_POSIX_TZ_RE, s)
        if m is None:
            raise ValueError(f"Invalid POSIX timezone string: {s}")

        std_name = m.group(1)
        std_off  = m.group(2)
        dst_name = m.group(6)
        dst_off  = m.group(7)
        start    = m.group(11)
        end      = m.group(12)

        # Standard time
        self._std_tz_name = std_name
        self._std_offset = -self._offset_str_to_posix_seconds(std_off)

        # DST (if present)
        if dst_name is None:
            self._has_dst = False
            self._dst_tz_name = None
            self._dst_offset = None
        else:
            self._has_dst = True
            self._dst_tz_name = dst_name
            if dst_off is None:
                self._dst_offset = self._std_offset + 3600
            else:
                self._dst_offset = -self._offset_str_to_posix_seconds(dst_off)

            self._dst_start_rule = _DSTRule(start, self._std_offset) if start is not None else None
            self._dst_end_rule = _DSTRule(end, self._dst_offset) if end is not None else None

    @staticmethod
    def _offset_str_to_posix_seconds(off: str) -> int:
        """
        Convert a POSIX offset string into seconds (POSIX sign convention).

        Supports:
          HH
          HH:MM
          HH:MM:SS
        with optional leading +/-
        """
        if off is None:
            raise ValueError("Offset must be a string, not None")

        off = off.strip()
        if not off:
            raise ValueError("Offset must not be empty")

        # MicroPython-friendly: no {m,n}, no non-capturing groups.
        m = re.match("^([+-])?([0-9]+)(:([0-9]+)(:([0-9]+))?)?$", off)
        if m is None:
            raise ValueError(f"Bad offset: {off!r}")

        sign_s = m.group(1)
        sign = -1 if sign_s == "-" else 1

        h = int(m.group(2))
        mm = int(m.group(4) or "0")
        ss = int(m.group(6) or "0")

        if mm < 0 or mm >= 60 or ss < 0 or ss >= 60:
            raise ValueError(f"Bad offset (minute/second out of range): {off!r}")

        return sign * (h * 3600 + mm * 60 + ss)

    def __repr__(self) -> str:
        return f"<TimeZone {self.iana_timezone_name}>"

