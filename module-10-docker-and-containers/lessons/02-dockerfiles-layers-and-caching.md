# Lesson 02 — Dockerfiles, Line by Line: Layers and Caching

**Verified against (August 2026):** `python:3.14-slim` confirmed current
via Docker Hub (Python 3.14.7, released August 5, 2026, is the latest
patch of the 3.14 line QuestLog's own backend already runs — see
`backend/README.md`'s stack table); `docker build`'s own layer-caching
behavior described here is core, stable Docker Engine behavior, unchanged
in shape for years, re-confirmed against Docker's own current
documentation while writing this lesson.

## What you'll learn

- What a `Dockerfile` actually is, and how to write one from scratch.
- What an image **layer** is, mechanically, and why `docker build`
  caches each one independently.
- How to order a `Dockerfile`'s instructions so editing your application
  code doesn't force Docker to redo slow, unrelated work (like
  reinstalling every dependency) on every single build.
- How to actually look at an image's layers (`docker history`) and
  confirm the caching behavior this lesson describes is real, not just
  claimed.
- What `.dockerignore` does and why it matters even for instructions that
  don't explicitly reference the files it excludes.

## Why this matters

Lesson 01 established what a container *is*; this lesson is about how
you actually get your own application packaged into a runnable image at
all. Every container this course runs from here on — QuestLog's backend,
QuestLog's frontend, and every toy example in this lesson and its
exercise — starts life as a `Dockerfile`. Writing one badly (in a way
this lesson explains exactly how to avoid) is the single most common
reason a real team's Docker builds feel painfully slow — every tiny code
change forcing a multi-minute `pip install`/`npm install` all over again,
for no real reason.

## Prerequisites

- **Lesson 01** — this lesson assumes you're comfortable with `docker
  run`, `docker ps`, and the container-vs-image distinction that lesson
  introduced.
- **Module 01's Python fundamentals** — the toy example below is a small
  Python script; nothing advanced.

## The concept, explained simply

A `Dockerfile` is a plain text recipe: a strict, top-to-bottom list of
instructions describing exactly how to build one specific container
image, starting from some existing base image and adding your own files
and setup on top. `docker build` reads this recipe and executes it, one
instruction at a time, completely mechanically — there's no cleverness
or guessing involved, which is exactly the point: the same `Dockerfile`,
built today or built a year from now, given the same base image tag and
the same source files, produces the same result.

**Game-dev analogy:** think of a `Dockerfile` as a build script for a
game project that starts from a specific engine version, then adds your
project's own content and code on top, one deterministic step at a time
— not unlike a real build pipeline that starts from a known-good engine
build, then layers your project's assets and compiled code on top of it,
producing one final, packaged build artifact.

Each individual instruction in a `Dockerfile` produces its own **layer**
— a self-contained, cacheable record of exactly what that one instruction
changed on the filesystem. An image is really just a stack of these
layers, one on top of the previous, each only ever storing the *diff*
from the layer below it. This is the entire reason Docker's caching is
possible at all: if Docker can prove a given instruction, and everything
that instruction depends on, hasn't changed since the last build, it
skips re-running that instruction entirely and reuses the exact layer it
already has sitting on disk — instantly, with zero work.

## The details

### The simplest possible Dockerfile

Create a new, empty folder anywhere outside this course's own repo (a
scratch folder is fine — this toy example isn't part of QuestLog):

**`hello.py`:**
```python
print("Hello from inside a container!")
```

**`Dockerfile`** (exactly this filename, no extension, in the same
folder):
```dockerfile
FROM python:3.14-slim
COPY hello.py .
CMD ["python", "hello.py"]
```

**Line by line:**
- `FROM python:3.14-slim` — every Dockerfile starts with `FROM`, naming
  the **base image** every later instruction builds on top of. This one
  line alone gives your image a complete Debian-based Linux filesystem
  with Python 3.14 already installed — you're not building an OS or a
  Python interpreter from scratch; you're starting from an image someone
  else already built and maintains (in this case, the official Python
  image, published to Docker Hub — a **container registry**, GLOSSARY.md
  has the full definition) and adding to it.
- `COPY hello.py .` — copies `hello.py` from your own machine (the
  **build context** — see this lesson's `.dockerignore` section below)
  into the image's current working directory (`.` — which defaults to
  `/` unless a `WORKDIR` instruction set it to something else; real
  Dockerfiles almost always set one explicitly, which the next example
  does).
- `CMD ["python", "hello.py"]` — the command this image runs *by
  default* when a container is started from it with no other command
  specified. The list-of-strings form shown here (`["python",
  "hello.py"]`, called "exec form") is the recommended form — it runs
  the command directly, without an intermediate shell process, which
  matters for correctly forwarding signals like `Ctrl+C`/`docker stop`
  to your actual program (a real, documented reason to prefer this form,
  not just a style preference).

Build it:
```bash
docker build -t hello-docker .
```
**Line by line:** `docker build` reads a `Dockerfile` and produces an
image from it. `-t hello-docker` **tags** (names) the resulting image
`hello-docker` (equivalent to `hello-docker:latest` — `latest` is just
the tag Docker assumes if you don't specify one; it is an ordinary tag
name, not a special "always the newest version" marker, a common and
important misconception). The final `.` is the **build context** — the
folder Docker sends to the daemon for this build to work with; every
`COPY`/`ADD` instruction can only reference files inside this context.

**Expected output** (abbreviated):
```
[+] Building 3.2s (7/7) FINISHED
 => [internal] load build definition from Dockerfile
 => [internal] load .dockerignore
 => [internal] load metadata for docker.io/library/python:3.14-slim
 => [1/2] FROM docker.io/library/python:3.14-slim@sha256:...
 => [internal] load build context
 => [2/2] COPY hello.py .
 => exporting to image
 => => naming to docker.io/library/hello-docker:latest
```

Run it:
```bash
docker run --rm hello-docker
```
**Expected:** `Hello from inside a container!`, then the container
exits immediately (this image's whole job is running one script once and
finishing — nothing keeps it alive the way Nginx's own server process
did in Lesson 01).

### Watching layer caching happen, for real

Rebuild with zero changes at all:
```bash
docker build -t hello-docker .
```
**Expected:** every step now shows `CACHED`:
```
[+] Building 0.1s (7/7) FINISHED
 => [internal] load build definition from Dockerfile
 => CACHED [1/2] FROM docker.io/library/python:3.14-slim@sha256:...
 => CACHED [2/2] COPY hello.py .
 => exporting to image
```
Notice the total time: a fraction of a second, versus over 3 seconds the
first time — Docker proved nothing relevant changed and reused every
layer it already had.

Now change something:
```python
print("Hello from inside a container! v2")
```
Rebuild again:
```bash
docker build -t hello-docker .
```
**Expected:** `FROM` is still `CACHED` (the base image didn't change),
but `COPY hello.py .` is **not** — Docker re-runs it, because the exact
bytes of `hello.py` changed, which is precisely what that layer's cache
key is based on.

### Why instruction *order* matters: a real caching win

This toy example has no dependencies to install, so it can't yet show
the single most important, real-world consequence of layer caching.
Extend it:

**`requirements.txt`:**
```
requests==2.32.3
```

**`app.py`** (replacing `hello.py`):
```python
import requests

print(f"requests version: {requests.__version__}")
```

**A naive `Dockerfile` — do NOT copy this pattern, on purpose, to see why:**
```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app.py"]
```
This `COPY . .` copies **everything** in the build context — both
`app.py` and `requirements.txt` — in one instruction, *before*
`pip install` runs. Build it once (`docker build -t hello-docker2 .`),
then change only `app.py` (e.g., tweak the printed message) and rebuild.
**Watch what happens to the `RUN pip install` step:** even though
`requirements.txt` itself never changed, Docker **still reinstalls
everything from scratch** — because `COPY . .` is one single layer
covering both files, and *any* change inside that layer (including one
completely unrelated file) invalidates every layer built on top of it,
including the expensive `pip install` step that comes after.

**The fix — copy dependency-defining files first, separately, before
your actual application code:**
```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
```
Build this version, then change only `app.py` and rebuild again.
**Expected:** `COPY requirements.txt .` and `RUN pip install ...` both
show `CACHED` — only `COPY app.py .` (and the final image-export step)
actually re-run. This is exactly the same principle
`backend/Dockerfile` (this module's own QuestLog capstone, Lesson 07)
already applies for real: dependency-defining files, copied and
installed first, application source code copied last — because
application code changes constantly, dependency lists change rarely, and
a Dockerfile's own instruction order is the only thing that determines
which of those two facts Docker's cache actually gets to take advantage
of.

**Try it yourself:** reorder the fixed Dockerfile back to `COPY . .`
form, deliberately, and time both versions with `time docker build ...`
after touching only `app.py` each time (`touch app.py` on Linux/WSL2, or
just add a comment). With a larger, real `requirements.txt` (QuestLog's
own has nine packages, several with real compiled dependencies) this
timing difference becomes dramatic — seconds of difference on a toy
example like this one, but easily *minutes* of difference on a real
project, on every single build, forever.

### Inspecting an image's actual layers

```bash
docker history hello-docker2
```
**Expected:** a table, one row per layer, newest at the top, each row
showing roughly what instruction produced it and how much disk space it
added. This is direct, checkable proof that an image really is a stack
of layers, not one opaque blob — and a genuinely useful debugging tool
for "why is this image so much bigger than I expected" (Lesson 03 comes
back to this exact command).

### `.dockerignore`

Create a `.dockerignore` file (same folder, alongside the `Dockerfile`):
```
__pycache__/
*.pyc
.git/
```
**What this actually does:** before `docker build` sends your build
context to the Docker daemon at all, it excludes anything matching these
patterns — meaning a `COPY . .` instruction (or any other) can never see
or copy these files, no matter what. This matters even for instructions
that don't reference these files explicitly, for two real reasons: (1) a
smaller build context uploads faster, especially significant if you're
building against a remote Docker daemon; (2) it's a genuine safety net —
without it, a stray `.env` file with a real secret sitting in your
project folder could get copied into an image layer by an overly broad
`COPY . .`, and, because image layers are immutable and often pushed to
a registry, simply deleting the file afterward would **not** remove it
from that already-built layer's history. `backend/.dockerignore` and
`frontend/.dockerignore` (this module's own capstone, Lessons 07-08) both
apply this exact same reasoning for real, excluding `.env` files, test
folders, and `node_modules`/`.venv` explicitly.

## Common mistakes & gotchas

- **`COPY failed: file not found`.** The path in your `COPY` instruction
  is relative to the **build context** (the folder you passed as
  `docker build`'s final argument, usually `.`), never relative to the
  `Dockerfile`'s own location if you happen to run `docker build` from
  somewhere else, and never an absolute path on your host machine at
  all — Docker builds run inside an isolated daemon process that has no
  access to your host filesystem except through the build context.
- **A `RUN` instruction runs, but its effects seem to vanish in a later
  step.** Every `RUN`, `COPY`, etc. instruction executes in a fresh shell
  process; `RUN cd /somewhere` on its own line, followed by a separate
  `RUN` instruction assuming you're still in `/somewhere`, does **not**
  work — each `RUN` starts over from the image's current `WORKDIR`. Chain
  related shell commands on one `RUN` line with `&&` instead, or set
  `WORKDIR` explicitly (which *does* persist across instructions,
  because it changes the image's own persistent state, not just one
  shell's transient one).
- **Editing one file causes a rebuild far more expensive than expected,
  despite instructions "looking" correctly ordered.** Double-check
  exactly what a `COPY` instruction's source actually includes — `COPY .
  .` still invalidates on *any* change anywhere in the context, even one
  that logically has nothing to do with dependencies; the fix is always
  the same, copy narrower, more specific paths first.
- **Assuming `latest` means "the newest version."** It's an ordinary tag
  name some projects (including the official `python`/`node`/`nginx`
  images) happen to also update to point at their newest release — but
  nothing about the string `latest` is special to Docker itself. Pinning
  a specific tag (`python:3.14-slim`, not `python:latest`) is what this
  course does throughout, for the exact same "don't let an environment
  drift out from under you unexpectedly" reason Module 01 pinned exact
  package versions in `requirements.txt`.

## How this connects

This lesson's caching principle — expensive, rarely-changing work first;
cheap, frequently-changing work last — is the exact same idea Lesson 03's
multi-stage builds take one step further (discarding an entire stage's
worth of now-unneeded files, not just reordering them), and it's the
reasoning directly behind the instruction order in `backend/Dockerfile`
and `frontend/Dockerfile`, both examined in full in Lessons 07-08.

## Quick self-check

1. What is an image layer, and what specifically determines whether
   Docker reuses a cached layer or re-runs its instruction on a rebuild?
2. Why does `COPY requirements.txt .` followed by `RUN pip install ...`,
   with `COPY app.py .` afterward, cache better across rebuilds than one
   single `COPY . .` before `RUN pip install ...`?
3. What does `.dockerignore` actually prevent, and why does it matter
   even for a `COPY` instruction that names specific files rather than
   `COPY . .`?
4. What does the tag `latest` actually mean to Docker, mechanically —
   and why does this course avoid relying on it?
5. Why does `RUN cd /somewhere` on one line have no effect on a
   completely separate `RUN` instruction later in the same Dockerfile?
