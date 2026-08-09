# Lesson 04 — Memory Patterns and Planning

## What you'll learn

- The difference between **short-term memory** (what an agent remembers
  within one conversation) and **long-term memory** (what it remembers
  *across* separate conversations) — and why these are genuinely
  different engineering problems, not two names for the same thing.
- What Anthropic's own memory tool is, at a conceptual level, and when
  reaching for it (versus building nothing at all) is the right call.
- What "planning" means for an agent, concretely — and why it's mostly
  *not* a separate mechanism from the loop you already built.
- How to state a memory decision honestly, the way this course expects
  you to state any scope decision — what a feature does, and what it
  deliberately doesn't do yet.

## Why this matters

Every agent conversation so far in this module has lived entirely inside
one Python list (`messages`) that exists only as long as your script or
one HTTP request is running. That's a real, honest design — most agent
features genuinely don't need more than that — but it's also a design
choice, not a law of nature, and this course's own QuestLog capstone
(Lessons 10–11) needs you to be able to *say*, precisely, what memory it
has and doesn't have, the same way Module 09 and Module 11 taught you to
state plainly what a deployment deliberately doesn't do yet. Vague
answers like "it remembers stuff" aren't good enough once real users
depend on knowing what an assistant will and won't recall.

## Prerequisites

- **Lessons 01–03, in full** — this lesson assumes the loop, its
  vocabulary, and the tool-design judgment from Lesson 03 are settled.
- **Module 13's own streaming/tool-use mechanics** — this lesson doesn't
  introduce any new API surface, only new ways of *using* what you
  already know.

## The concept, explained simply

Picture two very different kinds of memory an NPC might need in a game:

1. **What just happened in this fight.** The boss remembers it already
   used its fire breath twenty seconds ago and shouldn't reuse it until
   its cooldown expires. This state is scoped to the current encounter —
   the moment the fight ends (win, lose, or the player leaves the level),
   it's gone, and correctly so; the next encounter starts fresh.
2. **What this NPC remembers about you, permanently.** A merchant who
   remembers you haggled aggressively last time and now starts prices
   higher — persisted in a save file, surviving the player closing the
   game entirely and coming back next week.

These are **short-term** and **long-term** memory, and they need
completely different storage: short-term memory can live in a plain
variable that dies with the encounter; long-term memory has to be written
somewhere durable (a save file, a database row) and read back on a future,
unrelated session. An AI agent's memory splits along exactly this same
line, and conflating the two — building a system that treats "what's in
this conversation" and "what should persist forever" as the same
problem — is one of the most common design mistakes in agent systems.

## The details

### Short-term memory: the conversation history you already have

Every agent loop this module has built keeps its memory in exactly one
place: the growing `messages` list, resent in full on every single API
call (the same "the API is stateless; you resend history" fact Module 13
already taught you for a single exchange, now stretched across an entire
multi-turn conversation). This *is* short-term memory — there's no
separate "memory system" to add on top of it. As long as `messages`
stays in scope (in your Python process, in a frontend's own React state —
Lesson 10's own QuestLog agent keeps it in the browser, not the backend),
the agent "remembers" everything in it.

Two real limits worth naming honestly:

- **It's bounded by the context window**, and — more practically for a
  chat feature — by cost: resending a long history on every turn means
  paying to re-process it every single time (this is exactly the problem
  Anthropic's *prompt caching* and *compaction* features solve at scale;
  both are out of this course's own scope, but worth knowing they exist
  for a production system with genuinely long-running conversations).
- **It ends when the process or the browser tab does.** Close the tab,
  and — unless something else has written the conversation somewhere
  durable — it's gone. This is not a bug; it's simply what "short-term"
  means, made concrete.

### Long-term memory: what survives across separate conversations

Long-term memory means an agent recalling something from a conversation
that has *already ended* — a genuinely different problem, because it
requires **durable storage** (a database, a file, a dedicated memory
service) plus a way to decide, on a fresh conversation, what to retrieve
and hand back to the model. There are two broad approaches worth knowing
by name:

1. **A dedicated memory tool.** Anthropic ships a real, official
   **memory tool** (`type: "memory_20250818"`) — a client-side tool (you
   implement the storage; Claude decides when to read and write to it)
   that gives the model file-like operations (`view`, `create`,
   `str_replace`, `insert`, `delete`, `rename`) against a `/memories`
   directory you control. The model itself decides, mid-conversation,
   when something is worth writing down for later — "remember that this
   player prefers short answers" — and reads that same directory back at
   the start of a future conversation. This is the most direct fit when
   what you want is genuinely open-ended, model-directed recall ("let
   Claude decide what's worth remembering"), and it deliberately shifts
   the judgment of *what* to remember onto the model rather than your own
   application code.
2. **Retrieval, applied to past conversations instead of documents.**
   Nothing stops you from treating old conversation transcripts exactly
   like Module 14 treated quest notes: chunk them, embed them, store the
   vectors, and retrieve the most relevant past exchanges at the start of
   a new one. This is more application-specific work (you own the
   storage and retrieval logic entirely) but gives you precise control
   over *what* gets recalled and *why* — useful when "let the model
   decide" is too unpredictable for your product.

Both require real, durable storage and a real retrieval decision on every
new conversation — neither is something you get "for free" just by
building an agent loop, which is exactly why this lesson treats them as
their own, separate topic from short-term memory.

### Planning: mostly not a separate mechanism

"Planning" sounds like it should be some distinct phase before the loop
starts — and for the simplest agents, it mostly isn't. Look back at
Lesson 03's own worked example (find the quest, then search its notes,
then answer): the model "planned" that sequence *implicitly*, one
decision at a time, entirely inside the ordinary loop — no separate
planning step, no special prompt technique. This is the honest default,
and it's sufficient for the vast majority of agent tasks this course, and
most real products, actually need.

Where explicit planning *does* help is genuinely harder, more open-ended
tasks — the kind where a model benefits from writing out a rough sequence
of steps *before* committing to the first tool call, so it doesn't act
impulsively on an under-thought first instinct. Two real, current
techniques, both things you can layer on top of the same loop rather than
replacing it:

- **Extended/adaptive thinking** (already covered in Module 13) gives the
  model space to reason before producing its first `tool_use` block or
  final answer — this is often enough "planning" for moderately complex
  tasks, with zero extra application code.
- **A "think" or "plan" tool** — some agent systems give the model an
  explicit tool whose entire job is writing out a plan as text (no real
  side effect at all — the "action" is just producing a plan the model
  itself, or a later step, reads back). This makes planning visible and
  inspectable (you can look at exactly what the model decided to do and
  why) at the cost of one extra iteration per task.

Neither technique changes the loop's shape from Lesson 02 — they change
what's happening *during* the "decide" step, not the mechanism around it.

### QuestLog's own memory decision, stated the honest way

This course's own final capstone (Lessons 10–11) makes a real, bounded
decision, stated the way Module 09 and Module 11 taught you to state any
scope decision:

**What it implements:** short-term memory only, held entirely on the
*frontend* — the browser keeps the visible conversation transcript in
React state, and resends the whole thing on every new message. The
backend itself stores nothing about a conversation between requests.

**What it does NOT implement:** any persistence of a conversation across
a page reload or a new browser session; any long-term, cross-session
memory of a player's preferences (the kind of thing the memory tool above
is built for); and — a subtler, real limitation — even a *single* turn's
own internal tool-calling scratch work (which tools it called, what they
returned) is never persisted once that turn's final answer is produced.
Only the finished, visible answer text becomes part of the history the
next turn resends.

That last point is a genuine, stated trade-off, not an oversight: it
means the agent won't remember, three turns later, the *exact* raw output
of a tool call unless its own final answer happened to restate the
relevant part of it. Lesson 10 discusses exactly why this course accepts
that trade-off for QuestLog's own scope.

## Common mistakes & gotchas

- **Assuming "the agent seems to remember things" means you built
  memory.** If it's all happening inside one conversation's own
  `messages` list, that's short-term memory working exactly as designed
  — not evidence of anything durable. Test this honestly: does it still
  "remember" after a fresh process start, or a fresh browser session?
- **Reaching for a memory tool or a whole retrieval pipeline before
  confirming you actually need cross-session recall.** Most agent
  features genuinely don't — building long-term memory you don't need
  adds real storage, retrieval, and privacy surface area for no benefit.
- **Storing secrets or sensitive data in a memory tool's own files**
  without thinking about who else's conversation might later read that
  same memory directory back. A memory store is still just storage — the
  same data-handling judgment you'd apply to any database applies here
  too.
- **Confusing "extended thinking" with "the model has long-term memory."**
  Thinking happens once, during one turn, and is gone the moment that
  turn ends — it's a *reasoning* aid, not a storage mechanism.

## How this connects

Lesson 03 gave you tool-design judgment; this lesson gave you the
vocabulary to state, precisely, what an agent does and doesn't remember —
a question you'll be expected to answer honestly for QuestLog's own
feature in Lesson 10. Lesson 05 introduces MCP, a standardized way tools
themselves (including, potentially, memory-backed ones) get exposed to
any compliant client. Lesson 06 covers what happens when more than one
agent needs to coordinate — including how memory scope changes once
there's more than one "mind" in the loop.

## Quick self-check

1. In your own words, what is the actual engineering difference between
   short-term and long-term memory for an agent — not just "how long it
   lasts," but *what has to physically exist* for each to work at all?
2. Where does an ordinary agent loop's short-term memory actually live,
   concretely, in the code you wrote in Lesson 02?
3. Name the two long-term memory approaches this lesson describes, and
   state one real reason you'd pick one over the other for a given
   product.
4. Why does this lesson claim "planning" is mostly not a separate
   mechanism from the loop itself? What are the two real techniques that
   genuinely do add something on top of it?
5. State QuestLog's own memory-scope decision from memory, in one or two
   sentences, the way you'd have to explain it to a user asking "will it
   remember what I told it yesterday?"
