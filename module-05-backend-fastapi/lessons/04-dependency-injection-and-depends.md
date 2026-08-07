# Lesson 04 — Dependency Injection and `Depends`: Opening the Hood

**Verified against (August 2026):** confirmed directly against FastAPI's own documentation (`fastapi.tiangolo.com/tutorial/dependencies/`) while writing this lesson — including the current recommended `Annotated[Type, Depends(...)]` syntax (over the older bare `param: Type = Depends(...)` default-value style, which still works but is no longer what FastAPI's own docs lead with) and the per-request caching behavior described below.

## What you'll learn

- What **dependency injection** actually means, as a general software idea, before any FastAPI syntax at all.
- What `Depends()` actually does, mechanically — no unexplained magic, the real call-by-call sequence.
- The current, recommended `Annotated[Type, Depends(...)]` syntax, and why it exists.
- **Sub-dependencies** — dependencies that themselves depend on other dependencies — and how FastAPI resolves a whole chain of them.
- FastAPI's per-request dependency **caching** behavior, and the specific situation where you'd deliberately turn it off.
- A genuinely useful dependency for this module's capstone: "look up this quest by ID, or fail cleanly with a `404`."

## Why this matters

The master plan calls this lesson out specifically: `Depends()` is one of those pieces of FastAPI that looks like unexplained magic the first time you see it — a bare function name appears as a default value, with no call, and things just... work. This lesson opens the hood completely. Once you can explain exactly what FastAPI does with a `Depends(...)` value, you'll be equipped to use dependency injection deliberately for the rest of this course (database sessions in Module 06, authentication checks in Module 07) instead of copy-pasting a pattern you don't fully trust.

## Prerequisites

Lessons 01–03. Module 01, Lesson 02 (functions as first-class values — you'll pass a bare function name as an argument below, exactly the "no parentheses means the function itself, not a call" fact from that lesson). Module 01, Lesson 10 (decorators/closures — the mental model for "a function that produces another callable" transfers directly).

## The concept, explained simply

**Dependency injection**, as a general idea with nothing FastAPI-specific about it yet: instead of a function reaching out and creating (or fetching, or constructing) something it needs *by itself*, deep inside its own body, that something is instead handed to it — "injected" — from outside, usually as a parameter. The benefit isn't obvious until you've felt the pain it avoids: a function that hard-codes "go get the current database connection" or "go check who's logged in" *inside its own body* is difficult to test in isolation (you can't easily substitute a fake database for a test) and forces every function needing that same thing to duplicate the same setup logic. A function that instead simply *receives* that thing as a parameter — with something else responsible for actually producing it — can be tested by simply passing in a different, fake value, and never needs to duplicate the "how do I actually get this" logic itself.

**In Unreal terms:** this is close to the difference between an Actor's `BeginPlay()` reaching out and calling `GetWorld()->SpawnActor<AWeapon>()` itself, hard-coding exactly which weapon class to construct — versus a weapon reference being *injected* into the Actor from outside (a Blueprint-exposed property set by whoever spawns it, or a subsystem handing out shared instances), so the Actor's own code never needs to know or care exactly how that weapon came to exist, only that it received one meeting the expected interface. FastAPI's `Depends()` is a specific, concrete implementation of this same general idea, applied to route functions: **a route function that needs "the currently logged-in user" or "a specific quest looked up by ID" declares that need as a parameter, and hands the actual work of producing that value to a separate function — a dependency — that FastAPI calls on its behalf, automatically, before your route function ever runs.**

## The details

### The problem, without dependency injection

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

quests_db = {"quest-001": {"title": "Slay the Dragon"}}

@app.get("/quests/{quest_id}")
def get_quest(quest_id: str):
    quest = quests_db.get(quest_id)
    if quest is None:
        raise HTTPException(status_code=404, detail="Quest not found")
    return quest

@app.patch("/quests/{quest_id}")
def update_quest_title(quest_id: str, new_title: str):
    quest = quests_db.get(quest_id)
    if quest is None:
        raise HTTPException(status_code=404, detail="Quest not found")
    quest["title"] = new_title
    return quest
```

(`HTTPException` is Lesson 06's proper subject — for now, just read it as "stop here and answer with this status code and message.") **Notice the exact same three lines — look up the quest, check if it's `None`, raise a `404` if so — appear twice, identically, and would appear a third and fourth time in a `delete_quest` and a `toggle_done` route.** This is precisely the kind of duplicated setup logic dependency injection exists to remove.

### The same thing, with `Depends`

```python
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException

app = FastAPI()

quests_db = {"quest-001": {"title": "Slay the Dragon"}}

def get_quest_or_404(quest_id: str) -> dict:
    quest = quests_db.get(quest_id)
    if quest is None:
        raise HTTPException(status_code=404, detail="Quest not found")
    return quest

@app.get("/quests/{quest_id}")
def get_quest(quest: Annotated[dict, Depends(get_quest_or_404)]):
    return quest

@app.patch("/quests/{quest_id}")
def update_quest_title(quest: Annotated[dict, Depends(get_quest_or_404)], new_title: str):
    quest["title"] = new_title
    return quest
```

**Line by line — this is the whole mechanism, with zero steps skipped:**

- `def get_quest_or_404(quest_id: str) -> dict:` — an ordinary function, written exactly like any route function you've already seen — it can take path/query parameters (Lesson 02) itself, and Lesson 03's request-body rules apply to it too, if it needed a body. **A dependency is not a special kind of function** — it's any regular callable, and this is exactly why it can be tested in complete isolation, by simply calling it directly with a fake `quest_id`, with no FastAPI, no HTTP request, and no running server involved at all.
- `Depends(get_quest_or_404)` — notice `get_quest_or_404` is passed **without parentheses** — exactly Module 01, Lesson 02's "no parentheses means the function itself, not a call" fact, doing real work here. `Depends(...)` doesn't call the function itself; it wraps a *reference* to it in a marker object that tells FastAPI "when you see this, don't treat it as a normal value — call this function yourself, using your normal parameter-resolution rules, and use whatever it returns."
- `Annotated[dict, Depends(get_quest_or_404)]` — this is the current, FastAPI-docs-recommended syntax (verified for this lesson): `Annotated[SomeType, extra_metadata]` is a standard Python typing construct (not FastAPI-specific) for attaching extra information to a type hint without changing the type itself, as far as a type checker (Module 01, Lesson 09) is concerned — `Annotated[dict, Depends(get_quest_or_404)]` reads as "this parameter's type is `dict`; also, here's a `Depends(...)` marker for FastAPI to notice." You will still see the older, equivalent style in existing code — `quest: dict = Depends(get_quest_or_404)`, putting the `Depends(...)` call directly as the parameter's default value — which still works today but is no longer what FastAPI's own docs lead with; this course uses the `Annotated` form throughout.
- **The actual sequence FastAPI runs for a request to `GET /quests/quest-001`, step by step, with nothing hidden:** (1) FastAPI sees `get_quest`'s parameter `quest` is annotated with `Depends(get_quest_or_404)`. (2) Before calling `get_quest` itself, it calls `get_quest_or_404`, resolving *that* function's own parameters using the exact same rules as any route function — `quest_id: str` is a path parameter (Lesson 02), so FastAPI reads it straight from the URL, exactly as if `get_quest_or_404` were itself a route. (3) If `get_quest_or_404` raises `HTTPException` (as it does when the quest doesn't exist), FastAPI stops immediately, sends that error response, and **never calls `get_quest` at all.** (4) If `get_quest_or_404` returns normally, FastAPI takes that return value and passes it as the `quest` argument into `get_quest`, which then runs completely unaware of any of this — from `get_quest`'s own point of view, it simply received a `dict` as a parameter, the same as any other.

**This is the entire mechanism.** There is no separate "dependency injection container" object anywhere, no registration step beyond writing `Depends(...)` at the exact point you need something — it is, underneath, just FastAPI calling one function on your behalf, using rules you already know from every route function you've written since Lesson 01, and handing its result to another.

### Sub-dependencies — a dependency that itself has a dependency

```python
def get_quest_or_404(quest_id: str) -> dict:
    quest = quests_db.get(quest_id)
    if quest is None:
        raise HTTPException(status_code=404, detail="Quest not found")
    return quest

def require_incomplete_quest(quest: Annotated[dict, Depends(get_quest_or_404)]) -> dict:
    if quest.get("done"):
        raise HTTPException(status_code=409, detail="Quest is already completed")
    return quest

@app.patch("/quests/{quest_id}/rename")
def rename_quest(
    quest: Annotated[dict, Depends(require_incomplete_quest)],
    new_title: str,
):
    quest["title"] = new_title
    return quest
```

**What's new here:** `require_incomplete_quest` is itself a dependency (used with `Depends(...)` in `rename_quest`), and it has its own dependency (`get_quest_or_404`, via its own `Depends(...)`). FastAPI resolves this entire chain automatically, deepest dependency first: to run `rename_quest`, it must first run `require_incomplete_quest`, which itself must first run `get_quest_or_404` — and if *either* link in that chain raises an `HTTPException`, everything above it stops immediately, and `rename_quest`'s own body never executes. This is exactly the "hierarchical tree of sub-dependencies" FastAPI's own documentation describes, and it can be arbitrarily deep — each dependency only ever needs to know about its own, direct dependencies, never the whole chain above or below it.

### Caching — the same dependency, used twice in one request, runs once

```python
@app.patch("/quests/{quest_id}/complete")
def complete_quest(
    quest: Annotated[dict, Depends(get_quest_or_404)],
    also_quest: Annotated[dict, Depends(get_quest_or_404)],
):
    quest["done"] = True
    return {"same_object": quest is also_quest}
```
**Expected (calling this against an existing quest ID):** `{"same_object":true}`

**Why this matters, precisely:** FastAPI, by default, calls a given dependency **at most once per incoming request**, no matter how many times it's referenced across the whole dependency tree for that one request — the second (and any further) reference simply reuses the first call's already-computed result, rather than running the function again. This is a genuine, deliberate optimization: imagine a dependency that reads a request's auth header and looks up the current user in a database (Module 07) — if three different sub-dependencies all separately needed "the current user," you'd want that lookup to happen once per request, not three times. If you ever need a dependency to run fresh every single time it's referenced within one request (a genuinely rare, advanced need), FastAPI provides `Depends(get_quest_or_404, use_cache=False)` to opt out explicitly — the default (caching on) is correct for the overwhelming majority of cases, including everything in this module.

## Common mistakes & gotchas

- **Calling the dependency function yourself inside `Depends(...)`** — writing `Depends(get_quest_or_404())` instead of `Depends(get_quest_or_404)`. The first calls the function immediately, with no arguments, at the moment the route is *defined* (almost certainly crashing, since `quest_id` wouldn't be available yet) — exactly Module 01, Lesson 02's "parentheses mean call it now" rule, misapplied.
- **Forgetting that a dependency raising `HTTPException` stops the whole chain.** This is a feature, not a surprise once you know it — but it does mean a bug *inside a dependency* can make an otherwise-correct route always fail; when a route behaves unexpectedly, check its dependencies' own logic, not just the route function's body.
- **Writing dependency logic that has side effects you don't want repeated, and being surprised it's cached anyway** (or, more rarely, the reverse — needing `use_cache=False` and forgetting it exists). Per-request caching applies to the *return value*, keyed by the function+its resolved arguments, for that one request only — it is never shared *across* separate requests.
- **Trying to build a whole "dependency injection framework" abstraction on top of this before you actually need one.** Per FastAPI's own design and this lesson's mechanism: a dependency is just a function, `Depends()` is just a marker telling FastAPI to call it for you — resist over-engineering a small QuestLog route with layers of indirection it doesn't need yet.

## How this connects

You now have a complete, no-magic explanation of `Depends()` — a specific, working example of general dependency injection, built entirely on rules (parameter resolution, functions as values) you already had from Module 01 and Lessons 01–03. This module's capstone (Lesson 08) uses exactly the `get_quest_or_404`-shaped dependency shown above for every route that needs an existing quest by ID, so a `404` is handled correctly, once, in one place. Lesson 05 (middleware) is a related-but-distinct concept worth contrasting directly: middleware wraps *every* request/response, unconditionally, before routing even decides which route applies; a dependency is opted into by a *specific* route (or set of routes) and can read/use anything FastAPI's normal parameter-resolution rules expose (path/query params, request bodies) that middleware, running earlier and more generically, cannot.

## Quick self-check

1. In your own words, explain dependency injection as a general idea, with no FastAPI syntax — what problem does it solve, and how?
2. Why is `Depends(get_quest_or_404)` correct, while `Depends(get_quest_or_404())` is a bug — what specific earlier-module fact explains the difference?
3. Walk through, step by step, exactly what FastAPI does when a route function has a parameter annotated `Annotated[dict, Depends(get_quest_or_404)]`, for a request where the quest doesn't exist.
4. What does FastAPI's default dependency caching behavior actually guarantee, and within what scope (per-request? across all requests?) does it apply?
5. Give one concrete example, not from this lesson, of something worth making a dependency rather than duplicating inside multiple route functions.
