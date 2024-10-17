from parse_event import Event
from typing import Any
import json
import os
from requests import post
from colorama import Fore

from dotenv import load_dotenv

load_dotenv()
CALENDAR_ID = os.environ["CALENDAR_ID"]


def event_to_body(event: Event, timezone: str = "Europe/Stockholm") -> dict[str, Any]:
    entries = []

    if event.all_day:
        entries.append(
            (
                "start",
                {
                    "date": event.start.date(),
                    "timeZone": timezone,
                },
            )
        )
        entries.append(
            (
                "end",
                {
                    "date": event.end.date(),
                    "timeZone": timezone,
                },
            )
        )
    else:
        entries.append(
            (
                "start",
                {
                    "dateTime": event.start.isoformat(),
                    "timeZone": timezone,
                },
            )
        )
        entries.append(
            (
                "end",
                {
                    "dateTime": event.end.isoformat(),
                    "timeZone": timezone,
                },
            )
        )

    entries.append(("summary", event.summary))
    entries.append(("description", event.description))
    if event.location:
        entries.append(("location", event.location))

    return {k: v for k, v in entries}


def publish_event(event: Event):
    body = event_to_body(event)
    print(f"\n{Fore.LIGHTGREEN_EX}Constructed JSON body{Fore.RESET}")
    print(Fore.BLACK + json.dumps(body, indent=2) + Fore.RESET)

    print(f"\n{Fore.LIGHTGREEN_EX}Sending POST request{Fore.RESET}")

    headers = {}
    url = f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events"

    response = post(url, json=body, headers=headers)
    print(f"\n{Fore.CYAN}API response:{Fore.RESET}\n")

    if response.status_code == 200:
        print(Fore.LIGHTGREEN_EX + response.text + Fore.RESET)
    else:
        print(Fore.LIGHTRED_EX + response.text + Fore.RESET)
