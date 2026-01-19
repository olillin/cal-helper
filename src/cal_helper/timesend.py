from datetime import datetime

import requests

from .env import TIMESEND_URL
from .events_service import Event


def format_time(property: str, time: datetime, all_day: bool = False) -> str:
    if all_day:
        return property + ";VALUE=DATE:" + time.strftime("%Y%m%d")
    else:
        return property + ":" + time.strftime("%Y%m%dT%H%M%S")


def safe_string(text: str) -> str:
    return text.replace("\n", "").strip()


def event_to_ical(event: Event) -> str:
    summary = safe_string(event.summary)
    description = safe_string(event.description)
    location_line = (
        "LOCATION:" + safe_string(event.location)
        if event.location is not None
        else None
    )

    now = datetime.now()
    lines = [
        "BEGIN:VCALENDAR",
        "PRODID:cal-helper",
        "VERSION:2.0",
        "BEGIN:VEVENT",
        "UID:foo",
        "SUMMARY:" + summary,
        "DESCRIPTION:" + description,
        location_line,
        format_time("DTSTAMP", now),
        format_time("DTSTART", event.start, event.all_day),
        format_time("DTEND", event.end, event.all_day),
        "END:VEVENT",
        "END:VCALENDAR",
    ]

    body = "\r\n".join([line for line in lines if line is not None])
    return body


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
