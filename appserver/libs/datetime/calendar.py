from datetime import date, timedelta


def get_start_weekday_of_month(year, month):
    """
    월의 시작 요일을 가져옴(월요일=0~일요일=6
    >>> get_start_weekday_of_month(2024, 12)
    6
    >>> get_start_weekday_of_month(2025, 2)
    5
    """
    result = date(year, month, 1)
    return result.weekday()


def get_last_day_of_month(year, month):
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    last_day = next_month - timedelta(days=1)
    return last_day.day


def get_range_days_of_month(year, month):
    start_weekday = get_start_weekday_of_month(year, month)
    last_day = get_last_day_of_month(year, month)

    start_weekday = (start_weekday + 1) % 7

    result = [0] * start_weekday

    for day in range(1, last_day + 1):
        result.append(day)

    return result
