# Exercise 02 — Embeddings for Search

**Difficulty:** Guided. Builds directly on Module 12, Exercise 02
(embedding visualization) and this module's Lesson 03.

## What you'll build

A standalone script, `semantic_search.py`, that embeds a small collection
of quest-note sentences using the exact same free, local
`sentence-transformers` model this course already verified
(`all-MiniLM-L6-v2`), then implements a `search(query, top_k)` function
that returns the `top_k` most similar sentences to a query, ranked by
cosine similarity.

## Concepts this exercise requires

- What an embedding is and what cosine similarity measures (Module 12,
  Lesson 04 — **not re-taught here**).
- How `sentence-transformers`'s `SentenceTransformer.encode()` returns a
  batch of vectors (Module 12, Exercise 02, and this module's Lesson 03).
- Ranking multiple items by a similarity score (this module's Lesson 05
  previews this same idea for the real pgvector query — this exercise is
  its plain-Python, in-memory counterpart).

## Setup

```bash
cd module-14-rag/exercises/02-embeddings-and-similarity-search/starter
python -m venv venv
source venv/Scripts/activate
pip install sentence-transformers numpy
```

**This needs no Anthropic API key** — everything in this exercise is
free and runs entirely locally, exactly like Module 12's own embeddings
exercise.

## Instructions

1. Open `starter/semantic_search.py`. `CORPUS` is a small, provided list
   of quest-note-style sentences.
2. Implement `embed_corpus(corpus)`: call `model.encode(corpus)` once, and
   return the result (a NumPy array, one row per sentence).
3. Implement `cosine_similarity(a, b)`: the same formula Module 12,
   Lesson 04 introduced.
4. Implement `search(query, corpus, corpus_embeddings, top_k)`: embed the
   query, compute its cosine similarity against every row of
   `corpus_embeddings`, and return the `top_k` sentences from `corpus`
   with the highest similarity, most similar first.
5. Run the script with the three provided sample queries and check that
   the top result for each one is intuitively the most relevant sentence
   in `CORPUS`.

## Acceptance criteria

- `search("What should I bring to fight the dragon?", ..., top_k=1)`
  returns the sentence about fire-resistant armor and a silver sword as
  its top result.
- `search` never returns more than `top_k` results, even if `top_k` is
  larger than the corpus.
- Results are sorted with the highest similarity first.

## Hints

- **Level 1:** This is the same `rank_by_cosine_similarity` idea Lesson
  06 uses for real (`app/rag.py`) — read that function's docstring for
  the shape of the solution, without copying the QuestLog-specific
  parts (note titles, chunk indices) this exercise doesn't need.
- **Level 2:** `model.encode()` accepts a list of strings and returns one
  row per string — you only need to call it once for the whole corpus,
  and once per query.
- **Level 3:** Pair each corpus sentence with its similarity score using
  `zip(corpus, scores)`, then `sorted(..., key=lambda pair: pair[1],
  reverse=True)[:top_k]`.

## Running it

```bash
python semantic_search.py
```

**Expected output:** for each sample query, the top-1 or top-2 most
similar sentences from `CORPUS`, printed with their similarity scores.
The exact numeric scores will vary slightly by `sentence-transformers`
version, but the *ranking* (which sentence comes first) should match
this exercise's acceptance criteria.

**Try it yourself:** Add a new sentence to `CORPUS` that's completely
unrelated to dragons or quests (e.g. "The weather today is sunny"), run
a dragon-related query again, and confirm your unrelated sentence scores
lowest.
