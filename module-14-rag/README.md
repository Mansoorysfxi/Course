# Module 14 — RAG (Retrieval-Augmented Generation)

**Phase:** 4 — AI Engineering & Agents
**Estimated time:** 14-18 hours
**Verified against (August 2026):** `pgvector` Postgres extension `0.8.6`
(via the official `pgvector/pgvector:pg18` Docker image); `pgvector` the
PyPI/SQLAlchemy-integration package `0.5.0`; `sentence-transformers`
`5.7.0` with `all-MiniLM-L6-v2` (unchanged since Module 12); `anthropic`
Python SDK `0.121.0` and Claude Haiku 4.5 pricing ($1.00/million input
tokens, $5.00/million output tokens), both unchanged since Module 13.
Every fact above was checked with a live web search or fetch while writing
this module, on August 9, 2026 — see each lesson's own header for the
specific source and date.

## What this module is

Module 13 gave QuestLog its first real AI feature, entirely from what fit
in a single prompt. This module answers the next real question: what do
you do when the relevant information *doesn't* fit in one prompt, or
doesn't even exist until a player writes it? **Retrieval-Augmented
Generation (RAG)** is the answer — retrieve the small number of genuinely
relevant pieces of your own data, then hand them to the model as context,
instead of relying on what it learned during training or trying to stuff
everything into every request.

**QuestLog gains "chat with your quest notes" in this module:** a player
attaches free-text notes to a quest — battle strategies, planning, NPC
dialogue they want to remember — and can then ask a question that gets
answered by retrieving the most relevant pieces of their own notes and
having Claude answer **with real, trustworthy citations** back to which
note the answer came from. Per the master plan's own explicit instruction,
the retrieval pipeline is built **by hand first, with no framework** —
chunking, embeddings, a real `pgvector` similarity query, prompt assembly,
and citations are all real, readable application code you can trace end to
end — before Lesson 07 discusses LangChain and LlamaIndex honestly.

## What you'll be able to do after this module

- Explain, precisely, the problem RAG solves and why it's different from
  fine-tuning or "just put everything in the prompt."
- Chunk a document with a real, justified strategy, and explain the
  trade-offs of chunk size and overlap.
- Explain how Module 12's embeddings and cosine similarity apply directly
  to search, and make a real, well-reasoned decision about where
  embeddings should be computed (a local model vs. a paid API).
- Explain what `pgvector` adds to Postgres, install and enable it for this
  course's own Docker setup, and write a real, correct migration that adds
  a `vector` column and an index.
- Write and read a real `pgvector` cosine-distance query, and correctly
  reason about ascending-vs-descending sort order for distance vs.
  similarity.
- Build a complete RAG pipeline by hand, with no framework, and explain
  every one of its five steps from memory.
- Discuss LangChain and LlamaIndex's current positioning honestly, and
  give a real, reasoned answer to "when would a framework actually help
  here, versus just adding overhead?"
- Explain, end to end, exactly how QuestLog's own "chat with your quest
  notes" feature works, because you can read (and did read) every line of
  its real, tested implementation.

## Prerequisites

- **Module 06 (Databases)** — SQLAlchemy models, Alembic migrations, and
  the normalization/denormalization vocabulary this module builds on
  directly.
- **Module 10 (Docker)** — this module changes one line of
  `docker-compose.yml`; you should already be comfortable running it.
- **Module 12, Lesson 04, in full** — embeddings and cosine similarity are
  **not re-taught** in this module; they're assumed and built on.
- **Module 13 in full** — this module's own answer-generation step reuses
  the Anthropic API mechanics (streaming, the `AiClient`/`DbSession`
  dependency pattern) that module already established, deliberately
  without repeating tool use or structured output, both already taught
  there.

## A real Anthropic API key, and one new (free) piece of infrastructure

This module needs the same `ANTHROPIC_API_KEY` Module 13 already required
— nothing new there. What's new is a `pgvector`-enabled Postgres, set up
in `lessons/00-setup.md` by swapping one Docker image, and this module's
own embedding-model decision (Lesson 03): reusing Module 12's free, local
`sentence-transformers` model rather than a paid embeddings API, so this
module adds **zero new required signups or paid accounts** — only a
heavier `pip install`, explained honestly in Lesson 00.

## Module structure

```
module-14-rag/
├── README.md                                                     ← you are here
├── lessons/
│   ├── 00-setup.md                                                 ← pgvector, the embedding-model decision, cost
│   ├── 01-the-problem-rag-solves.md                                  ← why retrieval at all
│   ├── 02-chunking-strategies.md                                       ← splitting notes into searchable pieces
│   ├── 03-embeddings-for-search.md                                       ← local model vs. paid API, decided for real
│   ├── 04-vector-databases-and-pgvector.md                                 ← the extension, the migration, alternatives
│   ├── 05-similarity-search-in-practice.md                                   ← the real cosine-distance query
│   ├── 06-building-a-rag-pipeline-by-hand.md                                   ← chunk -> embed -> retrieve -> cite, by hand
│   ├── 07-rag-frameworks-honestly.md                                             ← LangChain/LlamaIndex, verified, honest
│   ├── 08-building-questlogs-notes-feature-backend.md                              ← the capstone backend, explained
│   └── 09-building-questlogs-notes-feature-frontend.md                               ← the capstone frontend, explained
├── exercises/
│   ├── 01-chunking-strategies/                                     ← easy
│   ├── 02-embeddings-and-similarity-search/                          ← guided
│   ├── 03-pgvector-similarity-queries/                                 ← guided -> independent (needs Docker)
│   └── 04-rag-pipeline-by-hand/                                          ← independent (rehearses the capstone)
├── project/
│   ├── BRIEF.md                                                     ← capstone: verify & extend "chat with your notes"
│   └── questlog/                                                      ← QuestLog, copied forward from Module 13,
│       ├── backend/app/chunking.py                                       ← NEW: paragraph-first chunking
│       ├── backend/app/embeddings.py                                       ← NEW: lazy-loaded local embedding model
│       ├── backend/app/rag.py                                                ← NEW: retrieval + citation-first generation
│       ├── backend/app/routers/notes.py                                       ← NEW: 4 routes, reusing existing auth
│       ├── backend/alembic/versions/..._add_quest_notes_and_note_chunks.py      ← NEW: the pgvector migration
│       ├── backend/tests/test_chunking.py, test_rag.py, test_notes.py,           ← NEW: real tests, no external infra
│       │       test_notes_pgvector_integration.py                                    needed for the default run
│       ├── frontend/src/api/notesApi.ts                                             ← NEW: SSE consumption, new event shape
│       └── frontend/src/components/QuestNotesPanel.tsx                                ← NEW: notes list, add-note form, ask UI
└── CHECKLIST.md
```

Read the lessons in order — Lessons 08-09 assume every technique in
Lessons 00-07 without re-explaining any of them. Exercises 01-04 go from
"almost impossible to fail if you read Lesson 02" to "build the whole
pipeline yourself, standalone" — see each exercise's own
`INSTRUCTIONS.md` for its specific difficulty and hints.

## How to work through this module

Follow the workflow in the [root README](../README.md): read a lesson,
answer its self-check questions, do the matching exercise without looking
at its solution, ask for a review, revise if needed, then move on. Once
all four exercises are done, work through `project/BRIEF.md`.

## A note on the running project

See [`RUNNING_PROJECT.md`](../RUNNING_PROJECT.md) for the full picture of
how QuestLog evolves across modules, and its "Fixed technology decisions"
section for this module's own embedding-model and pgvector/Docker-image
decisions, recorded there in full. This module's `project/questlog/` is
Module 13's finished QuestLog, copied forward, with `backend/app/` and
`frontend/src/` changed only for this module's own new, documented
"chat with your quest notes" feature — see Lessons 08-09 for the complete,
file-by-file account of exactly what changed and why.
