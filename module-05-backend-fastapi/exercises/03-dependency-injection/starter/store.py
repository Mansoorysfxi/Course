"""Already complete -- do not modify. See INSTRUCTIONS.md.

A tiny in-memory "database" of books, seeded with three starting entries.
Exactly the same "plain dict, module-level" pattern Lesson 08 uses for
QuestLog's own store -- deliberately temporary, simple, and easy to reason
about for the purposes of this exercise.
"""

from models import Book

_books: dict[str, Book] = {
    "book-001": Book(id="book-001", title="The Hobbit", author="J.R.R. Tolkien", checked_out=False),
    "book-002": Book(id="book-002", title="Dune", author="Frank Herbert", checked_out=True),
    "book-003": Book(id="book-003", title="Foundation", author="Isaac Asimov", checked_out=False),
}


def list_books() -> list[Book]:
    return list(_books.values())


def get_book(book_id: str) -> Book | None:
    return _books.get(book_id)


def set_checked_out(book_id: str, checked_out: bool) -> Book:
    existing = _books[book_id]
    updated = existing.model_copy(update={"checked_out": checked_out})
    _books[book_id] = updated
    return updated
