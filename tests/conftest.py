import pytest

from utimezone.timezone import TimeZone
from utimezone.utils import datetime_to_epoch


@pytest.fixture(scope="session")
def rng_seed() -> int:
    return 123456


@pytest.fixture(scope="session")
def samples() -> int:
    # Default sample count for fuzz tests; individual tests can override.
    return 500


@pytest.fixture(scope="session")
def small_samples() -> int:
    return 50


@pytest.fixture(scope="session")
def zone_names() -> list[str]:
    return [
        "Europe/London",
        "Pacific/Auckland",
        "Asia/Kolkata",
        "Asia/Kathmandu",
        "Pacific/Chatham",
        "Australia/Lord_Howe",
        "America/New_York",
        "America/Sao_Paulo",
        "Africa/Cairo",
    ]


@pytest.fixture
def tz_factory():
    return lambda name: TimeZone(name)


@pytest.fixture
def tz_london():
    return TimeZone("Europe/London")


@pytest.fixture
def tz_auckland():
    return TimeZone("Pacific/Auckland")


@pytest.fixture
def tz_kolkata():
    return TimeZone("Asia/Kolkata")


@pytest.fixture
def tz_kathmandu():
    return TimeZone("Asia/Kathmandu")


@pytest.fixture
def tz_chatham():
    return TimeZone("Pacific/Chatham")


@pytest.fixture
def tz_lord_howe():
    return TimeZone("Australia/Lord_Howe")


@pytest.fixture(scope="session")
def epoch_2026_jan15_noon() -> int:
    return datetime_to_epoch(2026, 1, 15, 12, 0, 0)


@pytest.fixture(scope="session")
def epoch_2026_jun15_noon() -> int:
    return datetime_to_epoch(2026, 6, 15, 12, 0, 0)
