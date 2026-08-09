# Lesson 02 — Chunking Strategies

**Verified August 9, 2026, via live web research:** the benchmark-cited
general-purpose default for RAG chunking is roughly 400-512 tokens per
chunk with 10-20% overlap (e.g. 50-100 tokens of overlap on a 500-token
chunk), based on a 2026 multi-strategy benchmark across real documents.
Smaller chunks (128-256 tokens) tend to suit narrow factual questions;
larger chunks (512-1024 tokens) suit broader, more analytical questions.
This lesson explains why QuestLog's own feature intentionally uses
smaller defaults than that benchmark's numbers, and why that's a
reasoned choice for this app's actual data, not a shortcut.

## What you'll learn

- What "chunking" means and why retrieval needs it at all.
- The two chunking strategies this lesson compares: fixed-size and
  paragraph-based, plus what "overlap" adds and costs.
- Current, real guidance on chunk size, and why QuestLog's own choice
  differs from the general benchmark default, for a specific, stated
  reason.
- How to read `app/chunking.py`'s real, tested implementation line by
  line.

## Why this matters

Before anything can be embedded (Lesson 03) or searched (Lesson 05), a
raw note has to be split into pieces. Get this step wrong and everything
downstream suffers no matter how good your embedding model or your
search query is: chunks that are too large dilute what an embedding can
represent (one vector now has to summarize several unrelated ideas at
once); chunks that are too small lose context (a sentence like "bring it
with you" means nothing once separated from whatever "it" refers to).
Chunking is the unglamorous first step that determines how good every
later step can possibly be.

## Prerequisites

- **Lesson 01** — why retrieval is needed at all.
- **Module 01's string/list handling** — this lesson's code is plain
  Python string manipulation; nothing new syntactically.

## The concept, explained simply

Think of a huge open-world game level. You don't load the entire level
into memory at once — you split it into streaming cells, and load only
the cells near the player. Two things matter about how you draw those
cell boundaries: cells that are too large defeat the point (you're
loading huge unnecessary chunks of the world again); cells that are too
small mean the player constantly crosses boundaries, and anything that
should read as one continuous space (a bridge, a hallway) gets awkwardly
split across two cells with a visible seam.

**Chunking** a document is exactly this problem, applied to text instead
of 3D space: split a note into pieces small enough that an embedding
model and a retrieval query can work with them individually, without
splitting so aggressively that you cut a coherent thought in half.

## The details

### Two real strategies

**1. Fixed-size chunking.** Split the text every *N* characters (or
tokens), regardless of where sentences or paragraphs actually end.
Simple, predictable, and guarantees every chunk is roughly the same
size — but it will sometimes cut a sentence, or even a word, right down
the middle, exactly like a level boundary cutting a room in half.

**2. Paragraph-based (or "semantic") chunking.** Split at natural
boundaries the author already created — blank lines between paragraphs,
in QuestLog's case. This respects the author's own structure (a
paragraph is usually one coherent thought), at the cost of variable chunk
sizes: one paragraph might be a single short sentence, another might run
long.

**QuestLog's own choice, and why:** `app/chunking.py`'s `chunk_text`
function uses **paragraph-first chunking, with a fixed-size-with-overlap
fallback** only for the unusual case of one paragraph that's still too
long on its own. This matches how a player actually writes a note — in
QuestLog's own scope decision (a few sentences to a few short
paragraphs, not a full manuscript), paragraph boundaries are almost
always both present and meaningful, so respecting them costs nothing and
preserves coherence. The fixed-size fallback exists purely as a safety
net for the rare case (one long paragraph, no blank lines at all) where
paragraph-splitting alone wouldn't produce anything smaller.

### Why QuestLog's own numbers are smaller than the general benchmark

This lesson's header cites 400-512 tokens with 10-20% overlap as a
general-purpose RAG benchmark default. `app/chunking.py` instead defaults
to `max_chunk_chars=800, overlap_chars=150` — at the commonly-cited "~4
characters per token" rule of thumb, that's roughly 200 tokens per chunk
with about 37 tokens of overlap, meaningfully smaller than the benchmark
number. This is a **deliberate, scoped decision, not an oversight**: that
benchmark was measured across long, dense documents (academic papers) where
512-token chunks capture a complete, meaningful unit of argument. QuestLog's
own notes are, by this module's own explicit scope decision (Lesson 00,
`project/BRIEF.md`), short — a few sentences to a few short paragraphs
about one quest. A 512-token chunk on data this short would often be
"the entire note," defeating chunking's whole purpose of letting
retrieval narrow in on the *specific* part of a note that's relevant.
Smaller chunks fit this app's actual data better than blindly copying a
number tuned for a different kind of document — the same "understand the
reasoning, don't just copy the config" discipline this course has applied
to Redis's TTL (Module 10) and QuestLog's own AI model choice (Module
13).

### Characters vs. tokens

`app/chunking.py` measures chunk size in **characters**, not tokens — a
deliberate simplification. This app already has three different
tokenizer-shaped concerns in play (`tiktoken` from Module 12, measuring
OpenAI-family tokens; Claude's own, different tokenizer; and the
embedding model's own, yet different tokenizer) — picking any one of them
just to measure chunk *size approximately* would add a real dependency
for a benefit this module's own scope doesn't need. Characters are close
enough for "roughly this many words," which is all chunk sizing actually
needs to get right here.

### Reading `chunk_text` itself

Open `module-14-rag/project/questlog/backend/app/chunking.py`. The core
function:

```python
def chunk_text(text: str, max_chunk_chars: int = 800, overlap_chars: int = 150) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return []
    # ... splits on blank lines into paragraphs ...
    # ... any paragraph over max_chunk_chars falls back to _split_with_overlap ...
```

Walk through what happens for a two-paragraph note:

1. `text.strip()` removes leading/trailing whitespace — an empty or
   whitespace-only note correctly produces zero chunks (there's nothing
   to search over).
2. The text is split into paragraphs by scanning line by line and
   grouping non-blank lines together, breaking the group whenever a
   blank line appears. This handles `\r\n` (Windows line endings) and
   more than one blank line between paragraphs correctly, because it
   groups by "any run of non-blank lines," not by matching the literal
   two-character string `"\n\n"`.
3. Each paragraph short enough on its own becomes exactly one chunk.
4. Any paragraph over `max_chunk_chars` — rare, given this app's own
   scope — falls through to `_split_with_overlap`, a plain sliding-window
   split: take `max_chunk_chars` characters, then start the next chunk
   `overlap_chars` characters *before* the previous one ended, so a
   sentence that would otherwise land exactly on a cut point still
   appears whole in at least one chunk.

### Why overlap at all?

Without overlap, a sentence that happens to straddle a cut boundary gets
split between two chunks, and neither chunk alone contains the complete
thought. Overlap means the last `overlap_chars` characters of one chunk
also appear as the first `overlap_chars` characters of the next — a
deliberate, small amount of duplication, in exchange for guaranteeing
no sentence-sized idea near a boundary is ever *only* half-visible in
every chunk that contains it. This is a real, still-actively-debated
trade-off in the broader field (more overlap costs more storage and more
near-duplicate chunks retrieval might return; less overlap risks
information loss at boundaries) — this course settles on a modest,
stated default rather than presenting either extreme as obviously
correct.

## Common mistakes & gotchas

- **Chunking on a fixed character count with zero regard for structure**,
  even when better boundaries (blank lines, sentence ends) are available
  in the text — this reliably produces chunks that start or end
  mid-sentence, which both confuses an embedding model and makes an
  eventual citation ("According to your note...") point at an
  awkward-looking fragment.
- **Copying a benchmark's chunk size number without checking whether it
  fits your own data** — this lesson's own "why QuestLog's numbers are
  smaller" section is the worked example of avoiding exactly this
  mistake.
- **Setting `overlap_chars >= max_chunk_chars`.** `app/chunking.py`'s
  `_split_with_overlap` explicitly raises a `ValueError` for this,
  because it would mean each new window starts at or before where the
  previous one started — a loop that never advances, and would hang a
  real HTTP request forever if it weren't guarded.
- **Forgetting that `chunk_text` can legitimately return an empty
  list** — only for empty/whitespace-only input, which QuestLog's own
  `QuestNoteCreate` Pydantic model (`Field(min_length=1)`) already
  rejects before this function is ever called with real data — but worth
  knowing if you reuse this function somewhere that input isn't already
  validated.

## How this connects

Chunking is step one of the pipeline Lesson 06 assembles end to end.
Every chunk `chunk_text` produces here is exactly what Lesson 03's
embedding step turns into a vector, and exactly what Lesson 05's
similarity search retrieves and Lesson 06's citations point back to by
title and index. Get this step right, and every later step has good raw
material to work with.

## Quick self-check

1. What's the difference between fixed-size chunking and paragraph-based
   chunking, and which does QuestLog use as its primary strategy?
2. Why does QuestLog's `chunk_text` use characters, not tokens, to
   measure chunk size?
3. Why does this module's own chunk-size default (roughly 200 tokens)
   differ from the general 400-512 token benchmark this lesson cites —
   and is that a mistake or a reasoned choice?
4. What problem does overlap solve, and what does it cost?
5. What does `chunk_text("")` return, and why is that the correct
   behavior rather than an error?
