from unittest.mock import mock_open, patch

import pytest

from utimezone.db import (
    _get_all_iana_names,
    _parse_zone_line,
    _read_zones,
    _zones_csv_path,
    get_posix_rule_for_iana_name,
)
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
    assert get_posix_rule_for_iana_name(name) is not None, (
        f"{name} timezone missing from database"
    )


def test_zones_csv_path():
    path = _zones_csv_path()
    assert path.endswith("zones.csv")


def test_parse_zone_line():
    assert _parse_zone_line('"America/New_York","EST5EDT"') == (
        "America/New_York",
        "EST5EDT",
    )
    assert _parse_zone_line('"Invalid"') is None
    assert _parse_zone_line("") is None


def test_read_zones():
    mock_data = '"America/New_York","EST5EDT"\n"Europe/London","GMT0BST"'
    with patch("builtins.open", mock_open(read_data=mock_data)):
        zones = list(_read_zones("mock_path"))
        assert zones == [("America/New_York", "EST5EDT"), ("Europe/London", "GMT0BST")]


def test_get_posix_rule_for_iana_name():
    mock_data = '"America/New_York","EST5EDT"\n"Europe/London","GMT0BST"'
    with patch("builtins.open", mock_open(read_data=mock_data)):
        assert get_posix_rule_for_iana_name("America/New_York") == "EST5EDT"
        assert get_posix_rule_for_iana_name("Invalid") is None


def test_get_all_iana_names():
    mock_data = '"America/New_York","EST5EDT"\n"Europe/London","GMT0BST"'
    with patch("builtins.open", mock_open(read_data=mock_data)):
        names = _get_all_iana_names()
        assert names == ["America/New_York", "Europe/London"]


def test_db_read_error_iana_names(monkeypatch):
    import utimezone.db as db

    def mock_read_zones(path):
        raise RuntimeError("Disk error")

    monkeypatch.setattr(db, "_read_zones", mock_read_zones)

    # Should return empty list on error
    assert db._get_all_iana_names() == []


def test_db_read_error_posix_rule(monkeypatch):
    import utimezone.db as db

    def mock_read_zones(path):
        raise RuntimeError("Disk error")

    monkeypatch.setattr(db, "_read_zones", mock_read_zones)

    # Should return None on error
    assert db.get_posix_rule_for_iana_name("UTC") is None


def test_zones_csv_path_fallback(monkeypatch):
    import utimezone.db as db

    monkeypatch.setattr(db, "__file__", "db.py")  # No slashes
    assert db._zones_csv_path() == "zones.csv"
