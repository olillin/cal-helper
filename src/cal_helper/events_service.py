from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict

import requests

from .env import CHALMERS_IT_URL


@dataclass
class Event:
    news_post_id: int
    summary: str
    description: str
    location: str | None
    start: datetime
    end: datetime
    all_day: bool


class EventData(TypedDict):
    id: int
    titleEn: str
    titleSv: str
    descriptionEn: str
    descriptionSv: str
    fullDay: bool
    startTime: str
    endTime: str
    location: str
    createdAt: str
    updatedAt: str
    newsPostId: int


def parse_event(data: EventData):
    start = datetime.fromisoformat(data["startTime"])
    end = datetime.fromisoformat(data["endTime"])
    return Event(
        data["newsPostId"],
        data["titleSv"],
        data["descriptionSv"],
        data["location"],
        start,
        end,
        data["fullDay"],
    )


class EventsService:
    @staticmethod
    def get_event(id: int) -> Event:
        url = f"{CHALMERS_IT_URL}/api/events/{id}"
        data: EventData = requests.get(url).json()
        return parse_event(data)

    @staticmethod
    def get_latest_events(count: int = 5) -> list[Event]:
        url = f"{CHALMERS_IT_URL}/api/events?pageSize={count}"
        data: list[EventData] = requests.get(url).json()
        return [parse_event(event) for event in data]
