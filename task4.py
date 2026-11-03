"""Console assistant bot: keeps a name -> phone dict and answers commands.

Commands: hello, add [name] [phone], change [name] [phone], phone [name],
all, close / exit. Commands are case-insensitive; names are matched
case-insensitively but stored as first typed.
"""


def _check_types(args, contacts) -> None:
    """Raise TypeError unless args is a list/tuple of str and contacts is a dict."""
    if not isinstance(args, (list, tuple)) or not all(isinstance(a, str) for a in args):
        raise TypeError("args must be a list or tuple of str")
    if not isinstance(contacts, dict):
        raise TypeError("contacts must be a dict")


def _find_name(name: str, contacts: dict[str, str]) -> str | None:
    """Return the stored key matching name case-insensitively, or None."""
    folded = name.casefold()
    return next((key for key in contacts if key.casefold() == folded), None)


def parse_input(user_input: str) -> tuple[str, ...]:
    """
    Split a command line into a lowercased command and its arguments.

    Args:
        user_input: Raw line typed by the user.

    Returns:
        A tuple (command, *args); arguments keep their casing.
        A blank line gives ("",).

    Raises:
        TypeError: If user_input is not a str.
    """
    if not isinstance(user_input, str):
        raise TypeError("user_input must be a str")
    cmd, *args = user_input.split() or [""]
    return cmd.lower(), *args


def add_contact(args: list[str], contacts: dict[str, str]) -> str:
    """
    Add a contact, or overwrite the phone if the name already exists.

    Args:
        args: [name, phone].
        contacts: Phone book to update in place.

    Returns:
        "Contact added.", or a usage hint if args does not hold two items.

    Raises:
        TypeError: If args is not a list/tuple of str or contacts is not a dict.
    """
    _check_types(args, contacts)
    if len(args) != 2:
        return "Usage: add [name] [phone]"
    name, phone = args
    contacts[_find_name(name, contacts) or name] = phone
    return "Contact added."


def change_contact(args: list[str], contacts: dict[str, str]) -> str:
    """
    Change the phone of an existing contact.

    Args:
        args: [name, new_phone].
        contacts: Phone book to update in place.

    Returns:
        "Contact updated.", "Contact not found.", or a usage hint if args
        does not hold two items. contacts changes only on success.

    Raises:
        TypeError: If args is not a list/tuple of str or contacts is not a dict.
    """
    _check_types(args, contacts)
    if len(args) != 2:
        return "Usage: change [name] [phone]"
    name, phone = args
    key = _find_name(name, contacts)
    if key is None:
        return "Contact not found."
    contacts[key] = phone
    return "Contact updated."


def show_phone(args: list[str], contacts: dict[str, str]) -> str:
    """
    Look up the phone number of a contact.

    Args:
        args: [name].
        contacts: Phone book to search.

    Returns:
        The phone number, "Contact not found.", or a usage hint if args
        does not hold one item.

    Raises:
        TypeError: If args is not a list/tuple of str or contacts is not a dict.
    """
    _check_types(args, contacts)
    if len(args) != 1:
        return "Usage: phone [name]"
    key = _find_name(args[0], contacts)
    return "Contact not found." if key is None else contacts[key]


def show_all(contacts: dict[str, str]) -> str:
    """
    Format every saved contact for display.

    Args:
        contacts: Phone book to list.

    Returns:
        One "name: phone" line per contact in insertion order,
        or "No contacts saved." if empty.

    Raises:
        TypeError: If contacts is not a dict.
    """
    _check_types([], contacts)
    if not contacts:
        return "No contacts saved."
    return "\n".join(f"{name}: {phone}" for name, phone in contacts.items())


def main() -> None:
    """Run the bot's input loop until close/exit, Ctrl-D or Ctrl-C."""
    contacts = {}
    print("Welcome to the assistant bot!")
    while True:
        try:
            user_input = input("Enter a command: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGood bye!")
            break
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, contacts))
        elif command == "change":
            print(change_contact(args, contacts))
        elif command == "phone":
            print(show_phone(args, contacts))
        elif command == "all":
            print(show_all(contacts))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
