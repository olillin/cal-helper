from scraper import get_latest_posts, scrape_post, Post


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


def main():
    post = select_post()

    print_post(post)

    # Confirm post
    print("\n")
    procceed = input("Continue? (y/N) ")
    if procceed.upper() != "Y":
        print("Cancelled")
        exit()

    # TODO: Create calendar event and add to Google Calendar


if __name__ == "__main__":
    main()
