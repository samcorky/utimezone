import time

from utimezone.timezone import TimeZone

timezone = TimeZone('Europe/London')
print(timezone)
print(timezone.__dict__)
dst_start = timezone._dst_start_rule.get_transition(2023)
print(dst_start)
print(time.gmtime(dst_start))
dst_end = timezone._dst_end_rule.get_transition(2023)
print(dst_end)
print(time.gmtime(dst_end))
print()

timezone = TimeZone('Africa/Bamako')
print(timezone)
print(timezone.__dict__)
print()


timezone = TimeZone('America/Miquelon')
print(timezone)
print(timezone.__dict__)
print()


timezone = TimeZone('Asia/Oral')
print(timezone)
print(timezone.__dict__)


timezone = TimeZone("Pacific/Auckland")
print(timezone)
print(timezone.__dict__)