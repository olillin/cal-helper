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


def get_optional_env_with_default(name: str, default: str) -> str:
    return os.environ.get(name, default)


def get_optional_env(name: str) -> Union[str, None]:
    return os.environ.get(name, None)


def setup_env():
    load_dotenv()

    global CHALMERS_IT_URL
    CHALMERS_IT_URL = get_optional_env_with_default(
        "CHALMERS_IT_URL", "https://chalmers.it"
    )
    global TIMESEND_URL
    TIMESEND_URL = get_optional_env_with_default(
        "TIMESEND_URL", "https://timesend.olillin.com"
    )


setup_env()
