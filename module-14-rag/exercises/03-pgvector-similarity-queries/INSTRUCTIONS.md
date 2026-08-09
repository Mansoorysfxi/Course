# Exercise 03 — Real pgvector Similarity Queries

**Difficulty:** Guided → independent. Requires the Docker + `pgvector`
setup from Lesson 00 — this is the first exercise in this module that
needs real infrastructure, not just a Python script.

## What you'll build

A standalone script, `pgvector_lab.py`, that connects directly to your
own `pgvector`-enabled Postgres (Lesson 00), creates a small, throwaway
table with a `vector` column, inserts a handful of hand-picked
embeddings, and runs a real `ORDER BY ... <=> ...` cosine-distance query
— the exact mechanism `app/repository.py`'s `find_similar_chunks` uses
for real, at a much smaller, easier-to-reason-about scale.

## Concepts this exercise requires

- What `pgvector` adds to Postgres, and the `<=>` cosine-distance
  operator (Lesson 04).
- Why distance and similarity sort in opposite directions (Lesson 05).
- Basic `psycopg`/raw SQL from Module 06 (this exercise deliberately uses
  raw SQL, not SQLAlchemy's ORM, so the real `pgvector` mechanism is
  fully visible with nothing abstracted away).

## Setup

Make sure Lesson 00's setup is complete — a running, `pgvector`-enabled
Postgres, reachable at the URL you verified there.

```bash
cd module-14-rag/exercises/03-pgvector-similarity-queries/starter
python -m venv venv
source venv/Scripts/activate
pip install psycopg[binary] pgvector
```

## Instructions

1. Open `starter/pgvector_lab.py`. It connects to your local Postgres
   (edit `DATABASE_URL` at the top if your setup differs from Lesson
   00's defaults) and creates a throwaway table, `pgvector_exercise`,
   with a `vector(3)` column — deliberately tiny (3 dimensions, not 384)
   so you can reason about the numbers by hand.
2. Implement `insert_sample_vectors(conn)`: insert the three provided
   sample rows (`SAMPLE_ROWS`) into `pgvector_exercise`.
3. Implement `find_nearest(conn, query_vector, top_k)`: run a real SQL
   query using `ORDER BY embedding <=> %s::vector LIMIT %s` and return
   the `top_k` closest rows' labels and distances.
4. Run the script with the provided query vector and check the ordering
   matches what you'd compute by hand (the docstring gives you the exact
   expected order).

## Acceptance criteria

- `find_nearest` returns rows sorted by *ascending* distance (closest
  first) — not similarity descending; this is the real pgvector
  convention (Lesson 05).
- The closest result to `[1.0, 0.0, 0.0]` is the row labeled `"close"`.
- The script cleans up the throwaway table (`DROP TABLE`) when it's
  done, leaving your database exactly as it was before.

## Hints

- **Level 1:** Re-read Lesson 05's walkthrough of `find_similar_chunks`
  — this exercise's query is the same shape, without the `quest_id`
  filter or the join.
- **Level 2:** `psycopg` with the `pgvector` Python package registers a
  vector type adapter automatically once you call
  `register_vector(conn)` — a Python `list[float]` can then be passed
  directly as a query parameter.
- **Level 3:** The SQL is:
  `SELECT label, embedding <=> %s AS distance FROM pgvector_exercise ORDER BY distance LIMIT %s`

## Running it

```bash
python pgvector_lab.py
```

**Expected output:** three rows, sorted by distance ascending, with the
`"close"` row first and a distance near 0, and the `"far"` row last with
a distance near 2 (a real pgvector cosine distance ranges from 0 to 2 —
Lesson 05's own header note).

**Try it yourself:** Change the query vector to `[0.0, 1.0, 0.0]` and
predict, before running, which sample row will now come first.
