import time

from utimezone.timezone import TimeZone

timezone = TimeZone('Europe/London')
timezone._ensure_cache(2026)
print(timezone)
print(timezone.__dict__)
if timezone._dst_start_rule is not None:
    dst_start = timezone._dst_start_rule.get_transition(2023)
    print(dst_start)
    print(time.gmtime(dst_start))
if timezone._dst_end_rule is not None:
    dst_end = timezone._dst_end_rule.get_transition(2023)
    print(dst_end)
    print(time.gmtime(dst_end))
print()


timezone = TimeZone('Africa/Bamako')
timezone._ensure_cache(2026)
print(timezone)
print(timezone.__dict__)
if timezone._dst_start_rule is not None:
    dst_start = timezone._dst_start_rule.get_transition(2023)
    print(dst_start)
    print(time.gmtime(dst_start))
if timezone._dst_end_rule is not None:
    dst_end = timezone._dst_end_rule.get_transition(2023)
    print(dst_end)
    print(time.gmtime(dst_end))
print()


timezone = TimeZone('America/Miquelon')
timezone._ensure_cache(2026)
print(timezone)
print(timezone.__dict__)
if timezone._dst_start_rule is not None:
    dst_start = timezone._dst_start_rule.get_transition(2023)
    print(dst_start)
    print(time.gmtime(dst_start))
if timezone._dst_end_rule is not None:
    dst_end = timezone._dst_end_rule.get_transition(2023)
    print(dst_end)
    print(time.gmtime(dst_end))
print()



timezone = TimeZone('Asia/Oral')
timezone._ensure_cache(2026)
print(timezone)
print(timezone.__dict__)
if timezone._dst_start_rule is not None:
    dst_start = timezone._dst_start_rule.get_transition(2023)
    print(dst_start)
    print(time.gmtime(dst_start))
if timezone._dst_end_rule is not None:
    dst_end = timezone._dst_end_rule.get_transition(2023)
    print(dst_end)
    print(time.gmtime(dst_end))
print()


timezone = TimeZone("Pacific/Auckland")
timezone._ensure_cache(2026)
print(timezone)
print(timezone.__dict__)
if timezone._dst_start_rule is not None:
    dst_start = timezone._dst_start_rule.get_transition(2023)
    print(dst_start)
    print(time.gmtime(dst_start))
if timezone._dst_end_rule is not None:
    dst_end = timezone._dst_end_rule.get_transition(2023)
    print(dst_end)
    print(time.gmtime(dst_end))
print()
