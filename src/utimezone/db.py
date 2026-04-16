import os

_CACHE = {}
_MAX_CACHE_SIZE = 10


def _zones_csv_path() -> str:
    return os.path.dirname(__file__) + os.sep + "zones.csv"


def get_posix_rule_for_iana_name(iana_timezone_name: str) -> str | None:
    if iana_timezone_name in _CACHE:
        return _CACHE[iana_timezone_name]

    current_dir = os.path.dirname(__file__)
    db_path = current_dir + os.sep + "zones.csv"

    if not os.path.exists(db_path):
        return None

    rule = None
    # noinspection PyBroadException
    try:
        with open(db_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('","')
                if len(parts) != 2:
                    continue
                name = parts[0].strip('"')
                posix_rule = parts[1].strip('"')
                if name == iana_timezone_name:
                    rule = posix_rule
                    break
    except Exception:
        return None

    if rule:
        if len(_CACHE) >= _MAX_CACHE_SIZE:
            # Simple cache eviction: just clear it
            _CACHE.clear()
        _CACHE[iana_timezone_name] = rule

    return rule


def _get_all_iana_names():
    current_dir = os.path.dirname(__file__)
    db_path = current_dir + os.sep + "zones.csv"
    names = []
    if os.path.exists(db_path):
        with open(db_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split('","')
                    if parts:
                        names.append(parts[0].strip('"'))
    return names