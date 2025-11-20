from typing import TypedDict, Union
import requests
from dataclasses import dataclass
from colorama import Fore
from events_service import Event
from env import BASE_URL


@dataclass
class Post:
    id: int
    title: str
    body: str
    event: Union[Event, None]


class WrittenForData(TypedDict):
    gammaSuperGroupId: str
    prettyName: str


class PostData(TypedDict):
    id: int
    titleEn: str
    titleSv: str
    contentEn: str
    contentSv: str
    createdAt: str
    updatedAt: str
    scheduledPublish: str
    writtenByGammaUserId: str
    status: str
    writtenFor: WrittenForData


def parse_post(data: PostData) -> Post:
    return Post(data["id"], data["titleSv"], data["contentSv"], None)


class NewsService:
    @staticmethod
    def get_news_post(id: int) -> Post:
        url = f"{BASE_URL}/api/news/{id}"
        print(f"{Fore.LIGHTBLACK_EX}URL is {url}{Fore.RESET}")
        data: PostData = requests.get(url).json()
        return parse_post(data)

    @staticmethod
    def get_latest_posts(count: int = 5) -> list[Post]:
        url = f"{BASE_URL}/api/news?pageSize={count}"
        data: list[PostData] = requests.get(url).json()
        return [parse_post(post) for post in data]
