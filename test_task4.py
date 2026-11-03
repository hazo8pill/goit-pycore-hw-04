"""Unit tests for task4 (CLI assistant bot).

Contract under test:
- parse_input: (cmd lowercased, *args as typed); blank -> ("",); non-str -> TypeError
- add_contact / change_contact / show_phone: names case-insensitive, stored as first typed
- add on existing name -> overwrite (original key casing kept)
- wrong arg count / unknown name -> message string, dict untouched, no exception
- args not list/tuple of str, contacts not dict -> TypeError
- show_all: "name: phone" lines; empty -> "No contacts saved."
- main: all print/input; exit/close (any case) or EOF -> "Good bye!"

Run: python -m pytest -v
"""

import pytest

from task4 import add_contact, change_contact, main, parse_input, show_all, show_phone


# --- parse_input -------------------------------------------------------------

def test_parse_splits_command_and_args():
    assert parse_input("add John 123") == ("add", "John", "123")


def test_parse_lowercases_command_only():
    assert parse_input("ADD John 123") == ("add", "John", "123")
    assert parse_input("HeLLo") == ("hello",)


def test_parse_ignores_extra_whitespace():
    assert parse_input("   phone    John  \n") == ("phone", "John")


@pytest.mark.parametrize("line", ["", "   ", "\t\n"])
def test_parse_blank_line(line):
    assert parse_input(line) == ("",)


@pytest.mark.parametrize("bad", [None, 123, b"add", ["add", "John"]])
def test_parse_rejects_non_str(bad):
    with pytest.raises(TypeError):
        parse_input(bad)


# --- add_contact -------------------------------------------------------------

def test_add_contact():
    contacts = {}
    assert add_contact(["John", "123"], contacts) == "Contact added."
    assert contacts == {"John": "123"}


def test_add_accepts_tuple_args():
    contacts = {}
    add_contact(("John", "123"), contacts)
    assert contacts == {"John": "123"}


def test_add_existing_overwrites_and_keeps_original_casing():
    contacts = {"John": "123"}
    assert add_contact(["JOHN", "999"], contacts) == "Contact added."
    assert contacts == {"John": "999"}


@pytest.mark.parametrize("args", [[], ["John"], ["John", "123", "extra"]])
def test_add_wrong_arg_count(args):
    contacts = {"Ann": "1"}
    assert add_contact(args, contacts) == "Usage: add [name] [phone]"
    assert contacts == {"Ann": "1"}


# --- change_contact ----------------------------------------------------------

def test_change_existing_case_insensitive():
    contacts = {"John": "123"}
    assert change_contact(["john", "0987654321"], contacts) == "Contact updated."
    assert contacts == {"John": "0987654321"}


def test_change_unknown_contact():
    contacts = {"John": "123"}
    assert change_contact(["Ann", "555"], contacts) == "Contact not found."
    assert contacts == {"John": "123"}


@pytest.mark.parametrize("args", [[], ["John"], ["John", "1", "2"]])
def test_change_wrong_arg_count(args):
    contacts = {"John": "123"}
    assert change_contact(args, contacts) == "Usage: change [name] [phone]"
    assert contacts == {"John": "123"}


# --- show_phone --------------------------------------------------------------

def test_show_phone_case_insensitive():
    assert show_phone(["JOHN"], {"John": "123"}) == "123"


def test_show_phone_unknown_contact():
    assert show_phone(["Ann"], {"John": "123"}) == "Contact not found."


@pytest.mark.parametrize("args", [[], ["John", "extra"]])
def test_show_phone_wrong_arg_count(args):
    assert show_phone(args, {"John": "123"}) == "Usage: phone [name]"


# --- show_all ----------------------------------------------------------------

def test_show_all_empty():
    assert show_all({}) == "No contacts saved."


def test_show_all_in_insertion_order():
    assert show_all({"John": "123", "Ann": "456"}) == "John: 123\nAnn: 456"


# --- type robustness ---------------------------------------------------------

HANDLERS = [
    (add_contact, ["John", "123"]),
    (change_contact, ["John", "123"]),
    (show_phone, ["John"]),
]


@pytest.mark.parametrize("handler, _", HANDLERS)
@pytest.mark.parametrize("bad_args", [None, "John 123", {"John": "123"}, [1, 2], ["John", None]])
def test_handlers_reject_bad_args_type(handler, _, bad_args):
    with pytest.raises(TypeError):
        handler(bad_args, {"John": "123"})


@pytest.mark.parametrize("handler, good_args", HANDLERS)
@pytest.mark.parametrize("bad_contacts", [None, [], "John:123"])
def test_handlers_reject_bad_contacts_type(handler, good_args, bad_contacts):
    with pytest.raises(TypeError):
        handler(good_args, bad_contacts)


@pytest.mark.parametrize("bad_contacts", [None, [], "John:123"])
def test_show_all_rejects_bad_contacts_type(bad_contacts):
    with pytest.raises(TypeError):
        show_all(bad_contacts)


# --- main --------------------------------------------------------------------

def run_session(monkeypatch, capsys, lines):
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(feed))
    feed = iter(lines)
    main()
    return capsys.readouterr().out.splitlines()


def test_main_full_session(monkeypatch, capsys):
    out = run_session(monkeypatch, capsys, [
        "hello",
        "add John 1234567890",
        "change john 0987654321",
        "phone JOHN",
        "add Ann 555",
        "all",
        "exit",
    ])
    assert out == [
        "Welcome to the assistant bot!",
        "How can I help you?",
        "Contact added.",
        "Contact updated.",
        "0987654321",
        "Contact added.",
        "John: 0987654321",
        "Ann: 555",
        "Good bye!",
    ]


@pytest.mark.parametrize("word", ["close", "CLOSE", "Exit"])
def test_main_exit_words_any_case(monkeypatch, capsys, word):
    out = run_session(monkeypatch, capsys, [word, "hello"])
    assert out == ["Welcome to the assistant bot!", "Good bye!"]


def test_main_invalid_and_blank_commands(monkeypatch, capsys):
    out = run_session(monkeypatch, capsys, ["test", "", "exit"])
    assert out[1:] == ["Invalid command.", "Invalid command.", "Good bye!"]


def test_main_wrong_args_does_not_crash(monkeypatch, capsys):
    out = run_session(monkeypatch, capsys, ["add", "phone", "exit"])
    assert out[1:] == ["Usage: add [name] [phone]", "Usage: phone [name]", "Good bye!"]


@pytest.mark.parametrize("exc", [EOFError, KeyboardInterrupt])
def test_main_eof_or_ctrl_c_exits(monkeypatch, capsys, exc):
    def raise_exc(_prompt=""):
        raise exc

    monkeypatch.setattr("builtins.input", raise_exc)
    main()
    assert capsys.readouterr().out.splitlines()[-1] == "Good bye!"
