from scraper import get_latest_posts, scrape_post, Post
from cal import event_from_post, publish_event, Event
from colorama import Fore


def select_post():
    latest_posts = get_latest_posts()

    print(f"{Fore.LIGHTCYAN_EX}Latest posts on chalmers.it:")
    for id, title in latest_posts:
        print(f" {Fore.LIGHTMAGENTA_EX}{id}{Fore.LIGHTBLACK_EX}: {Fore.RESET}{title}")

    print()
    selected = input(f"{Fore.YELLOW}Select post id (or enter url): {Fore.RESET}")

    return scrape_post(selected)


def print_post(post: Post):
    print(f"{Fore.LIGHTBLACK_EX}# {Fore.RESET}" + post.title)
    print(f"{Fore.LIGHTBLACK_EX}> {Fore.RESET}" + post.subtitle)
    print()
    print(post.body)


def print_event(event: Event):
    print(f"{Fore.LIGHTBLACK_EX}# {Fore.RESET}" + event.summary)
    print(f"{Fore.LIGHTBLACK_EX}@ {Fore.RESET}{event.location}")
    print(
        f"{Fore.LIGHTBLACK_EX}> {Fore.RESET}{event.start} {Fore.LIGHTBLACK_EX}until{Fore.RESET} {event.end}"
    )
    print()
    print(event.description)


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

    publish_event(event)


if __name__ == "__main__":
    main()
