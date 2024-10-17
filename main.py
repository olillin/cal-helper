from scraper import get_latest_posts, scrape_post, Post
from parse_event import event_from_post, Event
from publish_event import authorize, publish_event, refresh_token
from colorama import Fore
import os
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session


def get_required_env(name: str) -> str:
    if name not in os.environ:
        print(
            f"{Fore.LIGHTRED_EX}Missing required environment variable {name}{Fore.RESET}"
        )
        exit(1)
    return os.environ[name]


def setup_env():
    load_dotenv()

    global CLIENT_ID
    CLIENT_ID = get_required_env("CLIENT_ID")
    global CLIENT_SECRET
    CLIENT_SECRET = get_required_env("CLIENT_SECRET")
    global REDIRECT_URI
    REDIRECT_URI = get_required_env("REDIRECT_URI")
    global CALENDAR_ID
    CALENDAR_ID = get_required_env("CALENDAR_ID")


def select_post():
    latest_posts = get_latest_posts()

    print(f"{Fore.LIGHTCYAN_EX}Latest posts on chalmers.it:")
    for id, title in latest_posts:
        print(f" {Fore.LIGHTMAGENTA_EX}{id}{Fore.LIGHTBLACK_EX}: {Fore.RESET}{title}")

    print()
    selected = input(
        f"{Fore.YELLOW}Select post id (or enter url): {Fore.RESET}"
    ).strip()
    if selected == "":
        selected = latest_posts[0][0]

    return scrape_post(selected)


def print_post(post: Post):
    print(f"{Fore.LIGHTBLACK_EX}# {Fore.RESET}" + post.title)
    print(f"{Fore.LIGHTBLACK_EX}> {Fore.RESET}" + post.subtitle)
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
    # Get environment variables
    setup_env()

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
