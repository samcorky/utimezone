from utimezone.timezone import TimeZone

timezone = TimeZone('Europe/London')
print(timezone)
print(timezone.__dict__)
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