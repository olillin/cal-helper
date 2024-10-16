from scraper import get_latest_posts, scrape_post, Post
from cal import event_from_post, publish_event, Event


def select_post():
    latest_posts = get_latest_posts()

    print("Latest posts on chalmers.it:")
    for id, title in latest_posts:
        print(f" {id}: {title}")

    print()
    selected = input("Select post id (or enter url): ")

    return scrape_post(selected)


def print_post(post: Post):
    print("# " + post.title)
    print("> " + post.subtitle)
    print()
    print(post.body)


def print_event(event: Event):
    print("# " + event.summary)
    print(f"@ {event.location}")
    print(f"> {event.start} until {event.end}")
    print()
    print(event.description)


def main():
    post = select_post()

    # Create calendar event
    event = event_from_post(post)

    # Confirm post
    print("\nDrafted event:\n")
    print_event(event)
    print("\n")
    procceed = input("Continue? (y/N) ")
    if procceed.upper() != "Y":
        print("Cancelled")
        exit()

    publish_event(event)


if __name__ == "__main__":
    main()
