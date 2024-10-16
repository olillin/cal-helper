from scraper import Post
from dataclasses import dataclass
from datetime import datetime
import re
from os import environ

CALENDAR_ID: str = environ.get("CALENDAR_ID")


@dataclass
class Event:
    summary: str
    description: str
    location: str | None
    start: datetime
    end: datetime


def find_date(body: str) -> datetime:
    # Find date
    date_patterns = [  #
        r"(\d{1,2})/(\d{1,2})",
        r"(\d{1,2})-(\d{1,2})",
        r"(\d{1,2})(:e)? (\w+)",
    ]
    date: datetime | None = None

    if re.search(date_patterns[0], body):
        match = re.search(date_patterns[0], body)
        day = int(match.group(1))
        month = int(match.group(2))

        today = datetime.today()

        date = datetime(today.year, month, day)
        if date < today:
            date = datetime(today.year + 1, month, day)
    elif re.search(date_patterns[1], body):
        match = re.search(date_patterns[1], body)
        month = int(match.group(1))
        day = int(match.group(2))

        today = datetime.today()

        date = datetime(today.year, month, day)
        if date < today:
            date = datetime(today.year + 1, month, day)
    elif re.search(date_patterns[2], body):
        match = re.search(date_patterns[2], body)
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
        month = months.index(match.group(3).lower()) + 1
        day = int(match.group(1))

        today = datetime.today()

        date = datetime(today.year, month, day)
        if date < today:
            date = datetime(today.year + 1, month, day)
    else:
        weekdays = [
            "måndag",
            "tisdag",
            "onsdag",
            "torsdag",
            "fredag",
            "lördag",
            "söndag",
        ]
        weekday_pattern = re.compile(r"\b(" + "|".join(weekdays) + r")\b", flags=re.I)
        match = re.search(weekday_pattern, body)
        if match:
            weekday = weekdays.index(match.group(0).lower())

            week_offset = 0
            if "nästa vecka" in body:
                week_offset = 1

            today = datetime.today()

            if today.weekday() <= weekday:
                weekday += 7
                week_offset = 0

            day = today.day + weekday - today.weekday() + week_offset * 7
            month = today.month if day > today.day else today.month + 1
            year = today.year if month > today.month else today.year + 1

            date = datetime(year, month, day)

    # Failed to find date
    if date is None:
        print(body)
        print()
        manual_time = input("Could not find date, please enter manually: ").strip()
        if manual_time == "":
            print("Cancelled")
            exit()
        date = datetime.fromisoformat(manual_time)
    else:
        # Find time
        time: tuple[int, int] | None = None

        time_patterns = [  #
            r"(\d{1,2})[:.](\d{2})",
        ]
        if re.search(time_patterns[0], body):
            match = re.search(time_patterns[0], body)

            hour = int(match.group(1))
            minute = int(match.group(2))

            time = hour, minute

        if time is None:
            print(body)
            print()
            manual_time = input("Could not find time, please enter manually: ").strip()
            if manual_time != "":
                match = re.search(time_patterns[0], manual_time)

                hour = int(match.group(1))
                minute = int(match.group(2))

                date = datetime(date.year, date.month, date.day, hour, minute)
        else:
            date = datetime(date.year, date.month, date.day, time[0], time[1])

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
        return match.group(1)
    else:
        for l in common_locations:
            if l in body:
                return l


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

    return Event(summary, description, location, start, end)


def publish_event(event: Event) -> bool:
    # TODO
    return False
