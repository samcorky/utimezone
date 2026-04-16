import re

from .db import IANA_TO_POSIX_MAP
from .transition_rule import _TransitionRule
from .utils import (
    datetime_to_epoch,
    epoch_to_utc_year,
    epoch_to_ymdhms,
    parse_signed_hms_to_seconds,
)

_POSIX_TZ_RE: re.Pattern = re.compile(
    r"^(<[^>]+>|[A-Za-z]+)([+-]?[0-9]+(:[0-9]+(:[0-9]+)?)?)((<[^>]+>|[A-Za-z]+)([+-]?[0-9]+(:[0-9]+(:[0-9]+)?)?)?)?(,([^,]+),([^,]+))?$"
)


class TimeZone:
    iana_timezone_name: str | None
    _posix_timezone_string: str

    _std_offset: int
    _std_tz_name: str | None

    _has_dst: bool
    _dst_tz_name: str | None
    _dst_offset: int | None

    _dst_start_rule: _TransitionRule | None
    _dst_end_rule: _TransitionRule | None

    _cache_year: int | None
    _cache_dst_start: int | None
    _cache_dst_end: int | None

    def __init__(self, iana_timezone_name: str) -> None:
        self._init_state()

        self.iana_timezone_name = iana_timezone_name
        if iana_timezone_name not in IANA_TO_POSIX_MAP:
            raise ValueError(f"Unknown IANA timezone name: {iana_timezone_name}")

        self._posix_timezone_string = IANA_TO_POSIX_MAP[iana_timezone_name]
        self._parse_posix_timezone_string()

    @classmethod
    def from_posix_timezone_string(cls, posix_timezone_string: str) -> "TimeZone":
        tz = cls.__new__(cls)
        tz._init_state()
        tz._posix_timezone_string = posix_timezone_string
        tz._parse_posix_timezone_string()
        return tz

    def _init_state(self) -> None:
        self.iana_timezone_name = None
        self._posix_timezone_string = ""

        self._std_offset = 0
        self._std_tz_name = None

        self._has_dst = False
        self._dst_tz_name = None
        self._dst_offset = None

        self._dst_start_rule = None
        self._dst_end_rule = None

        self._cache_year = None
        self._cache_dst_start = None
        self._cache_dst_end = None

    def _parse_posix_timezone_string(self) -> None:
        s: str = self._posix_timezone_string.strip()

        m = re.match(_POSIX_TZ_RE, s)
        if m is None:
            raise ValueError(f"Invalid POSIX timezone string: {s}")

        std_name = m.group(1)
        std_off = m.group(2)
        dst_name = m.group(6)
        dst_off = m.group(7)
        start = m.group(11)
        end = m.group(12)

        # Standard time
        self._std_tz_name = std_name
        self._std_offset = -parse_signed_hms_to_seconds(std_off)

        # DST (if present)
        if dst_name is None:
            self._has_dst = False
            self._dst_tz_name = None
            self._dst_offset = None
            self._dst_start_rule = None
            self._dst_end_rule = None
        else:
            self._has_dst = True
            self._dst_tz_name = dst_name
            if dst_off is None:
                self._dst_offset = self._std_offset + 3600
            else:
                self._dst_offset = -parse_signed_hms_to_seconds(dst_off)

            self._dst_start_rule = (
                _TransitionRule(start, self._std_offset) if start is not None else None
            )
            self._dst_end_rule = (
                _TransitionRule(end, self._dst_offset) if end is not None else None
            )

    def _ensure_cache(self, year: int) -> None:
        if not self._has_dst:
            self._cache_year = year
            self._cache_dst_start = None
            self._cache_dst_end = None
            return

        if self._cache_year == year:
            return

        if self._dst_start_rule is None or self._dst_end_rule is None:
            raise ValueError(
                f"Incomplete DST rules for timezone: {self.iana_timezone_name}"
            )

        self._cache_year = year
        self._cache_dst_start = self._dst_start_rule.get_transition(year)
        self._cache_dst_end = self._dst_end_rule.get_transition(year)

    def is_dst(self, epoch_seconds: int) -> bool:
        if not self._has_dst:
            return False

        year = epoch_to_utc_year(epoch_seconds)
        self._ensure_cache(year)

        if self._cache_dst_start is None or self._cache_dst_end is None:
            return False

        # Northern hemisphere style: DST starts and ends within the same calendar year.
        if self._cache_dst_start < self._cache_dst_end:
            return self._cache_dst_start <= epoch_seconds < self._cache_dst_end

        # Southern hemisphere style: DST season crosses the new year boundary.
        return (
            epoch_seconds >= self._cache_dst_start
            or epoch_seconds < self._cache_dst_end
        )

    def is_dst_at(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
    ) -> bool:
        epoch_seconds = datetime_to_epoch(year, month, day, hour, minute, second)
        return self.is_dst(epoch_seconds)

    def offset_at(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
    ) -> int:
        if self.is_dst_at(year, month, day, hour, minute, second):
            if self._dst_offset is None:
                raise ValueError("DST offset missing for DST-aware timezone")
            return self._dst_offset
        return self._std_offset

    def name_at(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
    ) -> str | None:
        if self.is_dst_at(year, month, day, hour, minute, second):
            return self._dst_tz_name
        return self._std_tz_name

    # Convenience helpers that operate directly on epoch seconds
    def offset_for_epoch(self, epoch_seconds: int) -> int:
        """Return UTC->local offset in seconds for the given UTC epoch seconds."""
        return self._dst_offset if self.is_dst(epoch_seconds) else self._std_offset

    def name_for_epoch(self, epoch_seconds: int) -> str | None:
        """Return the active timezone abbreviation for the given UTC epoch seconds."""
        return self._dst_tz_name if self.is_dst(epoch_seconds) else self._std_tz_name

    def utc_epoch_to_local(
        self, epoch_seconds: int
    ) -> tuple[int, int, int, int, int, int]:
        """Convert a UTC epoch to local (year, month, day, hour, minute, second).

        The returned components are in local time (UTC + offset_for_epoch).
        """
        offset = self.offset_for_epoch(epoch_seconds)
        local_epoch = epoch_seconds + offset
        return epoch_to_ymdhms(int(local_epoch))

    def utc_datetime_to_local(self, dt: tuple[int, int, int, int, int, int]) -> tuple[int, int, int, int, int, int]:
        """Convert a UTC datetime tuple to local (year, month, day, hour, minute, second).

        Args:
            dt: (year, month, day, hour, minute, second) in UTC

        Returns:
            (year, month, day, hour, minute, second) in local wall-clock time
        """
        year, month, day, hour, minute, second = dt
        epoch = datetime_to_epoch(year, month, day, hour, minute, second)
        return self.utc_epoch_to_local(epoch)

    def local_datetime_to_utc(self, dt: tuple[int, int, int, int, int, int]) -> tuple[int, int, int, int, int, int]:
        """Convert a local naive datetime tuple to a UTC datetime tuple.

        This resolves ambiguous or skipped local times using the existing
        `local_to_utc_epoch` logic and then converts the resulting UTC epoch
        back to a (year, month, day, hour, minute, second) tuple.
        Args:
            dt: (year, month, day, hour, minute, second) in local wall-clock time

        Returns:
            (year, month, day, hour, minute, second) in UTC
        """
        year, month, day, hour, minute, second = dt
        utc_epoch = self.local_to_utc_epoch(year, month, day, hour, minute, second)
        return epoch_to_ymdhms(int(utc_epoch))

    def local_to_utc_epoch(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
    ) -> int:
        """Convert a local date/time to a UTC epoch (seconds since 1970-01-01).

        This performs a best-effort mapping. For zones with DST it will try both
        the standard and DST offsets and pick the candidate that is consistent
        with the timezone rules. If both are consistent (ambiguous local time)
        the earlier UTC instant is returned. If neither candidate appears valid
        (the local time was skipped by a forward transition), the standard-offset
        candidate is returned.
        """
        naive_epoch = datetime_to_epoch(year, month, day, hour, minute, second)

        candidates: list[int] = []
        std_candidate = int(naive_epoch) - self._std_offset
        candidates.append(std_candidate)

        if self._has_dst and self._dst_offset is not None:
            dst_candidate = int(naive_epoch) - self._dst_offset
            # avoid duplicate if offsets are equal
            if dst_candidate != std_candidate:
                candidates.append(dst_candidate)

        valid: list[int] = []
        for c in candidates:
            if self.offset_for_epoch(c) == self._std_offset:
                # candidate maps to standard offset
                if c == std_candidate:
                    valid.append(c)
            else:
                # candidate maps to dst offset
                if (
                    self._has_dst
                    and self._dst_offset is not None
                    and c == int(naive_epoch) - self._dst_offset
                ):
                    valid.append(c)

        if len(valid) == 1:
            return valid[0]

        if len(valid) > 1:
            # ambiguous time: return the earlier UTC instant
            return min(valid)

        # No valid candidate found (skipped time): fall back to standard candidate
        return std_candidate

    def __repr__(self) -> str:
        if self.iana_timezone_name is not None:
            return f"<TimeZone {self.iana_timezone_name}>"
        return f"<TimeZone {self._posix_timezone_string}>"
