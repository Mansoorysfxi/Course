# Lesson 03 — Embeddings for Search, and the Embedding-Model Decision

**Verified August 9, 2026:** `sentence-transformers` `5.7.0`,
`all-MiniLM-L6-v2` (384 dimensions) — the exact model Module 12, Lesson
04 already verified and live-ran; nothing has changed. Anthropic itself
still offers no embeddings model of its own and officially recommends
Voyage AI as a third-party partner (live search, August 9, 2026). Voyage
AI's current pricing: `voyage-4-lite` at $0.02/million tokens,
`voyage-4` at $0.06/million tokens, `voyage-4-large` at $0.12/million
tokens, with 200 million free tokens included on signup.

## What you'll learn

- How Module 12's "meaning as coordinates" idea gets used specifically
  for *search*, not just visualization.
- The real decision this module makes — local, free embeddings vs. a
  paid embeddings API — with real numbers on both sides.
- How `app/embeddings.py` actually works, including why it deliberately
  delays importing `sentence_transformers` until the first real call.

## Why this matters

Module 12, Lesson 04 taught you that an embedding turns text into a
vector, and that cosine similarity measures how close two vectors are.
This lesson doesn't re-teach either of those — it applies them to a new,
specific job: given a chunk of a note and a player's question, decide
*where those vectors come from* for a real, running backend, which is a
genuinely different question than "how do I compute one embedding in a
script for a demo," and one this module has to actually answer with
working code.

## Prerequisites

- **Module 12, Lesson 04, in full** — embeddings, cosine similarity, and
  the "meaning as coordinates" analogy. This lesson assumes all of that
  and will not re-explain it.
- **Lesson 02** — chunks are what get embedded; this lesson picks up
  exactly where chunking left off.

## The concept, explained simply

Module 12 already showed you *what* an embedding is. This lesson is
about a decision every real application using embeddings has to make:
**who computes them?** There are exactly two shapes of answer:

1. **A model that runs on your own server** — you load it into memory
   once, and every embedding computation happens locally, using your own
   CPU (or GPU), with no network call and no per-use cost beyond the
   compute you already own.
2. **A hosted API you call over the network** — someone else's server
   runs the model; you send text, get back a vector, and pay per token,
   the exact same shape of trade-off as calling Claude itself (Module
   13) instead of running an LLM locally.

This is the exact same "rent someone else's compute vs. run it on your
own machine" trade-off Module 13's own Lesson 00 introduced for large
language models generally — just applied here to the smaller, different
job of producing embeddings specifically.

## The details

### The two real options, with real numbers

**Option A — reuse Module 12's local `sentence-transformers` model
(`all-MiniLM-L6-v2`).** Free, no API key, and — because Module 12 already
verified it works and produces 384-dimensional vectors — zero new
research risk. The real cost is entirely on the *infrastructure* side:
`sentence-transformers` pulls in `torch` as a dependency, meaningfully
growing this backend's install size and Docker image, and loading the
model into memory the first time takes real, noticeable time (Lesson 00
had you observe this directly).

**Option B — a paid embeddings API, e.g. Voyage AI (Anthropic's own
recommended partner for Claude users, since Anthropic itself has no
embeddings model at all — verified live, August 9, 2026).** At
`voyage-4-lite`'s $0.02/million tokens, embedding QuestLog's entire
plausible note volume for a hobby project is genuinely cheap — the real
cost isn't dollars, it's **a second API key and account**, plus
**per-request network latency** on every single embedding call (both
when a note is first chunked, and every time a player asks a question),
where the local model's only latency cost is the one-time model load.

### The decision this module makes, and why

**This module reuses Option A — the local, free
`sentence-transformers` model — for QuestLog's own "chat with your quest
notes" feature.** Three concrete reasons, not just "it's free":

1. **No new API key or account.** This app already requires exactly one
   external credential (`ANTHROPIC_API_KEY`, since Module 13). Adding a
   second key for a genuinely optional convenience (cheap, fast embeddings)
   would add real setup friction — a new signup, a new secret to manage,
   a new failure mode (`/health`-style "what if this key is missing"
   handling to write) — for a job the free option already does
   perfectly well at QuestLog's actual scale (a hobbyist's own quest
   notes, not a production document-search product serving millions of
   queries).
2. **Zero new ongoing cost**, on top of the small, already-accepted
   Anthropic API cost from Module 13 — consistent with this course's
   running "small, real, well-justified" cost discipline (Module 10's
   Redis choice, Module 13's model choice).
3. **The one real cost (a heavier backend, slower first-embedding
   latency) is manageable and honestly small at this app's scale.**
   `app/embeddings.py`'s lazy-loading design (below) pays that cost at
   most once per running server process — not once per request, and not
   during every `uvicorn --reload` restart's *startup* (only its first
   real embedding call) — which matters a great deal for a learner
   restarting this backend constantly while working through exercises.

**When would Option B have been the better call?** If this were a
production system embedding a genuinely large, constantly growing corpus
across many users, at a scale where server memory/CPU spent on a local
model competed with serving real traffic, or where you wanted embedding
computation to happen somewhere other than your own application server
entirely (e.g., during an async ingestion pipeline with no local compute
available at all) — a paid API's "pay per call, no local compute" shape
would look more attractive. Stating this honestly matters: this isn't
"local is always right," it's "local is right for *this* app, at *this*
scale, for *these* reasons."

### Reading `app/embeddings.py`

```python
EMBEDDING_DIMENSIONS = 384
_MODEL_NAME = "all-MiniLM-L6-v2"
_model = None

def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(_MODEL_NAME)
    return _model
```

Notice the `import sentence_transformers` line lives *inside*
`_get_model()`, not at the top of the file. This is a deliberate lazy
import, for two real reasons:

1. **Startup speed.** A plain `import app.embeddings` (which happens
   just by starting this backend at all, since `app/routers/notes.py`
   imports from it) never triggers loading `torch` or the model itself —
   only the first actual embedding computation does. A learner restarting
   this backend to test an unrelated change never pays that cost
   unnecessarily.
2. **Test suite honesty.** Because the real import only happens inside
   `_get_model()`, and every test in this backend's own suite
   monkeypatches `embed_text`/`embed_texts` directly (never calling the
   real function), `sentence_transformers`/`torch` never has to be
   installed at all for `pytest` to pass. Lesson 08 covers this in full.

`embed_texts` (plural, batched) and `embed_text` (singular) are the only
two functions the rest of this app ever calls:

```python
def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = _get_model()
    embeddings = model.encode(texts)
    return [row.tolist() for row in embeddings]

def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
```

`model.encode(texts)` returns a NumPy array (one row per input string) —
`.tolist()` converts it to plain Python `list[float]`, because neither
`pgvector` nor a plain JSON column (Lesson 04) has any idea what a NumPy
array is; both only understand plain, JSON-serializable Python values.
`embed_text` is a thin wrapper around `embed_texts` — there is exactly
one real code path that ever talks to the model, whether embedding one
question or a whole note's worth of chunks at once.

## Common mistakes & gotchas

- **Embedding queries and documents with two different models.** Cosine
  similarity only means anything if both vectors being compared came
  from the *same* model's coordinate space — mixing models here would be
  like comparing GPS coordinates against a fictional map's coordinates:
  the numbers exist, but they don't relate to each other at all.
  QuestLog's own code avoids this by construction: `embed_text` and
  `embed_texts` are the only two functions anything calls, both funneling
  through the same `_get_model()`.
- **Assuming a heavier dependency at import time.** Importing
  `sentence_transformers` at the *top* of `app/embeddings.py` (instead of
  inside `_get_model()`) would make every test that imports this module
  at all pay the full `torch` import cost, and would force
  `sentence-transformers` to be installed just to run `pytest` — exactly
  what Lesson 08's testing strategy avoids.
- **Forgetting the model must load before it's fast** — the first
  embedding call in a freshly started process is genuinely slow (Lesson
  00 had you observe this); this is not a sign anything is broken.
- **Assuming "free" means "no trade-off."** This lesson's whole point is
  that the local model's real cost is infrastructure weight and latency,
  not dollars — a real trade-off, evaluated honestly, not a free lunch.

## How this connects

Embeddings are how Lesson 02's chunks, and a player's question, both
become vectors that can be compared. Lesson 04 covers *where* those
vectors get stored and indexed (`pgvector`); Lesson 05 covers the actual
similarity query. Nothing about *how* an embedding is computed changes
between those two lessons — this lesson's decision is now simply a fact
the rest of the pipeline builds on.

## Quick self-check

1. What are the two real "who computes the embedding" options this
   lesson names, and which does QuestLog pick?
2. Name the three concrete reasons this module gives for its choice —
   not just "it's free."
3. What real cost does the local model impose, and how does
   `app/embeddings.py`'s lazy-loading design manage it?
4. Why must a query and the documents it's compared against always come
   from the *same* embedding model?
5. Under what circumstances would this lesson's own reasoning point
   toward the paid-API alternative instead?
