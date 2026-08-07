from typing import Annotated

from fastapi import Depends, HTTPException, status

import store
from models import Book


def get_book_or_404(book_id: str) -> Book:
    book = store.get_book(book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No book with id '{book_id}'")
    return book


def require_available_book(book: Annotated[Book, Depends(get_book_or_404)]) -> Book:
    if book.checked_out:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Book is already checked out.")
    return book
