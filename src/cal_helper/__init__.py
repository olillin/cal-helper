import re

from colorama import Fore

from .env import CHALMERS_IT_URL
from .events_service import Event, EventsService
from .news_service import NewsService, Post
from .parse_event import event_from_post, parse_slack
from .timesend import create_url
from .util import get_id, saturate_posts


def select_post() -> Post:
    latest_posts = NewsService.get_latest_posts(10)
    latest_events = EventsService.get_latest_events(10)
    saturate_posts(latest_posts, latest_events)

    print(f"\n{Fore.LIGHTGREEN_EX}Latest posts from {CHALMERS_IT_URL}\n")

    for post in latest_posts:
        color = Fore.WHITE if post.event is None else Fore.CYAN
        suffix = "" if post.event is None else "*"
        print(
            f"  {Fore.LIGHTMAGENTA_EX}{post.id}{Fore.LIGHTBLACK_EX}: {color}{post.title}{suffix}{Fore.RESET}"
        )

    print(f"\n  * {Fore.CYAN}Cyan{Fore.RESET} posts have no event info\n")

    selected: str = input(
        f"{Fore.YELLOW}Select post id (or enter url): {Fore.RESET}"
    ).strip()
    id: int
    if selected == "":
        # Latest post on chalmers.it
        id = latest_posts[0].id
    elif re.match(r"\d+", selected):
        id = get_id(selected)
    else:
        # Text input
        lines = [selected]
        while len(line := input()) != 0:
            lines.append(line)
        return parse_slack("\n".join(lines))

    # Check if post fetched already
    for post in latest_posts:
        if id == post.id:
            return post

    # Get post from news service
    return NewsService.get_news_post(id)


def print_post(post: Post):
    print(f"{Fore.LIGHTBLACK_EX}# {Fore.RESET}" + post.title)
    print()
    print(post.body)


def print_event(event: Event):
    print(f"{Fore.LIGHTBLACK_EX}# {Fore.RESET}" + event.summary)
    print(f"{Fore.LIGHTBLACK_EX}@ {Fore.RESET}{event.location}")
    if event.all_day:
        print(f"{Fore.LIGHTBLACK_EX}> {Fore.RESET}{event.start.date()}")
    else:
        print(
            f"{Fore.LIGHTBLACK_EX}> {Fore.RESET}{event.start} {Fore.LIGHTBLACK_EX}until{Fore.RESET} {event.end}"
        )
    print()
    if event.description == "":
        print(f"{Fore.LIGHTBLACK_EX}No event description{Fore.RESET}")
    else:
        print(event.description)


def main():
    post = select_post()

    # Create calendar event
    event = event_from_post(post)

    # Confirm post
    print(f"\n{Fore.LIGHTGREEN_EX}Drafted event\n")
    print_event(event)

    print(f"\n{Fore.LIGHTGREEN_EX}Generating TimeSend URL{Fore.RESET}\n")
    url = create_url(event)
    print(f"{Fore.YELLOW}{url}{Fore.RESET}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"{Fore.RED}Cancelled{Fore.RESET}")
