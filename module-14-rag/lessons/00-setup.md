# Lesson 00 — Setup: pgvector, the Embedding-Model Decision, and What This Module Costs

**Verified against (August 2026), via live web research and live PyPI/Docker Hub fetches on August 9, 2026:**

| Fact | Verified value | Source |
|---|---|---|
| `pgvector` Postgres extension version bundled with the Docker image this course now uses | `0.8.6`, tagged for Postgres 18 | Docker Hub, `pgvector/pgvector` repository tags (`pg18`, `0.8.6-pg18`) |
| `pgvector-python` (the PyPI package, `import pgvector`) latest version | `0.5.0`, released 2026-07-06 | PyPI JSON API, `pypi.org/pypi/pgvector/json`, fetched live |
| `anthropic` Python SDK latest version | `0.121.0`, released 2026-08-07 | PyPI JSON API, `pypi.org/pypi/anthropic/json`, fetched live — unchanged since Module 13 verified the same version one day earlier |
| Claude Haiku 4.5 pricing (this module reuses Module 13's model choice) | $1.00 / million input tokens, $5.00 / million output tokens | Re-confirmed via live search; unchanged since Module 13 |
| `sentence-transformers` version this module reuses from Module 12 | `5.7.0`, `all-MiniLM-L6-v2` model, 384-dimensional output | Module 12, Lesson 04's own verification; re-confirmed nothing changed |
| Whether Anthropic offers its own embeddings API | No — Anthropic has no embeddings model and officially recommends Voyage AI as a third-party partner | Live search of current Anthropic/Voyage AI documentation and pricing pages |
| Voyage AI embeddings pricing, if you wanted the paid-API alternative | `voyage-4-lite`: $0.02/million tokens; `voyage-4`: $0.06/million tokens; `voyage-4-large`: $0.12/million tokens; 200 million free tokens on signup | Live search, August 9, 2026 |

## What you'll learn

- How to get a real `pgvector`-enabled Postgres running for this module,
  using a different Docker image than Module 10's plain `postgres:18-alpine`.
- The embedding-model decision this module makes (reusing Module 12's
  free, local model rather than a paid embeddings API) and exactly what
  that means for what you install.
- How to verify every new piece of this module's setup before Lesson 01
  needs any of it.
- What this module costs in real dollars — for most of you, **nothing
  new** beyond what Module 13 already required.

## Why this matters

Every module so far that added a new piece of infrastructure (Postgres in
Module 06, Redis in Module 10, the Anthropic API in Module 13) front-loaded
its setup into a dedicated `00-setup.md`, per Rule 8 — so you never hit a
lesson that assumes a tool you haven't installed yet. This module adds
two new pieces at once: a Postgres *extension* (`pgvector`) and a
decision about *where embeddings come from*. Getting both settled here,
before Lesson 01 ever mentions either, means the rest of this module can
focus entirely on the actual ideas (chunking, retrieval, citations)
instead of pausing mid-lesson to install something.

## Prerequisites

- **Module 06's Postgres + SQLAlchemy + Alembic** — this module adds two
  new tables via a real migration; if `CREATE TABLE`, foreign keys, and
  `alembic upgrade head` feel shaky, revisit that module's Lessons 05 and
  07 first.
- **Module 10's Docker Compose setup** — this module changes one line of
  `docker-compose.yml` (the Postgres image) and nothing else about how
  the stack runs.
- **Module 12's embeddings lesson (Lesson 04)** — this module assumes you
  already know what an embedding is and what cosine similarity measures.
  If "meaning as coordinates" doesn't ring a bell, go back and read that
  lesson before continuing; this module builds directly on top of it and
  will not re-teach it from scratch.
- **Module 13's Anthropic API key and SDK** — already required, unchanged
  here. If you skipped Module 13 entirely, go get a key first (that
  module's own Lesson 00).

## The concept, explained simply

Think of this module as adding two new departments to QuestLog's world,
and this lesson is where you hire both of them before asking them to do
any work:

1. **A place to store meaning-as-coordinates, indexed for fast lookup.**
   Module 12 taught you that an embedding turns a piece of text into a
   list of numbers — a point in a very high-dimensional space, where
   nearby points mean similar things. Module 06 already taught you that
   Postgres is where this app's data lives. `pgvector` is what teaches
   Postgres a *new kind of column* (a vector) and a *new kind of query*
   ("find the nearest points to this one") — the database equivalent of
   a game engine's spatial partitioning structure (an octree, a grid) that
   lets you ask "what's near this location?" without checking every single
   object in the level one by one.
2. **A decision about who computes those coordinates in the first
   place.** Something has to turn a player's note into a vector before
   `pgvector` has anything to store. Module 12 already showed you one way
   to do that — a free model that runs entirely on your own machine. This
   module could instead call a paid API to do the same job. Lesson 03
   makes this decision for real, with real numbers; this lesson just
   tells you the answer up front so your setup steps match it.

## The details

### Step 1 — The embedding-model decision, stated up front

**This module reuses Module 12's local `sentence-transformers` model
(`all-MiniLM-L6-v2`), not a paid embeddings API.** The full reasoning —
why this is a genuine trade-off, not an obvious choice, and what a paid
API would have cost instead — is Lesson 03's job. For setup purposes,
this decision means exactly one thing: **you do not need a second API key
or a second paid account for this module.** The only paid API this module
ever calls is the same Anthropic API Module 13 already set up, used
exactly the same way, for exactly one new thing (generating a cited
answer once retrieval has already found the relevant text — Lesson 06).

The trade-off you *are* accepting, in exchange for that "no new key, no
new cost" simplicity, is a bigger backend: `sentence-transformers` pulls
in `torch` (PyTorch) as a dependency, which is a genuinely large package
(hundreds of megabytes) and takes real, noticeable time to load into
memory the first time this backend computes an embedding after starting
up. This is a real cost, stated honestly — Lesson 03 walks through
exactly how QuestLog's own code (`app/embeddings.py`) manages it (loading
the model lazily, only when first needed, not at every server startup).

### Step 2 — Get `pgvector` into your Postgres

QuestLog's Module 10 `docker-compose.yml` used `postgres:18-alpine` — a
small, official Postgres image with no extensions beyond what ships with
plain Postgres. `pgvector` is a real Postgres *extension*, not something
built into Postgres itself, and (verified live, August 9, 2026) there is
no official Alpine-based image with `pgvector` pre-installed for Postgres
18 — Alpine Linux only carries a community `postgresql-pgvector` package
in its unstable `edge` branch, not something this course's reference
setup should depend on.

The fix: this module's `docker-compose.yml` changes the `postgres`
service's image to `pgvector/pgvector:pg18` — the extension's own
official image, which ships Postgres 18 with `pgvector` 0.8.6 already
built in. Nothing else about the service changes: same user, password,
database name, volume, and healthcheck as Module 10 left it.

```bash
cd module-14-rag/project/questlog
docker compose down          # stop anything left running from Module 13's copy
docker compose pull postgres # fetches the new pgvector/pgvector:pg18 image
docker compose up -d postgres
```

**Expected:** Docker pulls a new image (noticeably larger than plain
`postgres:18-alpine` — a real, honest size trade-off for a stable,
pre-built extension instead of an unofficial Alpine package) and starts a
container. `docker compose ps` should show `postgres` as `healthy` within
a few seconds.

### Step 3 — Enable the extension (handled by the migration, but verify it yourself once)

`pgvector` being *installed* in the image is not the same as it being
*enabled* in your specific database — that's a one-time, per-database SQL
statement: `CREATE EXTENSION IF NOT EXISTS vector`. This module's own
Alembic migration (Lesson 04 walks through it in full) runs that
statement for you automatically the first time you run
`alembic upgrade head` — you do not need to run it by hand. This step is
here so you can *verify* it worked, not because you need to do it
yourself:

```bash
docker compose exec postgres psql -U questlog -d questlog -c "SELECT extname FROM pg_extension;"
```

**Expected, after running migrations (Step 4 below):** a row for `vector`
appears in the output, alongside `plpgsql` (which every Postgres database
has by default).

### Step 4 — Install this backend's new Python dependencies and run migrations

```bash
cd module-14-rag/project/questlog/backend
python -m venv venv
source venv/Scripts/activate   # Git Bash on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
alembic upgrade head
```

**Expected:** `pip install` succeeds (this will take noticeably longer,
and download noticeably more, than any previous module's `pip install` —
`sentence-transformers` and its `torch` dependency are large; this is the
"bigger backend" trade-off Step 1 named honestly, happening in front of
you). `alembic upgrade head` prints the new migration's revision id and
applies it — Lesson 04 shows you exactly what SQL it runs.

### Step 5 — Your Anthropic API key (unchanged from Module 13)

If you still have `ANTHROPIC_API_KEY` set from Module 13 (or in this
project's `backend/.env`), nothing new is needed here. If you're picking
this module up fresh, revisit Module 13, Lesson 00 for how to get one —
the key, the SDK, and the cost reasoning are identical here.

## Verify your setup

**1. `pgvector` Python package imports correctly:**
```bash
python -c "from pgvector.sqlalchemy import Vector; print('ok')"
```
**Expected:** `ok`, with no import error.

**2. `sentence-transformers` imports correctly (this may take several seconds — it's importing `torch`):**
```bash
python -c "from sentence_transformers import SentenceTransformer; print('ok')"
```
**Expected:** `ok`, possibly after a noticeable pause. This is a live-verified,
honest observation: this import is measurably slower than any `import` in
this course so far, because of `torch`'s own size — see Lesson 03 for why
QuestLog's own application code makes sure this cost is paid at most once
per server process, never per-request.

**3. The `vector` extension is enabled in your database:**
```bash
docker compose exec postgres psql -U questlog -d questlog -c "\dx"
```
**Expected:** a table listing installed extensions, including a row for
`vector`.

**4. The new tables exist:**
```bash
docker compose exec postgres psql -U questlog -d questlog -c "\dt"
```
**Expected:** `quest_notes` and `note_chunks` appear alongside the
existing `users`, `quest_lines`, and `quests` tables.

**5. The backend's test suite passes with no real Postgres, no real
`sentence-transformers` model call, and no real Anthropic key:**
```bash
cd module-14-rag/project/questlog/backend
pytest -q
```
**Expected:** every test passes except the ones in
`tests/test_notes_pgvector_integration.py`, which are **skipped** (not
failed) with a message naming `TEST_PGVECTOR_DATABASE_URL`. This is
deliberate and explained in full in Lesson 08's testing section — this
one file is the sole exception to "no real infrastructure needed for
tests," and it says so honestly rather than silently passing for the
wrong reason.

**Try it yourself:** Run `docker compose exec postgres psql -U questlog -d
questlog -c "SELECT vector_dims('[1,2,3]'::vector);"` — a tiny, direct
proof the extension works, independent of this app's own code. Predict
the output (it's the number of entries in that literal vector) before
running it.

## Common mistakes & gotchas

- **`ERROR: type "vector" does not exist`.** This means either the
  extension was never enabled (re-run `alembic upgrade head`, or check
  Verify step 3), or you're still running the *old* `postgres:18-alpine`
  container from Module 13's copy of this project — `docker compose down`
  and `docker compose up -d postgres` again after pulling the new image
  (Step 2).
- **`pip install` seems to hang for a long time on `torch`.** This is
  real, not a bug — `torch` is a genuinely large download (often several
  hundred megabytes). Let it finish; there's no way around this cost
  short of the paid-API alternative Lesson 03 discusses and this module
  chose not to take.
- **The first embedding call in a fresh backend process takes a
  noticeable pause (a second or more), then every call after that is
  fast.** This is `app/embeddings.py`'s lazy-loaded model doing its
  one-time disk load — not a bug, and not something later calls repeat.
  See Lesson 03.
- **Forgetting `docker compose pull postgres` before `up`** means Docker
  may reuse an already-pulled, older image with the same tag cached
  locally instead of fetching the new one — if `\dx` doesn't show
  `vector` after a fresh `up`, an explicit `pull` first usually fixes it.
- **Running the pgvector-only integration tests expecting them to fail
  or error** — they don't error, they **skip**, with a clear reason
  printed. That's the intended behavior without a
  `TEST_PGVECTOR_DATABASE_URL` set; see Lesson 08.

## How this connects

Every lesson from here on assumes: a running `pgvector`-enabled Postgres
(this lesson, Steps 2-4), the embedding-model decision already made
(Step 1, justified in full in Lesson 03), and the same Anthropic API key
Module 13 already required (Step 5). Lesson 01 starts with the
conceptual "why" behind all of this — the problem RAG solves — before any
more setup or code.

## Quick self-check

1. Why does this module change the Postgres *Docker image* rather than
   just running an `ALTER` or install command inside the existing
   `postgres:18-alpine` container?
2. What two separate jobs does "pgvector" and "sentence-transformers"
   each do — and why are they two separate decisions, not one?
3. What new cost, if any, does this module add to your Anthropic API
   bill? What new cost does it add to your `pip install` time and disk
   space?
4. Why do `tests/test_notes_pgvector_integration.py`'s tests skip rather
   than fail when `TEST_PGVECTOR_DATABASE_URL` isn't set — and why is
   that the honest choice rather than a shortcut?
5. If you had chosen a paid embeddings API instead of the local model,
   what would Step 4's `pip install` have looked like differently?
