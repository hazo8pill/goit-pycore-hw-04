"""Unit tests for task2.get_cats_info.

Contract under test:
- valid file              -> list of {"id", "name", "age"} dicts, all values str
- missing/unreadable file -> [], no exception
- empty file              -> []
- malformed lines         -> skipped
- path not str/PathLike   -> TypeError

Run: python -m pytest -v
"""

from pathlib import Path

import pytest

from task2 import get_cats_info


@pytest.fixture
def cats_file(tmp_path):
    def make(content: str) -> Path:
        path = tmp_path / "cats.txt"
        path.write_text(content, encoding="utf-8")
        return path

    return make


EXAMPLE = (
    "60b90c1c13067a15887e1ae1,Tayson,3\n"
    "60b90c2413067a15887e1ae2,Vika,1\n"
    "60b90c2e13067a15887e1ae3,Barsik,2\n"
    "60b90c3b13067a15887e1ae4,Simon,12\n"
    "60b90c4613067a15887e1ae5,Tessi,5\n"
)


# --- happy path -------------------------------------------------------------

def test_example_from_task(cats_file):
    assert get_cats_info(str(cats_file(EXAMPLE))) == [
        {"id": "60b90c1c13067a15887e1ae1", "name": "Tayson", "age": "3"},
        {"id": "60b90c2413067a15887e1ae2", "name": "Vika", "age": "1"},
        {"id": "60b90c2e13067a15887e1ae3", "name": "Barsik", "age": "2"},
        {"id": "60b90c3b13067a15887e1ae4", "name": "Simon", "age": "12"},
        {"id": "60b90c4613067a15887e1ae5", "name": "Tessi", "age": "5"},
    ]


def test_returns_list_of_dicts_with_exact_keys(cats_file):
    result = get_cats_info(str(cats_file(EXAMPLE)))
    assert isinstance(result, list)
    assert all(isinstance(cat, dict) and set(cat) == {"id", "name", "age"} for cat in result)


def test_values_are_strings(cats_file):
    [cat] = get_cats_info(str(cats_file("abc,Vika,1\n")))
    assert all(isinstance(value, str) for value in cat.values())


def test_preserves_file_order(cats_file):
    result = get_cats_info(str(cats_file("1,B,1\n2,A,2\n3,C,3\n")))
    assert [cat["id"] for cat in result] == ["1", "2", "3"]


def test_accepts_pathlib_path(cats_file):
    assert get_cats_info(cats_file("1,Vika,1\n")) == [{"id": "1", "name": "Vika", "age": "1"}]


def test_no_trailing_newline(cats_file):
    assert len(get_cats_info(str(cats_file("1,A,1\n2,B,2")))) == 2


def test_blank_lines_and_whitespace_ignored(cats_file):
    path = cats_file("\n  1 , Vika , 1  \n\n2,Barsik,2\n\n")
    assert get_cats_info(str(path)) == [
        {"id": "1", "name": "Vika", "age": "1"},
        {"id": "2", "name": "Barsik", "age": "2"},
    ]


def test_utf8_names(cats_file):
    assert get_cats_info(str(cats_file("1,Мурчик,4\n"))) == [{"id": "1", "name": "Мурчик", "age": "4"}]


def test_name_with_spaces(cats_file):
    assert get_cats_info(str(cats_file("1,Sir Fluffy,4\n")))[0]["name"] == "Sir Fluffy"


# --- missing / corrupted files ------------------------------------------------

def test_missing_file(tmp_path):
    assert get_cats_info(str(tmp_path / "nope.txt")) == []


def test_directory_instead_of_file(tmp_path):
    assert get_cats_info(str(tmp_path)) == []


def test_empty_file(cats_file):
    assert get_cats_info(str(cats_file(""))) == []


def test_only_blank_lines(cats_file):
    assert get_cats_info(str(cats_file("\n\n   \n"))) == []


def test_binary_garbage_file(tmp_path):
    path = tmp_path / "cats.txt"
    path.write_bytes(b"\xff\xfe\x00\x81garbage")
    assert get_cats_info(str(path)) == []


@pytest.mark.parametrize(
    "bad_line",
    [
        "no commas at all",   # no separator
        "1,Vika",             # too few fields
        "1,Vika,1,extra",     # too many fields
        ",Vika,1",            # empty id
        "1,,1",               # empty name
        "1,Vika,",            # empty age
        "1,Vika,abc",         # age not a number
        "1,Vika,-3",          # negative age
    ],
)
def test_malformed_lines_are_skipped(cats_file, bad_line):
    path = cats_file(f"a,Tayson,3\n{bad_line}\nb,Tessi,5\n")
    assert [cat["name"] for cat in get_cats_info(str(path))] == ["Tayson", "Tessi"]


def test_all_lines_malformed(cats_file):
    assert get_cats_info(str(cats_file("foo\nbar,baz\n"))) == []


# --- invalid argument types -------------------------------------------------------

@pytest.mark.parametrize(
    "bad_path",
    [None, 42, True, 3.14, ["cats.txt"], {"path": "cats.txt"}],
    ids=["None", "int", "bool", "float", "list", "dict"],
)
def test_invalid_path_type_raises_type_error(bad_path):
    with pytest.raises(TypeError):
        get_cats_info(bad_path)
