# Notes on the reference solution

- `get_book_or_404` and `require_available_book` are each ordinary functions -- neither is
  "special" beyond being passed to `Depends(...)`, per Lesson 04.
- `require_available_book` is a genuine sub-dependency: its own parameter,
  `book: Annotated[Book, Depends(get_book_or_404)]`, means FastAPI resolves
  `get_book_or_404` *first*, and only calls `require_available_book`'s own body if that
  succeeded. A request for a nonexistent book hitting `/checkout` therefore correctly
  returns `404` (from `get_book_or_404`), never `409` -- the two failure modes are checked
  in the right order, for free, purely from the dependency chain's shape.
- No route function contains an `if book is None` or `if book.checked_out` check --
  exactly the acceptance criteria's point: that logic lives in exactly one place each.

**Verified:** run with `uvicorn main:app --reload`; `curl -X POST
http://127.0.0.1:8000/books/book-002/checkout` (already checked out) returns `409`;
`curl -X POST http://127.0.0.1:8000/books/book-001/checkout` returns `200` with
`"checked_out": true`; a nonexistent book ID on any of the three routes returns `404`.
