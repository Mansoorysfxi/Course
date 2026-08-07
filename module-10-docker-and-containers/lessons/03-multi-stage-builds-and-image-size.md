# Lesson 03 — Multi-Stage Builds and Image Size Optimization

**Verified against (August 2026):** `python:3.14-slim` and `node:24-alpine`
tags confirmed current via Docker Hub while writing this lesson (see
Lesson 00's and this module's `backend/Dockerfile`/`frontend/Dockerfile`
headers for the exact patch versions each resolves to at the time of
writing). The musl-vs-glibc compatibility trade-off described below is a
long-standing, well-documented characteristic of Alpine Linux, not a
fast-moving fact — still worth stating plainly rather than assumed, per
Rule 7.

## What you'll learn

- Why a single-stage Docker build often ships far more inside the final
  image than the running application actually needs.
- What a **multi-stage build** is, and how `COPY --from=<stage>` lets a
  later stage cherry-pick only specific files out of an earlier one.
- How to measure and compare real image sizes (`docker images`,
  `docker history`) — not just take this lesson's word for the
  difference.
- The genuine trade-off between Debian-based (`-slim`) and Alpine-based
  (`-alpine`) base images, and why this course doesn't blindly pick the
  smallest option every time.

## Why this matters

A smaller image isn't just a vanity metric. A smaller image pulls faster
(meaningful the moment Module 11 automates a deploy that pulls a fresh
image on every push), has a smaller **attack surface** (fewer installed
packages means fewer potential vulnerabilities sitting in the image at
all — a real security property, not just a size one), and, very
concretely for this course, is *cheaper and faster* to build and rebuild
constantly while you're learning. This lesson's technique is also
**required**, not merely nice-to-have, for QuestLog's own frontend
(Lesson 08): a Node.js toolchain capable of running Vite has no reason to
exist in the image that actually serves the finished static files to a
browser.

## Prerequisites

- **Lesson 02** — this lesson assumes you're comfortable with
  `Dockerfile` instructions, layers, and `docker build`/`docker history`.
- The toy `requests`-based example from Lesson 02 — this lesson builds on
  it directly.

## The concept, explained simply

Lesson 02's fixed Dockerfile already orders instructions well for
*caching*, but every one of pip's own temporary files, its download
cache, and pip itself, all still end up sitting inside the final image —
none of that was ever actually needed once `requests` is installed;
it's just leftover residue from *how* it got installed. A **multi-stage
build** is a Dockerfile with more than one `FROM` instruction, each
starting a completely fresh, separate, independent filesystem (a
"stage"). Earlier stages can do whatever messy, heavyweight work is
needed to *produce* something (compiling code, installing build tools,
running a full Node.js build), and a later, final stage can then reach
back with `COPY --from=<earlier stage>` and grab **only** the specific,
already-finished files it actually needs — leaving every stage's own
mess behind entirely; only the final stage's own filesystem ever becomes
the actual, shipped image.

**Game-dev analogy:** this is exactly the difference between shipping a
players a folder containing your entire Unreal project (every source
`.cpp` file, every intermediate build artifact, the whole multi-gigabyte
`Intermediate/` folder) versus shipping them just the final, packaged
`.exe`/`.pak` files a real "Package Project" build produces. Both
"contain" your game, in some sense — only one of them is what you'd
actually distribute.

## The details

### Turning Lesson 02's example into a multi-stage build

Recall Lesson 02's fixed, cache-friendly single-stage Dockerfile:
```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
```
Check its size first, for a real baseline:
```bash
docker build -t hello-single .
docker images hello-single
```
**Expected**, a `SIZE` column around **130-150MB** (exact number varies
by platform/architecture and exactly which packages `requests` itself
pulls in, but `python:3.14-slim` alone is already roughly this size
before anything else is added).

Now the multi-stage version:
```dockerfile
# ---- Stage 1: builder ----
FROM python:3.14-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: final image ----
FROM python:3.14-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app.py .
CMD ["python", "app.py"]
```
**Line by line, what's new:**
- `FROM python:3.14-slim AS builder` — the `AS builder` names this
  stage, so a later stage can refer back to it by name.
- `--prefix=/install` — instead of installing `requests` into this
  stage's own normal system location, pip installs it into a
  self-contained folder at `/install`, structured exactly like a real
  Python installation prefix.
- The second `FROM python:3.14-slim` starts a **completely fresh**
  stage — none of Stage 1's `pip` download cache, `pip` itself's own
  files, or anything else Stage 1's filesystem accumulated exists here
  at all, unless explicitly copied in.
- `COPY --from=builder /install /usr/local` — copies **only** the
  already-installed `requests` package (and nothing else Stage 1's
  filesystem contains) from Stage 1 into this final stage, landing it at
  `/usr/local`, exactly where Python's own default `sys.path` already
  expects to find installed packages.

Build and compare:
```bash
docker build -t hello-multistage .
docker images
```
**Expected:** for this particular tiny example (one small pure-Python
package), the size difference is modest — a few MB at most, since `pip`
itself and its download cache are small. **Try it yourself:** add a
package with real compiled dependencies to `requirements.txt` (e.g.
`pandas`) and rebuild both versions — the size difference becomes far
more dramatic, because compiling `pandas`'s own C extensions pulls in
real build tools (a C compiler, headers) that a naive single-stage build
has no way to discard afterward, but a multi-stage build's discarded
builder stage never lets reach the final image at all.

### Confirming the discarded stage is genuinely gone

```bash
docker history hello-multistage
```
**Expected:** no layer here shows pip's own download cache or the
Stage-1-only build tools at all — only the layers this specific,
final `FROM` actually produced. The builder stage still exists on your
machine as its own, separate, cached image (Docker keeps it around
specifically so a future rebuild can reuse its cache) — see it with:
```bash
docker images --filter "dangling=true"
```
**Expected:** an entry with `<none>` as both `REPOSITORY` and `TAG` —
this is Stage 1's own intermediate image, kept around for caching, never
shipped or run directly, and safe to clean up later with
`docker image prune` if you want to reclaim the disk space (Lesson 06's
own cleanup section covers this in full).

### The real, necessary multi-stage example this module builds toward

The toy example above shows the *mechanism*; `backend/Dockerfile` (this
module's own QuestLog capstone, Lesson 07) applies the exact same
`--prefix=/install` + `COPY --from=builder` pattern for real, and
`frontend/Dockerfile` (Lesson 08) needs multi-stage builds even more
essentially: Stage 1 runs a full Node.js/npm/Vite toolchain (genuinely
large — `node:24-alpine` alone plus ~170 installed npm packages) purely
to *produce* a `dist/` folder of plain HTML/CSS/JS; Stage 2 starts fresh
from `nginx:1.30-alpine` (a tiny, purpose-built web server image) and
copies in **only** that finished `dist/` folder. The final, shipped
frontend image contains zero trace of Node.js, npm, or any of those ~170
packages — exactly Module 09 Lesson 08's own "build on your own machine,
ship only `dist/` to the server" idea, now baked directly into the image
build itself instead of a manual, remembered step.

### `-slim` vs. `-alpine`: a real trade-off, not just "smaller is better"

You'll notice `backend/Dockerfile` uses `python:3.14-slim` (Debian-based)
while `frontend/Dockerfile`'s build stage uses `node:24-alpine`
(Alpine-based) and its final stage uses `nginx:1.30-alpine`. This isn't
inconsistent — it's a deliberate, per-case decision:

- **Alpine Linux** images are dramatically smaller (a base Alpine image
  is a few MB, versus tens of MB for a minimal Debian-based image)
  because Alpine uses **musl**, a smaller, simpler C standard library
  implementation, instead of the far more common **glibc**. This is the
  actual reason Alpine images are so small — not compression tricks, a
  genuinely different, more minimal core library.
- The trade-off: some compiled software (particularly Python packages
  with C extensions, historically) has occasionally shipped prebuilt
  binaries expecting glibc specifically, causing real, sometimes
  confusing failures on musl-based Alpine that don't reproduce on
  Debian-based images — a real, documented category of problem, which is
  exactly why `backend/Dockerfile`'s own header explains choosing
  `-slim` deliberately for QuestLog's backend, favoring
  compatibility over the smaller size Alpine would offer there.
- Nginx itself (`nginx:1.30-alpine`) and this project's own Node/Vite
  toolchain (`node:24-alpine`) don't carry this same risk to nearly the
  same degree — Nginx is a single, well-tested-on-Alpine C binary, and
  this project's own `package-lock.json` already resolves correct,
  Alpine-compatible native binaries automatically (the exact mechanism
  Lesson 08 explains in full, tied to this module's `optionalDependencies`
  fix). Alpine is the right choice for both of those, and the smaller
  size is pure upside with no realistic downside here.

The lesson to take from this, generally: "smallest possible image" is
not an unconditional goal — pick the smallest image that doesn't
introduce a real compatibility risk for *your specific* dependencies,
and know which category you're in before choosing.

## Common mistakes & gotchas

- **Forgetting `AS <name>` on an earlier stage, then trying to
  `COPY --from=` it anyway.** Without a name, you can still reference an
  earlier stage by its numeric index (`COPY --from=0 ...`, zero-based,
  in the order stages appear) — but a name is far more readable and far
  less fragile against someone later inserting a new stage in the
  middle, so this course always names stages explicitly.
- **`COPY --from=builder /install /usr/local` seems to "not work" —
  `import requests` still fails at runtime.** Double check the Python
  version matches **exactly** between both stages (`python:3.14-slim` in
  both `FROM` lines, not `3.14-slim` in one and `3.13-slim` in the
  other) — installed packages land in a version-specific path
  (`.../python3.14/site-packages`), and copying them into a
  differently-versioned final image puts them somewhere that Python
  version's own `sys.path` never looks.
- **Assuming Alpine is always the "more correct" choice because it's
  smaller.** See this lesson's own trade-off section — smaller is not
  automatically better if it introduces a real compatibility risk for
  your specific dependencies.
- **Confusing a discarded build stage with a dangling image you can
  safely `docker image prune` at any time mid-development.** True, but
  doing so also discards that stage's own build cache — your *next*
  build from scratch will be as slow as the very first one, since
  there's nothing left to reuse. Fine to do occasionally to reclaim disk
  space; not something to do reflexively after every single build.

## How this connects

Multi-stage builds are Lesson 02's layer-caching principle taken one
step further: instead of merely *ordering* instructions so cheap,
frequent changes don't invalidate expensive, rare ones, multi-stage
builds let you **discard entire stages'** worth of files that were only
ever needed to *produce* the final result, never to *run* it. Lesson 04
shifts focus from what's *inside* one image to how multiple running
containers find and talk to each other over a network — the next piece
QuestLog's own multi-container Compose setup (Lesson 06 onward) needs.

## Quick self-check

1. What does `COPY --from=builder /install /usr/local` actually do, and
   what does it deliberately leave behind in the builder stage?
2. Why does a multi-stage build matter *more* for the frontend's
   Dockerfile than for the backend's, given what each stage's tooling
   actually produces?
3. What is the real, mechanical reason Alpine-based images are so much
   smaller than Debian-based ones — not "compression," what specifically
   is different?
4. Name one real, documented risk of choosing an Alpine base image for a
   Python project with compiled dependencies, and why this course avoids
   it for QuestLog's own backend specifically.
5. If you `docker image prune` a discarded builder-stage image, what do
   you lose the ability to do quickly on your next build?
