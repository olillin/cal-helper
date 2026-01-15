import json
from typing import Any

from colorama import Fore
from requests_oauthlib import OAuth2Session

from .events_service import Event


def event_to_body(event: Event, timezone: str = "Europe/Stockholm") -> dict[str, Any]:
    entries: list[tuple[str, Any]] = []

    if event.all_day:
        entries.append(
            (
                "start",
                {
                    "date": event.start.date().isoformat(),
                    "timeZone": timezone,
                },
            )
        )
        entries.append(
            (
                "end",
                {
                    "date": event.end.date().isoformat(),
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


def authorize(
    client_id: str, client_secret: str, scope: list[str], redirect_uri: str
) -> OAuth2Session:
    session = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)

    # OAuth endpoints given in the Google API documentation
    token_url = "https://www.googleapis.com/oauth2/v4/token"
    authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"

    # Redirect user to Google for authorization
    authorization_url, _ = session.authorization_url(
        authorization_base_url,
        # offline for refresh token
        # force to always make user click authorize
        access_type="offline",
        prompt="consent",
    )
    print(
        f"Please go here and authorize: {Fore.LIGHTCYAN_EX}{authorization_url}{Fore.RESET}"
    )

    # Get the authorization verifier code from the callback url
    redirect_response = input(
        f"\n{Fore.YELLOW}Paste the full redirect URL here: {Fore.RESET}"
    )

    # Fetch the access token
    session.fetch_token(
        token_url, client_secret=client_secret, authorization_response=redirect_response
    )

    return session


def refresh_token(
    refresh_token: str, client_id: str, client_secret: str
) -> OAuth2Session:
    """Refresh an OAuth2 token using a refresh token."""
    token_url = "https://www.googleapis.com/oauth2/v4/token"

    session = OAuth2Session(client_id)
    session.token = session.refresh_token(
        token_url, refresh_token, client_id=client_id, client_secret=client_secret
    )
    return session


def publish_body(session: OAuth2Session, calendar_id: str, body: dict[str, Any]):
    url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"

    print(f"\n{Fore.LIGHTGREEN_EX}Sending POST request{Fore.RESET}")
    response = session.post(url, json=body)
    print(f"\n{Fore.CYAN}API response:{Fore.RESET}\n")

    if response.status_code == 200:
        print(Fore.LIGHTGREEN_EX + response.text + Fore.RESET)
    else:
        print(Fore.LIGHTRED_EX + response.text + Fore.RESET)


def publish_event(session: OAuth2Session, calendar_id: str, event: Event):
    body = event_to_body(event)
    print(f"\n{Fore.LIGHTGREEN_EX}Constructed JSON body{Fore.RESET}")
    print(Fore.LIGHTBLACK_EX + json.dumps(body, indent=2) + Fore.RESET)

    publish_body(session, calendar_id, body)
