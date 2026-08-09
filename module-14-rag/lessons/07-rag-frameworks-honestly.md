# Lesson 07 — RAG Frameworks, Honestly

**Verified August 9, 2026, via live web research:** LangChain's core
library remains focused on chain composition, with its agent-oriented use
cases having largely migrated to a separate project, LangGraph
(graph-based orchestration for multi-step AI workflows). LlamaIndex
remains a more narrowly-focused data/retrieval framework — 300+ data
connectors, deeper indexing and query primitives, reported to need
noticeably less code than LangChain for equivalent RAG pipelines in
several recent comparisons. Common production version pins observed in
late-2025/early-2026 write-ups: `langchain-openai` in the `1.1.x` range,
`llama-index` in the `0.14.x` range. This is a genuinely fast-moving
space — treat exact version numbers and specific benchmark claims here as
"true as of this research date," not permanent facts.

## What you'll learn

- What LangChain and LlamaIndex actually are, at a level you can hold a
  real conversation about.
- Their current, researched positioning relative to each other (not
  older, possibly stale, general impressions).
- A genuinely honest framework for deciding when hand-rolling (Lesson 06)
  is the right call, and when reaching for one of these libraries is.

## Why this matters

You just built a complete, working RAG pipeline with no framework at
all. That was deliberate — the master plan's own instruction — so you'd
understand every moving part before ever being handed an abstraction
that hides them. This lesson is the honest payoff of that choice: now
that you know what's actually happening under the hood, you can evaluate
whether a framework is solving a real problem for you, or just adding a
layer between you and code you already understand.

## Prerequisites

- **Lesson 06, in full.** This lesson only makes sense in contrast to
  the pipeline you just built by hand — reading this lesson first would
  make every comparison abstract and unearned.

## The concept, explained simply

Think of the difference between writing your own simple inventory system
in a small game project versus adopting a large, general-purpose
inventory/crafting plugin from the engine marketplace. The plugin
handles far more cases than your game needs (stacking rules, weight
limits, crafting trees, UI widgets) — genuinely useful if your game
needs most of that, and genuine overhead (a bigger dependency, more to
learn, more "why is it doing that?" moments) if it doesn't. Neither
choice is universally right; it depends on how much of what the plugin
offers your actual project needs.

## The details

### What LangChain actually is

LangChain is a broad framework for building LLM-powered applications —
RAG is one capability among many (agents, tool-calling chains, memory,
prompt templates), with a very large ecosystem of integrations (500+,
per current research) to different vector stores, document loaders, and
LLM providers. Its own agent-oriented functionality has increasingly
moved into a companion project, **LangGraph**, for building more complex,
stateful, multi-step workflows — worth knowing, since a search for "the
current way to build an agent in LangChain" will increasingly point you
toward LangGraph specifically, not the original LangChain agent classes.

### What LlamaIndex actually is

LlamaIndex is a narrower, retrieval-focused framework — its core job is
connecting LLMs to your own data, with deep support for chunking
strategies, indexing structures, and querying patterns beyond the single
similarity search this module built by hand (e.g., hierarchical chunking
across multiple granularities, or automatically merging small chunks
back into their parent context when several small chunks from the same
region all score well). Current research describes it as needing
noticeably less code than LangChain to build an equivalent RAG pipeline,
and several current write-ups describe a common production pattern as
"LlamaIndex for retrieval, LangGraph for orchestration" — using each
where it's strongest, rather than picking one framework for everything.

### What either framework would have actually saved you, in this module

Concretely, honestly: connectors to load documents from many different
formats and sources (PDFs, web pages, databases) without writing your own
loader for each; a wider menu of chunking strategies out of the box
(semantic chunking using an embedding model to detect topic boundaries,
recursive splitting that tries several separator types in priority
order); built-in integrations to a wide range of vector stores beyond
pgvector, so switching later wouldn't mean rewriting your retrieval code;
and more advanced retrieval patterns (re-ranking, hybrid keyword+vector
search, multi-step/agentic retrieval) than this module's fixed
`top_k = 3` similarity search.

### What you would give up

A real, working understanding of what's actually happening at each step
— which is precisely what Lesson 06 gave you, and what disappears the
moment retrieval, prompt-assembly, and citation-handling all happen
inside a framework's own classes. You'd also take on a real dependency
with its own release cadence, breaking changes, and — genuinely, for
this fast-moving space — a real risk that code written against today's
version looks noticeably different from a version six months from now
(this lesson's own header table is a small, live demonstration of that:
version numbers this course cites for these two libraries will likely be
stale within a year, in a way `pgvector` or `anthropic`'s own SDK moves
more slowly).

### An honest decision framework

Reach for a framework like LlamaIndex or LangChain when: your retrieval
needs are genuinely more complex than a single similarity query (multiple
document types, multi-step retrieval, hybrid search); you need to
support many different vector stores or LLM providers interchangeably;
or your team's velocity matters more than full visibility into every
step, and the framework's abstractions match your actual problem well.

Build it by hand, the way this module did, when: your retrieval need is
genuinely simple (one document type, one similarity query, one vector
store) — QuestLog's exact situation; you're learning, and understanding
every step matters more than shipping fast (this course's exact
reasoning for teaching it this way first); or the framework's
abstractions would need to be fought against more than they'd help,
which is a real, common experience with any sufficiently general tool
applied to a narrow problem.

**For QuestLog specifically:** hand-rolled remains the right call, not
just for this module's teaching purposes but for the app's actual scope
— one document type (plain text notes), one vector store (`pgvector`,
already chosen to build on Postgres knowledge), one simple similarity
query. Nothing about QuestLog's actual requirements needs what either
framework adds.

## Common mistakes & gotchas

- **Adopting a framework before understanding the fundamentals it
  wraps.** This is the exact trap Rule 7's ordering in this module
  avoids — by building the pipeline by hand first, you can now evaluate
  a framework's claims against real, first-hand experience instead of
  taking its marketing at face value.
- **Assuming "more features" always means "better."** A framework
  solving problems you don't have is pure overhead, not a free upgrade.
- **Treating framework version/positioning information as permanent.**
  This lesson's own header table is explicitly dated for exactly this
  reason — re-verify before trusting any specific claim here in the
  future.
- **Conflating "LangChain" with "LangGraph."** Current research shows
  these are increasingly separate concerns (general LLM app building vs.
  agent orchestration specifically) — worth being precise about which
  one a resource is actually describing.

## How this connects

This lesson closes the loop the master plan opened: hand-build first, so
nothing is magic, then evaluate frameworks with real, earned
understanding rather than blind trust. Lesson 08 now takes this exact,
hand-built pipeline and wires it into QuestLog's real backend, as an
actual, working feature.

## Quick self-check

1. What is LangChain's current core focus, and where has its
   agent-oriented functionality largely moved?
2. What is LlamaIndex specifically good at, relative to LangChain?
3. Name two concrete things a framework like LlamaIndex would have saved
   you in this module, and one concrete thing you'd give up by using it.
4. Why does this course teach the hand-built pipeline (Lesson 06) before
   this lesson, rather than the other way around?
5. Why might this lesson's specific version numbers be stale a year from
   now, and what should you do before trusting them?
