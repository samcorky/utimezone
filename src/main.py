import time

from utimezone.timezone import TimeZone

timezones = [TimeZone('Europe/London'), TimeZone('Africa/Bamako'), TimeZone('America/Miquelon'), TimeZone('Asia/Oral'), TimeZone("Pacific/Auckland")]
for timezone in timezones:
    timezone._ensure_cache(2026)
    print(timezone)
    print(timezone.__dict__)
    dst_start_rule, dst_end_rule = timezone._dst_start_rule, timezone._dst_end_rule
    if timezone._has_dst:
        print(f"DST Name: {timezone._dst_tz_name}")

    if dst_start_rule is not None:
        print("DST start:")
        print(dst_start_rule)
        dst_start = dst_start_rule.get_transition(2023)
        print(tuple(time.gmtime(dst_start)))
    if dst_end_rule is not None:
        print("DST end:")
        print(dst_end_rule)
        dst_end = dst_end_rule.get_transition(2023)
        print(tuple(time.gmtime(dst_end)))
    print()
