import calendar
import random


def standardize_weekday_string(weekday):
    """
    Sanitize the weekday string to ensure it is in lowercase and stripped of
    whitespace.
    """
    weekday = weekday.lower().strip()
    assert (
        len(weekday) > 1
    ), "Weekday string must be at least 2 characters long to be unique"
    for sanitized_weekday in [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]:
        if weekday in sanitized_weekday:
            break
    else:
        raise ValueError(
            f"Invalid weekday string: {weekday}. Must be one of ['monday', "
            "'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', "
            "'sunday']"
        )
    return sanitized_weekday


def random_date(start_year, end_year):
    """
    Generate a random date string (YYYY-MM-DD) between start_year and end_year.
    """
    total_days = 0
    year_day_ranges = []

    # Build year-to-day range mapping
    for current_year in range(start_year, end_year + 1):
        start_day_index = total_days
        days_in_year = 366 if calendar.isleap(current_year) else 365
        total_days += days_in_year
        end_day_index = total_days
        year_day_ranges.append({
            "year": current_year,
            "start": start_day_index,
            "end": end_day_index
        })

    # Choose a random day index within total span
    random_day_index = random.randint(0, total_days - 1)

    # Determine the corresponding year
    for entry in year_day_ranges:
        if entry["start"] <= random_day_index < entry["end"]:
            year = entry["year"]
            day_of_year = random_day_index - entry["start"]
            break

    # Determine the corresponding month and day
    for month in range(1, 13):
        days_in_month = calendar.monthrange(year, month)[1]
        if day_of_year < days_in_month:
            day = day_of_year + 1  # adjust since days start at 1
            break
        day_of_year -= days_in_month

    return f"{year}-{month:02d}-{day:02d}"


def derive_weekday(date_str):
    """
    Derive the weekday from a date string (YYYY-MM-DD).
    """
    year, month, day = map(int, date_str.split("-"))
    weekday_index = calendar.weekday(year, month, day)
    return calendar.day_name[weekday_index].lower()


if __name__ == "__main__":
    # Example usage
    start_year = 2000
    end_year = 2023
    date = random_date(start_year, end_year)
    print(f"Random date between {start_year} and {end_year}: {date}")
    print(f"Weekday is: {derive_weekday(date)}")
