import os
from typing import Union

from colorama import Fore
from dotenv import load_dotenv


def get_required_env(name: str) -> str:
    if name not in os.environ:
        print(
            f"{Fore.LIGHTRED_EX}Missing required environment variable {name}{Fore.RESET}"
        )
        exit(1)
    return os.environ[name]


def get_optional_env(name: str, default: Union[str, None] = None) -> Union[str, None]:
    return os.environ.get(name, default)


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
    global BASE_URL
    BASE_URL = get_optional_env("BASE_URL")


setup_env()
