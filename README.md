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

*Coming Soon*

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

Planned next steps include:

- public UTC offset lookup
- DST status lookup for a given timestamp
- timezone abbreviation lookup
- UTC-to-local conversion helpers
- more correctness tests around DST transitions
- MicroPython-focused examples and validation