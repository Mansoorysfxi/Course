# Lesson 08 — Building QuestLog's Notes Feature: Backend

## What you'll learn

- The complete backend shape of "chat with your quest notes": the
  schema, the migration, every new file, and every changed file.
- How `app/routers/notes.py` wires chunking, embedding, storage,
  retrieval, and generation into four real HTTP routes.
- This module's honest answer to a genuinely harder testing question
  than any prior module faced: how do you test code that depends on a
  real, Postgres-specific column type?

## Why this matters

Every earlier lesson in this module built one concept in isolation. This
lesson is where they become the actual, real, working QuestLog feature —
the same kind of "concepts, then the real app" transition Module 13's
Lesson 07 made for the quest-breakdown assistant.

## Prerequisites

- **Lessons 02-06, in full** — this lesson assumes you understand every
  piece it wires together; it will not re-explain chunking, embeddings,
  the pgvector query, or the citation design.
- **Module 13, Lesson 07** — this feature follows the exact same
  dependency-injection and streaming conventions QuestLog's first AI
  feature already established.
- **Module 08's testing lessons** — fixtures, `pytest`, mocking.

## The concept, explained simply

This lesson is the "assembly" step — like wiring a fully-tested set of
gameplay systems (movement, inventory, combat) into one actual level that
a player can walk through and interact with. Every system already works
on its own (Lessons 02-06); this lesson is the level script that calls
each one in the right order in response to a real player action (adding
a note, asking a question).

## The details

### The schema

Two new tables, added by
`backend/alembic/versions/..._add_quest_notes_and_note_chunks.py`
(Lesson 04 covers the migration itself in full):

- **`quest_notes`** — one row per note: `id`, `quest_id` (FK), `owner_id`
  (FK, denormalized directly onto this table for the same reason
  `Quest.owner_id` is — a direct ownership check with no join required),
  `title`, `content` (the full raw text), `created_at`.
- **`note_chunks`** — one row per chunk of a note: `id`, `note_id` (FK,
  `ON DELETE CASCADE` — Lesson 04), `quest_id` (FK, denormalized for
  read-performance on the hot retrieval path — Lesson 05's own query
  filters directly on this column), `chunk_index`, `content`,
  `embedding` (`Vector(384)`, Lesson 04), `created_at`.

### The new and changed files, in full

**New:**
- `app/chunking.py` — Lesson 02.
- `app/embeddings.py` — Lesson 03.
- `app/rag.py` — Lesson 06.
- `app/routers/notes.py` — this lesson's own subject, below.
- `alembic/versions/..._add_quest_notes_and_note_chunks.py` — Lesson 04.
- `tests/test_chunking.py`, `tests/test_rag.py`, `tests/test_notes.py`,
  `tests/test_notes_pgvector_integration.py` — this lesson's testing
  section.
- Frontend: `src/types/note.ts`, `src/api/notesApi.ts`,
  `src/components/QuestNotesPanel.tsx` — Lesson 09.

**Changed:**
- `app/db_models.py` — added `QuestNote` and `NoteChunk`.
- `app/models.py` — added `QuestNoteCreate`, `QuestNote` (the Pydantic
  API shape), `AskQuestionRequest`.
- `app/repository.py` — added `create_note_with_chunks`, `list_notes`,
  `delete_note`, `find_similar_chunks`.
- `app/main.py` — registered `notes.router`.
- `docker-compose.yml` — Postgres image changed to `pgvector/pgvector:pg18`
  (Lesson 00/04).
- `requirements.txt` — added `pgvector`, `sentence-transformers`, `numpy`.
- `RUNNING_PROJECT.md` — the embedding-model and pgvector decisions,
  recorded as two confined paragraphs.
- Frontend: `src/pages/QuestDetailPage.tsx` — renders `QuestNotesPanel`.

### The four routes, in `app/routers/notes.py`

```
POST   /api/quests/{quest_id}/notes         create_note
GET    /api/quests/{quest_id}/notes         list_notes
DELETE /api/quests/{quest_id}/notes/{id}    delete_note
POST   /api/quests/{quest_id}/notes/ask     ask_question
```

Every single one takes `quest: Annotated[Quest, Depends(get_quest_or_404)]`
— the exact same auth-scoped dependency every route in
`app/routers/quests.py` already uses (Module 07). There is no new
authorization logic anywhere in this file: a request for a quest that
doesn't exist, or belongs to someone else, never reaches any route body
at all.

**`create_note`** is the "ingest" half of the pipeline, all three steps
visible in one function, in order:

```python
chunks = chunk_text(data.content)
embeddings = embed_texts(chunks)
return await repository.create_note_with_chunks(
    session, quest_id=quest.id, owner_id=current_user.id,
    title=data.title, content=data.content,
    chunk_texts=chunks, chunk_embeddings=embeddings,
)
```

`chunk_text` and `embed_texts` run **in this route**, not inside
`app/repository.py` — the same "a route orchestrates a multi-step
operation; the repository only ever talks to the database" boundary this
codebase already drew for `create_quest`.

**`ask_question`** is the "retrieve and generate" half:

```python
if ai_client is None:
    raise HTTPException(503, ...)   # exact same pattern as Module 13's suggest-breakdown

query_embedding = embed_text(data.question)
retrieved_chunks = await repository.find_similar_chunks(
    session, quest_id=quest.id, query_embedding=query_embedding, top_k=TOP_K_CHUNKS
)

async def event_stream():
    async for event in stream_note_answer(ai_client, data.question, retrieved_chunks):
        yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"

return StreamingResponse(event_stream(), media_type="text/event-stream")
```

The SSE wire format lives here, and only here — `app/rag.py`'s
`stream_note_answer` (Lesson 06) knows nothing about Server-Sent Events
at all, exactly the same separation `app/ai_assistant.py` and
`app/routers/quests.py` already established in Module 13.

### The hard testing question, answered honestly

Module 08 chose in-memory SQLite for this whole backend's test suite,
because the schema used no Postgres-specific types. `pgvector`'s
`Vector` type genuinely is Postgres-specific — this is a real, new
problem, not something the SQLite choice was ever designed to cover.
This module's answer, in full:

1. **Everything that is *not* the real pgvector SQL is tested directly**,
   with no mocking of the logic itself: chunking (`tests/test_chunking.py`,
   pure Python, zero dependencies), the cosine-similarity ranking math
   and the full generation pipeline (`tests/test_rag.py`, using
   `rank_by_cosine_similarity` — a plain-Python function mirroring
   exactly what the real query does), and every route's own logic —
   auth scoping, chunking-and-embedding orchestration, SSE formatting,
   the 503-when-unconfigured path — (`tests/test_notes.py`, mocking
   `embed_text`/`embed_texts` and the Anthropic client, and, for the
   two tests that reach `/ask`, mocking `repository.find_similar_chunks`
   itself, since that one function's real SQL cannot run on SQLite at
   all — see its own module docstring for the full reasoning).
2. **The one thing that genuinely cannot be tested without real
   infrastructure** — whether `find_similar_chunks`'s actual
   `.cosine_distance()` SQL is syntactically and semantically correct
   against real Postgres+pgvector — gets its own, separate, explicitly
   gated file: `tests/test_notes_pgvector_integration.py`. Its tests are
   skipped, not run, unless a `TEST_PGVECTOR_DATABASE_URL` environment
   variable points at a real, migrated Postgres+pgvector database. This
   mirrors how many real teams handle "this one code path needs real
   infra": skip by default, opt in explicitly, never silently pass for
   the wrong reason.

This keeps the "tests never need real external creds" principle
(Module 08's database, Module 10's Redis, Module 13's AI client) intact
for the entire *default* test run, while still being honest that one
narrow, genuinely infrastructure-dependent piece exists and is tested
separately, on purpose, rather than hand-waved away.

## Common mistakes & gotchas

- **Trying to run `find_similar_chunks` against the default SQLite test
  database.** It fails with a SQL syntax error (`near ">"`), not a
  silent wrong answer — see Lesson 05's own note on this. Mock it in any
  route-level test that reaches `/ask`.
- **Forgetting `chunk_text`/`embed_texts` are imported by name into
  `app/routers/notes.py`'s own namespace** (`from app.embeddings import
  embed_text, embed_texts`) — tests monkeypatch
  `app.routers.notes.embed_text`/`embed_texts` specifically, not
  `app.embeddings.embed_text` directly, because Python's `from ... import
  ...` binds a new name in the importing module.
- **Adding a new authorization check for notes routes.** There isn't
  one needed — `get_quest_or_404` already does the entire job; adding a
  second check would be redundant, not safer.

## How this connects

This lesson is the backend half of the capstone. Lesson 09 completes the
picture with the frontend UI a player actually interacts with.

## Quick self-check

1. Name the two new database tables this feature adds, and what each one
   stores.
2. Why does `create_note` call `chunk_text`/`embed_texts` itself, rather
   than delegating that work to `app/repository.py`?
3. What does `ask_question` do when `ai_client` is `None`, and why is
   that the same pattern Module 13 already established?
4. What is the one thing this module's test suite genuinely cannot
   verify without real Postgres+pgvector, and how does it handle that
   honestly rather than hiding it?
5. Why do the two `/ask`-reaching tests in `tests/test_notes.py`
   monkeypatch `repository.find_similar_chunks` directly, rather than
   letting it run for real against the test database?
