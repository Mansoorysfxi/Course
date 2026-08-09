"""QuestLog's second real AI feature -- "chat with your quest notes," NEW
in Module 14. See lessons/06-building-a-rag-pipeline-by-hand.md for the
full, line-by-line walkthrough; this docstring is the short version.

**Deliberately simpler than app/ai_assistant.py on the "talking to Claude"
side, on purpose.** Module 13 already taught tool use and structured
output (`output_config.format`) minutely, end to end, with a real feature.
Repeating either technique here would be repetition, not new teaching --
so this file does neither. The genuinely new material in this module is
**retrieval**: chunking (app/chunking.py), embeddings (app/embeddings.py),
and a real `pgvector` similarity query (app/repository.py's
`find_similar_chunks`). Once the right chunks are in hand, this file
generates the actual answer with the *simplest* technique Module 13 taught
-- plain streamed text, the same `client.messages.stream(...)` /
`stream.text_stream` mechanics Lesson 02 of that module covered first,
before tool use or structured output ever entered the picture. Keeping the
generation step this simple is what keeps retrieval the star of this
module, exactly as the master plan intends.

**How citations work here, and why this is more honest than asking Claude
to produce them.** This file does NOT ask Claude to emit a structured
citations object as part of its answer (the way app/ai_assistant.py asks
for a structured `sub_quests` list) -- because Claude *inventing* a
citation is a real, documented failure mode of naive RAG (a model can
confidently attribute a claim to a source that didn't say it). Instead,
citations here are things this file already knows for certain, before
Claude is ever called at all: exactly which chunks `find_similar_chunks`
retrieved, and from which note. `stream_note_answer` below sends those as
a `sources` event *before* the first token of Claude's answer even starts
generating -- a deterministic, code-produced fact, not a model claim --
and the system prompt below simply instructs Claude to reference those
same notes by title in its prose (e.g. "According to your note 'Boss Fight
Prep': ..."), which a human reader can then cross-check against the
`sources` list that already arrived. See lessons/06's "citations you can
trust vs. citations you have to hope for" box for the full discussion.
"""

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

import anthropic
import numpy as np

from app.config import settings

# How many chunks to hand Claude as context for one question. Small and
# fixed, on purpose, for this course's own scope -- see
# lessons/05-similarity-search-in-practice.md's "why top_k = 3, and what a
# real system would do differently" box for the honest discussion of what
# a production system might add here (a similarity-score cutoff, re-ranking,
# a dynamically-sized k) that this module deliberately keeps out of scope.
TOP_K_CHUNKS = 3

SYSTEM_PROMPT = (
    "You are QuestLog's notes assistant. You will be given one or more "
    "excerpts from the player's own quest notes, each labeled with the "
    "note's title, followed by a question. Answer the question using ONLY "
    "the information in the provided excerpts -- never from your own "
    "general knowledge, and never by guessing. When you use an excerpt, "
    "say which note it came from by title (for example: According to your "
    "note 'Boss Fight Prep': ...). If the excerpts do not contain enough "
    "information to answer the question, say so plainly instead of "
    "guessing."
)


@dataclass
class RetrievedChunk:
    """One chunk, already retrieved and ranked, on its way into a prompt.
    Deliberately a plain dataclass, not an ORM row or a Pydantic model --
    this is the one shape both `app/repository.py`'s real pgvector query
    AND `rank_by_cosine_similarity` below (the plain-Python stand-in used
    in tests and in this lesson's own worked example) return, so the rest
    of this file (`build_answer_prompt`, `stream_note_answer`) never needs
    to know or care which of the two produced it."""

    note_id: str
    note_title: str
    chunk_index: int
    content: str
    embedding: list[float]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """The exact same formula Module 12, Lesson 04 introduced --
    `np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))` -- reused here
    verbatim, not reinvented. Kept as its own tiny function (rather than
    inlined into `rank_by_cosine_similarity` below) so lessons/05 and
    tests/test_rag.py can both call it directly, exactly the way Module 12
    Lesson 04's own worked example did."""
    vector_a = np.array(a)
    vector_b = np.array(b)
    return float(np.dot(vector_a, vector_b) / (np.linalg.norm(vector_a) * np.linalg.norm(vector_b)))


def rank_by_cosine_similarity(
    chunks: list[RetrievedChunk], query_embedding: list[float], top_k: int = TOP_K_CHUNKS
) -> list[RetrievedChunk]:
    """A plain-Python, in-memory re-implementation of exactly what
    `app/repository.py`'s real `find_similar_chunks` asks Postgres/pgvector
    to do with `ORDER BY embedding.cosine_distance(:query) LIMIT :top_k`.
    This function exists for two real reasons, not one:

    1. **Teaching.** lessons/05-similarity-search-in-practice.md and
       lessons/06-building-a-rag-pipeline-by-hand.md both use this function
       to show, in code you can step through in a debugger, exactly what
       the database's own `<=>` operator is doing under the hood -- the
       master plan's own "build it by hand first so nothing is magic"
       instruction, applied to the ranking step specifically.
    2. **Testing.** `NoteChunk.embedding` (app/db_models.py) compiles to a
       plain `JSON` column on SQLite (this backend's own test database --
       see that file's own docstring), which has no cosine-distance
       operator at all. This function is what tests/test_rag.py uses to
       verify ranking *logic* is correct without ever needing a real
       Postgres+pgvector instance -- see
       tests/test_notes_pgvector_integration.py's own module docstring for
       the one thing this function does NOT (and honestly cannot) stand in
       for.

    Note on distance vs. similarity: pgvector's `cosine_distance` returns a
    *distance* (0 = identical, 2 = opposite; smaller is better, so
    Postgres sorts `ORDER BY ... ASC`), while this function returns a
    *similarity* (1 = identical, -1 = opposite; larger is better, so this
    function sorts descending). The two are simply related --
    `distance = 1 - similarity` for cosine specifically -- but this
    function deliberately keeps `cosine_similarity`'s own "bigger is
    better" convention from Module 12, Lesson 04, rather than reimplementing
    pgvector's own "smaller is better" convention, so anyone reading this
    file after that lesson recognizes the same function immediately.
    """
    scored = [(cosine_similarity(chunk.embedding, query_embedding), chunk) for chunk in chunks]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]


def build_answer_prompt(question: str, retrieved_chunks: list[RetrievedChunk]) -> str:
    """Assembles the retrieved chunks and the player's question into the
    single user-turn prompt `stream_note_answer` sends to Claude. Each
    excerpt is labeled with its note's title (never its raw database id --
    a title is what SYSTEM_PROMPT actually asks Claude to cite, and what a
    human reading the answer can recognize) so Claude has everything it
    needs to follow SYSTEM_PROMPT's citation instruction without this file
    doing any further prompt engineering."""
    excerpts = "\n\n".join(
        f'Excerpt from note "{chunk.note_title}":\n{chunk.content}' for chunk in retrieved_chunks
    )
    return f"{excerpts}\n\nQuestion: {question}"


async def stream_note_answer(
    client: anthropic.AsyncAnthropic,
    question: str,
    retrieved_chunks: list[RetrievedChunk],
) -> AsyncGenerator[dict[str, Any], None]:
    """Yields plain dicts, each shaped `{"event": <name>, "data": <dict>}`
    -- the exact same "yield dicts, not SSE text" contract
    app/ai_assistant.py's `stream_quest_breakdown` already established, for
    the same reason: this function stays independently testable
    (tests/test_rag.py asserts against these dicts directly), and
    app/routers/notes.py owns the one, single place that knows what SSE's
    wire format looks like.

    Event names:

    - `sources` -- sent immediately, before any call to Claude at all
      (see this module's own docstring for why these are trustworthy in a
      way a model-generated citation wouldn't be).
      `data: {"sources": [{"note_id", "note_title", "chunk_index", "excerpt"}, ...]}`.
    - `token` -- one more piece of Claude's raw answer text, as it's
      generated. `data: {"text": "..."}`.
    - `result` -- the final, complete answer text, once the stream ends.
      `data: {"answer": "..."}`. Terminal.
    - `error` -- no chunks were retrieved at all (this quest has no notes
      yet -- Claude is never even called in this case), or Claude
      refused, or ran out of `max_tokens` mid-answer. `data: {"message": "..."}`.
      Terminal.
    """
    if not retrieved_chunks:
        yield {
            "event": "error",
            "data": {"message": "This quest has no notes yet. Add one before asking a question."},
        }
        return

    yield {
        "event": "sources",
        "data": {
            "sources": [
                {
                    "note_id": chunk.note_id,
                    "note_title": chunk.note_title,
                    "chunk_index": chunk.chunk_index,
                    "excerpt": chunk.content[:150],
                }
                for chunk in retrieved_chunks
            ]
        },
    }

    prompt = build_answer_prompt(question, retrieved_chunks)
    collected_text = ""
    async with client.messages.stream(
        model=settings.ai_model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        async for text in stream.text_stream:
            collected_text += text
            yield {"event": "token", "data": {"text": text}}
        final_message = await stream.get_final_message()

    if final_message.stop_reason == "refusal":
        # Same honest handling app/ai_assistant.py already established for
        # this exact stop_reason -- a refusal is a normal, successful HTTP
        # response whose stop_reason says "no," not an exception.
        yield {
            "event": "error",
            "data": {"message": "Claude declined to answer this question."},
        }
        return

    if final_message.stop_reason == "max_tokens":
        yield {
            "event": "error",
            "data": {"message": "The answer was cut off before it finished. Try again."},
        }
        return

    yield {"event": "result", "data": {"answer": collected_text}}
