from typing import Annotated

from fastapi import Depends, FastAPI

import store
from dependencies import get_book_or_404, require_available_book
from models import Book

app = FastAPI(title="Library API (Exercise 03)")


@app.get("/books", response_model=list[Book])
def list_books():
    return store.list_books()


@app.get("/books/{book_id}", response_model=Book)
def get_book(book: Annotated[Book, Depends(get_book_or_404)]):
    return book


@app.post("/books/{book_id}/checkout", response_model=Book)
def checkout_book(book: Annotated[Book, Depends(require_available_book)]):
    return store.set_checked_out(book.id, True)


@app.post("/books/{book_id}/return", response_model=Book)
def return_book(book: Annotated[Book, Depends(get_book_or_404)]):
    return store.set_checked_out(book.id, False)
