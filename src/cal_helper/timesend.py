from datetime import datetime

import requests
import icalendar as ical

from .env import TIMESEND_URL
from .events_service import Event


def format_time(property: str, time: datetime, all_day: bool = False) -> str:
    if all_day:
        return property + ";VALUE=DATE:" + time.strftime("%Y%m%d")
    else:
        return property + ":" + time.strftime("%Y%m%dT%H%M%S")


def to_one_line(text: str) -> str:
    return text.replace("\n", "").strip()

def event_to_ical(event: Event) -> str:
    summary = to_one_line(event.summary)
    description = event.description.strip()
    location = (
        to_one_line(event.location)
        if event.location is not None
        else None
    )
    start = event.start.date() if event.all_day else event.start
    end = event.end.date() if event.all_day else event.end
    now = datetime.now()

    # Create calendar
    cal = ical.Calendar()
    cal.add("PRODID", "cal-helper")
    cal.add("VERSION", "2.0")

    # Create event
    ical_event = ical.Event()
    ical_event.add("UID", "foo")
    ical_event.add("SUMMARY", summary)
    ical_event.add("DESCRIPTION", description)
    ical_event.add("DTSTAMP", now)
    ical_event.add("DTSTART", start)
    ical_event.add("DTEND", end)
    if location is not None:
        ical_event.add("LOCATION", location)

    cal.add_component(ical_event)

    # Return serialized body
    return cal.to_ical().decode("utf-8")


def create_url(event: Event) -> str:
    request_url = TIMESEND_URL + "/api/upload"
    body = event_to_ical(event)

    response = requests.post(
        url=request_url, data=body, headers={"content-type": "text/calendar"}
    )

    data = response.json()
    try:
        publish_url = data["url"]
        return publish_url
    except KeyError:
        if "error" in data:
            raise Exception(
                f"Received error from TimeSend: {data['error'].get('message')}"
            )
        raise Exception(f"Received error from TimeSend: {data}")
