# utimezone

Lightweight timezone helpers for Python and MicroPython-style environments.

`utimezone` is intended to be a small but practical timezone library for constrained systems, including microcontrollers
such as the Raspberry Pi Pico. The project uses embedded timezone data and POSIX timezone rules to provide IANA timezone
name support without depending on a large standard-library implementation.

> [!IMPORTANT]  
> This is a work in progress, and not production-ready, and is missing a lot of features

## Goals

- Keep the library lightweight
- Support familiar IANA timezone names like `Europe/London`
- Parse POSIX timezone strings
- Handle fixed-offset and DST-aware timezones
- Stay friendly to embedded and MicroPython-style environments
- Provide a simple, predictable API

## Project status

This project is currently early-stage, with the core timezone database and parsing logic in place.

The intended direction is a compact but feature-complete timezone library for modern timezone handling on constrained devices.

## Features

- IANA timezone name lookup
- Embedded timezone database
- POSIX timezone string parsing
- DST transition rule parsing
- No runtime dependencies

## Usage

Below are a few concise examples showing how to use the public `TimeZone` API and the small `utils` helpers. Examples use plain (year, month, day, hour, minute, second) tuples so they remain friendly to MicroPython.

Basic operations

```py
from utimezone.timezone import TimeZone

# Create a timezone by IANA name
tz = TimeZone("Europe/London")

# Query whether a UTC epoch is in DST
is_dst = tz.is_dst(1711672200)  # epoch seconds

# Convert UTC epoch to local tuple
local = tz.utc_epoch_to_local(1711672200)  # -> (y, m, d, h, m, s)

# Convert a local naive tuple to a resolved UTC epoch
utc_epoch = tz.local_to_utc_epoch(2026, 3, 29, 1, 30, 0)

# Convenience tuple-based helpers
local_tuple = tz.utc_datetime_to_local((2026, 6, 15, 12, 0, 0))
utc_tuple = tz.local_datetime_to_utc((2026, 1, 15, 12, 0, 0))
```
```

API reference (public)

### TimeZone(name: str)
Construct a timezone by IANA name. Raises ValueError for unknown names.

### TimeZone.from_posix_timezone_string(posix: str)
Create a TimeZone from a POSIX TZ string (useful for custom/compact definitions).

### is_dst(epoch_seconds: int) -> bool
Return True if the given UTC epoch (seconds since 1970-01-01) is in DST for this zone.

Example:
```py
tz.is_dst(1711672200)
```

### is_dst_at(dt_tuple_or_y, m=1, d=1, h=0, mi=0, s=0) -> bool
Convenience wrapper that accepts either a (y, m, d, [h, mi, s]) tuple or numeric date/time components and returns DST state.

Example:
```py
tz.is_dst_at(2026, 6, 15, 12, 0, 0)
tz.is_dst_at((2026, 6, 15, 12, 0, 0))
```

### offset_for_epoch(epoch_seconds: int) -> int
Return the active UTC->local offset in seconds for the given UTC epoch.

Example:
```py
tz.offset_for_epoch(1711672200)
```

### name_for_epoch(epoch_seconds: int) -> str | None
Return the active timezone abbreviation for the given UTC epoch.

Example:
```py
tz.name_for_epoch(1711672200)  # e.g. 'BST' or 'GMT'
```

### utc_epoch_to_local(epoch_seconds: int) -> (y, m, d, h, mi, s)
Convert a UTC epoch into a local wall-clock tuple (year, month, day, hour, minute, second).

Example:
```py
tz.utc_epoch_to_local(1711672200)
```

### local_to_utc_epoch(dt_tuple_or_y, m=1, d=1, h=0, mi=0, s=0) -> int
Resolve a local naive date/time to a UTC epoch. Accepts either a (y, m, d, [h, mi, s]) tuple
or numeric components. Handles ambiguous and skipped times according to the timezone DST rules
(returns the earlier UTC instant when ambiguous; falls back to the standard-offset candidate
when the local time was skipped).

Example:
```py
tz.local_to_utc_epoch(2026, 3, 29, 1, 30, 0)
tz.local_to_utc_epoch((2026, 3, 29, 1, 30, 0))
```

### utc_datetime_to_local(dt_tuple_or_y, m=1, d=1, h=0, mi=0, s=0) -> (y, m, d, h, mi, s)
Convenience wrapper that accepts either a (y, m, d, [h, mi, s]) UTC tuple or numeric components and returns a local tuple.

Example:
```py
tz.utc_datetime_to_local((2026, 6, 15, 12, 0, 0))
tz.utc_datetime_to_local(2026, 6, 15, 12, 0, 0)
```

### local_datetime_to_utc(dt_tuple_or_y, m=1, d=1, h=0, mi=0, s=0) -> (y, m, d, h, mi, s)
Convenience wrapper that accepts either a (y, m, d, [h, mi, s]) local naive tuple or numeric components and returns a resolved UTC tuple.

Example:
```py
tz.local_datetime_to_utc((2026, 1, 15, 12, 0, 0))
tz.local_datetime_to_utc(2026, 1, 15, 12, 0, 0)
```

Utilities (in `utimezone.utils`)
- datetime_to_epoch(y,m,d,h,mi,s) -> int
  - Convert a date/time tuple to an integer epoch (seconds since 1970-01-01). Works for non-negative epochs.
- epoch_to_ymdhms(epoch_seconds) -> (y,m,d,h,mi,s)
  - Convert a non-negative epoch to a UTC date/time tuple.
- epoch_to_utc_year(epoch_seconds) -> int
  - Return the UTC year for a non-negative epoch (used internally by TimeZone).
- parse_signed_hms_to_seconds(s: str) -> int
  - Parse a POSIX-style signed hour[:min[:sec]] string into signed seconds (used to parse POSIX TZ offsets).

Notes
- The public API is intentionally small and avoids heavy stdlib types so it can be used from MicroPython. The tuple-based helpers
  are the recommended integration points for embedded code.
- For CI and MicroPython verification, `tests/test_timezone_public_api.py` is executable directly under the MicroPython unix port
  (it includes a tiny __main__ runner that prints a test summary). Use that file to run quick smoke-tests inside the MicroPython binary.


## Intended scope

`utimezone` aims to cover the practical embedded use case:

- map IANA names to compact timezone definitions
- understand standard time and DST rules
- support UTC offset calculations
- support UTC-to-local conversion helpers

It is not intended to be a full replacement for CPython's `zoneinfo` module or a complete historical timezone engine.

## Timezone data source

The timezone mapping used by this project is based on POSIX timezone definitions derived from the Nayarsystems POSIX timezone database:

- <https://github.com/nayarsystems/posix_tz_db>

## POSIX timezone rule reference

For background on POSIX timezone string format, see:

- <https://www.postgresql.org/docs/current/datetime-posix-timezone-specs.html>

## Roadmap
Remaining work and next steps

The core tuple- and epoch-based API is implemented. Remaining priorities
include:

- Expand correctness tests for DST transition edge cases (ambiguous/skipped times).
- CI: add a workflow that builds the MicroPython unix port and runs MicroPython-compatible tests.
- Type-checking: enable mypy in CI and fix any remaining type issues across the codebase.
- Documentation: add more examples and a short API reference page (or docs/ directory).
- Packaging and release automation (build, wheel, and minimal distribution artifacts).
