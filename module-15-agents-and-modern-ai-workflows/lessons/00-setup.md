# Lesson 00 — Setup: What This Module Needs, and What It Costs

**Verified against (August 2026), via live web research and a live local install/run on August 9, 2026:**

| Fact | Verified value | Source |
|---|---|---|
| `anthropic` Python SDK latest version | `0.121.0`, released 2026-08-07 | PyPI JSON API, `pypi.org/pypi/anthropic/json`, fetched live — unchanged since Module 14 |
| Claude Haiku 4.5 pricing (this module reuses Module 13's model choice) | $1.00 / million input tokens, $5.00 / million output tokens | Re-confirmed live; unchanged since Modules 13–14 |
| Current Model Context Protocol (MCP) specification version | `2026-07-28` — a major, stateless-first rewrite of the protocol | `blog.modelcontextprotocol.io`, live fetch |
| Current official MCP Python SDK | package `mcp`, version `2.0.0` (released 2026-07-28) — installed live in a throwaway virtual environment and its API called directly, not just read about | `pypi.org/pypi/mcp/json`, live fetch; live local install and run |
| MCP server class in the current SDK | `mcp.server.MCPServer` (the in-SDK successor to the standalone `fastmcp` package's `FastMCP` class — same job, renamed as part of the 2.0.0 rework), with an `@mcp.tool()` decorator and `mcp.run()` defaulting to `transport="stdio"` | Confirmed by live `pip install "mcp[cli]"` and calling `MCPServer.tool`, `.list_tools()`, `.call_tool()`, `.run()` directly in a Python shell — this is a genuinely live-verified fact, not a paraphrase of documentation |
| Agent framework landscape (LangGraph, CrewAI, OpenAI Agents SDK) | All three are production-viable in 2026, with distinct philosophies (graph/state-machine, role-based crews, imperative handoffs) — full detail in Lesson 07 | Multiple independent 2026 comparison sources, cross-checked |
| Current agent-evaluation best practice | Multi-level evaluation (end-to-end, trajectory, component), with deterministic checks preferred over LLM-judges for tool-call correctness specifically | Confident AI, Braintrust, Atlan — cross-checked, August 2026 |

## What you'll learn

- What this module needs installed, and what (almost none of it) is new
  beyond Module 14.
- Why an **agent** changes this course's cost conversation — not because
  any single API call gets more expensive, but because one user action can
  now trigger *several* of them.
- How to install the one genuinely new, optional dependency this module
  uses (the MCP Python SDK) without touching QuestLog's own
  `requirements.txt` at all.
- How to verify every piece before Lesson 01 needs it.

## Why this matters

Every module in this course that introduced new infrastructure — Postgres
in Module 06, Redis in Module 10, the Anthropic API in Module 13,
`pgvector` in Module 14 — front-loaded its setup into its own `00-setup.md`,
per this course's Rule 8, specifically so you never hit a lesson that
assumes something you haven't installed. This module is the lightest
"new infrastructure" lift of the whole AI phase — you already have
everything QuestLog's agent needs — but it adds one real, new idea to your
cost model (a single conversation can cost several API calls, not one),
and one small, genuinely new, optional tool (the MCP SDK, used only in
Lesson 05 and its exercise). Both deserve to be settled before Lesson 01.

## Prerequisites

- **Module 13 in full** — this module assumes you already understand tool
  use (the full round-trip: model decides → calls a tool → your code runs
  it → the result goes back → the model continues) and streaming. Neither
  is re-taught here; this module's whole job is what you build *on top* of
  them.
- **Module 14 in full** — this module's own agent reuses Module 14's
  retrieval building blocks (`embed_text`, `find_similar_chunks`) as one of
  its tools. If "chunk → embed → retrieve → cite" doesn't ring a bell,
  revisit that module first.
- **Your `ANTHROPIC_API_KEY`, already configured since Module 13.** Nothing
  new here.
- **QuestLog's Module 14 backend and frontend running locally**, per that
  module's own setup lesson (a `pgvector`-enabled Postgres, the backend's
  `pip install`, the frontend's `npm install`).

## The concept, explained simply

Think back to how a behavior tree or a state machine you'd build for an
NPC in Unreal actually runs at game time: each tick, it evaluates the
world state and picks *one* action, then waits for the next tick to
re-evaluate. A **simple** NPC (say, a sentry that just patrols between two
points) needs exactly one tick's worth of decision before its next action
is obvious. A **complex** NPC (a boss that decides whether to flee, call
reinforcements, or attack, based on its own health, the player's distance,
and whether it's already used an ability on cooldown) needs the tree to
re-evaluate *every single tick*, sometimes several times in a row before
it settles on what to actually do this frame.

QuestLog's Module 13 AI feature was the sentry: one prompt in, at most one
tool call, one answer out — a fixed, small, predictable amount of "thinking."
This module's agent is the boss: a single player message ("break down my
dragon quest and add the pieces as real quests") can require the model to
decide, act, observe the result, and decide again — possibly several times
— before it has a real answer. Every one of those "ticks" is a real,
billed call to the Anthropic API. That's the one genuinely new thing this
setup lesson needs you to internalize before you write a line of this
module's code: **an agent's cost is per-turn, not per-message** — and a
guardrail that caps how many "ticks" one turn can take (this module's own
`MAX_AGENT_ITERATIONS`, which you'll meet for real in Lesson 08 and again
in the capstone) is not a nice-to-have, it's what keeps a badly-behaved
loop from turning into an unbounded bill the same way a badly-written
`while True` with no break condition would freeze a game's own tick loop.

## The details

### Step 1 — Nothing new to install for QuestLog itself

Every backend dependency this module's own capstone code needs
(`anthropic`, `pydantic`, SQLAlchemy, `pgvector`) is already in
`requirements.txt` from Module 13/14. QuestLog's agent feature is built
entirely out of code you already have installed — the master plan's own
"compose what you already have" instruction, taken seriously. If your
Module 14 backend already runs (`pytest -q` passes from
`module-14-rag/project/questlog/backend`), you have everything QuestLog's
own Module 15 capstone needs.

### Step 2 — The one new, optional dependency: the MCP Python SDK

Lesson 05 and Exercise 04 build a small, standalone MCP server. This uses
one new package, `mcp`, which is **not** added to QuestLog's own
`requirements.txt` — it isn't a dependency of the production app, only of
this module's own MCP-specific lesson material — matching the same
"installed in addition to, never instead of" boundary this course already
draws between `requirements.txt` and `requirements-dev.txt`.

Install it into a scratch location — the exercise's own `starter/`
folder is a good place, with its own tiny virtual environment, kept
completely separate from QuestLog's backend `venv`:

```bash
cd module-15-agents-and-modern-ai-workflows/exercises/04-building-an-mcp-server/starter
python -m venv venv
source venv/Scripts/activate   # Git Bash on Windows
pip install "mcp[cli]"
```

**Expected:** `pip install` resolves and installs `mcp` `2.0.0` (or
whatever is current when you run this — Rule 7 means this course verified
`2.0.0` on August 9, 2026; check `pip show mcp` against
`pypi.org/project/mcp` if it's been a while since this lesson was written).
The `[cli]` extra additionally installs the `mcp` command-line tool,
which Lesson 05 uses to test a server interactively without writing a
second script to act as its client.

### Step 3 — Your Anthropic API key (unchanged)

Still the same key from Module 13, still read from `ANTHROPIC_API_KEY` in
your shell or `backend/.env`. Nothing new here — restated only because
this lesson's own "Verify your setup" section checks it.

## The real cost conversation: agent loops multiply API calls

Every dollar-cost table this course has shown you so far (Module 13's
Lesson 00, Module 14's Lesson 00) priced a *single* Claude call. This
module's own capstone feature can make **up to `MAX_AGENT_ITERATIONS`
calls per user message** — 8, the value this module's own
`app/agent.py` uses (see Lesson 08 for exactly why 8, not some other
number). Here's the honest, worked-out worst case, using Claude Haiku
4.5's real, current pricing ($1.00 / million input tokens, $5.00 / million
output tokens):

- Each of the 8 possible turns is capped at `max_tokens=1024` output
  tokens — so the **absolute output ceiling** for one pathological user
  message (one that never gets a final answer and hits the loop cap) is
  `8 × 1024 = 8,192` output tokens, or **$0.041** at Haiku pricing.
- Input tokens grow every turn too — the whole conversation history, plus
  every tool result, gets resent on each iteration (the same "the API is
  stateless; you resend history" fact Module 13 already taught you,
  applied here across a whole tool-calling loop instead of one exchange).
  A realistic worst case for this feature's own system prompt + six tool
  definitions + a growing history over 8 turns lands somewhere in the
  neighborhood of 15,000–25,000 cumulative input tokens for one
  pathological turn — well under **$0.03** at Haiku's input price.

So: **a single, worst-case, guardrail-hitting agent turn on this feature
costs a few cents, not dollars** — genuinely cheap in absolute terms at
this scale. The point of this section isn't that you should be scared of
the bill; it's that the *shape* of the cost changed, from "one call, one
price" to "up to N calls, priced together" — and that shape is exactly
why a loop cap is a real guardrail, not decoration: without one, "up to N"
has no upper bound at all, and neither does the bill.

**Try it yourself:** Using this same math, work out what one pathological
turn would cost if QuestLog's agent instead used `claude-opus-5`
($5.00 / $25.00 per million tokens per this course's own current pricing
table) instead of Haiku. Is the *ratio* between the two models' costs the
same for this feature as it would be for Module 13's single-call feature?
(It is — but say why, in your own words, before moving on.)

## Verify your setup

**1. QuestLog's Module 14 backend still passes its full test suite (confirms nothing broke coming into this module):**
```bash
cd module-15-agents-and-modern-ai-workflows/project/questlog/backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest -q
```
**Expected:** every test passes except `tests/test_notes_pgvector_integration.py`'s
tests, which **skip** (not fail) without a real `pgvector`-enabled
Postgres — the exact same expected result Module 14's own setup lesson
described, now with this module's own new `tests/test_agent.py` passing
alongside everything else.

**2. Your Anthropic API key is set:**
```bash
python -c "import os; print('set' if os.environ.get('ANTHROPIC_API_KEY') else 'MISSING')"
```
**Expected:** `set`. If `MISSING`, revisit Module 13, Lesson 00.

**3. The MCP SDK installs and its server class is importable (do this inside the scratch venv from Step 2, not QuestLog's own backend venv):**
```bash
python -c "from mcp.server import MCPServer; print('ok')"
```
**Expected:** `ok`. This is the exact class Lesson 05 builds a real server
with.

**4. The `mcp` CLI is available:**
```bash
mcp --version
```
**Expected:** a version string, no error. If this fails but Step 3
succeeded, you installed plain `mcp` instead of `mcp[cli]` — reinstall
with the extra.

## Common mistakes & gotchas

- **Installing `mcp` into QuestLog's own backend `venv`.** Don't — it's
  not a dependency of the app, only of this lesson's own standalone
  example. Keep it in the exercise's own separate scratch environment (Step 2)
  so a fresh `pip install -r requirements.txt` for QuestLog itself never
  needs it.
- **`ImportError: cannot import name 'FastMCP' from 'mcp.server.fastmcp'`.**
  Some tutorials and older search results (including some this course's
  own Rule 7 research turned up) still reference `FastMCP` — that class
  lived in the *standalone* `fastmcp` PyPI package and an earlier
  generation of the official SDK. As of the `mcp` `2.0.0` rework (verified
  live, August 9, 2026), the official SDK's server class is
  `mcp.server.MCPServer`. If you find an example using `FastMCP`, the
  concepts transfer directly — only the import and class name changed.
- **Confusing "a `MAX_AGENT_ITERATIONS` cap exists" with "this feature is
  free."** The cap bounds the *worst* case; a normal, successful
  conversation turn (the model answers directly, or makes one or two tool
  calls before answering) costs far less than the worst-case math above —
  see this lesson's own worked numbers again once you've read Lesson 08.
- **Forgetting this module's agent needs the exact same `ANTHROPIC_API_KEY`
  Module 13 already required** — there's no separate signup, no second
  key, nothing new to pay for beyond what you've already set up.

## How this connects

Lesson 01 starts with the conceptual "why" — what an agent actually is,
and why the loop shape (decide → act → observe → repeat) is the right
mental model — before any more setup or code. Lesson 02 builds a real one,
by hand, in raw Python. Lessons 03–09 build up every remaining concept
(tool design, memory, MCP, multi-agent patterns, frameworks, guardrails,
evals, and using AI well in your own dev workflow) this module's own
capstone (Lessons 10–11) then applies for real, inside QuestLog.

## Quick self-check

1. What is the one genuinely new dependency this module introduces, and
   why is it kept out of QuestLog's own `requirements.txt`?
2. Why does an agent's cost model differ from Module 13's single-call
   feature's cost model — what changed, specifically?
3. In your own words, what does `MAX_AGENT_ITERATIONS` actually bound —
   the cost of *any* conversation, or the cost of the *worst-case*
   conversation? Why does that distinction matter?
4. What class does the current (`mcp` `2.0.0`) MCP Python SDK use to
   define a server, and what decorator does it use to expose a function
   as a tool?
5. If `tests/test_notes_pgvector_integration.py`'s tests fail instead of
   skipping when you run `pytest -q` in Step 1 above, what does that tell
   you, and where would you go to fix it?
