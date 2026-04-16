import pytest

from utimezone.db import IANA_TO_POSIX_MAP
from utimezone.timezone import TimeZone


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

@pytest.mark.parametrize("name",
                         [
                             "Europe/London",
                             "America/New_York",
                             "Asia/Tokyo",
                             "Etc/UTC",
                             "Etc/Greenwich",
                             "Etc/GMT",
                             "Etc/GMT+0",
                             "Etc/GMT-0",
                             "Etc/GMT0",
                             "Etc/Zulu",
                             "Etc/Universal",
                             "Etc/UCT",
                             "Etc/GMT+8",
                             "Etc/GMT-8",
                         ])
def test_common_timezone_names_in_db(name: str) -> None:
    """Ensure common timezone names are included in the database."""
    assert name in IANA_TO_POSIX_MAP, f"{name} timezone missing from database"

