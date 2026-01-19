import re

from colorama import Fore


def unmark_link(link: str) -> str:
    if link.startswith("!"):
        return ""

    text_match = re.search(r"(?<=^\[).*?(?=\]\()", link)
    url_match = re.search(r"(?<=\]\().*?(?=\)$)", link)
    if text_match is None or url_match is None:
        return link

    text = text_match.group().rstrip("/")
    url = url_match.group().rstrip("/")

    if text == url:
        return url

    return f"{text} ({url})"


def unmark(text: str) -> str:
    link_pattern = r"!?\[.*?\]\(.*?\)"
    links = list(re.finditer(link_pattern, text))

    for link in links[::-1]:
        unmarked_link = unmark_link(link.group())
        text = text[: link.start()] + unmarked_link + text[link.end() :]

    return text.strip()
