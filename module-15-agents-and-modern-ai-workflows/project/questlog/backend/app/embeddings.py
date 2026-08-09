"""Turns text into embedding vectors -- NEW in Module 14. See
lessons/03-embeddings-for-search.md for what an embedding actually is
(this file assumes Module 12, Lesson 04's "meaning as coordinates" vocabulary
and does not re-teach it) and lessons/00-setup.md for the full "why a local
model, not a paid embeddings API" reasoning this module settled on.

**The decision, short version** (full reasoning, with real 2026-08-09
pricing/versions, lives in lessons/00-setup.md and lessons/03): this app
uses the exact same free, local `sentence-transformers` model
(`all-MiniLM-L6-v2`, 384 dimensions) Module 12 already taught and
live-verified, rather than a paid embeddings API (Anthropic itself has no
embeddings model and officially recommends Voyage AI as a third-party
partner -- a real, credible, cheap alternative this course chose not to
take, mainly to avoid requiring a *second* API key/account beyond the
`ANTHROPIC_API_KEY` already required since Module 13).

**The real, accepted cost of that choice, and how this file manages it:**
`sentence-transformers` pulls in `torch` as a transitive dependency -- a
large package, and a real amount of time to load a model from disk into
memory the first time it's used. This file's answer is a **lazy-loaded
module-level singleton**: `sentence_transformers` is imported, and the
model is constructed, only *inside* `_get_model()`, the first time any
embedding is actually requested -- never at process startup, and never at
plain `import app.embeddings` time. Two real, deliberate reasons:

1. **A real trade-off, stated honestly.** The very first embedding call
   this process ever makes pays the full model-load cost (on the order of
   seconds, not milliseconds); every call after that, for the rest of the
   process's life, reuses the already-loaded model and is fast. A busier,
   more "always warm" production system might instead load the model
   eagerly during startup (trading a slower boot for a fast first request)
   -- this course picks lazy loading because a learner restarting this
   backend constantly while working through exercises benefits far more
   from a fast `uvicorn --reload` restart than from a fast *first*
   embedding call.
2. **It's what makes this module's own test suite honest.** Because the
   real import of `sentence_transformers` only happens inside `_get_model()`,
   a test that never calls a real embedding function (every test in this
   backend's own suite -- see tests/test_notes.py and
   tests/test_rag.py, both of which monkeypatch `embed_text`/`embed_texts`
   directly) never triggers that import at all. That is what lets this
   whole test suite pass without `sentence-transformers`/`torch` installed
   in a test environment -- see lessons/00-setup.md's own testing note, and
   `requirements.txt`'s comment on this same trade-off.
"""

EMBEDDING_DIMENSIONS = 384
_MODEL_NAME = "all-MiniLM-L6-v2"

# The module-level "cache slot" the singleton lives in once loaded. `None`
# means "not loaded yet" -- exactly the same sentinel-based lazy-init shape
# as any "compute once, reuse forever" pattern, just without `@lru_cache`
# (which would work here too, but a plain module-level variable is more
# obviously "this is a slow, one-time load," which is the whole point being
# taught in this file).
_model = None


def _get_model():
    """Loads the real model on first call, from disk into memory, and
    caches it in `_model` for every later call in this same process. The
    `import sentence_transformers` line below is the entire reason this
    function -- not the top of this file -- is where that import lives;
    see this file's own module docstring, point 2, for why that matters."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embeds a batch of strings in one call -- used by
    app/routers/notes.py when a new note is chunked, so every chunk from
    one note is embedded together in a single, more efficient call to the
    model, rather than one call per chunk. Returns one 384-number vector
    (a plain Python `list[float]`, not a numpy array -- see this function's
    own `.tolist()` call below) per input string, in the same order."""
    if not texts:
        return []
    model = _get_model()
    # `SentenceTransformer.encode` returns a numpy array by default (one
    # row per input string) -- `.tolist()` converts it to plain Python
    # lists of floats, which is what `NoteChunk.embedding`
    # (app/db_models.py, a `Vector(384)` / `JSON` column) actually stores;
    # neither Postgres's `pgvector` extension nor a plain SQLite `JSON`
    # column has any idea what a numpy array is.
    embeddings = model.encode(texts)
    return [row.tolist() for row in embeddings]


def embed_text(text: str) -> list[float]:
    """Embeds a single string -- used by app/routers/notes.py's `ask`
    route to embed the player's own question before searching for similar
    chunks. A thin convenience wrapper around `embed_texts` (never its own
    separate model call) so there is exactly one real code path that talks
    to the model at all."""
    return embed_texts([text])[0]
