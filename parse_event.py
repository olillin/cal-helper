from typing import Sequence
from scraper import Post
from dataclasses import dataclass
from datetime import datetime
import re
from colorama import Fore


def print_context(s: str):
    print(f"\n{Fore.MAGENTA}Context:{Fore.RESET}\n{s}\n")


@dataclass
class Event:
    summary: str
    description: str
    location: str | None
    start: datetime
    end: datetime
    all_day: bool


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
    r"(?<![:\d])(\d{1,2})/(\d{1,2})(?![:\d])",
    r"(?<![:\d])(\d{1,2})-(\d{1,2})(?![:\d])",
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
    if not lock_year and date is not None and date < today:
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


def find_date(body: str) -> datetime:
    date: datetime | None = None
    time: tuple[int, int] | None = None

    # Find date
    dates = find_all(body, date_patterns)

    if len(dates) > 0:
        date = extract_date(*dates[0], body)
    else:
        # Could not find date in body
        print_context(body)
        manual_date = input(
            f"{Fore.YELLOW}Could not find date, please enter manually: {Fore.RESET}"
        ).strip()
        if manual_date == "":
            print(f"{Fore.RED}Cancelled{Fore.RESET}")
            exit()

        date = datetime.fromisoformat(manual_date)

    # Find time
    times = find_all(body, time_patterns)

    if len(times) > 0:
        time = extract_time(*times[0], body)
    else:
        print_context(body)
        manual_time = input(
            f"{Fore.YELLOW}Could not find time, please enter manually: {Fore.RESET}"
        ).strip()
        if manual_time != "":
            match = re.search(time_patterns[0], manual_time)
            assert match

            hour = int(match.group(1))
            minute = int(match.group(2))

            time = hour, minute

    if time is not None:
        date = datetime(date.year, date.month, date.day, *time)
    else:
        date = datetime(date.year, date.month, date.day, 0, 0, 1)

    return date


def find_location(body: str) -> str | None:
    location_patterns = [  #
        r"^var\b.?\s*(.+)$"
    ]
    common_locations = [
        "Hubben 2.2",
        "Hubben",
    ]
    if re.search(location_patterns[0], body, flags=re.I + re.M):
        match = re.search(location_patterns[0], body, flags=re.I + re.M)
        assert match
        return match.group(1)
    else:
        for location in common_locations:
            if location in body:
                return location


def event_from_post(post: Post, default_duration: int = 60) -> Event:
    summary = post.title
    description = post.body

    # Start
    start = find_date(post.body)

    # End
    minute = start.minute + default_duration
    hour = start.hour
    day = start.day
    month = start.month
    year = start.year
    if minute >= 60:
        hour += minute // 60
        minute %= 60
    if hour >= 60:
        day += hour // 60
        hour %= 60

    end = datetime(year, month, day, hour, minute)

    # Location
    location = find_location(post.body)

    return Event(summary, description, location, start, end, start.second == 1)


def format_slack_body(body: str) -> str:
    return re.sub(r"(@\w+|:[\w-]+:)", "", body).strip()


def parse_slack(text: str) -> Post:
    title = input(f"{Fore.YELLOW}Please enter title: {Fore.RESET}")
    if len(title) == 0:
        print(f"{Fore.RED}Invalid title{Fore.RESET}")
        exit()
    body = format_slack_body(text)

    return Post(title, "", body)
