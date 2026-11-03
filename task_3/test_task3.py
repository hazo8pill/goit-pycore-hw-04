"""Unit tests for task3.directory_tree and task3.main.

Contract under test:
- valid directory          -> colored lines: dirs blue + "/", files green,
                              4-space indent per level, sorted case-insensitively
- unreadable subdirectory  -> red marker line, no exception
- symlink loop             -> listed, not followed
- missing path / null byte -> FileNotFoundError
- path is a file           -> NotADirectoryError
- empty / blank str        -> ValueError
- path not str/PathLike    -> TypeError
- main(): exit code 0 / 1 (bad path) / 2 (wrong argument count)

Run: python -m pytest -v
"""

import os
import re
import sys

import pytest

from task3 import DIR_COLOR, ERROR_COLOR, FILE_COLOR, directory_tree, main

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def plain(lines: list[str]) -> list[str]:
    """Strip color codes so the tree layout can be compared as text."""
    return [ANSI.sub("", line) for line in lines]


@pytest.fixture
def picture(tmp_path):
    """The example structure from the task description."""
    root = tmp_path / "picture"
    (root / "Logo").mkdir(parents=True)
    for name in ("IBM+Logo.png", "ibm.svg", "logo-tm.png"):
        (root / "Logo" / name).touch()
    (root / "bot-icon.png").touch()
    (root / "mongodb.jpg").touch()
    return root


# --- happy path -------------------------------------------------------------

def test_example_from_task(picture):
    assert plain(directory_tree(str(picture))) == [
        "picture/",
        "    bot-icon.png",
        "    Logo/",
        "        IBM+Logo.png",
        "        ibm.svg",
        "        logo-tm.png",
        "    mongodb.jpg",
    ]


def test_directories_and_files_have_different_colors(picture):
    lines = directory_tree(picture)
    assert lines[0].startswith(DIR_COLOR)
    assert f"{DIR_COLOR}Logo/" in lines[2]
    assert f"{FILE_COLOR}bot-icon.png" in lines[1]
    assert DIR_COLOR != FILE_COLOR


def test_accepts_pathlib_path(picture):
    assert directory_tree(picture) == directory_tree(str(picture))


def test_empty_directory(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    assert plain(directory_tree(empty)) == ["empty/"]


def test_deep_nesting_indentation(tmp_path):
    deep = tmp_path / "a" / "b" / "c"
    deep.mkdir(parents=True)
    (deep / "f.txt").touch()
    assert plain(directory_tree(tmp_path / "a")) == [
        "a/",
        "    b/",
        "        c/",
        "            f.txt",
    ]


def test_sorted_case_insensitive(tmp_path):
    for name in ("b.txt", "C.txt", "a.txt"):
        (tmp_path / name).touch()
    assert plain(directory_tree(tmp_path))[1:] == ["    a.txt", "    b.txt", "    C.txt"]


def test_unicode_and_spaces_in_names(tmp_path):
    (tmp_path / "Мої фото").mkdir()
    (tmp_path / "Мої фото" / "кіт.png").touch()
    assert plain(directory_tree(tmp_path))[1:] == ["    Мої фото/", "        кіт.png"]


def test_dot_path_shows_real_directory_name(picture, monkeypatch):
    monkeypatch.chdir(picture)
    assert plain(directory_tree("."))[0] == "picture/"


# --- unreadable / tricky directories ------------------------------------------

@pytest.mark.skipif(
    sys.platform == "win32" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    reason="chmod has no effect on Windows or for root",
)
def test_unreadable_subdirectory_does_not_crash(tmp_path):
    locked = tmp_path / "locked"
    locked.mkdir()
    locked.chmod(0)
    try:
        lines = directory_tree(tmp_path)
    finally:
        locked.chmod(0o755)
    assert plain(lines)[1] == "    locked/"
    assert ERROR_COLOR in lines[2] and "cannot read" in lines[2]


@pytest.mark.skipif(sys.platform == "win32", reason="symlinks need admin rights on Windows")
def test_symlink_loop_is_not_followed(tmp_path):
    (tmp_path / "loop").symlink_to(tmp_path, target_is_directory=True)
    assert plain(directory_tree(tmp_path))[1:] == ["    loop/"]


# --- invalid paths ----------------------------------------------------------------

def test_missing_path_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        directory_tree(tmp_path / "nope")


def test_file_instead_of_directory_raises(picture):
    with pytest.raises(NotADirectoryError):
        directory_tree(picture / "mongodb.jpg")


@pytest.mark.parametrize("bad_path", ["", "   "], ids=["empty", "spaces"])
def test_empty_string_raises_value_error(bad_path):
    with pytest.raises(ValueError):
        directory_tree(bad_path)


def test_null_byte_is_treated_as_missing():
    # Path.exists() returns False (not raises) for paths with a null byte.
    with pytest.raises(FileNotFoundError):
        directory_tree("bad\0path")


# --- invalid argument types -------------------------------------------------------

@pytest.mark.parametrize(
    "bad_path",
    [None, 42, True, 3.14, b"picture", ["picture"], {"path": "picture"}],
    ids=["None", "int", "bool", "float", "bytes", "list", "dict"],
)
def test_invalid_path_type_raises_type_error(bad_path):
    with pytest.raises(TypeError):
        directory_tree(bad_path)


# --- command line (main) -----------------------------------------------------------

def test_main_prints_tree(picture, capsys):
    assert main([str(picture)]) == 0
    out = capsys.readouterr().out
    assert plain(out.splitlines()) == plain(directory_tree(picture))


def test_main_reads_sys_argv(picture, capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["task3.py", str(picture)])
    assert main() == 0
    assert "mongodb.jpg" in capsys.readouterr().out


@pytest.mark.parametrize("argv", [[], ["a", "b"]], ids=["no-args", "too-many"])
def test_main_wrong_argument_count(argv, capsys):
    assert main(argv) == 2
    assert "Usage" in capsys.readouterr().err


@pytest.mark.parametrize(
    "make_arg",
    [
        lambda tmp: str(tmp / "nope"),            # missing
        lambda tmp: str(tmp / "file.txt"),        # a file
        lambda tmp: "",                           # empty
        lambda tmp: "bad\0path",                  # null byte
    ],
    ids=["missing", "file", "empty", "null-byte"],
)
def test_main_bad_path_returns_1(tmp_path, capsys, make_arg):
    (tmp_path / "file.txt").touch()
    assert main([make_arg(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err
    assert captured.out == ""
