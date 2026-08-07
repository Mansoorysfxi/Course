# Exercise 03 — Dependency Injection

**Lessons:** [`lessons/04-dependency-injection-and-depends.md`](../../lessons/04-dependency-injection-and-depends.md) (the whole exercise). You'll also reuse Pydantic models from [Lesson 03](../../lessons/03-request-bodies-and-pydantic-validation.md) and status codes from [Lesson 06](../../lessons/06-error-handling-status-codes-and-responses.md).

**Difficulty:** Guided/independent. The storage and models are given to you, fully working, in `starter/`; the dependencies and the routes that use them are yours to write.

## The task

`starter/` contains a small in-memory "Library" API with books that can be checked out. `starter/models.py` and `starter/store.py` are complete and already correct — **do not modify them.** `starter/main.py` has the app set up with one working route (`GET /books`) and several `# TODO` blocks for you to fill in.

Build:

1. A dependency `get_book_or_404(book_id: str) -> Book` in a new file `starter/dependencies.py`, following exactly the `get_quest_or_404` pattern from Lesson 04: look the book up via `store.get_book(book_id)`, raise `HTTPException(404, ...)` if it's `None`, otherwise return it.
2. A **sub-dependency**, `require_available_book`, that itself depends on `get_book_or_404` (via its own `Depends(...)`) and raises `HTTPException(409, ...)` if the book's `checked_out` field is already `True` — otherwise returns the book unchanged. (Directly modeled on Lesson 04's `require_incomplete_quest` example.)
3. Three routes in `main.py`, using these dependencies via `Depends(...)` and `Annotated`, with **no manual "does this book exist" checks written directly inside any of the three route functions themselves** — that check belongs only in your dependency:
   - `GET /books/{book_id}` — uses `get_book_or_404`, returns the book.
   - `POST /books/{book_id}/checkout` — uses `require_available_book`; if it doesn't raise, marks the book checked out (via `store.set_checked_out(book_id, True)`) and returns the updated book.
   - `POST /books/{book_id}/return` — uses `get_book_or_404` (a book can always be returned, even if — per this simplified exercise — it's already not checked out); marks it not checked out and returns it.

## Concepts this exercise uses (all already taught)

| Concept | Taught in |
|---|---|
| Writing a plain dependency function | [Lesson 04](../../lessons/04-dependency-injection-and-depends.md) |
| `Annotated[Type, Depends(...)]` | [Lesson 04](../../lessons/04-dependency-injection-and-depends.md) |
| Sub-dependencies (a dependency depending on another dependency) | [Lesson 04](../../lessons/04-dependency-injection-and-depends.md) |
| `HTTPException` with `404`/`409` | [Lesson 06](../../lessons/06-error-handling-status-codes-and-responses.md) (you only need the one-line usage shown in Lesson 04 already) |
| Reading an existing Pydantic model/store without needing to modify it | [Lesson 03](../../lessons/03-request-bodies-and-pydantic-validation.md) |

## Acceptance criteria

- [ ] `GET /books/{book_id}` for a real book returns `200`; for a fake ID, returns `404`.
- [ ] `POST /books/{book_id}/checkout` on an available book returns `200` with `checked_out: true`.
- [ ] `POST /books/{book_id}/checkout` on an **already checked-out** book returns `409`, and the book's state is unchanged.
- [ ] `POST /books/{book_id}/return` correctly sets `checked_out` back to `false`, even on a book that was already available.
- [ ] Neither `get_book_or_404` nor `require_available_book` is ever called with an explicit function call (`get_book_or_404(...)`) anywhere in `main.py` — only ever via `Depends(...)`.
- [ ] None of the three new route functions contains an `if book is None:` (or equivalent) check written directly inside it — that logic lives only in `dependencies.py`.

## What to submit

Point your AI session at your completed `starter/` folder and say *"Review my solution for exercise 03."*

## Hints

**Level 1:** Re-read Lesson 04's `get_quest_or_404`/`require_incomplete_quest` example side by side with this exercise's book-themed version — the structure is meant to be nearly identical, just renamed.

**Level 2:** `require_available_book`'s own parameter list needs exactly one parameter: `book: Annotated[Book, Depends(get_book_or_404)]` — it receives an already-looked-up `Book`, it does not look one up itself.

**Level 3 (near-answer):**
```python
def require_available_book(book: Annotated[Book, Depends(get_book_or_404)]) -> Book:
    if book.checked_out:
        raise HTTPException(status_code=409, detail="Book is already checked out.")
    return book
```
Your checkout route's own signature then looks like:
```python
@app.post("/books/{book_id}/checkout")
def checkout_book(book: Annotated[Book, Depends(require_available_book)]):
    return store.set_checked_out(book.id, True)
```
