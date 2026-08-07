# Lesson 02 — Path Parameters and Query Parameters

## What you'll learn

- What a **path parameter** is, and how FastAPI extracts one from a URL and converts it to the type you asked for.
- What a **query parameter** is, how it differs from a path parameter, and when to use each.
- How FastAPI decides a function parameter is a path parameter, a query parameter, or something else entirely — the actual rule, not a guess.
- Optional query parameters, defaults, and `Optional`/`| None` from Module 01, Lesson 09, doing real, functional work for the first time.
- What happens, precisely, when a client sends a value that can't be converted to the type you declared.

## Why this matters

Every route in Lesson 01 ignored anything specific about the request — every call to `/ping` behaved identically to every other call. Real APIs need to answer questions like "get me *this specific* quest" or "get me quests, *filtered* to this priority" — and path/query parameters are the two mechanisms FastAPI gives you for exactly that, both built directly on the type hints Module 01, Lesson 09 taught you as advisory-only. This lesson is where that changes: from here on, a type hint you write is read by FastAPI *at runtime* and used to actually convert and validate incoming data, not just checked by an external tool while you're editing.

## Prerequisites

Lesson 01 (routes, decorators). Module 01, Lesson 09 (type hints — `str`, `int`, `bool`, `| None` are used constantly below, exactly as taught there). Module 02, Lesson 05 (you already know what a query string is — `?key=value` pairs after a `?` in a URL).

## The concept, explained simply

A **path parameter** is a piece of the URL's *path itself* that stands in for a specific value — recall React Router's dynamic segments (`:id`) from Module 04, Lesson 08; FastAPI's path parameters are the exact same idea, just on the server side instead of the client side: `/quests/{quest_id}` means "match any path shaped like `/quests/` followed by something, and hand me that something." A **query parameter** is an optional `key=value` pair appended after a `?` in the URL (Module 02, Lesson 05 already defined this exact term) — used for things that filter, sort, or page through a result rather than identifying *which specific resource* you mean. The rule of thumb, and the one this course follows throughout: **if a value identifies which specific resource you're talking about, it's a path parameter; if it's an optional modifier — a filter, a sort order, a page number — it's a query parameter.**

## The details

### Path parameters — the basics

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/quests/{quest_id}")
def get_quest(quest_id: str):
    return {"quest_id": quest_id}
```

```bash
curl http://127.0.0.1:8000/quests/quest-001
```
**Expected:** `{"quest_id":"quest-001"}`

**Line by line:** `{quest_id}` inside the path string passed to `@app.get(...)` declares a **path parameter** named `quest_id`. FastAPI matches this against whatever segment actually appears in that position of a real request's path, and — this is the mechanism worth slowing down on — it looks at your function's own parameter list, finds a parameter with the **exact same name** (`quest_id`), and passes the matched value into it as a normal Python argument. The connection between `{quest_id}` in the decorator's string and `quest_id: str` in the function signature is made **by name, not by position** — rename one without the other and FastAPI will complain loudly (a `500` error mentioning the mismatch) rather than silently misbehaving.

### Type conversion — where the type hint starts doing real work

```python
@app.get("/quests/by-index/{index}")
def get_quest_by_index(index: int):
    return {"index": index, "type": str(type(index))}
```

```bash
curl http://127.0.0.1:8000/quests/by-index/2
```
**Expected:** `{"index":2,"type":"<class 'int'>"}`

**This is the entire point of this lesson, stated directly:** every piece of a URL is, at the network level, just text — there is no such thing as "a number" traveling over HTTP; `2` arrives as the two-character string `"2"`. FastAPI reads your function's type hint (`index: int`), and — completely unlike Module 01, Lesson 09's "hints are purely advisory, Python itself never checks them" rule for plain Python code — **actually converts** the raw text `"2"` into the real Python integer `2` before your function ever runs, using Pydantic (which you'll meet directly, by name, starting in Lesson 03) as the engine that does this conversion and checking. This is a genuinely different relationship with type hints than anything Module 01 showed you: here, the hint is not just documentation for a separate tool — it is the literal mechanism FastAPI uses to decide how to parse the incoming request.

Now see what happens when conversion fails:

```bash
curl -i http://127.0.0.1:8000/quests/by-index/not-a-number
```
**Expected:**
```
HTTP/1.1 422 Unprocessable Content

{"detail":[{"type":"int_parsing","loc":["path","index"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"not-a-number"}]}
```

**This is your first real look at the exact error shape Lesson 03 covers in full depth** — for now, just notice the status code: `422 Unprocessable Content`, not `400 Bad Request` and not `500`. Recall Module 02, Lesson 03's own note that `422` is specifically for "well-formed syntactically, but semantically invalid" — `not-a-number` is a perfectly valid piece of text to put in a URL (nothing about the *request itself* is malformed), it just can't be turned into the integer your route demanded. FastAPI never even calls your function's body in this case — the failure happens entirely inside its own validation step, before your code runs at all.

### Query parameters — any other typed parameter becomes one, automatically

```python
@app.get("/search")
def search_quests(quest_line: str, limit: int = 10):
    return {"quest_line": quest_line, "limit": limit}
```

```bash
curl "http://127.0.0.1:8000/search?quest_line=Main%20Story&limit=5"
```
**Expected:** `{"quest_line":"Main Story","limit":5}`

**This is the actual rule FastAPI uses, stated precisely (not a guess, the real mechanism):** any function parameter whose name appears inside `{curly braces}` in the route's path string is a **path parameter**. Every *other* parameter that is a simple type (`str`, `int`, `bool`, `float`, and a few more) is automatically treated as a **query parameter** — you did not need to write anything special to mark `quest_line` or `limit` as query parameters; the absence of `{quest_line}`/`{limit}` in the path string, combined with their simple types, is what tells FastAPI to look for them in the query string instead. (Later modules cover the one other common source FastAPI reads simple-typed parameters from — request bodies, Lesson 03 — and the rule for telling those apart from query parameters.)

**Line by line of the quoting above:** `%20` inside the URL is a **percent-encoded** space — URLs can't contain literal spaces, so `curl` (and every browser) encode reserved/unsafe characters this way; you'll see this constantly and should recognize `%20` on sight as "a space, encoded for a URL." The double quotes around the whole URL in the `curl` command are a shell-level necessity (Module 00) so the `&` in a multi-parameter query string isn't misinterpreted by Git Bash itself as "run this command in the background" — always quote a URL containing `&` or spaces when using `curl`.

**Defaults:** `limit: int = 10` gives `limit` a default value, exactly like Module 01, Lesson 02's function defaults — omit it entirely from the request and FastAPI uses `10`:

```bash
curl "http://127.0.0.1:8000/search?quest_line=Main+Story"
```
**Expected:** `{"quest_line":"Main Story","limit":10}` (note `+` also decodes to a space in a query string — an older, URL-specific convention alongside `%20`; both work, `curl` and browsers use `%20` more consistently today, but you'll see `+` in older code).

### Genuinely optional query parameters — `| None`

`quest_line` above is **required** — omit it and see what happens:

```bash
curl -i "http://127.0.0.1:8000/search"
```
**Expected:** `422 Unprocessable Content`, with a `detail` array naming `quest_line` as `"Field required"`. Any parameter with **no default value at all** is required by FastAPI — this is a direct, deliberate consequence of the exact same rule you already used constantly in Module 01: a function parameter with no default must be supplied by the caller.

To make a query parameter genuinely optional — allowed to be entirely absent, with no automatic value substituted, distinct from "give it a specific default":

```python
@app.get("/search-optional")
def search_quests_optional(quest_line: str | None = None, done: bool | None = None):
    return {"quest_line": quest_line, "done": done}
```

```bash
curl "http://127.0.0.1:8000/search-optional"
```
**Expected:** `{"quest_line":null,"done":null}`

```bash
curl "http://127.0.0.1:8000/search-optional?done=true"
```
**Expected:** `{"quest_line":null,"done":true}`

**Line by line:** `quest_line: str | None = None` is exactly Module 01, Lesson 09's union type hint (`X | None`), now put to direct, functional use — it tells FastAPI "this may genuinely be absent; if it is, use `None`," which is a meaningfully different statement than a plain default like `limit: int = 10` (there, `10` is a real, specific fallback value; here, `None` is standing in for "nothing was provided at all," and your own code is expected to check for it, exactly as Lesson 09 described). Note `curl`'s `true`/`false` text is automatically converted to Python's real `bool` `True`/`False` — the same "raw text, converted by the type hint" mechanism from path parameters above, applying just as much to query parameters.

## Common mistakes & gotchas

- **Naming a path parameter in the decorator string but giving the function parameter a different name.** FastAPI matches by name — `@app.get("/quests/{quest_id}")` paired with `def get_quest(id: str):` does not work; the names must match exactly.
- **Forgetting a value is required just because it "seems obviously optional."** A parameter with no default is required, full stop, regardless of what your route's *purpose* is — if you want it genuinely optional, you must write `| None = None` (or a concrete default) explicitly; FastAPI does not infer "optional" from context.
- **Confusing `int = 10` (a real default value) with `int | None = None` (genuinely optional, no substitute value).** The first says "if omitted, use `10` and proceed as if that were provided." The second says "if omitted, this is legitimately absent, and my own code needs an `if x is None:` check" — exactly Module 01, Lesson 09's warning about `dict | None` return types, applied here to input instead of output.
- **Forgetting to URL-encode/quote a query string containing `&`, spaces, or other special characters when testing with `curl`.** Always wrap the full URL in quotes when it contains a query string with more than one parameter.
- **Expecting a `400` for a bad path/query value instead of `422`.** FastAPI's own validation layer (Pydantic, underneath — Lesson 03) consistently uses `422` for "syntactically fine request, semantically invalid value," per Module 02, Lesson 03's own definition of that code — get comfortable seeing `422` for this specific category of problem throughout this module.

## How this connects

Path and query parameters are how a route learns *which* resource, and *which optional filters*, a specific request is about — the missing piece every Lesson 01 route lacked. You've also now seen, for the first time, a type hint doing real, functional, runtime work (raw text in, converted+validated Python value out) rather than being purely advisory the way Module 01, Lesson 09 described plain Python type hints — this exact mechanism, built on Pydantic, is what Lesson 03 opens up fully, this time for **request bodies** — structured JSON data sent in a request, rather than plain text in a URL.

## Quick self-check

1. What's the precise rule FastAPI uses to decide whether a function parameter is a path parameter or a query parameter?
2. Why does `curl .../quests/2` still work correctly even though the `2` traveled over the network as plain text, and what earlier-module fact about type hints does this lesson directly contradict for FastAPI specifically?
3. What status code does FastAPI return when a path parameter can't be converted to its declared type, and why is that code more precise than a plain `400`?
4. What's the actual difference between `limit: int = 10` and `limit: int | None = None`, and when would you want each?
5. Why must a `curl` URL containing more than one query parameter (joined by `&`) be wrapped in quotes in Git Bash?
