import requests
import re
from dataclasses import dataclass
import html


def get_latest_posts():
    homepage = requests.get("https://chalmers.it/").text
    pattern = re.compile(r'<a href="/post/(\d+)">(.*?)</a>')
    return re.findall(pattern, homepage)


def id_to_url(id: str) -> str:
    if id.startswith("https://"):
        return id
    elif re.match(r"\d+", id):
        # Numeric id
        return f"https://chalmers.it/post/{id}"
    else:
        raise ValueError("Invalid id provided")


def get_html(id: str) -> str:
    url = id_to_url(id)
    print("URL is", url)
    return html.unescape(requests.get(url).text)


def remove_tags(html: str) -> str:
    pattern = re.compile("<.*?>")
    return re.sub(pattern, "", html)


def remove_repeating(s: str, char: str = " ") -> str:
    """Replace repeating characters with a single one"""
    return re.sub(char + "+", char, s)


def format_tag(html: str) -> str:
    return remove_repeating(remove_tags(re.sub(r"<br */>", "\n", html))).strip()


@dataclass
class Post:
    title: str
    subtitle: str
    body: str


def scrape_post(id: str) -> Post:
    html = get_html(id)

    title = re.findall(r'<h2 class="NewsPost_title_.{6}">(.*?)</h2>', html)[0]

    subtitle = re.findall(r'<p class="NewsPostMeta_subtitle__uaB4X">(.+?)</p>', html)[0]
    subtitle = remove_repeating(remove_tags(subtitle))

    body_html = re.findall(
        r'<div class="MarkdownView_content_.{6}">(.+?)</div>', html, flags=re.S
    )[0]

    paragraphs = re.findall(r"<p>(.*?)</p>", body_html, flags=re.S)
    body = "\n\n".join([format_tag(p) for p in paragraphs])

    return Post(title, subtitle, body)


@dataclass
class Subtitle:
    posted: str
    author: str
    committee: str | None
    edited: str | None


def parse_subtitle(subtitle: str) -> Subtitle:
    split = subtitle.split(" | ")
    if len(split) == 2:
        posted, author_line = split
        edited_line = None
    elif len(split) == 3:
        posted, author_line, edited_line = split
    else:
        raise ValueError(f"Found invalid subtitle: {subtitle}")

    if author_line.startswith("Skriven av "):
        author = author_line[len("Skriven av ") :]
        committee = None
    else:
        av_index = author_line.find(" av ")
        author = author_line[av_index + 4 :]
        committee = author_line[len("Skriven för ") : av_index]

    if edited_line:
        edited = edited_line[len("Redigerad: ")]
    else:
        edited = None

    return Subtitle(posted, author, committee, edited)
