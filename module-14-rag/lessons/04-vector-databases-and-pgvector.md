# Lesson 04 — Vector Databases and pgvector

**Verified August 9, 2026:** `pgvector/pgvector:pg18` (Docker Hub) ships
Postgres 18 with the `pgvector` extension version `0.8.6` pre-built.
`pgvector-python` (the PyPI package providing SQLAlchemy 2.0 integration)
is at version `0.5.0`, released 2026-07-06 (PyPI JSON API, fetched live).
No official Alpine-based pgvector image exists for Postgres 18 as of this
date — Alpine only carries a community `postgresql-pgvector` package in
its unstable `edge` branch.

## What you'll learn

- What a vector database actually is, and why a plain Python list of
  embeddings stops working at scale.
- What `pgvector` specifically adds to Postgres, and how it's installed
  for this course's Docker setup.
- How `NoteChunk.embedding`'s type (`Vector(384).with_variant(JSON(),
  "sqlite")`) works, and why it exists.
- What real alternatives to `pgvector` exist, and when they'd make more
  sense than "add an extension to the database you already have."

## Why this matters

Lesson 03 settled *where embeddings come from*. This lesson answers the
other half of the storage question the master plan explicitly calls
out: *where do they live, and how do you search them fast?* QuestLog
already has a real, working Postgres database (Module 06) — this lesson
is about extending it, rather than introducing an entirely separate kind
of database just for one feature.

## Prerequisites

- **Module 06, Lesson 05** (SQLAlchemy basics) and **Lesson 07** (Alembic
  migrations) — this lesson's migration and ORM column both build
  directly on those.
- **Module 12, Lesson 04** and **this module's Lesson 03** — you need to
  already know what an embedding vector is before "a database column that
  holds one" means anything.

## The concept, explained simply

Picture a game world with thousands of NPCs, and you need to answer "who
are the 5 nearest NPCs to the player right now?" many times per second.
Checking every single NPC's distance from the player, one by one, every
single query, works — but it doesn't scale; that's an $O(n)$ scan every
time. Real game engines instead use a spatial index (an octree, a grid,
a BSP tree) that lets a proximity query skip huge swaths of the world
that are obviously too far away, without ever checking most objects
individually.

A **vector database** — or, as in this module's case, a *database
extension that adds vector capabilities* — solves the exact same problem
for embeddings instead of 3D positions: "which of these thousands of
stored vectors are closest, in meaning-space, to this one query vector?"
`pgvector` is Postgres's own answer: a real extension that adds a new
column type (a fixed-length list of numbers) and new index types built
specifically for fast nearest-neighbor search over vectors, the same
spirit as a spatial index, just for a different kind of "nearness."

## The details

### Why not just a Python list of embeddings?

For a handful of chunks, looping over a plain Python list and computing
cosine similarity by hand (exactly what Lesson 05's
`rank_by_cosine_similarity` does, and exactly what you'll do in this
module's own exercises) works completely fine — that's genuinely how
this app's own test suite verifies ranking *logic* without touching a
real database at all. It stops being practical once the number of chunks
grows large: every query becomes a full scan of every vector in memory,
and every one of them has to already be loaded into your Python
process. A real database gives you persistence (chunks survive a
restart — Module 06's whole reason for existing in the first place),
concurrent access from multiple requests safely, and, crucially for this
lesson, **specialized indexes** that make nearest-neighbor search fast
without a full scan.

### What `pgvector` actually adds

`pgvector` is a real Postgres *extension* — not something built into
Postgres by default, and not a separate database product. Three pieces:

1. **A new column type**, `vector(N)` — a fixed-length array of floating
   point numbers, `N` dimensions. QuestLog's `NoteChunk.embedding` is
   `vector(384)`, matching `all-MiniLM-L6-v2`'s own output size exactly.
2. **New distance operators** — `<->` (Euclidean/L2 distance), `<#>`
   (negative inner product), and `<=>` (cosine distance, the one this
   app uses). These compute a distance between two vectors directly
   inside a SQL query, at the database level, without pulling every row
   back into Python first.
3. **New index types** built for approximate nearest-neighbor search —
   `IVFFlat` and `HNSW`. QuestLog's migration uses **HNSW** specifically
   because, unlike `IVFFlat` (which needs a representative sample of real
   data already present to pick good cluster centers), HNSW can be built
   on a table with zero rows — which matters because this migration runs
   before any note has ever been created.

### Installing `pgvector` for this course's Postgres

Module 10 chose `postgres:18-alpine` — small, official, no extensions
beyond what plain Postgres ships with. As this lesson's header states,
there is no official Alpine-based pgvector image for Postgres 18
(verified live). This module's `docker-compose.yml` instead switches the
`postgres` service to `pgvector/pgvector:pg18` — the extension's own
official image, Debian-based, with pgvector 0.8.6 already built in. This
is a real, honest trade-off: a bigger image than Alpine, in exchange for
a stable, pre-built, officially-supported combination instead of an
unstable Alpine package. Nothing else about the service (user, password,
volume, healthcheck) changes.

Being *installed* in the image isn't the same as being *enabled* per
database — `CREATE EXTENSION IF NOT EXISTS vector` is a one-time, real
SQL statement that has to run once per database before any table in it
can use the `vector` type. QuestLog's migration runs this for you (next
section).

### The migration, concretely

`backend/alembic/versions/..._add_quest_notes_and_note_chunks.py` does
three things a normal migration in this course hasn't needed before:

```python
def upgrade() -> None:
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))

    op.create_table("quest_notes", ...)   # ordinary columns, ordinary FKs

    op.create_table(
        "note_chunks",
        ...,
        sa.Column("embedding", Vector(384), nullable=False),
        ...,
    )

    op.execute(sa.text(
        "CREATE INDEX ix_note_chunks_embedding_hnsw ON note_chunks "
        "USING hnsw (embedding vector_cosine_ops)"
    ))
```

1. **Enable the extension first** — a table column can't use a type
   (`vector(384)`) that doesn't exist in the database yet.
2. **Create both tables** — `quest_notes` (raw note text) and
   `note_chunks` (each chunk plus its embedding), exactly the shape
   `app/db_models.py`'s ORM classes describe.
3. **Create the HNSW index with a raw `op.execute`, not
   `op.create_index`.** Alembic and SQLAlchemy Core have no built-in
   knowledge of pgvector's own index syntax (`USING hnsw (... vector_cosine_ops)`)
   — this is the same "drop to plain SQL for anything Alembic's own
   helpers don't model" pattern Module 06, Lesson 07 already introduced
   in the abstract, now used for a genuinely new reason.
   `vector_cosine_ops` specifically tells pgvector to build this index
   for *cosine*-distance queries — the only kind this app ever runs
   (Lesson 05).

The migration's `downgrade()` deliberately does **not** `DROP EXTENSION
vector` — a Postgres extension is database-wide, and this one feature's
own downgrade shouldn't assume nothing else in the database depends on
it (there's nothing else, in QuestLog's case, but the general principle
holds: an extension's own lifecycle is a database-level decision, not
a single feature's).

### `NoteChunk.embedding`'s real column type, in full

```python
embedding: Mapped[list[float]] = mapped_column(Vector(384).with_variant(JSON(), "sqlite"))
```

`.with_variant(JSON(), "sqlite")` tells SQLAlchemy: "use `Vector(384)` as
this column's real type on every database dialect *except* SQLite, where
use plain `JSON` instead." This exists for one reason: this backend's
test suite runs against in-memory SQLite (Module 08's own choice,
unchanged), and SQLite has no concept of a `vector` type at all —
`with_variant` lets the *same* ORM class compile to the *real* pgvector
column on Postgres (where this app actually runs) and a structurally
equivalent, storable-and-retrievable `JSON` column on SQLite (where tests
run), without maintaining two separate model files. The real cost, stated
honestly: SQLite's `JSON` variant can store and round-trip a chunk's
embedding for structural tests, but it has **no distance operator at
all** — which is exactly why the real similarity *math* also exists as
a plain, database-independent Python function (`app/rag.py`'s
`rank_by_cosine_similarity`, Lesson 05) that tests use instead of the
real query.

### `ON DELETE CASCADE` — the first foreign key in this app to use it

`NoteChunk.note_id`'s foreign key uses `ondelete="CASCADE"` — the first
one in this entire codebase. Every earlier foreign key (`Quest.owner_id`,
`Quest.quest_line_id`) relied on the ORM/repository layer to handle
deletion itself; this one instead tells Postgres directly: "if the parent
`quest_notes` row is deleted, delete this row too, as part of the same
transaction." The trade-off, honestly: this rule now lives in the
database schema rather than in Python you can read and step through.
This module accepts that trade-off specifically for this relationship,
because a chunk has no meaning at all without its parent note — there is
no scenario where you'd want an orphaned chunk to survive its note's
deletion.

### Alternatives to pgvector, honestly

The master plan explicitly asks for this: pgvector isn't the only way to
store and search vectors. Dedicated vector databases exist —
**Pinecone** (fully managed, no infrastructure to run yourself),
**Weaviate** and **Qdrant** (open-source, self-hostable, built
vector-first), **Chroma** (lightweight, popular for prototypes and small
apps). Each of these can outperform `pgvector` at very large scale or
offer retrieval features `pgvector` doesn't (e.g., built-in hybrid
keyword+vector search). This course picks `pgvector` specifically
because the master plan wants it to build on Postgres knowledge you
already have (Module 06) rather than introduce an entirely new database
product and its own connection/deployment/backup story just for this one
feature — for an app QuestLog's size, adding a whole second database
system would be real, unjustified incidental complexity.

## Common mistakes & gotchas

- **`ERROR: type "vector" does not exist`.** The extension was never
  enabled in this specific database — re-run `alembic upgrade head`
  (Lesson 00's Verify step 3 checks this directly).
- **Inserting a vector with the wrong number of dimensions.** pgvector
  raises a real, immediate error the instant a mismatched-size vector is
  inserted — not a silent truncation or padding. If you ever see this,
  it almost always means the embedding model changed (a different
  model, different output size) without updating the column's declared
  dimension count.
- **Choosing `IVFFlat` for a brand-new, empty table.** `IVFFlat` needs a
  representative sample of real data to build good clusters — building
  it before any data exists produces a poor index. HNSW doesn't have
  this requirement, which is exactly why this migration uses it.
- **Assuming SQLite's `JSON`-variant column can be queried the same way
  as real `pgvector`.** It can store and return the same values, but has
  no `.cosine_distance()` operator at all — see Lesson 05 and Lesson 08
  for how this app's test suite handles that gap honestly.

## How this connects

This lesson gave vectors a home and an index. Lesson 05 is the query
that actually uses that index — the real `ORDER BY ... <=> ...` statement
`app/repository.py`'s `find_similar_chunks` runs.

## Quick self-check

1. What three things does the `pgvector` extension add to Postgres?
2. Why does this module's `docker-compose.yml` change the Postgres image
   entirely, rather than installing pgvector into the existing
   `postgres:18-alpine` image?
3. Why does the migration use HNSW rather than IVFFlat for this table?
4. What does `.with_variant(JSON(), "sqlite")` actually do, and what real
   capability does the SQLite version of this column lack?
5. Name one dedicated vector database and one concrete reason a real
   project might choose it over `pgvector`.
