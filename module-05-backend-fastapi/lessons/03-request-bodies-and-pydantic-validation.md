# Lesson 03 — Request Bodies and Pydantic Models: Validation, Explained Deeply

**Verified against (August 2026):** Pydantic **2.13.4** (confirmed via `https://pypi.org/pypi/pydantic/json`). Pydantic's own migration guide (`docs.pydantic.dev/latest/migration/`), confirmed while writing this lesson, is explicit that the old Pydantic v1 style (`class Config:` nested inside a model; the bare `@validator` decorator) is deprecated in favor of the `model_config = ConfigDict(...)` class attribute and the `@field_validator` decorator shown below — this lesson teaches only the current, v2 idioms; if you ever see the older style in an existing codebase or tutorial, recognize it as legacy, not something to write in new code.

## What you'll learn

- What a **request body** is, and how it's genuinely different from a query parameter — same underlying idea (data traveling *in* to your route), different location in the request.
- What **Pydantic** actually is, and what job it does inside FastAPI specifically.
- How to define a **Pydantic model**, and how it becomes the shape of a request body automatically.
- What **validation** actually means, precisely — not "checking if data is correct" in the abstract, but the exact mechanical process Pydantic runs, and exactly what happens, step by step, when a request fails it.
- The precise shape of a validation error response — every field in it, and what each one is for.
- `model_config`, `Field`, and `@field_validator` — the current, real tools for constraining and cross-checking data beyond plain type hints.
- Pydantic's `Literal` type, and using `Field(alias=...)` to accept/return a different name than your Python code uses internally.

## Why this matters

The master plan flags this specific lesson for real depth, and for good reason: **Pydantic models and the validation they perform are the actual foundation everything else in this module sits on top of.** Lesson 02's path/query parameter conversion was already a small taste of this; this lesson is where you meet the real engine doing that work, by name, and use it deliberately for the first time — to describe, precisely, what a valid "create a quest" request must look like, and to get a real, structured, useful error back the instant a request doesn't match. This is also the lesson that makes the QuestLog capstone's `Quest` model possible, matching the exact shape Module 04's frontend already expects.

## Prerequisites

Lessons 01–02. Module 01, Lesson 09 (type hints — Pydantic models are built entirely out of type-hinted class attributes). Module 01, Lesson 05 (classes — a Pydantic model *is* a Python class, inheriting from `BaseModel`). Module 02, Lesson 03 (status codes — `422` reappears constantly in this lesson, now fully explained). Module 01, Lesson 08 (JSON — a request body, in this course, is always JSON text).

## The concept, explained simply

A **request body** is data a client sends *inside* the request, as opposed to *in the URL* (a path/query parameter). Recall Module 02, Lesson 03: `POST`, `PUT`, and `PATCH` requests commonly carry a body; `GET` requests conventionally don't. Where a query parameter is naturally one small piece of text, a request body is naturally *structured* — a whole object's worth of fields at once (a new quest's title, description, priority, and quest line, all together) — and JSON (Module 01, Lesson 08; Module 02, Lesson 05) is the format it's almost always written in.

**Pydantic** is the library FastAPI uses, under the hood, to describe "what shape of data is acceptable here" and to actually check incoming data against that description. A **Pydantic model** is a Python class — you write it once, as a set of type-hinted attributes — that becomes, simultaneously, three things: a description of the *shape* you expect (used to generate documentation, Lesson 07), the actual code that *checks* incoming data against that shape, and a real Python object your route function can then work with directly, with every field already the correct type. **Validation** is the precise name for that checking step: the process of confirming that a piece of raw data (here, JSON text from a request body) actually matches a described shape, converting each field to its correct Python type as it goes, and — this is the part beginners underestimate — producing a specific, itemized, machine-readable description of *exactly* what's wrong, field by field, the instant it doesn't match, rather than just a vague pass/fail.

## The details

### Your first Pydantic model

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Quest(BaseModel):
    title: str
    description: str
    priority: str

@app.post("/quests")
def create_quest(quest: Quest):
    return {"received": quest}
```

**Line by line:**
- `from pydantic import BaseModel` — `BaseModel` is the class every Pydantic model inherits from (Module 01, Lesson 05's inheritance, doing real work again). Inheriting from it is what turns an ordinary-looking class into something Pydantic actively validates and FastAPI actively recognizes.
- `class Quest(BaseModel): title: str ...` — each type-hinted class attribute (no `__init__` needed — `BaseModel` generates one for you, based on exactly these annotations) declares one required field of that model, with its required type. This is genuinely new compared to Module 01, Lesson 05's classes: you never wrote `self.title = title` anywhere, and it still works.
- `def create_quest(quest: Quest):` — here's the second half of the rule Lesson 02 introduced: a function parameter whose type hint is a **Pydantic model** (not a simple type like `str`/`int`) tells FastAPI "expect a JSON request body shaped like this model," rather than "expect a query parameter." FastAPI reads the raw JSON body, hands it to `Quest` for validation, and — if it passes — calls your function with a real, fully-formed `Quest` instance already assigned to `quest`.

```bash
curl -i -X POST http://127.0.0.1:8000/quests \
  -H "Content-Type: application/json" \
  -d '{"title": "Slay the Dragon", "description": "...", "priority": "high"}'
```
**Expected:** `HTTP/1.1 200 OK` and a JSON body echoing the same data back (wrapped in `{"received": ...}`). The `-H "Content-Type: application/json"` flag sets the exact header Module 02, Lesson 04 taught you about, telling the server how to interpret the bytes in `-d`'s body — always include it when sending JSON with `curl`, even though some servers guess correctly without it.

### What validation actually does, step by step, when a request is bad

Send a request missing a required field:

```bash
curl -i -X POST http://127.0.0.1:8000/quests \
  -H "Content-Type: application/json" \
  -d '{"title": "Slay the Dragon"}'
```

**Expected, exactly:**
```
HTTP/1.1 422 Unprocessable Content

{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "description"],
      "msg": "Field required",
      "input": {"title": "Slay the Dragon"}
    },
    {
      "type": "missing",
      "loc": ["body", "priority"],
      "msg": "Field required",
      "input": {"title": "Slay the Dragon"}
    }
  ]
}
```

**This is the exact shape you need to be able to read fluently, field by field — this is the actual payoff of this lesson:**

- **`detail`** is always a list, never a single object — because a single request can fail validation for *multiple, independent* reasons at once (here: two separate missing fields), and Pydantic reports every one it finds, not just the first.
- **Each item's `type`** is a short, stable, machine-readable error category (`missing`, `int_parsing` from Lesson 02, and many more you'll meet as this lesson continues) — code (yours, or a frontend's) can safely branch on this string; it will not change wording between Pydantic versions the way `msg` occasionally might.
- **`loc`** (short for "location") is a list describing exactly *where*, in the structure of the request, the problem is — `["body", "description"]` means "inside the request body, the top-level field named `description`." For a path/query parameter (Lesson 02), you'd instead see `["path", "index"]` or `["query", "quest_line"]` — the same `loc` mechanism, just pointing somewhere else, which is exactly why Lesson 02's error example used this identical shape.
- **`msg`** is a short, human-readable explanation, meant for a developer reading logs or a UI displaying an error message directly — not meant to be pattern-matched by code (use `type` for that).
- **`input`** is the *actual value* Pydantic received at that location, before rejecting it — genuinely useful for debugging "why did this fail," since it shows you exactly what the server saw, not what you *think* you sent.

**Crucially: your `create_quest` function's body never ran at all.** FastAPI intercepted the request, ran Pydantic's validation, found it invalid, and generated this entire `422` response itself, automatically — the exact same "validation happens before your code, and produces this specific shape" fact Lesson 02 already showed you for a single bad path parameter, now shown at full scale for a whole request body with multiple problems reported at once.

**Try it yourself:** send a request with `priority` present but as a number instead of a string (`"priority": 5`) instead of omitting a field. Predict the `type` value in the resulting error before running it. (Pydantic will actually accept `5` here and silently coerce it to the string `"5"`, by default, for a plain `str` field — a real, sometimes-surprising Pydantic v2 behavior worth knowing; the `Literal` type shown below is exactly how you close this gap for a field like `priority`, which should only ever be one of a few exact values.)

### `Literal` — an exact set of allowed values, not just "any string"

Recall Module 01, Lesson 09's union type hint, `X | None` — "this value is one type, or `None`." **`Literal`** is a related but distinct idea: "this value must be *exactly* one of these specific literal values," not merely "some string" or "some int." Module 04's frontend already relies on this exact idea in TypeScript (`type Priority = "low" | "medium" | "high"`, a union of specific string literals, from `types/quest.ts`) — Pydantic's `Literal` is Python's own version of precisely that concept.

```python
from typing import Literal
from pydantic import BaseModel

class Quest(BaseModel):
    title: str
    description: str
    priority: Literal["low", "medium", "high"]
```

```bash
curl -i -X POST http://127.0.0.1:8000/quests \
  -H "Content-Type: application/json" \
  -d '{"title": "T", "description": "D", "priority": "urgent"}'
```
**Expected:** `422`, with an error item whose `type` is `"literal_error"` and `msg` reading something like `"Input should be 'low', 'medium' or 'high'"`. Unlike the plain `str` field above, there is no coercion possible here — `"urgent"` is a perfectly good string, it simply isn't one of the three exact values allowed, and Pydantic rejects it outright.

### `Field()` — constraints beyond a bare type hint

```python
from pydantic import BaseModel, Field

class Quest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str
    priority: Literal["low", "medium", "high"]
```

`Field(...)` lets you attach constraints to a field beyond what its bare type hint alone can express — `min_length=1` specifically closes a gap plain `str` leaves wide open: an empty string `""` is a perfectly valid `str`, but almost certainly not a valid quest title. Send `{"title": "", ...}` and confirm you now get a `422` with `type: "string_too_short"` — a real, deliberate quality-of-data rule, not just a type check.

### `model_config` — configuring a model's overall behavior

Pydantic v2's current, correct way to configure a model's own behavior (its Pydantic v1 predecessor used a nested `class Config:` inside the model — deprecated; do not write that in new code) is a single class attribute:

```python
from pydantic import BaseModel, ConfigDict

class Quest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str
    description: str
```

`str_strip_whitespace=True` makes every `str` field on this model automatically have leading/trailing whitespace stripped during validation — `"  Slay the Dragon  "` in becomes `"Slay the Dragon"` out, with zero extra code in your route. This is one of many available config options; you'll meet one more, `populate_by_name`, in the aliasing section below.

### `@field_validator` — custom, code-driven checks

Some rules can't be expressed as a bare type or a `Field(...)` constraint — they need actual logic. Pydantic v2's current, correct tool for this is the `@field_validator` decorator (its v1 predecessor, the bare `@validator` decorator, is deprecated — do not write that in new code):

```python
from pydantic import BaseModel, field_validator

class Quest(BaseModel):
    title: str
    description: str

    @field_validator("title")
    @classmethod
    def title_must_not_be_generic(cls, value: str) -> str:
        if value.strip().lower() in {"quest", "task", "todo"}:
            raise ValueError("Title is too generic — be specific about what this quest actually is.")
        return value
```

**Line by line:** `@field_validator("title")` — another decorator (Module 01, Lesson 10 continuing to pay off), this time named for the specific field it validates — registers this method to run, specifically, whenever the `title` field is being validated. `@classmethod` — required here because Pydantic calls this as a method on the *class*, not on any particular instance (there isn't a real, fully-formed `Quest` instance yet — validation is still in progress). The method receives the field's already-type-checked value (`value: str` — by this point, Pydantic has already confirmed it's a string; a field validator runs *after* the basic type check, by default, checking mode `"after"`) and must either `return` the value (unchanged, or transformed — this is also where you could `return value.strip()` to clean it up) or `raise ValueError(...)` with a clear message to reject it. **Whatever text you pass to `ValueError` appears in that specific error's `msg` in the `422` response** — writing a genuinely clear, specific message here directly improves the real error a real API consumer will actually see. (Verified precisely, running this exact example: Pydantic v2 prepends the literal text `"Value error, "` in front of your own message, so `raise ValueError("Title is too generic...")` produces `msg: "Value error, Title is too generic..."` — expect that fixed prefix, not your text alone, word for word.)

```bash
curl -i -X POST http://127.0.0.1:8000/quests \
  -H "Content-Type: application/json" \
  -d '{"title": "Quest", "description": "D"}'
```
**Expected:** `422`, `type: "value_error"`, `msg` reading exactly `"Value error, Title is too generic — be specific about what this quest actually is."` — Pydantic's own fixed `"Value error, "` prefix followed by the exact text you wrote.

### Aside: matching an existing frontend's camelCase with `Field(alias=...)`

Python convention (and this course's own, throughout Module 01) is `snake_case` for variable/attribute names — but Module 04's frontend `Quest` type uses `camelCase` field names (`questLine`, `createdAt`), because that's the JavaScript/TypeScript convention instead. Rather than forcing one side's convention onto the other, Pydantic's `Field(alias=...)` lets a model use idiomatic Python names *internally* while accepting and returning a *different* name in the actual JSON:

```python
from pydantic import BaseModel, ConfigDict, Field

class Quest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str
    quest_line: str = Field(alias="questLine")
```

**Line by line:** `Field(alias="questLine")` says "in JSON, this field is called `questLine`; in my Python code, I still want to call it `quest_line`." `populate_by_name=True` is necessary specifically so that Python code *inside your own backend* can still construct a `Quest` using the Python name (`Quest(title="...", quest_line="...")`) — without it, only the alias (`questLine`) would be accepted, which would be awkward for your own server-side code, even though it's exactly what you want for the JSON travelling to/from the frontend. FastAPI, by default, serializes a Pydantic model's *response* using its aliases (not the internal Python names) — so a route returning this `Quest` produces real JSON with `"questLine"`, matching Module 04's frontend exactly, while every line of your own backend code reads and writes the idiomatic `quest_line`. This is precisely the tool the QuestLog capstone (Lesson 08) uses to match Module 04's existing `Quest` type without changing a single field name on the frontend.

## Common mistakes & gotchas

- **Believing a `422` means "something is broken."** It means the *client's* request didn't match the described shape — exactly a `4xx`, per Module 02, Lesson 03's own category rule: the client did something the server won't accept, not a server-side bug. Read `detail` before assuming anything is actually wrong with your API.
- **Using a plain `str` field for something that should be a fixed, exact set of values (a status, a priority, a category) and being surprised any string is silently accepted.** Use `Literal[...]` specifically for "exactly one of these values" — it rejects everything else outright, with a clear error, instead of quietly accepting a typo'd value your own code never expected.
- **Writing a Pydantic v1-style `class Config:` block or bare `@validator` in new code**, copied from an older tutorial. Both are deprecated in Pydantic v2 — use `model_config = ConfigDict(...)` and `@field_validator`, per this lesson.
- **Forgetting `@classmethod` on a `@field_validator` method**, or forgetting to `return value` at the end of one (returning `None` implicitly, which then silently becomes the field's actual value — a subtle, confusing bug, since nothing raises an error, the field just quietly becomes `None`).
- **Assuming `input` in an error response is safe to display directly to an end user without sanitizing it.** It's genuinely useful for developers debugging via logs or the docs UI; treat it as internal-facing information, not something to blindly render in a production frontend's error message.

## How this connects

You've now met the real engine behind everything Lesson 02's path/query parameters already hinted at, and used it deliberately to describe a request body's exact required shape — this is the single most-used mechanism for the rest of this module and, per `RUNNING_PROJECT.md`'s fixed technology decisions, for the rest of this course's backend work (Pydantic v2 is the course's permanent choice for request/response modeling). Lesson 04 covers `Depends()` — FastAPI's dependency injection mechanism — which frequently works *alongside* Pydantic models exactly like the ones you just built (e.g., a dependency that looks up a quest by the `quest_id` Lesson 02 taught you to read, and hands back a real `Quest` — or raises a clean `404` if it doesn't exist, foreshadowing Lesson 06).

## Quick self-check

1. What's the actual difference between a query parameter (Lesson 02) and a request body, in terms of *where* the data lives in an HTTP request?
2. Walk through, field by field, what `type`, `loc`, `msg`, and `input` each mean in a validation error response.
3. Why does a plain `str` field accept `5` and silently convert it to `"5"`, while a `Literal["low", "medium", "high"]` field rejects `"urgent"` outright — what's the actual difference in what each one is checking?
4. What must a `@field_validator` method do to (a) accept a value and (b) reject one — and what determines the exact `msg` text a caller sees when it rejects one?
5. Why does `Field(alias="questLine")` combined with `populate_by_name=True` let your own backend code use `quest_line` while a client still sends/receives `questLine`?
