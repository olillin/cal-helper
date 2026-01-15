import os
import re

from colorama import Fore
from requests_oauthlib import OAuth2Session

from .env import CALENDAR_ID, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from .events_service import Event, EventsService
from .news_service import NewsService, Post
from .parse_event import event_from_post, parse_slack
from .publish_event import authorize, publish_event, refresh_token
from .util import get_id, saturate_posts


def select_post() -> Post:
    latest_posts = NewsService.get_latest_posts(10)
    latest_events = EventsService.get_latest_events(10)
    saturate_posts(latest_posts, latest_events)

    print(f"{Fore.LIGHTCYAN_EX}Latest posts on chalmers.it:")
    for post in latest_posts:
        color = Fore.WHITE if post.event is None else Fore.CYAN
        print(
            f" {Fore.LIGHTMAGENTA_EX}{post.id}{Fore.LIGHTBLACK_EX}: {color}{post.title}{Fore.RESET}"
        )

    print()
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
    print(event.description)


def get_session() -> OAuth2Session:
    global CLIENT_ID
    global CLIENT_SECRET
    global REDIRECT_URI

    session = None
    if os.path.isfile("refresh-token"):
        try:
            with open("refresh-token", "r", encoding="utf-8") as f:
                token = f.read()
            session = refresh_token(token, CLIENT_ID, CLIENT_SECRET)
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Failed to refresh token:\n{e}{Fore.RESET}\n")

    if not session:
        scope = ["https://www.googleapis.com/auth/calendar.events.owned"]
        session = authorize(CLIENT_ID, CLIENT_SECRET, scope, REDIRECT_URI)

    with open("refresh-token", "w+") as f:
        f.write(session.token.get("refresh_token"))

    return session


def main():
    post = select_post()

    # Create calendar event
    event = event_from_post(post)

    # Confirm post
    print(f"\n{Fore.LIGHTGREEN_EX}Drafted event:\n")
    print_event(event)
    print()
    procceed = input(f"{Fore.YELLOW}Continue? (Y/n): {Fore.RESET}")
    if procceed.lower() == "n":
        print(f"{Fore.RED}Cancelled{Fore.RESET}")
        exit()

    print(f"\n{Fore.LIGHTGREEN_EX}Authorizing with Google{Fore.RESET}\n")
    session = get_session()

    publish_event(session, CALENDAR_ID, event)


if __name__ == "__main__":
    main()
