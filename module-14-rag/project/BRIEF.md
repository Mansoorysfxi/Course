# Capstone Brief — QuestLog's "Chat with Your Quest Notes," Verified End to End

## What you're doing

This module's `project/questlog/` already contains a real, working
feature: a player can attach free-text notes to a quest, and QuestLog will
chunk them, embed them with a free local model, store them in a real
`pgvector`-enabled Postgres column, and answer questions about them with a
streamed, cited response (Lessons 02-06, applied for real in Lessons
08-09). Both the retrieval logic and the generation logic are fully
tested — 72 backend tests (2 of them intentionally skipped without a real
Postgres+pgvector instance — see `backend/tests/test_notes_pgvector_integration.py`'s
own module docstring) and 28 frontend tests, all passing with no real
Anthropic key or Postgres+pgvector instance required.

Your job in this capstone is **not to build this feature from scratch** —
it's to **get it running live (with a real `pgvector`-enabled Postgres and
your own Anthropic API key, or do a thorough, honest dry run), verify it
genuinely works the way Lessons 08-09 claim, break something on purpose
and fix it, and write up what you found** — the same "understand it well
enough to explain and to fix" standard every capstone since Module 09 has
used.

## Before you start

- [ ] All four exercises in this module are done and reviewed.
- [ ] You've read Lessons 00-09 in full, in order.
- [ ] You've completed Lesson 00's setup: a `pgvector`-enabled Postgres
      (the `pgvector/pgvector:pg18` image) with the migration applied, and
      either a real `ANTHROPIC_API_KEY` or a decision to do a dry run
      instead (see "A note on scope," at the bottom).
- [ ] You've read `project/questlog/README.md` for how to run the backend
      and frontend locally.

## What to actually do

### Part 1 — Get the feature running live

1. Confirm your `docker-compose.yml` Postgres service is
   `pgvector/pgvector:pg18` and `alembic upgrade head` has run (Lesson
   00's "Verify your setup").
2. In `project/questlog/backend/.env`, set a real `ANTHROPIC_API_KEY`.
3. Start the backend and frontend, log in as the seeded demo account
   (`player@questlog.local` / `dragon-slayer-1`), and open a quest's
   detail page.
4. **Add at least two notes** to one quest — real, different text for
   each (e.g. one about combat strategy, one about an unrelated topic like
   a shopping list). **Confirm** each appears in the notes list with the
   correct chunk count.
5. **Ask a question** that's clearly answerable from only one of your two
   notes. **Confirm, watching it happen live:**
   - A **Sources** list appears, naming the note(s) actually retrieved,
     **before** any answer text appears.
   - The answer text visibly streams in, token by token.
   - The final answer references the correct note by name, and does not
     reference your unrelated note.
6. **Delete one note**, then ask the same question again. **Confirm** the
   sources/answer now reflect only your remaining note (or, if you deleted
   the only relevant one, confirm you get an honest "not enough
   information" style answer, not a hallucinated one).

### Part 2 — Break something on purpose, then fix it (pick one)

- Temporarily unset `ANTHROPIC_API_KEY` (restart the backend) and ask a
  question again. **Confirm** a clean `503`, not a confusing crash — then
  restore the key and confirm it works again.
- Ask a question on a quest with **zero notes**. **Confirm** you get the
  "This quest has no notes yet" error *without* Claude ever being called —
  check your Anthropic dashboard (or a debug log line you add temporarily)
  to confirm no API call was actually made for this case, then explain in
  your own words why `app/rag.py`'s `stream_note_answer` is written to
  guarantee that.
- Deliberately break the embedding-model consistency: temporarily change
  `EMBEDDING_DIMENSIONS`/the model name in `app/embeddings.py` to something
  that would produce a different vector size, try adding a note, and
  **confirm** you get a real, loud pgvector dimension-mismatch error — then
  revert your change and confirm it works again. Explain why this failure
  is a *good* thing (Lesson 04's own reasoning) rather than a silent bug.

### Part 3 — Extend it, in one small, well-justified way

Pick **one** small, real addition and implement it — not a large
redesign:

- Add a minimum-similarity-score cutoff to `find_similar_chunks` (or a
  post-filter in `rank_by_cosine_similarity`) so a genuinely irrelevant
  question doesn't return `top_k` chunks regardless of how unrelated they
  are — Lesson 05's own "what a real system would add" section names this
  exact idea.
- Let a player edit a note's title after creation (`PATCH
  /api/quests/{quest_id}/notes/{note_id}`) — decide, and justify in
  writing, whether editing content should re-chunk and re-embed the note
  (hint: yes, and explain why leaving stale chunks would be a real,
  silent correctness bug).
- Add a real, small eval harness for this feature (Module 13, Lesson 06's
  pattern, applied here): a handful of golden question/expected-source
  pairs, checked automatically, that runs with **no real API key required**
  in mocked mode and optionally live if one is set.

### Part 4 — Run the actual pgvector integration tests, if you can

If you have a real, running `pgvector`-enabled Postgres (which you do, if
you completed Part 1), set `TEST_PGVECTOR_DATABASE_URL` to it and run:

```bash
cd project/questlog/backend
TEST_PGVECTOR_DATABASE_URL="postgresql+asyncpg://questlog:questlog_dev_password@localhost:5432/questlog" pytest tests/test_notes_pgvector_integration.py -v
```

**Confirm** both tests in this file now run for real (not skip) and pass —
this is the one thing the module's own generation process could not
verify live (no Docker/Postgres was available while writing it) and is
exactly the kind of gap this capstone exists to close for real.

## Deliverables

Write up a short report (`project/NOTES_FEATURE_REPORT.md` — create this
yourself; no fixed template, honest content matters more than a fixed
shape) covering:

1. **Part 1's confirmation**, describing what you actually observed —
   real screenshots, terminal output, or a precise written account if you
   did a dry run instead (see "A note on scope" below).
2. **Part 2's broken-then-fixed scenario** — the exact behavior you
   observed when it was broken, and confirmation it works again once
   fixed.
3. **Part 3's extension** — what you built, why you chose it, and the
   actual diff.
4. **Part 4's result** — did the pgvector integration tests actually run
   and pass for you? If you couldn't run them (no Docker/Postgres
   available), say so honestly, and explain what you'd expect based on
   reading `app/repository.py`'s `find_similar_chunks` and the test file
   itself.
5. **An honest accounting of what this feature still doesn't do** — for
   example: no re-ranking, no similarity-score cutoff (unless you built
   Part 3's version), no support for editing a note's content, notes are
   plain text/markdown only, never a PDF. For each, say whether that's a
   real gap or a reasonable scope decision, and why.

## Acceptance criteria (what "done" looks like)

- [ ] The feature genuinely chunks, embeds, stores, retrieves, and
      answers with real citations when run live (or a thorough, honest
      dry-run account exists instead).
- [ ] Part 2's break-then-fix scenario is genuinely reproduced and
      explained, not just asserted.
- [ ] Part 3's extension is implemented, small, and well-justified.
- [ ] Part 4 is attempted honestly — either real pgvector-integration
      test results, or an honest account of why you couldn't get them.
- [ ] `NOTES_FEATURE_REPORT.md` exists and covers all five numbered points
      above, honestly.
- [ ] You can explain, without looking anything up, the complete path a
      single question takes — chunking, embedding, the real SQL query,
      prompt assembly, and the streamed, cited answer — from a note being
      added to an answer appearing on screen.
- [ ] No more than a few cents of real API spend was required for
      anything in this capstone, per Lesson 00's own cost estimate.

## A note on scope

Consistent with this module's own Lesson 00 framing, and the same pattern
Modules 09, 11, 12, and 13 all used for real infrastructure or paid-API
requirements: if you'd rather not set up a real `pgvector`-enabled
Postgres or spend even the small amount this capstone genuinely costs
right now, a thorough, honest dry run — reading every relevant line of
`app/rag.py`, `app/routers/notes.py`, and `QuestNotesPanel.tsx`, tracing
exactly what would happen at each step of Parts 1-3, and writing up
precisely what you'd expect to observe, citing this module's own lessons
by name — is a fully legitimate way to complete this capstone. What
matters is demonstrated understanding of *why* the feature works the way
it does, not a specific number of dollars spent or a specific piece of
infrastructure running, proving it.
