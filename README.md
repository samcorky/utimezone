# utimezone

Lightweight timezone helpers for Python and MicroPython.

`utimezone` is a lightweight, dependency-free library for handling IANA and POSIX timezones on constrained systems like the Raspberry Pi Pico. It uses embedded timezone rules to provide accurate UTC-to-local conversions and DST support without the overhead of a full standard library.

> [!IMPORTANT]
> Status: stable. Core logic is verified against IANA data.

## Features

- **IANA Name Support:** Look up timezones by name (e.g., `Europe/London`, `America/New_York`).
- **POSIX Rule Parsing:** Support for custom POSIX TZ strings (e.g., `EST5EDT,M3.2.0,M11.1.0`).
- **MicroPython Optimized:** Avoids heavy objects and `datetime` dependencies; uses simple tuples and epoch integers. Supports negative epochs (pre-1970).
- **DST Aware:** Correctly handles DST transitions, including ambiguous (clocks back) and skipped (clocks forward) local times.
- **Embedded Database:** Includes a built-in mapping of IANA names to POSIX rules.
- **MicroPython Package Manager:** Fully compatible with `mip` for easy installation.
- **Zero Dependencies:** Pure Python implementation with no runtime requirements.

## Installation

### MicroPython (recommended)

The easiest way to install `utimezone` is using `mip`. Run this on your MicroPython board (requires internet access):

```python
import mip
mip.install("github:samcorky/utimezone")
```

Alternatively, you can manually copy the `src/utimezone` directory from this repository to your board's `lib/` folder so it appears as `lib/utimezone/`.

### Python (Development)

If you are using this on standard Python for testing or simulation:

```bash
pip install .
```

### Testing the Installation (MicroPython)

You can verify the installation using the MicroPython Unix port (via Docker) with this one-liner:

```bash
git clone https://github.com/samcorky/utimezone.git

docker run --rm -it -v "$(pwd):/app" -w /app micropython/unix sh -c "
  export MICROPYPATH=/app/src:/root/.micropython/lib && \
  micropython tests/test_timezone_public_api.py
"
```

## Quick Start

The API is designed to be familiar yet lightweight, primarily using epoch seconds (UTC) and date/time tuples `(y, m, d, h, mi, s)`.

### Basic Usage

```python
from utimezone.timezone import TimeZone

# 1. Initialise a timezone
tz = TimeZone("Europe/London")

# 2. Convert UTC epoch to local time tuple
local_dt = tz.utc_epoch_to_local(1711672200)
# -> (2024, 3, 29, 0, 30, 0)

# 3. Check if a local time is in DST
is_dst = tz.is_dst_at(2026, 6, 15, 12, 0, 0)
# -> True

# 4. Resolve local time to UTC epoch
# Handles transitions automatically (e.g., returns earlier instant for ambiguous times)
utc_epoch = tz.local_to_utc_epoch(2026, 3, 29, 1, 30, 0)
```

### Tuple-based Helpers

If you already have your date/time components in a tuple (common in MicroPython `time` or `machine.RTC` APIs), you can pass them directly:

```python
from utimezone import TimeZone
tz = TimeZone("Europe/London")
now_utc = (2026, 6, 15, 12, 0, 0)
local_now = tz.utc_datetime_to_local(now_utc)
# -> (2026, 6, 15, 13, 0, 0)
```

## API Reference

### `TimeZone` Class

| Method                                   | Description                                                               |
|:-----------------------------------------|:--------------------------------------------------------------------------|
| `TimeZone(iana_name)`                    | Constructor. Creates a zone from an IANA name (e.g., `"Asia/Tokyo"`).     |
| `from_posix_timezone_string(rule)`       | Class method. Creates a zone from a POSIX string.                         |
| `is_dst(epoch)`                          | Returns `True` if the UTC epoch is in DST.                                |
| `is_dst_at(*dt)`                         | Returns `True` if the local date/time (tuple or args) is in DST.          |
| `offset_for_epoch(epoch)`                | Returns the active UTC offset (seconds) for a UTC epoch.                  |
| `offset_at(*dt)`                         | Returns the active UTC offset (seconds) for a local date/time.            |
| `name_for_epoch(epoch)`                  | Returns the abbreviation (e.g., `"GMT"`, `"BST"`) or `None` for a UTC epoch. |
| `name_at(*dt)`                           | Returns the abbreviation for a local date/time.                           |
| `utc_epoch_to_local(epoch)`              | Converts UTC epoch to a local time tuple.                                 |
| `utc_datetime_to_local(*dt)`             | Converts UTC date/time to a local time tuple.                             |
| `local_datetime_to_utc(*dt, fold=False)` | Converts local naive date/time to a UTC time tuple.                       |
| `local_to_utc_epoch(*dt, fold=False)`    | Resolves local naive date/time to a UTC epoch integer.                    |
| `to_iso8601(*dt, is_local=False)`        | Returns an ISO 8601 formatted string (e.g., `2026-04-16T13:41:00+01:00`). |

> **Note:** All methods accepting `*dt` support both a single tuple `(y, m, d, [h, mi, s])` OR individual numeric arguments. For `to_iso8601`, zero UTC offsets (e.g., GMT) are formatted with a `Z` suffix.

### `utimezone.utils`

- `datetime_to_epoch(y, m, d, h, mi, s)`: Convert components to UTC epoch seconds.
- `epoch_to_ymdhms(epoch)`: Convert UTC epoch to a `(y, m, d, h, mi, s)` tuple.
- `format_iso8601(y, m, d, h, mi, s, offset_seconds=0)`: Format components and offset (seconds) as ISO 8601.
- `parse_signed_hms_to_seconds(s)`: Parse POSIX-style offset strings like `"-05:30"`.

## Intended Scope

`utimezone` is designed for **embedded applications** where memory and storage are limited. It does not aim to replace the full Python `zoneinfo` or `pytz` modules, nor does it provide historical timezone data (it uses the most current rules for a given zone).

## Design Choices & Behaviour

`utimezone` prioritises memory efficiency and consistency. Here are some key behaviours:

### Ambiguity Handling (clocks back)
When a local time repeats at DST end, use the `fold` flag:
- `fold=False` (default): earlier UTC instant
- `fold=True`: later UTC instant

This mirrors PEP 495 semantics.

### Skipped-time handling (clocks forward)
If a local time is skipped at DST start, `utimezone` falls back to the standard offset for that naive time.

### Extreme POSIX transitions
POSIX allows transition times from -167 to +167 hours; `utimezone` shifts the date accordingly.

### MicroPython optimisation
- Uses integers and 6-element tuples (no datetime objects) for low memory overhead
- Lazy caching: DST transitions are computed per-year on demand

## Licence & Data Credits

- **Licence:** MIT
- **Timezone Data:** Based on POSIX definitions from [nayarsystems/posix_tz_db](https://github.com/nayarsystems/posix_tz_db).
- **POSIX Specs:** See [PostgreSQL POSIX specs](https://www.postgresql.org/docs/current/datetime-posix-timezone-specs.html) for format details.
