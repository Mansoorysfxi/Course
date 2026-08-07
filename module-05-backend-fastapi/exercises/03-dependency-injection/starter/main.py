from typing import Annotated

from fastapi import Depends, FastAPI

import store
from models import Book

# TODO: import your two dependencies once you've written them in
# dependencies.py -- e.g.:
# from dependencies import get_book_or_404, require_available_book

app = FastAPI(title="Library API (Exercise 03)")


@app.get("/books", response_model=list[Book])
def list_books():
    return store.list_books()


# TODO: GET /books/{book_id}
# Use Depends(get_book_or_404) -- do NOT write an `if book is None` check
# directly in this function. See INSTRUCTIONS.md.


# TODO: POST /books/{book_id}/checkout
# Use Depends(require_available_book). On success, call
# store.set_checked_out(book.id, True) and return the result.


# TODO: POST /books/{book_id}/return
# Use Depends(get_book_or_404) -- a book can always be returned. Call
# store.set_checked_out(book.id, False) and return the result.
