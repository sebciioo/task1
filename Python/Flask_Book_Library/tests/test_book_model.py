"""Testy jednostkowe walidatora danych wejściowych w modelu Book"""
import pytest
from project.books.models import Book, ValidationError, FORBIDDEN_CHARS


def make_book(name="lalka", author="henryj sienkiewicz",
              year_published=1890, book_type="5days"):
    return Book(name=name, author=author,
                year_published=year_published, book_type=book_type)


# Scenariusz POPRAWNY - prawidłowe dane są akceptowane

def test_valid_book_is_created():
    book = make_book()
    assert book.name == "lalka"
    assert book.author == "henryj sienkiewicz"
    assert book.year_published == 1890
    assert book.book_type == "5days"


def test_text_is_trimmed():
    book = make_book(name="  Pan Tadeusz  ")
    assert book.name == "Pan Tadeusz"


@pytest.mark.parametrize("book_type", ["2days", "5days", "10days"])
def test_all_allowed_book_types(book_type):
    book = make_book(book_type=book_type)
    assert book.book_type == book_type


# Scenariusz NIEPOPRAWNY - złośliwe dane (XSS) są odrzucane

@pytest.mark.parametrize("payload", [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert(1)>",
    "<svg/onload=alert(1)>",
    "\"><script>alert(document.cookie)</script>",
    "'; DROP TABLE books; --",
])
def test_xss_payload_in_name_is_rejected(payload):
    with pytest.raises(ValidationError):
        make_book(name=payload)


@pytest.mark.parametrize("payload", [
    "<script>alert(1)</script>",
    "<b onmouseover=alert(1)>Autor</b>",
])
def test_xss_payload_in_author_is_rejected(payload):
    with pytest.raises(ValidationError):
        make_book(author=payload)


@pytest.mark.parametrize("char", FORBIDDEN_CHARS)
def test_each_forbidden_char_is_rejected(char):
    with pytest.raises(ValidationError):
        make_book(name=f"abc{char}def")


def test_xss_rejected_also_on_edit():
    book = make_book()
    with pytest.raises(ValidationError):
        book.name = "<script>alert(1)</script>"


# Scenariusz NIEPOPRAWNY - pozostałe reguły

def test_empty_name_is_rejected():
    with pytest.raises(ValidationError):
        make_book(name="   ")


def test_too_long_name_is_rejected():
    with pytest.raises(ValidationError):
        make_book(name="a" * 65)


@pytest.mark.parametrize("year", [1, 1000, 3000, "abc", None])
def test_invalid_year_is_rejected(year):
    with pytest.raises(ValidationError):
        make_book(year_published=year)


@pytest.mark.parametrize("book_type", ["99days", "1day", "<script>", ""])
def test_invalid_book_type_is_rejected(book_type):
    with pytest.raises(ValidationError):
        make_book(book_type=book_type)