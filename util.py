import re

from events_service import Event
from news_service import Post


def get_id(id_or_url: str) -> int:
    if id_or_url.startswith("https://"):
        match = re.match(r"\d+", id_or_url)
        if match is None:
            raise ValueError("Unable to find ID in URL")
        return int(match.group(0))
    else:
        return int(id_or_url)


def saturate_posts(posts: list[Post], events: list[Event]):
    index = {event.news_post_id: event for event in events}
    for post in posts:
        if post.id in index:
            post.event = index[post.id]
