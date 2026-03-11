import re

from .transition_rule import _TransitionRule
from .db import IANA_TO_POSIX_MAP
from .utils import parse_signed_hms_to_seconds

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
        self._dst_start_rule: _TransitionRule | None = None
        self._dst_end_rule: _TransitionRule | None = None

        # Per-year computed cache (epoch seconds)
        self._cache_year: int | None = None
        self._cache_dst_start: int | None = None
        self._cache_dst_end: int | None = None

        self._parse_posix_timezone_string()

    def from_posix_timezone_string(self, posix_timezone_string: str) -> "TimeZone":
        self._posix_timezone_string = posix_timezone_string
        self._parse_posix_timezone_string()
        return self

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
        self._std_offset = -parse_signed_hms_to_seconds(std_off)

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
                self._dst_offset = -parse_signed_hms_to_seconds(dst_off)

            self._dst_start_rule = _TransitionRule(start, self._std_offset) if start is not None else None
            self._dst_end_rule = _TransitionRule(end, self._dst_offset) if end is not None else None

    def _ensure_cache(self, year: int) -> None:
        if not self._has_dst:
            self._cache_year = year
            self._cache_dst_start = None
            self._cache_dst_end = None
            return

        if self._cache_year == year:
            return

        if self._dst_start_rule is None or self._dst_end_rule is None:
            raise ValueError(f"Incomplete DST rules for timezone: {self.iana_timezone_name}")

        self._cache_year = year
        self._cache_dst_start = self._dst_start_rule.get_transition(year)
        self._cache_dst_end = self._dst_end_rule.get_transition(year)

    def __repr__(self) -> str:
        return f"<TimeZone {self.iana_timezone_name}>"

