# Lesson 08 — Building the QuestLog API: A Full In-Memory CRUD Backend

**Verified against (August 2026):** the recommended multi-file project structure below (`app/main.py`, `app/routers/`, `app/dependencies.py`) is confirmed directly against FastAPI's own "Bigger Applications - Multiple Files" documentation (`fastapi.tiangolo.com/tutorial/bigger-applications/`), built around `APIRouter` — FastAPI's own term for exactly this pattern.

## What you'll learn

- **CRUD** — Create, Read, Update, Delete — as a concrete, standard shape for a resource's API, and how it maps onto specific HTTP methods (Module 02, Lesson 03) you already know the meaning of.
- `APIRouter` — organizing routes across multiple files instead of one growing `main.py`, following FastAPI's own recommended structure for a project bigger than a single file.
- How to put every piece from Lessons 01–07 together: Pydantic models with aliases (Lesson 03), a `get_quest_or_404` dependency (Lesson 04), CORS middleware (Lesson 05), deliberate status codes and a `response_model` (Lesson 06) — into one real, working API.
- Why this capstone's "database" is a plain Python `dict`, and exactly what that choice does and doesn't cost you.
- How to actually run this backend alongside Module 04's frontend, and swap the frontend's mocked `fetchQuests()` for real HTTP calls.

## Why this matters

This is where every separate piece from Lessons 00–07 stops being a small, isolated example and becomes one real, coherent API — the same one Module 04's frontend will actually call. Reading this lesson alongside `project/questlog/backend/` (this module's real, working capstone code) is intentional: this lesson explains the *decisions* behind that code; the code itself is the complete, runnable proof those decisions work.

## Prerequisites

Lessons 00–07, all of them — this lesson assumes every concept from each is already solid, since it uses all of them together with no further re-explanation.

## The concept, explained simply

**CRUD** is a standard, widely-recognized shorthand for the four basic operations almost any "manage a collection of things" API needs: **C**reate a new one, **R**ead (list all, or get one specific one), **U**pdate an existing one, **D**elete one. Mapped onto HTTP methods, following exactly what Module 02, Lesson 03 already taught about what each method *means*: **C**reate → `POST`; **R**ead → `GET` (both the list and the single-item variants); **U**pdate → `PATCH` (a *partial* update — QuestLog's frontend, per Module 04's `QuestUpdate` type, already only ever sends the fields that changed, never the whole object, so `PATCH` — "apply a partial update," per Module 02 — is the semantically correct method here, not `PUT`, which would imply a full replacement); **D**elete → `DELETE`. This module's QuestLog API is a complete CRUD API for exactly one resource: quests.

**Why in-memory, deliberately, for now:** a plain Python `dict`, living in your running server process's own memory, holding every quest, is the simplest possible "database" — and it is explicitly, deliberately temporary. It has one real, honest limitation worth naming directly rather than glossing over: **every quest disappears the instant the server process stops** (a crash, a deploy, even just `--reload` restarting after certain kinds of changes) — there is no actual persistence to disk or to any real storage system at all. Module 06 replaces this exact `dict` with a real PostgreSQL database via SQLAlchemy, and nothing about the *routes* or their contracts changes when that happens — only what's *behind* `get_quest_or_404` and its siblings. Building this in-memory version correctly, with a clean separation between "the routes" and "the storage," is exactly what makes that later swap land cleanly instead of requiring you to rewrite this module's work.

## The details

### Project structure

```
backend/
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py            — creates the FastAPI() app, CORS middleware, includes the router
│   ├── models.py           — the Quest/QuestCreate/QuestUpdate Pydantic models
│   ├── store.py             — the in-memory "database": a dict, plus small helper functions
│   ├── dependencies.py     — get_quest_or_404
│   └── routers/
│       ├── __init__.py
│       └── quests.py        — every /quests route, as an APIRouter
```

This follows FastAPI's own documented recommendation (verified for this lesson) for a project with more than a couple of routes: a `routers/` folder of `APIRouter`s, kept out of `main.py` itself, so `main.py` stays small and focused purely on assembling the pieces. Recall Module 01, Lesson 07's convention — every folder here is a real Python package, with an explicit `__init__.py`, exactly as that lesson recommended for every project from here on.

### The models (`app/models.py`)

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Priority = Literal["low", "medium", "high"]

class QuestBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    description: str
    priority: Priority
    quest_line: str = Field(alias="questLine", min_length=1)

class QuestCreate(QuestBase):
    """Exactly the fields a client supplies to create a quest -- matches
    Module 04's NewQuestInput type: id/done/createdAt are always assigned
    by the server, never accepted from a client."""

class QuestUpdate(BaseModel):
    """Every field optional -- matches Module 04's QuestUpdate
    (Partial<Omit<Quest, "id" | "createdAt">>). A client sends only the
    fields it's actually changing."""
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    priority: Priority | None = None
    quest_line: str | None = Field(default=None, alias="questLine", min_length=1)
    done: bool | None = None

class Quest(QuestBase):
    """The full stored/returned shape -- matches Module 04's Quest type
    exactly, field for field."""
    id: str
    done: bool
    created_at: str = Field(alias="createdAt")
```

**Line by line of what's new, tying directly back to Lesson 03:** `QuestBase` holds every field common to both "creating" and "the full stored quest" — `QuestCreate` and `Quest` both inherit from it (Module 01, Lesson 05's inheritance, doing real, practical work here: no duplicated field declarations between the two). `Field(alias="questLine", ...)` and `Field(alias="createdAt")` are exactly Lesson 03's aliasing technique, used for real this time, for the specific reason that lesson set up: Module 04's frontend `Quest` type uses `questLine`/`createdAt`, and this alias means the JSON travelling to/from the frontend uses those exact names while every line of this backend's own Python code uses idiomatic `quest_line`/`created_at`. `QuestUpdate` makes every field genuinely optional (`| None = None`, per Lesson 02's own distinction between a real default and "genuinely absent") — matching Module 04's `QuestUpdate = Partial<...>` type precisely: a client updating only a quest's `done` status sends `{"done": true}` alone, and every other field simply stays whatever it already was.

### The in-memory store (`app/store.py`)

```python
import uuid
from datetime import datetime, timezone
from app.models import Quest, QuestCreate, QuestUpdate

_quests: dict[str, Quest] = {}

def seed() -> None:
    """Populates the store with the same starting quests Module 04's
    fetchQuests() used, so the API behaves familiarly on first run."""
    starter = [
        QuestCreate(title="Slay the Dragon", description="...", priority="high", quest_line="Main Story"),
        QuestCreate(title="Gather Healing Herbs", description="...", priority="low", quest_line="Village Errands"),
    ]
    for quest_create in starter:
        create_quest(quest_create)

def list_quests() -> list[Quest]:
    return list(_quests.values())

def get_quest(quest_id: str) -> Quest | None:
    return _quests.get(quest_id)

def create_quest(data: QuestCreate) -> Quest:
    quest = Quest(
        id=str(uuid.uuid4()),
        done=False,
        created_at=datetime.now(timezone.utc).isoformat(),
        **data.model_dump(),
    )
    _quests[quest.id] = quest
    return quest

def update_quest(quest_id: str, changes: QuestUpdate) -> Quest | None:
    existing = _quests.get(quest_id)
    if existing is None:
        return None
    updated = existing.model_copy(update=changes.model_dump(exclude_unset=True))
    _quests[quest_id] = updated
    return updated

def delete_quest(quest_id: str) -> bool:
    return _quests.pop(quest_id, None) is not None
```

**Line by line of the genuinely new pieces:**
- `_quests: dict[str, Quest] = {}` — the entire "database": a Python dict, module-level (Module 01, Lesson 07's own warning about top-level code applies here deliberately — this dict is created once, when this module is first imported, and every route shares this exact same dict for the life of the running server process), keyed by each quest's `id`.
- `str(uuid.uuid4())` — Python's standard-library way of generating a random, effectively-unique identifier — the direct server-side equivalent of Module 04's frontend using `crypto.randomUUID()` for exactly the same purpose. Neither one needs to check for collisions in practice; the space of possible UUIDs is astronomically large.
- `datetime.now(timezone.utc).isoformat()` — produces an ISO 8601 timestamp (Module 01, Lesson 08's own format — Module 04's frontend `createdAt` field is documented as exactly this same standard), in UTC specifically (never a server's local time zone, which would make timestamps ambiguous the moment this app is ever deployed somewhere else — a real, professional habit worth having from day one). **Note the exact text differs slightly from JavaScript's `.toISOString()`** — Python's version ends in `+00:00` rather than a bare `Z`, both are equally valid ISO 8601 (the format explicitly allows either), and both still sort correctly as plain strings (exactly the property Module 04's `QuestListPage.tsx` already relies on for its "sort by newest" feature), so this difference causes no real problem.
- `**data.model_dump()` — `model_dump()` is a Pydantic v2 method converting a model instance back into a plain Python `dict` of its fields; the `**` spreads that dict's key/value pairs directly into `Quest(...)`'s keyword arguments (Module 01, Lesson 02's own `**kwargs`-spreading mechanism, used here in the opposite direction from where you usually see it — spreading data *into* a call rather than collecting it *from* one).
- `existing.model_copy(update=changes.model_dump(exclude_unset=True))` — `model_copy(update={...})` is Pydantic's way of producing a new model instance that's identical to an existing one except for specific overridden fields — this is precisely the "produce a new object rather than mutating the old one" discipline Module 04's own `updateQuest` (`{ ...quest, ...changes }`) already followed on the frontend, just Pydantic's own version of it. `exclude_unset=True` is the crucial piece making `QuestUpdate` genuinely partial: it excludes any field the client's request simply never mentioned at all (as opposed to a field explicitly sent as `null`) from the resulting dict, so those fields are left completely untouched on `existing` rather than being overwritten with `None`.

### The dependency (`app/dependencies.py`)

```python
from fastapi import HTTPException, status
from app.models import Quest
from app import store

def get_quest_or_404(quest_id: str) -> Quest:
    quest = store.get_quest(quest_id)
    if quest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No quest with id '{quest_id}'")
    return quest
```

Exactly Lesson 04's own dependency, now for real — every route below that needs an *existing* quest by ID uses this one function, via `Depends(...)`, instead of repeating this exact check.

### The router (`app/routers/quests.py`)

```python
from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.dependencies import get_quest_or_404
from app.models import Quest, QuestCreate, QuestUpdate
from app import store

router = APIRouter(prefix="/api/quests", tags=["quests"])

@router.get("", response_model=list[Quest])
def list_quests(done: bool | None = None, priority: str | None = None):
    quests = store.list_quests()
    if done is not None:
        quests = [q for q in quests if q.done == done]
    if priority is not None:
        quests = [q for q in quests if q.priority == priority]
    return quests

@router.get("/{quest_id}", response_model=Quest)
def get_quest(quest: Annotated[Quest, Depends(get_quest_or_404)]):
    return quest

@router.post("", response_model=Quest, status_code=status.HTTP_201_CREATED)
def create_quest(data: QuestCreate):
    return store.create_quest(data)

@router.patch("/{quest_id}", response_model=Quest)
def update_quest(
    quest: Annotated[Quest, Depends(get_quest_or_404)],
    changes: QuestUpdate,
):
    return store.update_quest(quest.id, changes)

@router.delete("/{quest_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quest(quest: Annotated[Quest, Depends(get_quest_or_404)]):
    store.delete_quest(quest.id)
    return None
```

**Line by line of what's new:** `APIRouter(prefix="/api/quests", tags=["quests"])` — an `APIRouter` behaves like a small, separate `FastAPI()` app (Lesson 01) that hasn't been wired into a real one yet; every route below is declared on `router`, not `app` directly. `prefix="/api/quests"` means every route's own path is written *relative* to that prefix — `@router.get("")` really means `GET /api/quests`, and `@router.get("/{quest_id}")` really means `GET /api/quests/{quest_id}` — avoiding repeating `/api/quests` at the start of every single route. `tags=["quests"]` purely affects how Lesson 07's auto-generated docs group these routes visually — no functional effect. Notice `get_quest` and `delete_quest` both use `Depends(get_quest_or_404)` and never need to check for a missing quest themselves at all — exactly Lesson 04's promised payoff, now used four times across this one small file, with the actual "not found" logic written and tested in exactly one place.

### Wiring it together (`app/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import quests
from app import store

app = FastAPI(title="QuestLog API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quests.router)

@app.on_event("startup")
def startup() -> None:
    store.seed()

@app.get("/")
def root():
    return {"message": "QuestLog API. See /docs for interactive documentation."}
```

**Line by line of what's new:** `app.include_router(quests.router)` is the step that actually attaches every route declared on `quests.router` onto the real, running `app` — before this line, `quests.router` exists as a real Python object with routes recorded on it, but Uvicorn never sees them; this one call merges them in. `@app.on_event("startup")` registers a function to run exactly once, when the server first starts (not per-request) — used here to seed the in-memory store with a few starting quests, so the API isn't empty the very first time you (or the frontend) call it, mirroring Module 04's own `seedQuests` in its mocked `fetchQuests.ts`.

### Running it, and testing every operation with `curl`

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

```bash
curl http://127.0.0.1:8000/api/quests
```
**Expected:** a JSON array of the two seeded quests.

```bash
curl -i -X POST http://127.0.0.1:8000/api/quests \
  -H "Content-Type: application/json" \
  -d '{"title": "Repair the Bridge", "description": "It has a collapsed section.", "priority": "medium", "questLine": "Side Quests"}'
```
**Expected:** `201 Created`, and a full `Quest` JSON object — note the request body used `questLine` (the alias), and the response also uses `questLine` — matching Module 04's frontend exactly, per Lesson 03's aliasing.

```bash
curl -i -X PATCH http://127.0.0.1:8000/api/quests/<the-id-from-above> \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```
**Expected:** `200 OK`, the same quest, now with `"done": true` and every other field completely unchanged.

```bash
curl -i -X DELETE http://127.0.0.1:8000/api/quests/<the-id-from-above>
```
**Expected:** `204 No Content`, no body.

**Try it yourself:** repeat every one of the above through Swagger UI (`/docs`) instead of `curl`, and confirm you get the identical results — this is exactly Lesson 07's promised payoff, used for real for the first time.

### Connecting Module 04's frontend

This module's `project/questlog/` (covered fully in `project/BRIEF.md`) copies Module 04's finished frontend forward and swaps its mocked `fetchQuests()` for real `fetch()` calls to exactly this backend, running on `http://localhost:8000`. Run both at once, per Lesson 00's Step 6 (two terminals), and the Quest Board you already built in Module 04 will show data coming from this real, running Python process instead of a hard-coded mock array — the exact moment this course's running project stops being a frontend-only illusion of a backend.

## Common mistakes & gotchas

- **Forgetting `python -m venv .venv` for the backend and reusing Module 04's frontend's own tooling by mistake.** These are two entirely separate projects, in two entirely separate languages — Module 04's `node_modules/` has nothing to do with this backend's Python packages, and vice versa.
- **CORS errors in the browser console, even though `curl` against the backend works fine.** `curl` never enforces CORS (it isn't a browser) — if the frontend's own `fetch()` calls fail specifically in the browser with a CORS-related console error, re-check `allow_origins` in `main.py` matches the frontend's exact running address (`http://localhost:5173`, unless Vite chose a different port because `5173` was already busy — recall Module 04's own port-conflict note).
- **Quests disappearing after every `--reload`-triggered restart, and being alarmed.** This is the deliberate, stated cost of an in-memory store (Lesson 08's own "why in-memory" section) — expected, not a bug, and the exact motivation for Module 06.
- **Sending `PUT` instead of `PATCH` for an update, out of habit from an older tutorial.** Recall Module 02, Lesson 03's precise distinction — this API's update semantics are genuinely partial (only changed fields, per `QuestUpdate`), which is `PATCH`'s contract, not `PUT`'s.
- **Forgetting `response_model=list[Quest]` on the list route and being surprised the aliasing (`questLine`/`createdAt`) doesn't apply consistently.** `response_model` (Lesson 06) is what actually triggers alias-based serialization on the way out — omitting it can leave you looking at Python's internal field names instead of the aliases the frontend expects.

## How this connects

This lesson is the payoff for every lesson before it in this module — a real, complete, working CRUD API, structured the way FastAPI's own documentation recommends for a project bigger than one file, tested with both of the tools this course has built up (`curl` from Module 02, Swagger UI from this module's own Lesson 07). `project/BRIEF.md` and `project/questlog/` are this exact lesson's code, extended slightly and wired to Module 04's real frontend. Module 06 replaces `app/store.py`'s in-memory `dict` with a real PostgreSQL database via SQLAlchemy — and, because every route only ever talks to `store.py`'s functions (never touching `_quests` directly), that swap changes almost nothing about `app/routers/quests.py` at all.

## Quick self-check

1. Map each of CRUD's four operations to the specific HTTP method this API uses for it, and explain why `PATCH` (not `PUT`) is the correct choice for updates here.
2. What does `app.include_router(quests.router)` actually do, and what would be true (or not true) about `quests.router`'s routes before that line runs?
3. Why does `QuestUpdate.model_dump(exclude_unset=True)` matter specifically for correct partial-update behavior — what would go wrong without `exclude_unset=True`?
4. What is this capstone's "database," precisely, and what specific, real limitation does that choice have — which later module removes it?
5. If the frontend's `fetch()` calls fail in the browser with a CORS-related error but the exact same request succeeds via `curl`, what does that difference tell you about where the problem actually is?
