# Exercise 04 — Middleware and Error Handling

**Lessons:** [`lessons/05-middleware.md`](../../lessons/05-middleware.md) and [`lessons/06-error-handling-status-codes-and-responses.md`](../../lessons/06-error-handling-status-codes-and-responses.md). You'll also reuse Pydantic models ([Lesson 03](../../lessons/03-request-bodies-and-pydantic-validation.md)) and dependencies ([Lesson 04](../../lessons/04-dependency-injection-and-depends.md)).

**Difficulty:** Independent. Less scaffolding than Exercises 02–03 — you're given the domain and the requirements, not a template with `# TODO`s in exactly the right spots.

## The task

`starter/` contains a working "Vault" API — a small in-memory store of secret items, each with a `locked: bool` field and an internal-only field `owner_note` (a string every item has, for internal bookkeeping only, that must never appear in any response — see `models.py`). Build:

1. **Custom middleware** (`@app.middleware("http")`, per Lesson 05) that adds a response header `X-Response-Time-Ms`, containing the request's total handling time in milliseconds, to **every** response — not just specific routes.
2. **A custom exception** `VaultLockedError` (carrying the item's `id`), and a matching `@app.exception_handler(...)` that turns it into a `409 Conflict` response with `detail` reading exactly `f"Vault item '{item_id}' is locked."` (Lesson 06's own pattern — do not use a plain `HTTPException` directly inside your route for this specific case; the point of this exercise is practicing the custom-exception-plus-handler pattern.)
3. A route `POST /vault/{item_id}/reveal` that: looks up the item (`404` if missing, via a dependency — reuse Lesson 04's pattern), raises `VaultLockedError` if `locked` is `True`, and otherwise returns the item **using a `response_model` that excludes `owner_note`** — that internal field must never appear in any response body, no matter what.
4. A route `POST /vault/{item_id}/lock` and `POST /vault/{item_id}/unlock`, each returning the updated item (also through the same `response_model` that hides `owner_note`).

## Concepts this exercise uses (all already taught)

| Concept | Taught in |
|---|---|
| `@app.middleware("http")`, `call_next`, response headers | [Lesson 05](../../lessons/05-middleware.md) |
| A custom exception class + `@app.exception_handler(...)` | [Lesson 06](../../lessons/06-error-handling-status-codes-and-responses.md) |
| `response_model` hiding an internal field | [Lesson 06](../../lessons/06-error-handling-status-codes-and-responses.md) |
| A `get_item_or_404`-style dependency | [Lesson 04](../../lessons/04-dependency-injection-and-depends.md) |
| Choosing `404` vs `409` correctly | Module 02, Lesson 03, applied via [Lesson 06](../../lessons/06-error-handling-status-codes-and-responses.md) |

## Acceptance criteria

- [ ] Every response from this API, for every route (including ones you didn't add — check the given `GET /vault` route too), includes an `X-Response-Time-Ms` header.
- [ ] `POST /vault/{item_id}/reveal` on a locked item returns `409` with the exact `detail` text specified above.
- [ ] `POST /vault/{item_id}/reveal` on an unlocked item returns `200`, and the response body **does not contain `owner_note` anywhere**, even though the underlying stored object has that field.
- [ ] `POST /vault/{item_id}/lock` and `.../unlock` correctly flip `locked` and return the updated item (also without `owner_note`).
- [ ] A request for a nonexistent `item_id`, on any of the three new routes, returns `404`.
- [ ] `VaultLockedError` is a real, custom exception class — the `409` for a locked reveal is produced by your `@app.exception_handler(...)`, not by a `raise HTTPException(409, ...)` written directly inside the route.

## What to submit

Point your AI session at your completed `starter/` folder and say *"Review my solution for exercise 04."*

## Hints

**Level 1:** For the header timing, Lesson 05's own `add_process_time_header` example is almost exactly this task — just rename the header and convert to milliseconds (`elapsed * 1000`).

**Level 2:** For hiding `owner_note`, define a second, smaller Pydantic model (e.g. `VaultItemOut`) with only the fields that should ever be visible externally, and pass it as `response_model=VaultItemOut` on each of the three routes.

**Level 3 (near-answer):**
```python
class VaultLockedError(Exception):
    def __init__(self, item_id: str):
        self.item_id = item_id

@app.exception_handler(VaultLockedError)
async def vault_locked_handler(request: Request, exc: VaultLockedError):
    return JSONResponse(status_code=409, content={"detail": f"Vault item '{exc.item_id}' is locked."})
```
Your `reveal` route then simply does `if item.locked: raise VaultLockedError(item.id)` — no status code or response-shape knowledge needed inside the route itself.
