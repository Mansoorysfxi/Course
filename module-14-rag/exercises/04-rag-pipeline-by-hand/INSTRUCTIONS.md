# Exercise 04 — A Complete RAG Pipeline, by Hand

**Difficulty:** Independent. This is the last exercise before this
module's capstone (QuestLog's real "chat with your quest notes"
feature) — it's deliberately the same pipeline, in miniature, as a
standalone script with no database and no FastAPI app, so you can trace
every step without any application-framework scaffolding around it.

## What you'll build

A standalone script, `mini_rag.py`, that chunks a small set of documents,
embeds every chunk, stores them in a plain Python list (no database —
this exercise's own "vector store" is just a list, deliberately, to keep
focus on the pipeline shape rather than infrastructure), retrieves the
most relevant chunks for a question, and generates a cited answer using
the real Anthropic API.

## Concepts this exercise requires

- Chunking (Lesson 02), embeddings (Lesson 03), cosine-similarity ranking
  (Lesson 05), and the full pipeline shape and citation design (Lesson
  06) — this exercise is a smaller, standalone version of exactly what
  Lesson 06 and `app/rag.py` do for real.
- Calling and streaming from the Anthropic API (Module 13, Lessons 01-02).

## Setup

```bash
cd module-14-rag/exercises/04-rag-pipeline-by-hand/starter
python -m venv venv
source venv/Scripts/activate
pip install sentence-transformers numpy anthropic
export ANTHROPIC_API_KEY="sk-ant-...your-real-key..."
```

**Cost:** this exercise makes a small number of real Anthropic API
calls — the same order of magnitude as a single Module 13 exercise, well
under a cent per run at Claude Haiku 4.5's rates (Lesson 00's header
table).

**If you don't have a key:** you can still complete Steps 1-4 (chunking,
embedding, retrieval) fully for free — only Step 5 (generation) needs a
real key. The starter script clearly separates these.

## Instructions

1. Open `starter/mini_rag.py`. `DOCUMENTS` is a small, provided
   dictionary of document title → raw text (a stand-in for QuestLog's own
   quest notes).
2. Implement `chunk_and_embed(documents)`: for every document, chunk its
   text (reuse the paragraph-based approach from Exercise 01, or a
   simpler `text.split("\n\n")` — your choice, this exercise doesn't
   grade chunking strategy), embed every chunk, and return a flat list of
   `(document_title, chunk_index, chunk_text, embedding)` tuples — this
   is your entire "vector store."
3. Implement `retrieve(question, store, top_k)`: embed the question, rank
   every entry in `store` by cosine similarity, and return the `top_k`
   most similar entries.
4. Implement `build_prompt(question, retrieved)`: assemble the retrieved
   chunks and the question into one prompt string, labeling each excerpt
   with its source document's title — the same shape as
   `app/rag.py`'s `build_answer_prompt` (Lesson 06).
5. Implement `generate_answer(prompt)`: call the real Anthropic API
   (`claude-haiku-4-5`, matching this course's own model choice) with a
   system prompt instructing it to answer using only the provided
   excerpts and to cite which document each fact came from, then print
   the answer.

## Acceptance criteria

- `retrieve` for a question clearly about one specific document returns
  that document's chunks ranked first.
- `build_prompt`'s output includes each retrieved chunk's source
  document title, not just its raw text.
- The final printed answer references at least one document by name (a
  real, working citation, using this exercise's own retrieved sources —
  not fabricated).
- Running the script with a question that has **no** relevant document at
  all (a `DOCUMENTS`-unrelated topic) either says so honestly (if you
  implement that check) or is at minimum something you can explain after
  running it — this is intentionally left slightly open so you engage
  with Lesson 06's "should you even call the model with irrelevant
  context" discussion yourself.

## Hints

- **Level 1:** This exercise is Lesson 06's pipeline, restated without a
  database — re-read that lesson's full walkthrough before writing code.
- **Level 2:** Your "vector store" is genuinely just a Python list of
  tuples — resist the urge to build anything more elaborate than that for
  this exercise.
- **Level 3:** For `generate_answer`, `client.messages.stream(...)` with
  `model="claude-haiku-4-5"`, a system prompt matching `app/rag.py`'s own
  (Lesson 06), and printing `stream.text_stream` as it arrives is exactly
  the pattern Module 13 already taught and Lesson 06 reused.

## Running it

```bash
python mini_rag.py
```

**Expected output:** for the provided sample question, a printed list of
the top retrieved chunks (with their source titles), the assembled
prompt, and finally Claude's streamed, cited answer.

**Try it yourself:** Add a new, unrelated document to `DOCUMENTS`, ask a
question that should retrieve chunks from *two* different documents, and
check that your citation in the final answer correctly distinguishes
which fact came from which one.
