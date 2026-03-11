import pytest

from utimezone.timezone import TimeZone
from utimezone.db import IANA_TO_POSIX_MAP

@pytest.mark.parametrize("iana_name", IANA_TO_POSIX_MAP.keys())
def test_valid_iana_names(iana_name: str) -> None:
    """Ensure every IANA name in the embedded database can be constructed."""
    # Guard against accidental bad keys in the generated mapping.
    assert iana_name is not None, "iana_name is None"

    timezone = TimeZone(iana_name)
    assert timezone.iana_timezone_name == iana_name


def test_invalid_iana_name() -> None:
    """Ensure an unknown IANA timezone name is rejected."""
    with pytest.raises(ValueError):
        TimeZone("invalid/iana/name")