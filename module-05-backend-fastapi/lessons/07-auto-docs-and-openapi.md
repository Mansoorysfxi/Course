# Lesson 07 — Auto Docs and OpenAPI: What's Actually Generating That Page

## What you'll learn

- What **OpenAPI** actually is — a specification, not "the docs page" — and what a **schema** written in it actually looks like.
- Exactly where FastAPI's OpenAPI document comes from, mechanically, out of everything you've already written.
- **Swagger UI** and **ReDoc** — two different, ready-made tools that both read the *same* OpenAPI document and render it differently — and how to actually use Swagger UI to test your API by hand.
- How to view the raw OpenAPI JSON yourself, directly.
- How `response_model`, `status_code`, `Literal` types, and docstrings all feed into this document, tying together nearly everything this module has taught so far.

## Why this matters

You've been visiting `/docs` since Lesson 00 without knowing what's actually generating it. This lesson closes that gap completely — and, practically, gives you your primary manual-testing tool for the rest of this module's exercises and the capstone: Swagger UI's "Try it out" button lets you send real requests to your own running server, with real validation errors shown exactly as Lesson 03 described them, without writing a single `curl` command, though you'll keep using `curl` too since each tool is better for different things.

## Prerequisites

Lessons 01–06 — this lesson is largely "here's what all of that was quietly feeding into the whole time." Module 02, Lesson 05 (you already know what JSON is; an OpenAPI document is itself just JSON, describing an API rather than being data from one).

## The concept, explained simply

**OpenAPI** is a **specification** — a formally agreed-upon way of describing, in a structured JSON (or YAML) document, everything about an HTTP API: every route, every parameter each one accepts, every possible response shape and status code, every request body's exact structure. It is not a tool, a page, or a product — it's closer to a *file format*, the same category of thing as JSON itself (Module 01, Lesson 08) or HTML (Module 03, Lesson 01): a precise, machine-readable description that many different tools can then read and do something useful with. **Swagger UI** and **ReDoc** are two, separate, independently-developed tools that both do exactly this: read an OpenAPI document and render a human-friendly documentation page from it — the same underlying description, rendered two different ways by two different renderers, the same relationship JSON has to the many different programs that can read and display it.

**The genuinely important fact, and the actual point of this lesson:** FastAPI does not maintain some separate, hand-written "documentation" anywhere. It generates a complete, valid OpenAPI document **automatically**, entirely out of the same Python code — type hints, Pydantic models, `response_model`s, status codes — you were already writing for entirely different, functional reasons (Lessons 01–06). The documentation is a byproduct of writing correctly-typed code, not a separate task you do afterward.

## The details

### Seeing the raw OpenAPI document

With any FastAPI app running (any of your `main.py` files from earlier lessons will do):

```bash
curl http://127.0.0.1:8000/openapi.json
```

**Expected:** a large JSON document. Skim it — it'll be dense, but two parts are worth recognizing immediately: a top-level `"paths"` key, listing every route you've registered, each with its methods, parameters, and possible responses; and a `"components"` → `"schemas"` section, listing every Pydantic model you've used anywhere, described in a standard way (this is, itself, a well-known sub-format called **JSON Schema** — a way of describing "what shape must this JSON have," which is exactly what a Pydantic model already is, just re-expressed in a format meant for tools other than Python to read too).

FastAPI builds this document by inspecting, at startup, every route you registered with `@app.get(...)`/`@app.post(...)`/etc. — its path, its path/query parameters and their types (Lesson 02), the Pydantic model of any request body (Lesson 03) or `response_model` (Lesson 06), and every status code you explicitly declared. **Nothing in that document was written by hand** — it is a direct, mechanical translation of the exact same information your route functions' signatures already carry, into the OpenAPI specification's standard shape.

### Swagger UI — `/docs`

Visit `http://127.0.0.1:8000/docs`. This page is **Swagger UI** — a genuinely separate, open-source project (not written by FastAPI's own team) that FastAPI bundles and configures automatically to read exactly the `/openapi.json` document above and render it as an interactive page.

**Using it as a real testing tool, right now:** click on any route to expand it, click **"Try it out,"** fill in whatever parameters/body it asks for, and click **"Execute."** Swagger UI sends a real HTTP request to your actual running server (visible, if you watch closely, as a genuine network request your browser's own developer tools could show you) and displays the real response — status code, headers, and body — directly on the page. **Try it yourself:** open Swagger UI against one of your own routes from Lesson 03 (a `POST` route with a Pydantic request body), deliberately submit an invalid value through the UI's own form fields, and confirm you see the exact same `422` error shape Lesson 03 taught you to read via `curl` — same underlying mechanism, a different, more visual way of triggering and reading it.

### ReDoc — `/redoc`

Visit `http://127.0.0.1:8000/redoc`. **This is the same OpenAPI document, read by a different tool** — ReDoc, another separate open-source project, also bundled and auto-configured by FastAPI. Notice it looks meaningfully different (a clean, three-panel reading layout, no "Try it out" buttons) despite describing the *exact same API* — concrete, hands-on proof that OpenAPI really is a separate, tool-agnostic specification, not something inseparable from Swagger UI's specific look.

### What actually feeds into the generated docs

```python
from typing import Literal
from pydantic import BaseModel
from fastapi import FastAPI, status

app = FastAPI(title="QuestLog API", version="0.1.0")

class QuestCreate(BaseModel):
    """The fields required to create a new quest."""
    title: str
    priority: Literal["low", "medium", "high"]

class QuestOut(BaseModel):
    id: str
    title: str
    priority: Literal["low", "medium", "high"]

@app.post(
    "/quests",
    response_model=QuestOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new quest",
)
def create_quest(quest: QuestCreate):
    """Creates a quest and returns it, including its newly-assigned id."""
    ...
```

Reload `/docs` and look specifically at the `POST /quests` entry: the **summary** you wrote appears as the route's title in the list; the function's own **docstring** (Module 01's own convention for documenting a function, reused directly here) appears as its longer description; `QuestCreate`'s fields appear as the exact required request body shape, with `priority` shown as a dropdown of precisely `low`/`medium`/`high` — directly because it's a `Literal` type (Lesson 03), not a plain `str`, so Swagger UI can render it as a real, constrained choice rather than an open text field; and the documented successful response is shown as `201`, with `QuestOut`'s exact shape — both taken straight from your `status_code=` and `response_model=` arguments (Lesson 06), not inferred or guessed.

**Try it yourself:** change `priority`'s type hint from `Literal["low", "medium", "high"]` back to a plain `str`, reload `/docs`, and compare the rendered form field for that route before and after. (You'll see it change from a fixed dropdown back to a free-text box — direct, visible proof of exactly how much of this documentation is mechanically derived from your own type hints, not separately maintained.)

## Common mistakes & gotchas

- **Believing you need to write or maintain documentation separately from your code.** For everything this module covers, you don't — the discipline is keeping your type hints, Pydantic models, and `response_model`/`status_code` declarations accurate; the docs then stay accurate automatically, for free.
- **Confusing OpenAPI (the specification/document) with Swagger UI (one specific tool that renders it).** "Swagger" and "OpenAPI" get used interchangeably in casual conversation constantly, but they're genuinely different things, and this lesson's own `/redoc` example is concrete proof the same underlying document supports more than one renderer.
- **Assuming `/docs` and `/redoc` are safe to leave exposed on a real, public production deployment without thinking about it.** For this module's local development, they're purely a convenience with essentially no downside. Once a real API is live on the public internet, exposing full API documentation (including every request/response shape) is a genuine, deliberate choice with real security tradeoffs — not covered in depth in this module, but worth flagging now: this is exactly the kind of decision Module 09–11's deployment content revisits with real production concerns in mind.
- **Testing exclusively through Swagger UI and never touching `curl` again.** Both matter for different reasons: Swagger UI is faster for exploring an API interactively and reading its documented shape; `curl` (Module 02's own skill) is scriptable, precise, and exactly what you'd use to write an automated test (Module 08) or to debug a request header-by-header. This module's exercises and capstone deliberately ask you to use both.
- **Forgetting the docstring/summary is genuinely part of your API's real, external documentation** the moment anyone else (a teammate, a future you) reads `/docs` — write them as if a stranger needs to understand this route with zero other context, not as a throwaway comment.

## How this connects

You now know precisely what `/docs` and `/redoc` are, where the information they display actually comes from, and how to use Swagger UI as a genuine, hands-on testing tool — not just a page that happens to exist. Nearly every earlier lesson in this module (routing, parameters, Pydantic models, response models, status codes) turns out to have been feeding this document the whole time, which is worth sitting with for a moment: writing good, precisely-typed FastAPI code and writing good API documentation are, in this framework, almost the same activity. Lesson 08 puts every single piece from Lessons 01–07 together into one real, working, in-memory CRUD API — the QuestLog capstone's actual backend — tested with exactly the two tools (`curl`, Swagger UI) this lesson and Module 02 gave you.

## Quick self-check

1. What is OpenAPI, precisely — and name two separate tools that can both read the same OpenAPI document and render it differently.
2. Where does the JSON at `/openapi.json` actually come from — is any part of it hand-written, separately from your route code?
3. Why does a `Literal["low", "medium", "high"]` field render as a dropdown in Swagger UI while a plain `str` field renders as free text?
4. What specific role does `response_model` (Lesson 06) play in what `/docs` shows for a route's successful response?
5. Give one concrete reason you'd still use `curl` for something, even with Swagger UI's "Try it out" available.
