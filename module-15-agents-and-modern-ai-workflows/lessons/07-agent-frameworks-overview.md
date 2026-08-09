# Lesson 07 — Agent Frameworks Overview

**Verified August 9, 2026, via live web research, cross-checking multiple
independent 2026 comparison sources:** LangGraph, CrewAI, and the OpenAI
Agents SDK are all reported as production-viable as of mid-2026, each
with a distinct core philosophy — LangGraph models agents as explicit
state machines over a graph; CrewAI composes them as role-driven "crews"
with declarative tasks; the OpenAI Agents SDK treats them as imperative
handoff chains. Reported adoption signals at research time: LangGraph
around 39.2 million monthly PyPI downloads; CrewAI around 46,000 GitHub
stars with first-class MCP support; the OpenAI Agents SDK reported to
support 100+ models via LiteLLM (not just OpenAI's own). This continues
directly from Module 14, Lesson 07's own research (also dated August 9,
2026), which found LangChain's own agent-oriented use cases had already
migrated into the separate LangGraph project — consistent with what this
lesson's own research confirms independently. Treat every specific
number in this lesson as "true as of this research date" in a fast-moving
space, exactly as Module 14's own framework lesson cautioned.

## What you'll learn

- What LangGraph, CrewAI, and the OpenAI Agents SDK actually are, and how
  each one's core philosophy maps onto the loop, tool-design, memory, and
  multi-agent concepts you've already built by hand.
- Anthropic's own current agent-building surfaces — the Tool Runner, and
  Managed Agents — and how they relate to (and differ from) both the
  frameworks above and the raw loop you built in Lesson 02.
- A genuinely honest decision framework for when reaching for a framework
  is worth it, and when it's adding a layer between you and code you
  already understand for no real benefit.

## Why this matters

This lesson comes *last* among the concept lessons, deliberately, per the
master plan's own instruction: you now understand the loop, tool design,
memory, MCP, and multi-agent patterns well enough to look at any
framework's own documentation and immediately map its abstractions onto
concepts you already have names for. Reading this lesson first — the
order every rushed tutorial takes — would leave you cargo-culting a
framework's own vocabulary without the judgment to tell whether it's
solving a real problem for your specific case.

## Prerequisites

- **Lessons 01–06, in full.** Every framework below is described in terms
  of those lessons' own vocabulary (loop, tool, memory scope, multi-agent
  pattern) — if any of those feel shaky, this lesson will read as a list
  of unfamiliar names instead of recognizable ideas wearing new labels.

## The concept, explained simply

You already know what a framework *can't* give you that matters: none of
them invented a new way for an LLM to decide what to do next. Every one
of them runs, underneath its own abstractions, the exact decide → act →
observe → repeat loop from Lesson 02. What they actually offer is
**pre-built scaffolding around that loop** — ready-made patterns for
memory, multi-agent coordination, error handling, and observability, so
you don't hand-write them yourself every time. The real question a
framework has to answer, for your specific project, is: *does the
scaffolding it offers match the shape of what I'm building, or does it
fight against it?* This lesson gives you enough of each framework's real
shape to answer that honestly.

## The details

### LangGraph — agents as an explicit graph of states

LangGraph models an agent (or a multi-agent system) as a **graph**: nodes
are steps (an LLM call, a tool call, a human-approval gate — Lesson 06's
own human-in-the-loop pattern, offered as a built-in primitive here),
edges are the possible transitions between them, and the graph's own
runtime handles executing it, including genuinely hard things to
hand-roll well: **durable execution** (the graph's state can be
checkpointed and resumed, surviving a process restart mid-conversation)
and built-in state inspection for debugging a long-running, complex flow.

**When this fits:** workflows that are genuinely non-linear or stateful
enough that a plain `for` loop starts fighting you — many possible paths
depending on what happens, a real need to pause and resume days later, or
a multi-agent system complex enough that seeing it as an explicit graph
(rather than reading nested function calls) actually clarifies what's
happening. The reported trade-off: a real learning curve (commonly cited
around one to two weeks to get comfortable) before that clarity pays off.

### CrewAI — agents as role-driven "crews" with declarative tasks

CrewAI's own mental model is closer to assembling a team: you declare a
set of agents, each with a role, a goal, and a backstory (yes, genuinely
— this shapes the system prompt each agent gets), then declare **tasks**
and assign them to agents, and the framework handles running the crew
through those tasks, including delegation between crew members. This is
the coordinator/worker pattern from Lesson 06, formalized as the
framework's own primary abstraction rather than something you build by
hand.

**When this fits:** a problem that already naturally decomposes into
distinct *roles* — "a researcher, a writer, a reviewer, an analyst" is
the shape CrewAI's own examples and reported adoption lean into. It's
reported as fast to prototype with specifically because that decomposition
maps directly onto the framework's own vocabulary, and (verified in this
lesson's own research) it has first-class support for connecting to
tools over MCP (Lesson 05) directly.

### OpenAI Agents SDK — agents as imperative handoff chains

A lighter-weight model: you write agents and their tools mostly as plain
code, and the framework's own contribution is making the Lesson 06
**handoff** pattern (one agent transferring an entire conversation to
another) a first-class, minimal-boilerplate primitive, plus built-in
guardrail hooks. Despite the name, it's reported (as of this lesson's own
research) to support 100+ models beyond OpenAI's own, via a compatibility
layer (LiteLLM) — worth knowing if "OpenAI" in the name makes it sound
narrower than it actually is in practice.

**When this fits:** you want the *least* framework overhead of the three
— close to writing the loop yourself, with handoffs and guardrails as
pre-built conveniences rather than a whole new mental model (a graph, a
crew) to learn first.

### Anthropic's own surfaces: Tool Runner and Managed Agents

Two things worth knowing that aren't third-party frameworks at all —
they ship as part of Anthropic's own API and SDKs:

- **The Tool Runner** (a beta helper in the official `anthropic` Python
  and TypeScript SDKs) automates exactly the loop you wrote by hand in
  Lesson 02 — you define tools as decorated functions, and
  `client.beta.messages.tool_runner(...)` handles the call → execute →
  feed-back-the-result cycle for you, while still giving you hooks for
  approval gates, logging, and result modification when you need to
  intervene. It's the smallest possible step up from what you already
  built: same mental model, less boilerplate, and you still host and run
  the loop yourself.
- **Managed Agents** is a different kind of thing entirely: a hosted
  platform where Anthropic runs the agent loop *and* provisions a
  sandboxed container as its workspace — you define an agent
  configuration once (model, system prompt, tools, MCP servers), and
  sessions against it run on Anthropic's own infrastructure, with
  built-in session budgets, outcome-graded iteration, and multi-agent
  orchestration as platform features rather than code you write. This
  is the right tool when you want to stop owning the deployment and the
  sandbox entirely, not just the loop.

Neither of these is "the framework to use instead of LangGraph/CrewAI/the
OpenAI Agents SDK" — they solve a different question (how much of the
*infrastructure*, not just the loop's code, do you want to own yourself)
and are worth knowing about specifically so a real project's framework
decision considers the full field, not just the three third-party
options above.

### An honest decision framework

Before reaching for *any* of the above, ask the same four questions this
course's own research turned up as current, sound practice for deciding
whether you need an agent at all (not specific to any framework):

- **Complexity** — is the task genuinely multi-step and hard to fully
  specify as a fixed sequence in advance?
- **Value** — does getting it right justify the extra cost and latency an
  agent (versus one plain API call) adds?
- **Viability** — is the model actually capable at this kind of task?
- **Cost of error** — can a wrong action be caught and reasonably undone?

If you've answered "yes, this genuinely needs an agent," then choose
scaffolding by matching its *shape* to your problem, not by popularity:

| Your project looks like... | Reach for... |
|---|---|
| A single, well-tooled agent, hosted on your own infra, that you fully understand and control | Nothing — Lesson 02's own loop, or the Tool Runner for less boilerplate |
| A complex, non-linear, or long-running/resumable workflow | LangGraph |
| A problem that naturally decomposes into named roles | CrewAI |
| Minimal overhead, mostly plain code, with handoffs as the main multi-agent need | OpenAI Agents SDK |
| You don't want to run the loop *or* the sandbox yourself | Managed Agents |

## Common mistakes & gotchas

- **Adopting a framework because a tutorial used it, not because your own
  problem matches its shape.** A framework built for non-linear,
  resumable workflows adds real overhead on a task that's genuinely
  linear — you'll be fighting the abstraction, not benefiting from it.
- **Assuming a framework replaces the judgment from Lessons 03/06/08.**
  None of them design your tools for you, decide your memory scope, or
  choose your guardrails — they give you a place to put those decisions,
  not the decisions themselves.
- **Treating "more popular" as "more correct for me."** Download counts
  and star counts (cited honestly above, with a date, per this course's
  own research standard) describe adoption, not fit — the decision table
  above is about shape-matching, not popularity.
- **Forgetting version numbers and specific claims in this space go stale
  fast.** Everything numeric in this lesson is dated August 9, 2026 —
  re-verify before trusting it in your own later work, exactly as Module
  14's own framework lesson already warned you to.

## How this connects

Lessons 01–06 gave you the fundamentals well enough to read this lesson
critically instead of taking any framework's own marketing at face value.
Lesson 08 covers guardrails and evals — concerns that matter identically
whether you're running a hand-built loop or a framework's own runtime.
Lessons 10–11 build QuestLog's own capstone agent with **no framework at
all**, per the master plan's own instruction — you now understand exactly
why that's a deliberate teaching choice, not an oversight, and what you'd
gain (and give up) by reaching for one of the options above instead.

## Quick self-check

1. What is the one thing *no* agent framework changes, no matter how much
   scaffolding it adds on top?
2. Match each framework (LangGraph, CrewAI, OpenAI Agents SDK) to the
   Lesson 06 pattern it makes into a first-class, built-in primitive.
3. What's the real difference between the Tool Runner and Managed Agents
   — what does each one still leave you responsible for, and what does
   each take off your plate?
4. Name the four questions this lesson gives for deciding whether a task
   needs an agent at all, before ever comparing frameworks.
5. Why does this course build QuestLog's own capstone agent with no
   framework, even though you now know several real ones exist?
