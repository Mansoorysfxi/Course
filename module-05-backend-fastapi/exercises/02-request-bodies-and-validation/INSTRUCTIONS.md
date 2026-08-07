# Exercise 02 — Request Bodies and Pydantic Validation

**Lessons:** [`lessons/03-request-bodies-and-pydantic-validation.md`](../../lessons/03-request-bodies-and-pydantic-validation.md) (Pydantic models, `Literal`, `Field`, `@field_validator`, reading the exact `422` error shape). You'll also use path/query parameters from [Lesson 02](../../lessons/02-path-and-query-parameters.md).

**Difficulty:** Guided. The model shape and most routes are specified precisely; you're asked to deliberately trigger and read several different validation errors, not just make the happy path work.

## The task

Build a tiny "Adventurer Registry" API, in `starter/main.py`:

1. A Pydantic model `AdventurerCreate` with:
   - `name: str`, at least 1 and at most 50 characters (use `Field`).
   - `level: int`, at least 1 and at most 100 (use `Field(ge=1, le=100)` — `ge`/`le` are Pydantic's "greater-or-equal"/"less-or-equal" numeric constraints, the numeric equivalent of `min_length`/`max_length`; they weren't shown by name in the lesson's exact examples, but they follow the exact same `Field(...)` pattern the lesson taught, just for numbers instead of strings).
   - `character_class: Literal["warrior", "mage", "rogue", "cleric"]`.
2. A custom `@field_validator` on `name` that rejects a name of just whitespace (e.g. `"   "`) even though it passes `min_length=1` (a plain length check doesn't catch this) — raise a `ValueError` with a clear message.
3. `POST /adventurers` — accepts an `AdventurerCreate` body, returns it back with `status_code=201`.
4. `GET /adventurers/search` — query parameters `min_level: int | None = None` and `character_class: str | None = None`, both genuinely optional; for this exercise, it's fine for this route to always return an empty list `[]` (no real storage needed — the point here is practicing optional query parameters, not building a second CRUD API; Exercise 03 gives you real storage).

Then, in a separate file `starter/VALIDATION_NOTES.md`, write down — in your own words, from what you actually saw in the terminal or Swagger UI, not copied from the lesson — the exact `type` and `loc` values you get back for **three** different deliberate mistakes:
- Omitting `character_class` entirely.
- Sending `level: 150`.
- Sending `character_class: "necromancer"`.

## Concepts this exercise uses (all already taught)

| Concept | Taught in |
|---|---|
| `BaseModel`, type-hinted fields | [Lesson 03](../../lessons/03-request-bodies-and-pydantic-validation.md) |
| `Literal[...]` for an exact set of allowed values | [Lesson 03](../../lessons/03-request-bodies-and-pydantic-validation.md) |
| `Field(min_length=..., max_length=...)` | [Lesson 03](../../lessons/03-request-bodies-and-pydantic-validation.md) (`ge`/`le` for numbers follow the identical pattern) |
| `@field_validator` + `@classmethod`, raising `ValueError` | [Lesson 03](../../lessons/03-request-bodies-and-pydantic-validation.md) |
| Reading `detail`/`type`/`loc`/`msg`/`input` in a `422` response | [Lesson 03](../../lessons/03-request-bodies-and-pydantic-validation.md) |
| Optional query parameters (`X | None = None`) | [Lesson 02](../../lessons/02-path-and-query-parameters.md) |
| `status_code=201` on a decorator | [Lesson 06](../../lessons/06-error-handling-status-codes-and-responses.md) (a brief forward-reference — you only need the one line, not the whole lesson yet) |

## Acceptance criteria

- [ ] A valid `POST /adventurers` request returns `201` and echoes the data back.
- [ ] `level: 0` and `level: 101` both return `422`.
- [ ] `character_class: "necromancer"` returns `422` with `type` containing `"literal_error"`.
- [ ] `name: "   "` (three spaces) returns `422` with a `msg` matching your own custom validator's message, not a generic Pydantic one.
- [ ] `GET /adventurers/search?min_level=10` and `GET /adventurers/search` (no query params at all) both succeed with `200` and `[]`.
- [ ] `VALIDATION_NOTES.md` accurately records the three requested `type`/`loc` pairs, in your own words.

## What to submit

Point your AI session at your completed `starter/` folder and say *"Review my solution for exercise 02."*

## Hints

**Level 1:** Start from Lesson 03's own `Quest` example almost directly — same shape (a `BaseModel`, a `Literal` field, a `Field`-constrained string, a `@field_validator`), different field names.

**Level 2:** For the whitespace-only name check: `value.strip()` gives you the name with leading/trailing whitespace removed — if that's empty, the original was whitespace-only (or truly empty, which `min_length=1` might not even catch, since `"   "` has length 3).

**Level 3 (near-answer):**
```python
@field_validator("name")
@classmethod
def name_must_not_be_blank(cls, value: str) -> str:
    if not value.strip():
        raise ValueError("Name cannot be blank or only whitespace.")
    return value
```
