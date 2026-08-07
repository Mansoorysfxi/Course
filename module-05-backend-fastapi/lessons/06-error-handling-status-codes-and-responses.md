# Lesson 06 — Error Handling, Status Codes, and Structured Responses

## What you'll learn

- `HTTPException` — FastAPI's standard way of deliberately stopping a route and answering with a specific error, on purpose.
- How to set the exact status code a *successful* route returns, beyond FastAPI's defaults.
- `response_model` — describing, and enforcing, the shape of a successful response.
- Custom **exception handlers** — reacting to a whole category of exception, application-wide, instead of catching it in every route individually.
- How to design your own API's errors so they're actually useful to whoever's calling it — a real design skill, not just syntax.

## Why this matters

Lesson 03 already showed you the error shape FastAPI generates *automatically* when a request fails validation. This lesson is about the errors *you* deliberately produce — "this quest doesn't exist," "you can't delete a quest that's already done" — and about controlling exactly what a successful response looks like too, not just relying on FastAPI's defaults. This is also where Module 02, Lesson 03's whole status-code vocabulary (already taught in full there — this lesson does not re-teach what `404` or `201` *mean*, only how to actually produce them from FastAPI) becomes something you use deliberately, on every route you write from here on.

## Prerequisites

Lessons 01–05. **Module 02, Lesson 03 in full** — this lesson assumes you already know what every common status code means and the difference between safe/idempotent methods; it only covers the FastAPI-specific mechanics of producing them. Module 01, Lesson 06 (Python's own `raise`/exceptions — `HTTPException` is a real Python exception, raised exactly the way Lesson 06 taught).

## The concept, explained simply

An HTTP response always has a status code, whether you think about it or not — every route you've written so far has been quietly returning FastAPI's default of `200 OK` for success. **Error handling, in FastAPI, is mostly about being deliberate instead of accidental about status codes and response shapes** — recognizing the specific situations (a missing resource, a business-rule violation, an unexpected server-side failure) where the default isn't right, and having one clear, consistent way to produce the correct one every time, rather than each route inventing its own ad-hoc error format.

## The details

### `HTTPException` — stopping a route on purpose

You've already seen this used, without a full explanation, in Lesson 04:

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()
quests_db = {"quest-001": {"title": "Slay the Dragon", "done": False}}

@app.get("/quests/{quest_id}")
def get_quest(quest_id: str):
    quest = quests_db.get(quest_id)
    if quest is None:
        raise HTTPException(status_code=404, detail="Quest not found")
    return quest
```

```bash
curl -i http://127.0.0.1:8000/quests/does-not-exist
```
**Expected:**
```
HTTP/1.1 404 Not Found

{"detail":"Quest not found"}
```

**Line by line:** `HTTPException` is a real Python **exception class** (Module 01, Lesson 06 — it inherits from Python's own `Exception`, just like the custom exceptions that lesson taught you to write). `raise HTTPException(status_code=404, detail="Quest not found")` immediately stops the current function's execution — exactly Lesson 06's own definition of what `raise` does — and, because FastAPI specifically watches for this exception type at a level above every route, it catches it and builds a proper HTTP response from its two arguments: `status_code` becomes the response's actual status code, and `detail` becomes the body's `"detail"` field — the exact same field name you already saw in Lesson 03's automatic validation errors, which is not a coincidence: FastAPI's own automatic `422` responses are themselves implemented as a specific kind of `HTTPException`-like mechanism internally, using this same field name deliberately, so a client can check `response.json()["detail"]` consistently regardless of whether an error came from your own code or from Pydantic's automatic validation.

`detail` can be more than a plain string, when a richer error would genuinely help the caller:

```python
raise HTTPException(
    status_code=409,
    detail={"error": "quest_already_done", "quest_id": quest_id, "message": "This quest is already marked done."},
)
```

Recall Module 02, Lesson 03's precise definition of `409 Conflict`: "the request conflicts with the resource's current state" — exactly the case here (trying to do something that's only valid for an *incomplete* quest, against one that's already done).

### Setting a status code for a *successful* response

FastAPI defaults every route to `200 OK` on success unless told otherwise — correct for `GET`, but not for every method (recall Module 02, Lesson 03: `POST` that creates something conventionally returns `201 Created`; a `DELETE` with nothing meaningful to send back conventionally returns `204 No Content`):

```python
from fastapi import status

@app.post("/quests", status_code=status.HTTP_201_CREATED)
def create_quest(quest: Quest):
    ...
    return quest

@app.delete("/quests/{quest_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quest(quest_id: str):
    quests_db.pop(quest_id, None)
    return None
```

**Line by line:** `status_code=status.HTTP_201_CREATED` on the decorator itself (not inside the function) sets the status code for the *successful* path — FastAPI's `fastapi.status` module is nothing more than a large collection of named constants (`HTTP_201_CREATED` is literally the integer `201`, just written with a name a reader doesn't need to look up) — using the named constants over bare numbers is this course's convention throughout, purely for readability; both work identically. `HTTP_204_NO_CONTENT`, per its own definition (Module 02, Lesson 03), means the response deliberately has no body at all — returning `None` (or nothing) from a `204` route is correct and expected; returning a real body from a `204` route is technically against the HTTP spec and some clients will treat it as a bug.

### `response_model` — describing (and enforcing) what a successful response looks like

```python
from pydantic import BaseModel

class QuestOut(BaseModel):
    id: str
    title: str
    done: bool

@app.get("/quests/{quest_id}", response_model=QuestOut)
def get_quest(quest_id: str):
    quest = quests_db[quest_id]
    return quest   # a plain dict, possibly with MORE fields than QuestOut declares
```

**What `response_model` actually does, precisely:** it's a second, independent validation/serialization step — separate from any input validation Lesson 03 already taught you — applied to whatever your function *returns*, before it goes out over the network. Two real, practical consequences: (1) if `quest` (a plain `dict`, in the example above) has *extra* fields beyond what `QuestOut` declares, they are silently dropped from the response — this is a genuinely useful, deliberate way to avoid ever accidentally leaking an internal-only field (a stored password hash, in a later module, is the canonical example) just because it happened to exist on the object you returned; and (2) if your function returns something *missing* a field `QuestOut` requires, FastAPI raises a server-side error rather than silently sending broken data — catching a real bug in your own route before it ever reaches a client. `response_model` also feeds directly into the auto-generated docs (Lesson 07) — the exact shape of a successful response becomes part of your API's documented contract, not just its errors.

### Custom exception handlers — one place to handle a whole category of problem

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

class QuestNotFoundError(Exception):
    def __init__(self, quest_id: str):
        self.quest_id = quest_id

@app.exception_handler(QuestNotFoundError)
async def quest_not_found_handler(request: Request, exc: QuestNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": f"No quest with id '{exc.quest_id}'"},
    )

@app.get("/quests/{quest_id}")
def get_quest(quest_id: str):
    quest = quests_db.get(quest_id)
    if quest is None:
        raise QuestNotFoundError(quest_id)
    return quest
```

**Line by line:** `QuestNotFoundError` is a **custom exception** — exactly Module 01, Lesson 06's own pattern, a plain class inheriting from `Exception`, carrying whatever extra information (`quest_id`, here) is useful to whoever eventually handles it. `@app.exception_handler(QuestNotFoundError)` registers a function to run, application-wide, any time *any* route raises this specific exception type — your route function itself just `raise`s a plain, meaningful, domain-specific exception (`QuestNotFoundError(quest_id)`) with zero knowledge of HTTP status codes or response shapes at all; a separate handler, defined once, is entirely responsible for turning that into an actual HTTP response. **Why this is worth the extra structure over just using `HTTPException` everywhere:** once your application has more than a couple of routes that can all hit "quest not found," a custom exception plus one handler means the exact response shape only has to be decided, and fixed, in one place — change the handler once, and every route raising `QuestNotFoundError` gets the update automatically, instead of hunting down every individual `raise HTTPException(...)` call across your codebase.

## Common mistakes & gotchas

- **Using a bare `Exception` (or a generic one) for `raise` instead of `HTTPException` or a purpose-built custom exception, and letting it propagate unhandled.** An unhandled exception FastAPI doesn't recognize produces a generic `500 Internal Server Error` with no useful `detail` for the caller — always raise something specific and meaningful, or let a registered exception handler (or `HTTPException` itself) turn it into a proper, informative response.
- **Choosing `404` vs `422` vs `409` inconsistently.** Recall Module 02, Lesson 03's precise definitions: `404` — nothing exists at this path/identifier; `422` — the request was syntactically fine but semantically invalid (almost always Pydantic's own automatic errors, from Lesson 03, though you can raise this yourself for a business rule too); `409` — the request conflicts with the resource's *current state* (trying to complete an already-completed quest, for instance). Getting these consistently right, across your whole API, is a real, valuable design skill — pick deliberately, every time, rather than defaulting to whichever code you remember first.
- **Forgetting `response_model` and being surprised an internal-only field leaked into a real response.** If a route ever returns something built from a larger internal object than the client should see, add a `response_model` explicitly naming only what should actually go out.
- **Registering an exception handler for a type that's too broad** (e.g., handling bare `Exception` itself) **and accidentally swallowing genuine bugs as if they were expected, well-formed errors.** Keep exception handlers scoped to specific, meaningful exception types you deliberately raise yourself — never so broad they hide a real, unexpected crash behind a misleadingly clean error response.
- **Returning a body from a `204 No Content` route.** Per the HTTP spec (and Module 02, Lesson 03's own definition), `204` means "no body is coming" — return `None`, not an empty dict or any other value, from a route declared with this status code.

## How this connects

You now have full, deliberate control over both your errors and your successful responses' shapes and status codes — directly using Module 02, Lesson 03's vocabulary, which this lesson never re-taught, only wired up to real FastAPI code. Lesson 07 covers the interactive docs and OpenAPI properly — and every `response_model`, every `status_code`, and every `HTTPException` you write from here on feeds directly into exactly what that documentation shows, which is why getting this lesson's habits right now pays off doubly.

## Quick self-check

1. What two arguments does `HTTPException` take, and where does each one end up in the actual HTTP response?
2. Why does `HTTPException`'s response body use the field name `"detail"`, and where else in this module have you already seen that exact field name?
3. What does `response_model` actually do to a route's return value that plain type hints on the function's return type annotation would not do at runtime?
4. Walk through why a custom exception (`QuestNotFoundError`) plus one `@app.exception_handler(...)` can be a better design than raising `HTTPException` directly in every route that might hit the same "not found" situation.
5. Using Module 02, Lesson 03's own definitions, explain why "the quest you're trying to complete is already complete" is a `409`, not a `404` or a `422`.
