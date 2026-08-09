# Module 14 Checklist — RAG (Retrieval-Augmented Generation)

Complete this before moving on to Module 15. Check off each item
honestly — this is a self-assessment, not a formality.

## Lessons

- [ ] Read `lessons/00-setup.md` and confirmed every command in its
      "Verify your setup" section — the `vector` extension is enabled,
      the new tables exist, and the backend test suite passes with no
      real Postgres+pgvector, no real embedding model, and no real
      Anthropic key required.
- [ ] Read `lessons/01-the-problem-rag-solves.md` and can explain, from
      memory, why fine-tuning and "just put everything in the prompt"
      both fail to solve QuestLog's actual problem.
- [ ] Read `lessons/02-chunking-strategies.md` and can explain the
      difference between fixed-size and paragraph-based chunking, and why
      QuestLog's own chunk-size default is smaller than the general
      benchmark this lesson cites.
- [ ] Read `lessons/03-embeddings-for-search.md` and can state, without
      looking it up, the three concrete reasons this module chose a
      local embedding model over a paid API.
- [ ] Read `lessons/04-vector-databases-and-pgvector.md` and can explain
      what `pgvector` actually adds to Postgres, why this module's Docker
      image changed, and why the migration uses HNSW instead of IVFFlat.
- [ ] Read `lessons/05-similarity-search-in-practice.md` and can explain,
      from memory, why `find_similar_chunks` sorts ascending while
      `rank_by_cosine_similarity` sorts descending for "the same" ranking.
- [ ] Read `lessons/06-building-a-rag-pipeline-by-hand.md` and can walk
      through all five pipeline steps from memory, and explain why
      citations in this app are a fact the code already knows, not
      something asked of the model.
- [ ] Read `lessons/07-rag-frameworks-honestly.md` and can explain
      LangChain's and LlamaIndex's current positioning, and give a real,
      reasoned answer for when a framework would actually help QuestLog.
- [ ] Read `lessons/08-building-questlogs-notes-feature-backend.md` and
      `lessons/09-building-questlogs-notes-feature-frontend.md` in full,
      and have actually read `project/questlog/backend/app/rag.py` and
      `project/questlog/frontend/src/components/QuestNotesPanel.tsx` end
      to end, not just the lessons describing them.

## Exercises

- [ ] Exercise 01 (chunking strategies) — done and reviewed.
- [ ] Exercise 02 (embeddings and similarity search) — done and reviewed,
      including a real, live run of the local embedding model.
- [ ] Exercise 03 (pgvector similarity queries) — done and reviewed
      against a real, running `pgvector`-enabled Postgres, or a thorough,
      honest dry run if you don't have one available yet.
- [ ] Exercise 04 (RAG pipeline by hand) — done and reviewed, including
      correctly retrieving the right document's chunks for a targeted
      question.

## Capstone

- [ ] `project/BRIEF.md` Part 1 — the feature genuinely chunks, embeds,
      stores, retrieves, and answers with real citations, run live (or a
      thorough, honest dry run exists instead).
- [ ] Part 2 — the deliberately-broken scenario was genuinely reproduced
      and then fixed, with the real behavior documented.
- [ ] Part 3 — one small, real extension was implemented and explained.
- [ ] Part 4 — the pgvector integration tests were run for real against a
      real Postgres+pgvector instance, or an honest account exists of why
      that wasn't possible.
- [ ] `project/NOTES_FEATURE_REPORT.md` written, covering all five
      required points from the brief.
- [ ] You can explain, unprompted, the complete path a single question
      takes — chunking, embedding, the real pgvector query, prompt
      assembly, and the streamed, cited answer — from a note being added
      to an answer appearing on screen.
- [ ] The backend test suite (`pytest`, from
      `project/questlog/backend/`) and frontend test suite (`npx vitest
      run`, from `project/questlog/frontend/`) both still pass in full,
      with no `ANTHROPIC_API_KEY` and no `TEST_PGVECTOR_DATABASE_URL` set
      anywhere in your shell (the pgvector-integration tests should show
      as **skipped**, not failed, in that case).

## Spaced repetition — review questions from earlier modules

Per this course's Rule 6, answer these without re-reading the original
lesson first; check your answer against the linked material afterward.

1. **(Module 06)** What does "normalizing" a database schema actually
   mean, and what specific problem does it prevent? *(See
   `module-06-databases/lessons/09-normalization-and-schema-design.md`
   — and notice this module's own `NoteChunk.quest_id` deliberately does
   the *opposite*, for a stated, honest reason — see
   `lessons/04-vector-databases-and-pgvector.md`.)*
2. **(Module 08)** Why did this course choose in-memory SQLite, not a
   dedicated Postgres test database, for the backend test suite? *(See
   `module-08-testing-and-quality/lessons/06-testing-with-a-database.md`
   — and notice this module's own Lesson 08 had to extend that same
   reasoning to cover a genuinely new problem: a Postgres-specific column
   type.)*
3. **(Module 10)** What does a FastAPI dependency like `DbSession` or
   `RedisClient` actually let a test do that a hardcoded, real connection
   wouldn't? *(See
   `module-10-docker-and-containers/lessons/07-containerizing-questlogs-backend.md`
   — this module's own notes routes reuse the exact same
   `Depends(get_quest_or_404)` pattern for auth scoping.)*
4. **(Module 12)** What does cosine similarity actually measure, and why
   does it divide out each vector's length rather than using a plain dot
   product? *(See
   `module-12-ai-ml-foundations/lessons/04-embeddings-meaning-as-coordinates.md`
   — this module's own `cosine_similarity`/`cosine_distance` are the
   exact same idea, reused for real search instead of a demo script.)*
5. **(Module 13)** Why does streaming a response make structured output
   harder to reconcile, and how did QuestLog's own AI assistant resolve
   that tension? *(See
   `module-13-building-with-llm-apis/lessons/07-building-questlogs-ai-assistant-backend.md`
   — and notice this module's own `app/rag.py` deliberately sidesteps the
   whole tension by not using structured output at all; explain why that
   was the right call here specifically.)*

## Before moving to Module 15

- [ ] All boxes above are checked honestly.
- [ ] You understand, in your own words, why this module builds the RAG
      pipeline by hand before ever mentioning LangChain or LlamaIndex,
      and can name at least one concrete thing each framework would
      genuinely have saved you.
- [ ] You can explain why QuestLog's citations are built from what the
      code already knows was retrieved, rather than asked of the model —
      and why that distinction matters for trustworthiness.
- [ ] You understand this module's testing decision well enough to
      explain it to someone else: which parts of this feature are tested
      by the default `pytest` run, and which one narrow piece genuinely
      needs real Postgres+pgvector, and why.
