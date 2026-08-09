# Exercise 01 — Chunking Strategies

**Difficulty:** Easy. If you've read Lesson 02 carefully, this exercise
should be almost impossible to fail.

## What you'll build

A standalone Python script, `chunking_lab.py`, implementing **two**
chunking strategies from scratch — fixed-size and paragraph-based — and
a small comparison that shows, on the same sample text, how differently
they cut it up.

## Concepts this exercise requires (all taught in Lesson 02)

- What chunking is and why it's needed before embedding.
- Fixed-size chunking vs. paragraph-based chunking.
- What overlap does and why `overlap_chars` must be smaller than
  `max_chunk_chars`.

## Instructions

1. Open `starter/chunking_lab.py`. It has two function stubs:
   `fixed_size_chunks(text, max_chunk_chars, overlap_chars)` and
   `paragraph_chunks(text, max_chunk_chars)`.
2. Implement `fixed_size_chunks`: split `text` into pieces of at most
   `max_chunk_chars` characters, with each chunk after the first starting
   `overlap_chars` characters before the previous one ended. (This is the
   same algorithm as `app/chunking.py`'s `_split_with_overlap` — Lesson
   02 walks through it in full; don't just copy it without understanding
   each line.)
3. Implement `paragraph_chunks`: split `text` on blank lines (one or more
   consecutive empty lines) into paragraphs, and return each non-empty
   paragraph as one chunk. Don't worry about the "overly long single
   paragraph" fallback for this exercise — that's `app/chunking.py`'s own
   extra complexity, not required here.
4. Run the script. It runs both strategies against the same provided
   sample quest note and prints both results side by side.
5. Answer, in a comment at the bottom of your file: for the *specific*
   sample text provided, which strategy produces more sensible chunks,
   and why?

## Acceptance criteria

- `fixed_size_chunks` never returns a chunk longer than `max_chunk_chars`.
- `fixed_size_chunks` raises `ValueError` if `overlap_chars >= max_chunk_chars`.
- `paragraph_chunks` correctly splits the sample text (three paragraphs)
  into exactly three chunks.
- Both functions return an empty list for empty or whitespace-only input.
- Your written answer (Step 5) references something specific about the
  sample text, not a generic statement.

## Hints

- **Level 1:** Re-read Lesson 02's walkthrough of `chunk_text` and
  `_split_with_overlap` before writing any code — this exercise is
  deliberately close to that real implementation.
- **Level 2:** For `paragraph_chunks`, `text.split("\n\n")` is a
  reasonable starting point for this exercise's scope (the real
  `app/chunking.py` handles more edge cases — multiple blank lines,
  Windows line endings — but that's not required here).
- **Level 3:** For `fixed_size_chunks`, track a `start` index, slice
  `text[start:start+max_chunk_chars]`, then advance `start` by
  `max_chunk_chars - overlap_chars` each time, stopping once
  `start >= len(text)`.

## Running it

```bash
cd module-14-rag/exercises/01-chunking-strategies/starter
python chunking_lab.py
```

**Expected output shape:** two labeled lists of chunks, printed to the
console, followed by a chunk count for each strategy.
