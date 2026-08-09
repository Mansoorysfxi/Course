# Lesson 05 — Similarity Search in Practice

## What you'll learn

- How Module 12's cosine similarity becomes a real, running SQL query
  via `pgvector`'s `<=>` operator.
- The exact line-by-line behavior of `app/repository.py`'s
  `find_similar_chunks`.
- Why distance and similarity sort in opposite directions, and how to
  keep that straight.
- Why this app's own test suite cannot run this exact query, and what it
  uses instead.

## Why this matters

Lesson 04 gave embeddings a place to live and an index built for fast
nearest-neighbor search. This lesson is where that index actually gets
used — the one real database query this entire feature exists to run:
"given this question's embedding, which chunks, among only *this quest's*
notes, are most similar in meaning?"

## Prerequisites

- **Module 12, Lesson 04** — cosine similarity, with intuition. This
  lesson assumes you remember what it measures and why 1 means identical
  and -1 means opposite.
- **Lesson 04** — the `vector` column type and HNSW index this query
  actually uses.
- **Module 06's SQL/SQLAlchemy lessons** — `ORDER BY`, `LIMIT`, and
  `WHERE` should already be familiar.

## The concept, explained simply

This is a spatial/proximity query, exactly like Lesson 04's NPC example,
except "nearness" means "similar in meaning" instead of "close in 3D
space." A cosine-distance query asks Postgres: "of all the points I have
stored, sort them by how close they are to this one query point, and
give me the closest few" — the meaning-space equivalent of "find the 5
nearest NPCs to the player."

## The details

### `find_similar_chunks`, read in full

```python
async def find_similar_chunks(
    session: AsyncSession, quest_id: str, query_embedding: list[float], top_k: int = 3
) -> list[RetrievedChunk]:
    stmt = (
        select(NoteChunk, QuestNote.title)
        .join(QuestNote, QuestNote.id == NoteChunk.note_id)
        .where(NoteChunk.quest_id == quest_id)
        .order_by(NoteChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )
    result = await session.execute(stmt)
    return [
        RetrievedChunk(
            note_id=chunk.note_id, note_title=note_title,
            chunk_index=chunk.chunk_index, content=chunk.content,
            embedding=list(chunk.embedding),
        )
        for chunk, note_title in result
    ]
```

Line by line:

- **`.where(NoteChunk.quest_id == quest_id)`** filters to only this
  quest's chunks, *before* any distance is even computed. This is not
  just an optimization — it's the actual security boundary that keeps
  one player's notes on a different quest from ever leaking into a
  question's answer. `quest_id` is a denormalized column on `NoteChunk`
  directly (Lesson 04's own db_models.py docstring explains why) — this
  filter needs no join to `quest_notes` at all.
- **`.order_by(NoteChunk.embedding.cosine_distance(query_embedding))`** —
  `.cosine_distance(...)` is a real method `pgvector-python` adds
  directly onto a `Vector`-typed column. It compiles to Postgres's own
  `<=>` operator. This is the query-level equivalent of Module 12's
  `1 - cosine_similarity(a, b)` — smaller distance means more similar.
- **No `.desc()`** — because smaller is better for *distance*, this sorts
  **ascending** (the default), the opposite direction from ranking by
  *similarity* (Lesson 06's `rank_by_cosine_similarity` sorts
  descending). Mixing these up is a real, easy mistake — see below.
- **`.limit(top_k)`** — only the closest few rows are ever pulled back
  into Python at all; Postgres does the sorting, using the HNSW index
  (Lesson 04) to avoid a full table scan.
- **`.join(QuestNote, QuestNote.id == NoteChunk.note_id)`** — needed only
  to read `QuestNote.title` back for each chunk, for a citation (Lesson
  06). Filtering itself never touches this join, for the same
  denormalization reason as above.

### Distance vs. similarity: the one thing to keep straight

- **`cosine_distance`** (pgvector, this query): 0 = identical, 2 =
  completely opposite. **Smaller is better** → sort ascending.
- **`cosine_similarity`** (Module 12's own function, and
  `app/rag.py`'s `rank_by_cosine_similarity`, Lesson 06): 1 = identical,
  -1 = completely opposite. **Bigger is better** → sort descending.

They're simply related (`distance = 1 - similarity`, for cosine
specifically) — but sorting the wrong direction for whichever one you're
using is a real, silent bug: your query would still run, still return
`top_k` rows, and still *look* correct at a glance — just returning the
*least* relevant chunks instead of the most relevant ones.

### Why `top_k = 3`, and what a real system would add

QuestLog fixes `TOP_K_CHUNKS = 3` — a small, deliberately simple choice
for this course's own scope. A production RAG system serving much larger
or more varied document collections might add: a similarity-score
*cutoff* (discard chunks below some minimum relevance, rather than
always returning exactly `top_k` even when nothing is truly relevant),
a re-ranking step (a second, more expensive model that re-scores the
top handful of candidates a cheap first pass already narrowed down), or
a dynamically-sized `k` based on the question. This module deliberately
keeps all of that out of scope — three fixed, unconditional results is
enough to teach the real mechanism without extra machinery this course's
"chunking-strategy no re-teaching, keep it small" scope already asked for.

### The one thing this query genuinely cannot be tested without

`NoteChunk.embedding` compiles to plain `JSON` on SQLite (Lesson 04) —
which has no `.cosine_distance()` at all. Running this exact query
against this backend's own SQLite test database doesn't quietly do the
wrong thing; it fails outright with a SQL syntax error, because SQLite
has no idea what `<=>` means. This is a real, honest limit on what the
main test suite can verify — Lesson 08 covers the full decision: a
separate, explicitly-gated test file
(`tests/test_notes_pgvector_integration.py`) proves the real query
against a real Postgres+pgvector instance, only when one is available,
while the main suite verifies the *ranking logic* itself (Lesson 06's
`rank_by_cosine_similarity`) in plain Python instead.

## Common mistakes & gotchas

- **Sorting descending on a `cosine_distance` query** (`.desc()` tacked
  on out of habit) — this silently returns the *least* similar chunks.
  Always double check: distance ascending, similarity descending.
- **Filtering by `owner_id` instead of, or in addition to,
  `quest_id`.** This app's own auth model already scopes a quest to its
  owner via `get_quest_or_404` before `find_similar_chunks` is ever
  called — filtering by `quest_id` alone is correct and sufficient here,
  because a quest a caller doesn't own never reaches this function in
  the first place (Lesson 08 covers this dependency chain in full).
- **Forgetting the `top_k` limit is applied by the database, not by
  Python** — `.limit(top_k)` means Postgres itself only ever computes
  and returns `top_k` rows; it is not "fetch everything, then slice in
  Python," which would defeat the whole point of the index.
- **Assuming a passing main test suite proves the real pgvector query
  works.** It proves the *ranking logic* is correct — the real SQL
  statement is only proven by `test_notes_pgvector_integration.py`
  against a real Postgres+pgvector instance. Don't conflate the two.

## How this connects

This lesson's query is what actually finds the chunks Lesson 06's
pipeline hands to Claude. The `RetrievedChunk` shape this function
returns is the exact same shape `rank_by_cosine_similarity` (the
in-memory, test-friendly stand-in) also returns — so everything
downstream of retrieval never needs to know or care which one produced
its input.

## Quick self-check

1. Why does `find_similar_chunks` filter by `quest_id` *before* computing
   any distance, rather than computing distance over every chunk and
   filtering afterward?
2. Why does this query sort ascending, while `rank_by_cosine_similarity`
   (Lesson 06) sorts descending, for what's conceptually "the same"
   ranking?
3. What does `.limit(top_k)` actually control, and why does running it at
   the database level matter more than it would for a small, in-memory
   list?
4. Why can't this exact query be run against this backend's own SQLite
   test database, and what does the test suite use instead to verify
   ranking logic?
5. Name one thing a production RAG system might add to this retrieval
   step that QuestLog deliberately leaves out.
