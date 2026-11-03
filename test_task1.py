"""Unit tests for task1.total_salary.

Contract under test:
- valid file             -> (total, average)
- missing/unreadable file -> (0, 0), no exception
- empty file             -> (0, 0), no ZeroDivisionError
- malformed lines        -> skipped; average uses valid lines only
- path not str/PathLike  -> TypeError

Run: python -m pytest -v
"""

from pathlib import Path

import pytest

from task1 import total_salary


@pytest.fixture
def salary_file(tmp_path):
    def make(content: str) -> Path:
        path = tmp_path / "salary.txt"
        path.write_text(content, encoding="utf-8")
        return path

    return make


# --- happy path -------------------------------------------------------------

def test_example_from_task(salary_file):
    path = salary_file("Alex Korp,3000\nNikita Borisenko,2000\nSitarama Raju,1000\n")
    assert total_salary(str(path)) == (6000, 2000)


def test_returns_tuple_of_two(salary_file):
    result = total_salary(str(salary_file("A,100\n")))
    assert isinstance(result, tuple) and len(result) == 2


def test_accepts_pathlib_path(salary_file):
    assert total_salary(salary_file("A,100\nB,300\n")) == (400, 200)


def test_single_developer(salary_file):
    assert total_salary(str(salary_file("Solo Dev,4500"))) == (4500, 4500)


def test_non_integer_average(salary_file):
    total, average = total_salary(str(salary_file("A,1000\nB,2000\nC,2000\n")))
    assert total == 5000
    assert average == pytest.approx(5000 / 3)


def test_no_trailing_newline(salary_file):
    assert total_salary(str(salary_file("A,100\nB,200"))) == (300, 150)


def test_blank_lines_and_whitespace_ignored(salary_file):
    path = salary_file("\n  A,100  \n\n B , 200\n\n")
    assert total_salary(str(path)) == (300, 150)


def test_utf8_names(salary_file):
    path = salary_file("Тарас Шевченко,3000\nЛеся Українка,1000\n")
    assert total_salary(str(path)) == (4000, 2000)


# --- missing / corrupted files ------------------------------------------------

def test_missing_file(tmp_path):
    assert total_salary(str(tmp_path / "nope.txt")) == (0, 0)


def test_directory_instead_of_file(tmp_path):
    assert total_salary(str(tmp_path)) == (0, 0)


def test_empty_file(salary_file):
    assert total_salary(str(salary_file(""))) == (0, 0)


def test_only_blank_lines(salary_file):
    assert total_salary(str(salary_file("\n\n   \n"))) == (0, 0)


def test_binary_garbage_file(tmp_path):
    path = tmp_path / "salary.txt"
    path.write_bytes(b"\xff\xfe\x00\x81garbage")
    assert total_salary(str(path)) == (0, 0)


@pytest.mark.parametrize(
    "bad_line",
    [
        "No Comma 1000",      # no separator
        "Bob,abc",            # salary not a number
        "Bob,",               # empty salary
        ",1000",              # empty name
        "Bob,1000,extra",     # too many fields
    ],
)
def test_malformed_lines_are_skipped(salary_file, bad_line):
    path = salary_file(f"A,100\n{bad_line}\nB,300\n")
    assert total_salary(str(path)) == (400, 200)


def test_all_lines_malformed(salary_file):
    assert total_salary(str(salary_file("foo\nbar,baz\n"))) == (0, 0)


# --- invalid argument types -------------------------------------------------------

@pytest.mark.parametrize(
    "bad_path",
    [None, 42, True, 3.14, ["salary.txt"], {"path": "salary.txt"}],
    ids=["None", "int", "bool", "float", "list", "dict"],
)
def test_invalid_path_type_raises_type_error(bad_path):
    with pytest.raises(TypeError):
        total_salary(bad_path)
