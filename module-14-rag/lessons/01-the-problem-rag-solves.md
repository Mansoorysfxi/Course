# Lesson 01 — The Problem RAG Solves

## What you'll learn

- Why a large language model, on its own, cannot answer questions about
  your own private data — no matter how capable it is.
- The two real alternatives to "the model just knows it" — retraining the
  model, and retrieval-augmented generation (RAG) — and why this course,
  and most real applications, pick the second.
- What "retrieval-augmented generation" actually means, term by term.
- Where RAG fits among everything Modules 12-13 already taught.

## Why this matters

Module 13 gave QuestLog its first AI feature: an assistant that reads one
quest's title and description and suggests a breakdown. That worked
because everything the model needed was already sitting right there in
the prompt — a title and a description, a few hundred tokens. This
module's feature is different in a way that matters: a player might
attach *dozens* of notes to a quest over time — battle strategies, NPC
dialogue, their own planning scribbles — and then ask a question like
"what did I learn about the boss's weakness?" There is no way to just
"put it all in the prompt" once notes pile up across many quests: context
windows are large but not infinite (Module 12, Lesson 06), and even where
it would technically fit, it's wasteful and expensive to make Claude read
every single note just to answer a question about one of them. RAG is the
answer to exactly this problem, and understanding *why* it's needed is
what makes the rest of this module make sense rather than feel like
arbitrary machinery.

## Prerequisites

- **Module 12, Lesson 03** — what an LLM's context window is and why it's
  finite.
- **Module 12, Lesson 04** — embeddings and cosine similarity ("meaning
  as coordinates"). This lesson assumes you remember that vocabulary.
- **Module 13, Lesson 01-02** — calling the Anthropic API and streaming a
  response; this module's own answer-generation step reuses that
  mechanism directly, just with different content in the prompt.

## The concept, explained simply

Imagine an NPC in a game who is supposed to answer the player's questions
about the world's lore — quest history, NPC relationships, item lists.
There are two ways to build that NPC:

1. **Bake everything into the NPC's own head at design time.** You write
   all the lore into the NPC's dialogue tree or fine-tune its behavior
   ahead of time. This works, but every time the lore changes (a patch
   adds a new quest, an item gets renamed), you have to redo that work —
   and the NPC's "knowledge" is frozen at whatever point you last did it.
2. **Give the NPC a lookup into the actual, current quest journal/lore
   database before it answers.** The NPC doesn't need to have
   memorized anything — when the player asks a question, the NPC's
   *first* move is to look up the relevant pages in the journal, then
   answer using what it just read. Update the journal, and the NPC's
   answers update immediately, with zero retraining.

**Retrieval-Augmented Generation (RAG)** is option 2, applied to a large
language model. The name breaks down exactly like this:

- **Retrieval** — before generating anything, find the small number of
  relevant pieces of your own data (Lesson 05 covers exactly how).
- **Augmented** — add those pieces into the prompt you send the model,
  on top of ("augmenting") the player's actual question.
- **Generation** — the model then generates its answer the normal way
  (Module 13's territory), except now it has real, current, relevant
  information to work from instead of only what it learned during
  training.

## The details

### Why not just fine-tune the model on your own data?

Fine-tuning (retraining a model, or part of it, on your own data) is a
real technique, and it's the right tool for some problems — but it is a
poor fit for "answer questions about a specific player's specific notes,"
for three concrete reasons:

1. **It doesn't update easily.** Every time a player adds a new note,
   you'd need to retrain — for one player's five sentences. That's
   absurd at QuestLog's scale, and still expensive and slow even at a
   much bigger one.
2. **It's shared across every use of the model, not scoped to one
   player.** A fine-tuned model's weights are the same for every request
   — there's no clean way to fine-tune "just for this one player's
   notes, until they log out."
3. **It's a much bigger, much more expensive operation than a database
   query.** Retrieval, by contrast, is exactly what Module 06 already
   taught you a database is good at: store data, query for what's
   relevant, right now, per request.

RAG sidesteps all three: your data lives in an ordinary, easily updated
database (Postgres, this module's `pgvector`-enabled tables), retrieval
is a normal, fast, per-request query, and nothing about the model itself
ever changes.

### Why not just put everything in the prompt?

For a *small* amount of data — one quest's own title and description
(Module 13) — this is exactly the right, simple choice, and RAG would be
needless complexity. It stops working once the amount of your own data
grows past what comfortably fits in a prompt:

- **Context windows are large but finite** (Module 12, Lesson 06) — Claude
  Haiku 4.5's is 200,000 tokens, generous, but not infinite, and a player
  with enough notes across enough quests could genuinely exceed it.
- **Cost scales with tokens sent, every single call** (Module 13, Lesson
  05's cost-management lesson) — stuffing every note into every question's
  prompt means paying to have Claude read irrelevant notes on every single
  question, forever.
- **Relevance gets diluted.** Even well within the context window, giving
  a model a hundred paragraphs when only two are relevant makes it more
  likely to reference the wrong one, or blend information from unrelated
  notes — the same "which fact was that, again?" problem a human would
  have skimming a hundred pages to answer one specific question.

RAG's retrieval step exists specifically to solve this: find the *few*
genuinely relevant pieces, and send only those.

### What RAG does NOT fix

Stated honestly, because it matters for how you'll read the rest of this
module: RAG does not eliminate hallucination (Module 12, Lesson 06) —it
narrows the *space* in which the model is answering, from "anything it
learned during training" to "the specific text retrieval handed it," which
makes ungrounded answers much less likely, but a model can still
misread, misattribute, or fill gaps in what was retrieved. Lesson 06's
citation design is this module's real, concrete answer to *that*
specific risk — a citation lets a human verify what the model claims,
rather than trusting it blindly.

## Common mistakes & gotchas

- **Confusing RAG with fine-tuning.** They solve different problems.
  Fine-tuning changes what the model *is*; RAG changes what the model is
  *given* for one specific request. This course teaches RAG because it
  fits QuestLog's actual need — private, frequently-changing, per-user
  data — much better.
- **Assuming RAG is only for huge document collections.** QuestLog's own
  feature works with even a single short note — the pipeline (chunk,
  embed, retrieve, generate) is the same regardless of scale; what
  changes is only how much retrieval actually matters (with one short
  note, retrieval barely narrows anything down — the value compounds as
  a player accumulates more notes over time).
- **Thinking retrieval alone is "the RAG system."** Retrieval is one
  half. The other half — actually handing what was retrieved to the model
  well, and being honest about what it found — matters just as much, and
  is Lesson 06's subject.

## How this connects

Module 12 gave you the vocabulary this whole module builds on (tokens,
context windows, embeddings, cosine similarity). Module 13 gave you the
mechanism for talking to Claude, including streaming a response. This
lesson is the "why" that ties them together into a new kind of feature.
Lesson 02 starts the "how," at the very first step of the pipeline:
turning a raw note into pieces small enough to search over.

## Quick self-check

1. In your own words, what do "retrieval," "augmented," and "generation"
   each refer to in "Retrieval-Augmented Generation"?
2. Why is fine-tuning a poor fit for "answer questions about one
   player's own quest notes," even though it's a real, valid technique
   in general?
3. Name two concrete costs (not just "it might not fit") of putting
   every one of a player's notes into every question's prompt, instead
   of retrieving only the relevant ones.
4. Does RAG eliminate hallucination? What does it actually reduce, and
   what does Lesson 06's citation design add on top of that?
5. Would QuestLog's "suggest a quest breakdown" feature (Module 13)
   benefit from RAG? Why or why not?
