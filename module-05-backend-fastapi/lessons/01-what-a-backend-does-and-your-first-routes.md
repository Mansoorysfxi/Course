# Lesson 01 — What a Backend Framework Actually Does, and Your First Real Routes

## What you'll learn

- What a "backend" is, precisely, and what specific job a **web framework** like FastAPI does versus everything else involved in serving a web request.
- Why this course picked FastAPI specifically, verified against current facts rather than reputation.
- What `@app.get(...)` actually does, mechanically, reusing Module 01's decorator mechanism directly instead of treating it as new magic.
- How to define multiple routes, for multiple HTTP methods, on the same FastAPI app.
- What FastAPI does automatically with a function's return value, and why that matters.

## Why this matters

Lesson 00 got a FastAPI app running without explaining much about *why* any of it worked. This lesson is where that gets filled in properly, before you touch anything more complex (parameters in Lesson 02, request bodies in Lesson 03). Every FastAPI feature this module covers is, underneath, a variation on the exact same idea this lesson establishes: a decorator tells FastAPI "this function handles requests matching this description," and FastAPI's whole job is turning real, raw HTTP traffic into ordinary Python function calls and back again.

## Prerequisites

Lesson 00 (a working venv, FastAPI, and Uvicorn installed and verified). Module 01, Lesson 10 (decorators — you're about to see FastAPI's most-used decorator explained in exactly those terms). Module 02, Lesson 03 (HTTP methods and status codes — you already know what `GET`/`POST`/etc. *mean*; this lesson shows you how to make Python code respond to them). Module 01, Lesson 11 (async/await — referenced directly below).

## The concept, explained simply

Recall Module 02's whole picture: a **client** sends an HTTP **request** (a method, a path, headers, maybe a body) over the network; a **server** sends back an HTTP **response** (a status code, headers, maybe a body). A **backend** is the program running on the server side that decides *what response to send back* for a given request — usually by running some actual logic (reading/writing data, checking permissions, doing a calculation) rather than just serving a fixed file off disk the way a plain file server would.

Writing a backend completely from scratch — reading raw bytes off a network socket, parsing them into a method/path/headers/body by hand, building a correctly-formatted response and writing *those* bytes back out — is real, tedious, error-prone work that has nothing to do with your actual application logic (quests, in this course's case). A **web framework** exists specifically to remove that burden: it (working together with an ASGI server like Uvicorn, Lesson 00) handles all of the "turn raw bytes into something usable" plumbing, and lets you write plain functions that receive already-parsed, already-convenient Python values and return plain Python values back. **FastAPI is a specific framework choice** — there are others in the Python world (Flask, Django) — chosen for this course for reasons verified, not assumed: it's built specifically around Python's type hints (Module 01, Lesson 09) as the actual mechanism for validating incoming data (Lesson 03) and generating documentation (Lesson 07) — not just as advisory annotations the way Lesson 09 described them in general Python code; it's built around `async def` from the ground up (Module 01, Lesson 11), matching the ASGI standard Lesson 00 introduced; and, per its own published, actively-maintained release notes and extremely wide current production adoption (verified while writing this lesson, August 2026), it remains one of the most current and commonly used Python API frameworks for exactly the kind of API this course builds.

## The details

### What `FastAPI()` actually is

```python
from fastapi import FastAPI

app = FastAPI()
```

`FastAPI` is a Python **class** (Module 01, Lesson 05). `app = FastAPI()` creates one **instance** of it. That single object is a container that will accumulate every route, every piece of middleware (Lesson 05), and every other piece of configuration you attach to it over the rest of this module — there is deliberately only ever one of these per running application, and Uvicorn (Lesson 00) is told exactly which variable holds it (`main:app`).

### `@app.get(...)` — the decorator, explained with Module 01's own mechanism

You already know, from Module 01, Lesson 10, that `@some_decorator` above a function definition is exactly equivalent to writing `my_function = some_decorator(my_function)` immediately after defining it — nothing more, nothing magic. `@app.get("/")` is a real, working instance of precisely that pattern:

```python
def read_root():
    return {"message": "QuestLog API is alive."}

read_root = app.get("/")(read_root)
```

**This is, functionally, what `@app.get("/")` above `def read_root():` actually does** — `app.get("/")` is a call that itself returns a decorator (recall Module 01, Lesson 10's "a decorator that takes its own arguments" three-layer pattern: `repeat(times) -> decorator(func) -> wrapper(...)`; `app.get("/")` plays exactly the role `repeat(times)` played there), and that returned decorator is then applied to `read_root`. What that inner decorator actually does, conceptually: it records, inside `app`'s own internal bookkeeping, "when a `GET` request arrives at path `/`, call this specific function and use whatever it returns to build the response" — and then gives you back essentially the same function, still callable directly in plain Python if you ever wanted to (FastAPI doesn't need to hide or wrap the function the way your own `log_calls` example did in Module 01; it mainly needs to *remember* it). There is nothing conceptually new here beyond what you already built by hand — only a specific, real, extremely common application of it.

FastAPI provides one such decorator per HTTP method you'll actually use: `@app.get(...)`, `@app.post(...)`, `@app.put(...)`, `@app.patch(...)`, `@app.delete(...)` — each one registers a function against that specific method and path combination.

### Multiple routes, multiple methods

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "QuestLog API is alive."}

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.post("/echo")
def echo():
    return {"message": "You sent a POST request."}
```

Save this as `main.py`, run `uvicorn main:app --reload` (Lesson 00), then:

```bash
curl http://127.0.0.1:8000/ping
```
**Expected:** `{"status":"ok"}`

```bash
curl -X POST http://127.0.0.1:8000/echo
```
**Expected:** `{"message":"You sent a POST request."}`

```bash
curl -X POST http://127.0.0.1:8000/ping
```
**Expected:**
```json
{"detail":"Method Not Allowed"}
```
with an HTTP status of `405` (add `-i` to `curl` to see it: `curl -i -X POST http://127.0.0.1:8000/ping`). **This is FastAPI enforcing exactly the contract Module 02, Lesson 03 described:** `/ping` was only ever registered for `GET` — asking for it with `POST` isn't "close enough," it's a genuinely different, unregistered combination, and FastAPI answers with the correct status code (`405 Method Not Allowed`) for exactly this situation, automatically, with zero extra code from you.

**Try it yourself:** add a third route, `@app.get("/version")`, returning `{"version": "0.1.0"}`. Restart is unnecessary — `--reload` already picked it up. Confirm it with `curl` before moving on.

### `async def` vs plain `def` route functions

Every example so far used a plain `def`. FastAPI also lets any route function be `async def`:

```python
import asyncio

@app.get("/slow")
async def slow_route():
    await asyncio.sleep(1)
    return {"message": "That took about a second."}
```

**Why both are allowed, and when each matters:** recall Module 01, Lesson 11 in full — `async def` only pays off when a function actually `await`s something I/O-bound (a database query, a call to another API), because that's the only situation where handing control back to the event loop lets Uvicorn serve a *different* request during the wait instead of sitting idle. This module's capstone is in-memory only (Lesson 08 explains why, and Module 06 is where a real, genuinely slow database query arrives) — so for now, plain `def` and `async def` route functions behave identically in practice, and this module's own example code mostly uses plain `def` for that reason, reserving `async def` for the one route (Lesson 08's health-check-style endpoint, if you choose to add one) where it's illustrative. **The one thing to get right regardless:** never put a genuinely blocking, synchronous call (the exact `time.sleep()` mistake Module 01, Lesson 11 warned about) directly inside an `async def` route — it would freeze Uvicorn's entire event loop for every other request currently in flight, not just your own.

### What FastAPI does with your function's return value

Every example above returned a plain Python `dict`. FastAPI's job, once your function returns, includes converting that Python value into a valid HTTP response:

```python
@app.get("/quest-names")
def quest_names():
    return ["Slay the Dragon", "Gather Herbs"]
```
```bash
curl -i http://127.0.0.1:8000/quest-names
```
**Expected:**
```
HTTP/1.1 200 OK
content-type: application/json
...

["Slay the Dragon","Gather Herbs"]
```

**Line by line of what just happened, that you didn't write any code for:** FastAPI serialized your Python `list` into a JSON array (Module 01, Lesson 08 already taught you the mapping between Python's `dict`/`list`/`str`/etc. and JSON's own types — this is that exact mapping, applied automatically instead of by your own explicit `json.dumps()` call), set the response's status code to `200 OK` (the correct default for a successful `GET`, per Module 02, Lesson 03) with no code from you asking for it specifically, and set a `Content-Type: application/json` header (Module 02, Lesson 04) so that whatever receives this response — a browser, `curl`, the React frontend's `fetch()` — knows exactly how to interpret the bytes that follow. You can return a `dict`, a `list`, a `str`, a number, or (starting Lesson 03) a Pydantic model, and FastAPI converts every one of them correctly.

## Common mistakes & gotchas

- **Defining two routes for the same method and path.** FastAPI doesn't raise an error — it silently only ever calls the *first* one registered, top to bottom, for a matching request; the second is dead code. This is a real, quiet bug source in a larger file with many routes — keep route paths per method unique and legible.
- **Believing `async def` alone makes a route "faster."** Per Module 01, Lesson 11 (and restated above): it only helps when the function actually awaits genuine I/O. An `async def` route with no real `await` inside it gains nothing over a plain `def` one.
- **Forgetting the decorator returns the function it wraps, and trying to call the *decorator itself* like a route function.** `@app.get("/")` is a call that produces a decorator; the thing actually applied to `read_root` is that decorator's return value. This distinction rarely bites in practice for this specific decorator, but it's worth being able to explain precisely, since Lesson 04's `Depends()` reuses the exact same "a call that produces something else usable" shape.
- **Restarting `uvicorn` manually out of habit.** With `--reload` active, you almost never need to — check the terminal for `Reloading...` after saving a file before assuming the server didn't pick up your change.
- **Testing a route with the wrong HTTP method and being confused by a `405`.** Recheck exactly which decorator (`@app.get`, `@app.post`, ...) you used to register that path — the method genuinely has to match, by design (Module 02, Lesson 03's whole point about methods carrying real, distinct meaning).

## How this connects

You now understand `@app.get(...)` and its siblings as a direct, working application of Module 01, Lesson 10's decorator mechanism — not a new kind of magic FastAPI invented. Lesson 02 extends this immediately: routes so far have ignored *anything specific about the request itself* (which quest, which page, which filter) — path and query parameters are how a route learns those details, and they're where FastAPI's type-hint-driven behavior (Module 01, Lesson 09) starts actually doing real work instead of being purely advisory.

## Quick self-check

1. In your own words, what specific job does a web framework do that a raw ASGI server (Lesson 00) doesn't?
2. Write out, using Module 01, Lesson 10's own vocabulary, what `@app.post("/echo")` is doing to the function directly below it.
3. What HTTP status code does FastAPI return, automatically, for a request whose path matches a registered route but whose method doesn't — and why does that specific code (not, say, `404`) make sense given what you learned in Module 02, Lesson 03?
4. Does making a route function `async def` automatically make it handle requests faster? Under what specific condition would it actually help?
5. If a route function returns a Python `list` of strings, what does the client actually receive on the wire, and which earlier module already taught you the type mapping FastAPI is relying on?
