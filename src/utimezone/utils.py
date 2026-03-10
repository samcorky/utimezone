def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def days_in_month(year: int, month: int) -> int:
    return 28 + int(is_leap_year(year)) if month == 2 else 31 - month % 7 % 2