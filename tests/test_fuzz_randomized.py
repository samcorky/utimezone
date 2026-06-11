import random

import pytest

from utimezone.timezone import TimeZone
from utimezone.utils import datetime_to_epoch, epoch_to_ymdhms


@pytest.fixture(scope="module")
def rng_seed() -> int:
    return 123456


@pytest.fixture(scope="module")
def samples() -> int:
    return 500


@pytest.fixture(scope="module")
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


def test_random_epoch_roundtrip(rng_seed: int, samples: int):
    """Random epochs should round-trip through epoch_to_ymdhms -> datetime_to_epoch."""
    random.seed(rng_seed)
    epoch_max = datetime_to_epoch(2030, 12, 31, 23, 59, 59)

    for _ in range(samples):
        e = random.randint(0, epoch_max)
        y, m, d, h, mi, s = epoch_to_ymdhms(e)
        e2 = datetime_to_epoch(y, m, d, h, mi, s)
        assert e2 == e


def test_random_timezone_roundtrip_from_utc(
    rng_seed: int, samples: int, zone_names: list[str]
):
    """Pick random UTC epochs and random zones; UTC->local->UTC should round-trip."""
    random.seed(rng_seed)

    epoch_min = datetime_to_epoch(1970, 1, 1, 0, 0, 0)
    epoch_max = datetime_to_epoch(2030, 12, 31, 23, 59, 59)

    for _ in range(samples):
        e = random.randint(epoch_min, epoch_max)
        tz = TimeZone(random.choice(zone_names))
        local = tz.utc_epoch_to_local(e)
        e_back = tz.local_to_utc_epoch(*local)
        assert e_back == e
