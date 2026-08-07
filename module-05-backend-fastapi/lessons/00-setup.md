# Lesson 00 — Setup: A New Venv, FastAPI, and Uvicorn

**Verified against (August 2026):** FastAPI **0.141.1** (confirmed via PyPI's JSON API, `https://pypi.org/pypi/fastapi/json`, and FastAPI's own docs at fastapi.tiangolo.com); Uvicorn **0.52.1** (confirmed via `https://pypi.org/pypi/uvicorn/json`); Pydantic **2.13.4** (confirmed via `https://pypi.org/pypi/pydantic/json` — installed automatically as a FastAPI dependency, since FastAPI requires Pydantic `>=2.9.0`, but pinned explicitly here too since this module uses it directly). Python **3.14.x**, the same interpreter Module 01 installed. FastAPI's own release notes (`fastapi.tiangolo.com/release-notes/`) confirm the framework is still on a `0.x` version number by design — the maintainers treat this as a deliberate signal that breaking changes can land in a minor release, not as a sign of instability; the framework has been in wide, serious production use for years regardless. Every command in this lesson was actually run, in order, against these exact versions, while writing this module.

## What you'll learn

- Why this module needs a **second, separate** virtual environment, even though you already made one in Module 01.
- How to install FastAPI and Uvicorn, and what job each one actually does (they are not the same thing).
- How to write and run the smallest possible FastAPI app, and what "ASGI" means.
- How to run two servers — this backend and Module 04's React frontend — at the same time, in two terminals, without them fighting over a port.
- How to verify every piece of this setup, including the interactive API docs, before Lesson 01 asks anything more of you.

## Why this matters

Every lesson and exercise in this module, and the QuestLog API capstone, run on top of exactly two new packages: FastAPI and Uvicorn. Per the master plan's Rule 8, none of this module's teaching content is allowed to assume they're installed until a dedicated setup lesson has actually installed and verified them — exactly the same discipline Module 01's Lesson 00 (Python/venv/pip) and Module 04's Lesson 00 (Vite/React/Tailwind/React Router) already put you through. This lesson does that for FastAPI and Uvicorn specifically, and adds one new wrinkle neither of those modules had: for the first time in this course, you will have **two servers running at once** — this module's backend and Module 04's frontend — and you need to understand why that's fine, not a conflict.

## Prerequisites

**Module 01 in full**, especially [Lesson 00](../../module-01-python-properly/lessons/00-setup.md) (you already know what a virtual environment is, how to create/activate one with `python -m venv`, and how `pip`/`requirements.txt` work — this lesson applies that exact knowledge to a second, brand-new project, it does not re-explain the concepts) and [Lesson 07](../../module-01-python-properly/lessons/07-modules-packages-and-virtual-environments.md) (why isolation matters, and why every real Python project — FastAPI ones very much included — uses an explicit `__init__.py`). **Module 04 in full**, especially its own [Lesson 00](../../module-04-react/lessons/00-setup.md) — you'll be running the exact frontend it produced, alongside this module's new backend.

## The concept, explained simply

You already know, from Module 01, that every Python project should get its **own** virtual environment — a private, disposable folder of installed packages, isolated from every other project on your machine. This module's backend is a genuinely separate project from Module 04's frontend (different language, different package manager, different tools), so it gets its own venv, in its own project folder, exactly the same way you'd give a new Unreal project its own `.uproject` and plugin set rather than forcing it to share one global Engine install with every other project you've ever made.

Two new tools, and what each actually is, before you install either:

- **FastAPI** is a **web framework** — a library that lets you describe, in Python, what should happen when a specific HTTP request (recall Module 02's methods and paths) arrives, and turns your plain functions into something that can actually receive and answer real network requests. FastAPI itself does not listen on a network port, open a socket, or talk to a browser directly — that job belongs to the next tool.
- **Uvicorn** is an **ASGI server** — the actual program that opens a real network port, accepts incoming HTTP connections, parses the raw bytes into something Python can work with, hands each request to your FastAPI app, and sends the app's response back out over the network. **ASGI** (Asynchronous Server Gateway Interface) is the standard *interface* — an agreed-upon shape of function calls — that lets any compliant server (Uvicorn is the most common; there are others) talk to any compliant Python web framework (FastAPI is one; there are others) without the two needing to be written by the same team or know anything about each other's internals beyond that shared agreement. This split — a framework that describes behavior, and a separate server that actually runs it — is the same "front sits on top of; back sits underneath" division you already know as *fact* from Module 04: Vite serves your React app while React itself has no idea how it's being served. FastAPI is deliberately built around `async def` (Module 01, Lesson 11) specifically because a real server juggles many requests arriving close together, each one potentially waiting on something slow (a database query, in later modules) — precisely the I/O-bound scenario that lesson's `asyncio.gather` example demonstrated. **ASGI is also the reason**: it's the modern, async-capable successor to an older standard called WSGI, which could only hand a server one request at a time, one thread each — ASGI was created specifically so Python web servers could finally take advantage of `async`/`await`.

## The details

### Step 1 — A new project folder, a new venv

Pick where you keep your own throwaway practice work (not inside this course's repository — exactly Module 04's convention: this lesson's examples are practice, the graded work lives in `exercises/` and `project/`, which already have their own files).

```bash
mkdir ~/fastapi-practice
cd ~/fastapi-practice
python -m venv .venv
source .venv/Scripts/activate
```

**Expected:** your prompt shows `(.venv)` at the start — identical mechanics to Module 01, Lesson 00, just a brand-new, empty venv for a brand-new project. Confirm you're really inside it:

```bash
which python
```
**Expected:** a path ending inside this project's own `.venv/Scripts/python`, not your system Python.

### Step 2 — Install FastAPI and Uvicorn

```bash
pip install fastapi==0.141.1 "uvicorn[standard]==0.52.1"
```

**Expected output:** several lines ending in `Successfully installed fastapi-0.141.1 ... pydantic-2.13.4 ... uvicorn-0.52.1 ...` (plus a longer list of smaller packages each one depends on — `starlette`, which FastAPI is actually built on top of internally; `click`, which Uvicorn's command-line interface uses; and several more).

**Line by line:**
- `fastapi==0.141.1` — pins the exact version this module was verified against (Rule 7's "pin versions so exercises don't break"). Notice you did **not** separately `pip install pydantic` — FastAPI declares Pydantic as one of its own dependencies (it requires `pydantic>=2.9.0`), so `pip` installs a compatible version (2.13.4, also verified for this lesson) automatically. You'll `import pydantic` directly starting in Lesson 03, so it's worth knowing it's there and why, rather than it feeling like it appeared from nowhere.
- `"uvicorn[standard]==0.52.1"` — the quotes matter in some shells because of the square brackets (Git Bash is generally fine either way, but quoting is the universally safe habit — the exact same reason Module 00 taught you to quote paths with spaces). The `[standard]` part is called an **extra** — an optional bundle of additional packages a package can declare, that you only get if you ask for it by name in brackets. Plain `uvicorn` alone is deliberately minimal; `uvicorn[standard]` pulls in, among other things, `watchfiles` (the library that actually watches your files on disk and triggers Uvicorn's auto-reload — covered below) and `websockets`. Skipping `[standard]` would still let you run FastAPI apps, just without auto-reload during development — always install the `[standard]` extra for local work.

Record it, exactly as Module 01 taught:

```bash
pip freeze > requirements.txt
cat requirements.txt
```
**Expected:** a longer list than just two lines — `fastapi`, `pydantic`, `pydantic_core` (Pydantic's Rust-based validation engine, installed alongside it automatically), `starlette`, `uvicorn`, and several more, each pinned to an exact version. This is the exact same reproducibility mechanism from Module 01 — anyone (including future you) can run `pip install -r requirements.txt` in a fresh venv and get this identical set of packages.

### Step 3 — The smallest possible FastAPI app

```bash
cat > main.py << 'EOF'
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "QuestLog API is alive."}
EOF
```

**Line by line (Lesson 01 goes much deeper — this is just enough to run something and see it work):**
- `from fastapi import FastAPI` — imports the one class this entire framework is built around.
- `app = FastAPI()` — creates a single **application instance**. Everything you add to your API — every route, every piece of middleware (Lesson 05) — gets attached to this one object. Uvicorn (next step) is told specifically to run *this* object.
- `@app.get("/")` — a **decorator** (Module 01, Lesson 10 — this is exactly why that lesson got the full "open the hood" treatment: this is a real, working example of precisely the "function that takes a function and returns it, wired up with `@`" mechanism you built by hand there, applied by FastAPI itself). It registers the function immediately below it to run whenever an HTTP `GET` request (Module 02, Lesson 03) arrives at the path `"/"`. Lesson 01 explains exactly what FastAPI's version of this decorator does with the function it wraps.
- `def read_root(): return {"message": ...}` — an ordinary Python function returning an ordinary Python `dict`. FastAPI converts that `dict` into a real JSON HTTP response body automatically — no manual `json.dumps()` call (Module 01, Lesson 08) needed; FastAPI does that conversion for you as part of its job.

### Step 4 — Run it with Uvicorn

```bash
uvicorn main:app --reload
```

**Expected output:**
```
INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Line by line:** `uvicorn` is the command-line program you just installed. `main:app` tells it exactly two things, separated by a colon: `main` is the Python module to import (i.e., `main.py`, in the current folder — recall Module 01, Lesson 07's exact "a `.py` file is a module, importable by its filename minus `.py`" rule), and `app` is the specific variable *inside* that module holding your `FastAPI()` instance — the same `app` you created in Step 3. Uvicorn imports your module, finds that object, and starts listening for real HTTP connections on it. `--reload` tells Uvicorn to watch your project's files (using `watchfiles`, from the `[standard]` extra) and automatically restart the server the instant you save a change — genuinely essential for development, and something you should **never** enable in a real production deployment (a topic Module 11 covers properly; for now, just know `--reload` is a development-only flag).

Open a browser to `http://127.0.0.1:8000/` (or `http://localhost:8000/` — Module 02, Lesson 01 already taught you `localhost` and `127.0.0.1` mean the same thing). **Expected:** the raw JSON `{"message":"QuestLog API is alive."}`, rendered plainly by the browser since there's no HTML involved — you're looking directly at an HTTP response body, exactly as Module 02 described one, just viewed through a browser instead of `curl`.

**Try it yourself:** with the server still running (`--reload` active), change the message string in `main.py`, save the file, and watch the terminal — it should print new `INFO` lines about reloading, with no need to stop and restart `uvicorn` yourself. Refresh the browser tab and confirm the new text appears.

### Step 5 — The interactive docs (a first look — Lesson 07 covers this properly)

With the server still running, visit `http://127.0.0.1:8000/docs` in your browser. **Expected:** a full interactive page, generated automatically, listing your one `GET /` route, with an expandable panel and a "Try it out" button that actually calls your running server and shows you the real response — you wrote zero lines of documentation-specific code for this to exist. Lesson 07 explains exactly what's generating this page and why it's able to.

Stop the server with `Ctrl+C` once you've confirmed this.

### Step 6 — Running the backend and Module 04's frontend at the same time

Real full-stack development means two servers running simultaneously: this backend (port `8000` by default), and Module 04's Vite dev server (port `5173` by default, per that module's own setup lesson). Neither one is aware of the other's existence unless your own code makes an HTTP request between them — they're two entirely separate programs, listening on two entirely separate ports of the same machine.

**Open two separate Git Bash terminal windows/tabs** (recall Module 00's terminal-vs-shell distinction — you need two independent shell sessions, not one window running two things):

- **Terminal 1** — the backend: `cd` into your FastAPI project, activate its `.venv`, run `uvicorn main:app --reload`.
- **Terminal 2** — the frontend: `cd` into a Module 04-style Vite project, run `npm run dev`.

Both stay running, independently, for as long as you're working. This is precisely the setup this module's capstone (Lesson 08 onward) uses for real — the React frontend, running on `:5173`, will make real `fetch()` calls (Module 03, Lesson 07) to the FastAPI backend running on `:8000`.

**One thing to flag now, and fully explain only in Module 07:** a browser page served from one port (`:5173`) making a `fetch()` request to a *different* port (`:8000`) is a **cross-origin** request, and browsers apply a security policy called **CORS** (Cross-Origin Resource Sharing) to these by default, which — without one specific, small piece of server configuration — would silently block the frontend's requests even though the backend itself is running correctly. This module's capstone backend includes the minimum needed to unblock this (a few lines using FastAPI's built-in `CORSMiddleware`, shown in Lesson 08), but the *why* behind CORS, what a "preflight" request is, and how to configure it properly and safely are Module 07's job in full, per the master plan — treat Lesson 08's CORS lines as "flip this switch so the two servers can talk," not as something to deeply understand yet.

## Verify your setup

Run each command below in a fresh Git Bash window, inside `~/fastapi-practice`, `.venv` **not yet activated**:

```bash
source .venv/Scripts/activate
python --version
```
**Expected:** `Python 3.14.x` — same interpreter Module 01 installed, now used inside a second, separate venv.

```bash
pip show fastapi uvicorn
```
**Expected:** two blocks of package metadata, showing `Version: 0.141.1` for `fastapi` and `Version: 0.52.1` for `uvicorn` (or later versions in the same lines, if you installed after this lesson was written — check this module's README for whether a newer pinned version applies).

```bash
uvicorn main:app --reload
```
(in a second terminal, while that's running)
```bash
curl http://127.0.0.1:8000/
```
**Expected:** `{"message":"QuestLog API is alive."}` printed directly in the terminal — your first `curl` request against your *own* server, not someone else's public API, closing the loop from Module 02.

```bash
curl -i http://127.0.0.1:8000/docs
```
**Expected:** `HTTP/1.1 200 OK` followed by a large block of HTML (`curl` doesn't render pages — Module 02, Lesson 05's client/server distinction again: a browser interprets that HTML, `curl` just shows you the raw bytes). Confirm the same URL actually renders as the interactive docs page when opened in a real browser.

Stop the server (`Ctrl+C`) once everything above matches.

## Common mistakes & gotchas

- **`uvicorn: command not found`.** Almost always the venv isn't active — check for `(.venv)` in your prompt, and run `which uvicorn` (should point inside `.venv/Scripts/`). Exactly Module 01, Lesson 00's most common failure, transplanted to a new project.
- **`ModuleNotFoundError: No module named 'fastapi'` the instant `main.py` runs, even though you just installed it.** Same root cause as the previous bullet, viewed from the Python side instead of the shell side — `pip install` happened in one venv (or no venv at all), but `python`/`uvicorn` is currently resolving to a different one. Recall Module 01, Lesson 07's `sys.path` explanation for exactly why this happens mechanically.
- **`ERROR: [Errno 98] Address already in use` (or, on Windows, a similarly-worded port conflict).** Port `8000` is already occupied — either an earlier `uvicorn` process you forgot to stop (check other terminal tabs, or Windows Task Manager's "Details" tab for a stray `python.exe`), or genuinely some other program. Fix: stop whatever's using it, or run this one on a different port explicitly: `uvicorn main:app --reload --port 8001`. This is the exact same category of problem as Module 04's Lesson 00 flagging Vite's port `5173` conflict — the fix (find the conflicting process, or just use the next port) is identical in spirit.
- **Frontend and backend "can't see each other" even though both terminals show they're running.** First confirm each one works **on its own** — `curl http://localhost:8000/` for the backend, opening `http://localhost:5173/` for the frontend — before suspecting anything about them talking to each other. If both work alone but a `fetch()` from the frontend fails specifically with a browser console error mentioning "CORS," that's the cross-origin policy flagged in Step 6 above — Lesson 08 shows you the exact fix for this module's capstone; a full explanation is Module 07's job.
- **Editing `main.py` while `--reload` is active, but the browser still shows old output.** `--reload` restarts the *server*; it does not clear your *browser's* own cache of the page. Hard-refresh the browser tab (`Ctrl+Shift+R` in most browsers) if a change doesn't seem to appear, before assuming the reload itself failed — check the terminal for a fresh `INFO: Reloading...` line to confirm the server side actually did its part.
- **Forgetting which terminal is which once you have two open.** A small, real productivity habit: rename terminal tabs (most terminal emulators support this, including Windows Terminal running Git Bash) to "backend" and "frontend," or keep them in a consistent left/right arrangement — this stops becoming "which one do I even look at" the moment something breaks.

## How this connects

You now have a second, independent Python project — its own venv, its own `requirements.txt`, its own running server — using exactly the isolation discipline Module 01 taught, applied for real to a genuinely different kind of project than any CLI tool. You've also, for the first time in this course, run two servers simultaneously and seen that they're just two separate programs on two separate ports, which is precisely the shape every remaining module through the final capstone will keep using (frontend and backend, running side by side, talking over HTTP). Lesson 01 starts writing real routes, and explains exactly what that `@app.get(...)` decorator does under the hood, building directly on Module 01, Lesson 10's mechanism.

## Quick self-check

1. What specific job does FastAPI do, and what specific job does Uvicorn do — and why does an app need both, rather than just one?
2. What does "ASGI" stand for, and what problem was it created to solve that its predecessor (WSGI) couldn't?
3. In `uvicorn main:app --reload`, what do `main` and `app` each refer to, and how does Uvicorn find them?
4. Why should `--reload` never be used in a real production deployment?
5. If your FastAPI server and your Vite dev server are both running and both individually work when visited directly, but a `fetch()` call from the React app to the FastAPI server fails with a browser console error mentioning CORS, what's actually happening — and which future module explains it in full?
