def get_welcome_message(name: str) -> str:
    """Return a personalized welcome message.

    Raises:
        ValueError: if name is empty or only whitespace.
    """
    if not name or not name.strip():
        raise ValueError("Name cannot be empty.")
    return f"Welcome, {name.strip()}! Glad to have you in the AI Internship."


def main() -> None:
    """Return apersonlized Welcome message.
     Raises:
       ValueErrot: if name is empty or only whitespace.
     """
    name = input("Enter your name: ")
    try:
        print(get_welcome_message(name))
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
