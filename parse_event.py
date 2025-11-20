from typing import Sequence
from news_service import Post
from datetime import datetime
from calendar import monthrange
import re
from colorama import Fore
from events_service import Event

DEFAULT_EVENT_DURATION = 60


def print_context(s: str):
    print(f"\n{Fore.MAGENTA}Context:{Fore.RESET}\n{s}\n")


def find_all(
    body: str, patterns: Sequence[re.Pattern[str] | str]
) -> list[tuple[int, re.Match[str]]]:
    all_matches: list[tuple[int, re.Match[str]]] = []

    for i, pattern in enumerate(patterns):
        matches = re.finditer(pattern, body)
        all_matches.extend([(i, match) for match in matches])

    all_matches.sort(key=lambda x: x[1].pos)

    return all_matches


weekdays = [
    "måndag",
    "tisdag",
    "onsdag",
    "torsdag",
    "fredag",
    "lördag",
    "söndag",
]


weekday_pattern = re.compile(r"\b(" + "|".join(weekdays) + r")\b", flags=re.IGNORECASE)

months = [
    "januari",
    "februari",
    "mars",
    "april",
    "maj",
    "juni",
    "juli",
    "augusti",
    "september",
    "oktober",
    "november",
    "december",
]

month_pattern = re.compile(
    r"(0?[1-9]|[1-2]\d|3[0-1])(:[ea])? (" + "|".join(months) + r")\b",
    flags=re.IGNORECASE,
)

date_patterns = [  #
    r"(?<![:\d])(\d{1,2})/(1?\d)(?![:\d])",
    r"(?<![:\d])(1?\d)-(\d{1,2})(?![:\d])",
    month_pattern,
    weekday_pattern,
]


def extract_date(pattern_num: int, match: re.Match[str], body: str) -> datetime:
    """Convert a matched date to datetime"""
    date = None
    today = datetime.today()
    lock_year = False

    if pattern_num == 0:
        day = int(match.group(1))
        month = int(match.group(2))

        date = datetime(today.year, month, day)
    elif pattern_num == 1:
        month = int(match.group(1))
        day = int(match.group(2))

        date = datetime(today.year, month, day)

    elif pattern_num == 2:
        month = months.index(match.group(3).lower()) + 1
        day = int(match.group(1))

        date = datetime(today.year, month, day)

    elif pattern_num == 3:
        weekday = weekdays.index(match.group(0).lower())

        week_offset = 0
        if "nästa vecka" in body:
            week_offset = 1

        if today.weekday() <= weekday:
            weekday += 7
            week_offset = 0

        day = today.day + weekday - today.weekday() + week_offset * 7
        month = today.month if day > today.day else today.month + 1
        year = today.year if month > today.month else today.year + 1

        date = datetime(year, month, day)
        lock_year = True

    else:
        raise ValueError(f"Illegal pattern number {pattern_num}")

    # Move to next year instead of beginning of this year
    if not lock_year and date < today:
        date = datetime(today.year + 1, date.month, date.day)

    return date


time_patterns = [  #
    r"(\d{1,2})[:.](\d{2})",
]


def extract_time(pattern_num: int, match: re.Match[str], body: str) -> tuple[int, int]:
    """Convert a matched time to hours and minutes"""
    if pattern_num == 0:
        hours = int(match.group(1))
        minute = int(match.group(2))
    else:
        raise ValueError(f"Illegal pattern number {pattern_num}")

    return hours, minute


def later(date: datetime, minutes: int) -> datetime:
    """Returns a new time an amount of minutes later"""
    if minutes < 0:
        raise ValueError("minutes cannot be negative")

    minute = date.minute + minutes
    hour = date.hour
    day = date.day
    month = date.month
    year = date.year
    if minute >= 60:
        hour += minute // 60
        minute %= 60
    if hour >= 24:
        day += hour // 24
        hour %= 24

    last_day_of_month = monthrange(year, month)[1]
    while day > last_day_of_month:
        month += 1
        day -= last_day_of_month

        if month > 12:
            year += month // 12
            month %= 12

        last_day_of_month = monthrange(year, month)[1]

    if month > 12:
        year += month // 12
        month %= 12

    return datetime(year, month, day, hour, minute)


def find_date(
    body: str, default_duration: int = DEFAULT_EVENT_DURATION
) -> tuple[datetime, datetime]:
    """Get the start and end of an event from the body"""
    date: datetime | None = None
    time: tuple[int, int] | None = None
    end_date: datetime | None = None

    # Find date
    dates = find_all(body, date_patterns)

    if len(dates) == 0:
        # Enter manually
        print_context(body)
        manual_date = input(
            f"{Fore.YELLOW}Could not find date, please enter manually: {Fore.RESET}"
        ).strip()
        if manual_date == "":
            print(f"{Fore.RED}Cancelled{Fore.RESET}")
            exit()

        dates = find_all(manual_date, date_patterns)

        if len(dates) == 0:
            print(f"{Fore.RED}Could not parse date{Fore.RESET}")
            exit()

    date = extract_date(*dates[0], body)

    # Find time
    times = find_all(body, time_patterns)

    if len(times) == 0:
        # Enter manually
        print_context(body)
        manual_time = input(
            f"{Fore.YELLOW}Could not find time, please enter manually: {Fore.RESET}"
        ).strip()
        times = find_all(manual_time, time_patterns)

    if len(times) > 0:
        time = extract_time(*times[0], body)

        date = datetime(date.year, date.month, date.day, *time)

        if len(times) >= 2:
            end_time = extract_time(*times[1], body)
            end_date = datetime(date.year, date.month, date.day, *end_time)
            if end_date <= date:
                end_date = later(end_date, 24 * 60)
    else:
        date = datetime(date.year, date.month, date.day, 0, 0, 1)

    if end_date is None:
        end_date = later(date, default_duration)

    return date, end_date


def find_location(body: str) -> str | None:
    location_patterns = [  #
        r"^(?:vart?|plats|location).+?\b(.+)$",
        r"\bHubben 2.2\b",
        r"\bStorhubben\b",
        r"\bHubben\b",
        r"\bSandlådan\b",
        r"\bCTC\b",
    ]

    for pattern in location_patterns:
        match = re.search(pattern, body, flags=re.I + re.M)
        if match:
            assert match
            if len(match.groups()) > 0:
                return match.group(1)
            return match.group(0)


def event_from_post(post: Post, default_duration: int = 60) -> Event:
    if post.event is not None:
        return post.event

    summary = post.title
    description = post.body

    # Time
    start, end = find_date(post.body, default_duration)

    # Location
    location = find_location(post.body)

    return Event(post.id, summary, description, location, start, end, start.second == 1)


def format_slack_body(body: str) -> str:
    return re.sub(r"(@\w+|:[\w-]+:)", "", body).strip()


def parse_slack(text: str) -> Post:
    title = input(f"{Fore.YELLOW}Please enter title: {Fore.RESET}")
    if len(title) == 0:
        print(f"{Fore.RED}Invalid title{Fore.RESET}")
        exit()
    body = format_slack_body(text)

    return Post(-1, title, body, None)
