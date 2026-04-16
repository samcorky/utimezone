import pytest

from utimezone.db import _get_all_iana_names, get_posix_rule_for_iana_name
from utimezone.timezone import TimeZone

ALL_IANA_NAMES = _get_all_iana_names()


@pytest.mark.parametrize("iana_name", ALL_IANA_NAMES)
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


@pytest.mark.parametrize(
    "name",
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
    ],
)
def test_common_timezone_names_in_db(name: str) -> None:
    """Ensure common timezone names are included in the database."""
    assert get_posix_rule_for_iana_name(name) is not None, f"{name} timezone missing from database"
