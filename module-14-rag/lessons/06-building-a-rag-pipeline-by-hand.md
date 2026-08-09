# Lesson 06 — Building a RAG Pipeline by Hand

## What you'll learn

- How chunking (Lesson 02), embeddings (Lesson 03), and similarity search
  (Lesson 05) all connect into one complete, working pipeline.
- How `app/rag.py` assembles retrieved chunks into a prompt, and why it
  deliberately uses the *simplest* Claude-calling technique Module 13
  taught, not tool use or structured output.
- Why citations in this app are a fact the code already knows, not
  something asked of the model — and why that distinction matters.

## Why this matters

Every earlier lesson in this module built one piece. This is where the
pieces become an actual feature: a player asks a question, and gets back
a real, streamed, grounded, cited answer. The master plan is explicit
that this pipeline should be built by hand first, with no framework —
this lesson is that "by hand" walkthrough, end to end, so nothing about
Lesson 07's framework discussion is ever a black box.

## Prerequisites

- **Lessons 02, 03, 05** — chunking, embeddings, and the similarity
  query this pipeline strings together.
- **Module 13, Lessons 01-02** — calling the Anthropic API and streaming
  a response; this lesson reuses that mechanism directly.

## The concept, explained simply

Recall Lesson 01's NPC-with-a-lookup analogy. This lesson is that NPC's
actual internal process, spelled out as real steps: the player asks a
question → the NPC looks up the relevant journal pages (retrieval) →
the NPC reads those specific pages (augmenting the prompt) → the NPC
answers, out loud, citing which page it read (generation, with
citations). Nothing about this process is magic — it's five concrete,
readable steps, and this lesson traces every one.

## The details

### The full pipeline, step by step

1. **Chunk** the note's content (`app/chunking.py`, Lesson 02).
2. **Embed** every chunk (`app/embeddings.py`, Lesson 03) — this happens
   once, when a note is created, not on every question.
3. **Store** the note and its chunks (`app/repository.py`'s
   `create_note_with_chunks`) — a real Postgres write, via `pgvector`
   (Lesson 04).
4. **Retrieve**: embed the player's *question* (one call to `embed_text`,
   Lesson 03), then run `find_similar_chunks` (Lesson 05) to get the
   `top_k` most relevant chunks for that specific quest.
5. **Augment + Generate**: assemble those chunks into a prompt, and
   stream Claude's answer, citing which note each fact came from — this
   lesson's own subject, in `app/rag.py`.

Steps 1-3 happen in `app/routers/notes.py`'s `create_note` route, once,
when a note is added. Steps 4-5 happen in `ask_question`, once per
question. This split matters: embedding and storing a note is comparably
expensive and should happen rarely; retrieval and generation happen on
every single question, so they need to be fast.

### Why the generation step is deliberately simple

`app/rag.py`'s own module docstring says this directly: Module 13 already
taught tool use and structured output (`output_config.format`)
minutely, with a real feature. Repeating either technique here would be
repetition, not new teaching. This module's genuinely new material is
**retrieval** — so the generation step uses the *simplest* Claude-calling
shape Module 13 taught: plain streamed text, via
`client.messages.stream(...)` and `stream.text_stream`, with no tools and
no schema. Keeping generation this simple is what keeps retrieval the
star of this lesson, on purpose.

### Assembling the prompt

```python
def build_answer_prompt(question: str, retrieved_chunks: list[RetrievedChunk]) -> str:
    excerpts = "\n\n".join(
        f'Excerpt from note "{chunk.note_title}":\n{chunk.content}' for chunk in retrieved_chunks
    )
    return f"{excerpts}\n\nQuestion: {question}"
```

Each retrieved chunk is labeled with its **note's title** — never its
raw database id — because a title is both what the system prompt asks
Claude to cite, and what a human reading the answer can actually
recognize. This is the entire "augmentation" step: the player's raw
question becomes a much richer prompt, with real, relevant context
already attached, before Claude ever sees it.

### Citations you can trust vs. citations you have to hope for

This is the most important design decision in this lesson, stated
explicitly in `app/rag.py`'s own docstring: **this file does not ask
Claude to produce a structured citations object as part of its answer.**
A model *inventing* a citation — confidently attributing a claim to a
source that didn't actually say it — is a real, documented failure mode
of naive RAG systems. Instead:

```python
yield {
    "event": "sources",
    "data": {"sources": [
        {"note_id": chunk.note_id, "note_title": chunk.note_title,
         "chunk_index": chunk.chunk_index, "excerpt": chunk.content[:150]}
        for chunk in retrieved_chunks
    ]},
}
```

The `sources` event is sent **before Claude is ever called at all** —
built directly from what `find_similar_chunks` actually retrieved, a
deterministic, code-produced fact, not a model claim. The system prompt
then simply instructs Claude to *reference* those same notes by title in
its prose ("According to your note 'Boss Fight Prep': ..."), which a
human reader can cross-check against the `sources` list that already
arrived — rather than trusting a citation the model invented after the
fact.

### The system prompt, and why it says what it says

```python
SYSTEM_PROMPT = (
    "You are QuestLog's notes assistant. You will be given one or more "
    "excerpts from the player's own quest notes, each labeled with the "
    "note's title, followed by a question. Answer the question using ONLY "
    "the information in the provided excerpts -- never from your own "
    "general knowledge, and never by guessing. ... If the excerpts do not "
    "contain enough information to answer the question, say so plainly "
    "instead of guessing."
)
```

Two instructions do real work here: "using ONLY the information in the
provided excerpts" is what keeps the model grounded in what retrieval
actually found, instead of falling back on whatever it learned during
training (Lesson 01's whole point). "say so plainly instead of guessing"
gives the model an explicit, honest way to fail — an "I don't know" is a
far better outcome than a confident, ungrounded answer.

### The zero-chunks case

```python
if not retrieved_chunks:
    yield {"event": "error", "data": {"message": "This quest has no notes yet. ..."}}
    return
```

If retrieval finds nothing (a quest with no notes yet), `stream_note_answer`
never calls Claude at all — there's no reason to spend an API call
asking a model to answer from zero context, and no honest answer it could
give anyway. This is verified directly by
`tests/test_rag.py::test_stream_note_answer_with_no_chunks_never_calls_claude`
using a fake client configured with zero response turns, so calling it at
all would fail the test loudly.

### Streaming, end to end

Exactly like Module 13's `stream_quest_breakdown`, `stream_note_answer`
yields plain dicts (`{"event": ..., "data": ...}`), never pre-formatted
SSE text — that formatting is `app/routers/notes.py`'s job, and only
its job, keeping this file independently testable with plain Python
assertions. The event sequence a player's browser actually receives:
`sources` (immediately), then one or more `token` events as Claude's
answer streams in, then a final `result` with the complete text.

## Common mistakes & gotchas

- **Asking the model to generate its own citations.** This is the single
  biggest mistake this lesson's design avoids — see the "citations you
  can trust" section above.
- **Calling Claude even when retrieval found nothing.** Wastes a real,
  billed API call for a question the app already knows it can't
  honestly answer.
- **Forgetting to cap what an excerpt shows in the `sources` event.**
  `chunk.content[:150]` deliberately truncates — the full chunk text
  already went to Claude in the prompt; the `sources` event's job is a
  short, human-scannable preview, not a full re-transmission of every
  chunk.
- **Skipping the "using ONLY the provided excerpts" instruction.**
  Without it, nothing stops Claude from blending in outside knowledge —
  RAG's whole grounding benefit (Lesson 01) depends on the model actually
  restricting itself to what was retrieved, and a system prompt is how
  you ask for that restriction.

## How this connects

This lesson is the payoff of everything Lessons 02-05 built. Lesson 07
now steps back and asks an honest question: given that you've just built
this by hand, when (if ever) would a framework like LangChain or
LlamaIndex actually be worth adopting instead? Lesson 08 then shows this
exact pipeline wired into real HTTP routes.

## Quick self-check

1. List the five steps of this module's RAG pipeline, in order, and name
   which file/function implements each one.
2. Why does `app/rag.py` deliberately avoid tool use and structured
   output, even though Module 13 already taught both?
3. Why is the `sources` event sent *before* Claude is called, rather than
   asking Claude to include citations in its own answer?
4. What does the system prompt's "using ONLY the provided excerpts"
   instruction actually protect against?
5. What happens when `find_similar_chunks` returns zero chunks, and why
   is that the right behavior rather than calling Claude anyway?
