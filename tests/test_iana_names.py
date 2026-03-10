import pytest

from utimezone.timezone import TimeZone
from utimezone.db import IANA_TO_POSIX_MAP

@pytest.mark.parametrize("iana_name", IANA_TO_POSIX_MAP.keys())
def test_valid_iana_names(iana_name: str):
    """ Test all timezone names in the internal DB """
    assert iana_name is not None, "iana_name is None"

    timezone = TimeZone(iana_name)
    assert timezone.iana_timezone_name == iana_name


def test_invalid_iana_name():
    """ Test that invalid IANA timezone names raise ValueError """
    with pytest.raises(ValueError):
        TimeZone("invalid/iana/name")