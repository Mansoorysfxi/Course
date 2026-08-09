# Module 15 — Agents & Modern AI Workflows

**Phase:** 4 — AI Engineering & Agents
**Estimated time:** 16-20 hours
**Verified against (August 2026):** `anthropic` Python SDK `0.121.0`
(released 2026-08-07, unchanged since Modules 13–14) and Claude Haiku 4.5
pricing ($1.00/million input tokens, $5.00/million output tokens,
re-confirmed, unchanged); current Model Context Protocol specification
`2026-07-28` and its official Python SDK, package `mcp` version `2.0.0`
(released the same day) — installed live and exercised directly, not
just read about; current 2026 positioning of LangGraph, CrewAI, and the
OpenAI Agents SDK; current guardrail and multi-level agent-evaluation
practice. Every fact above was checked with a live web search, a live
package-registry fetch, or a live local install-and-run on August 9,
2026 — see each lesson's own header for the specific source and method.

## What this module is

This is the final module of the course, and its own final capstone. Every
earlier module in Phase 4 taught you one real AI capability in isolation
— prompting and tokens (Module 12), tool use and streaming (Module 13),
retrieval-augmented generation (Module 14). This module's job is the one
thing none of those did alone: the **agent loop** that lets a model
decide, act, observe, and repeat — chaining tools, reasoning across
several steps, and doing it safely — built entirely by hand first, per
this course's own master plan, so nothing about "an agent" is ever magic
to you.

**QuestLog gains a real, autonomous, tool-using agent in this module:** a
chat panel where a player can ask the assistant to list, create, update,
and complete their quests, search a specific quest's own notes and answer
with citations, and suggest a quest breakdown — composing Module 13's and
Module 14's own AI features as tools, rather than reinventing them —
with real, stated guardrails (a hard iteration cap, no destructive tool
at all, ownership scoping on every tool call, and Pydantic-validated tool
inputs) and an honestly-bounded memory scope (short-term only, held on
the frontend, stated plainly).

## What you'll be able to do after this module

- Explain, precisely, what an agent is: the decide → act → observe →
  repeat loop, and build one from scratch in raw Python with no
  framework.
- Design a good tool — one whose name, description, and schema actually
  help a model use it correctly — and reason about when a narrower tool
  beats a general one.
- State, honestly and precisely, what an agent feature's memory does and
  doesn't cover, across a single conversation and across sessions.
- Build a real MCP server using the current official SDK, and explain
  what problem MCP actually solves.
- Design and justify multi-agent patterns (coordinator/worker, handoff)
  and a hand-built human-in-the-loop approval gate.
- Give an informed, non-cargo-culted opinion on when LangGraph, CrewAI,
  the OpenAI Agents SDK, or neither, fits a given project.
- Implement real guardrails (loop caps, tool-sandboxing discipline,
  destructive-action scoping) and write a deterministic, trajectory-level
  eval for an agent — not just a single-call one.
- Use an AI coding assistant well yourself: prompt it with a real spec,
  review its output with a real checklist, and guard against skill
  atrophy with concrete, practiced habits.
- Explain, end to end, exactly how QuestLog's own final capstone agent
  works, because you can read (and did read) every line of its real,
  tested implementation — and explain how it reaches production using
  nothing this course hasn't already built.

## Prerequisites

- **Module 13 in full** — tool use, streaming, and structured outputs are
  assumed, not re-taught.
- **Module 14 in full** — this module's own agent reuses Module 14's
  retrieval primitives (`embed_text`, `find_similar_chunks`) as a tool,
  unmodified.
- **Module 07's ownership-scoping discipline** — this module's own agent
  tools apply that exact discipline to model-supplied arguments.

## A real Anthropic API key, and one new, optional, free piece of tooling

This module needs the same `ANTHROPIC_API_KEY` Module 13 already
required — nothing new to sign up for. What's new is one **optional**
package, the MCP Python SDK (`mcp[cli]`), used only by Lesson 05 and
Exercise 04 — kept entirely out of QuestLog's own `requirements.txt`,
since it's a teaching tool, not a dependency of the production app. See
Lesson 00 for the full setup and the honest cost conversation this module
adds: an agent can call the API several times per single user message,
not once — Lesson 00 works through exactly what that means in real
dollars.

## Module structure

```
module-15-agents-and-modern-ai-workflows/
├── README.md                                                          ← you are here
├── lessons/
│   ├── 00-setup.md                                                      ← what's new, and the real cost conversation
│   ├── 01-what-an-agent-is-the-loop.md                                    ← the mechanical definition
│   ├── 02-building-a-minimal-agent-from-scratch.md                         ← raw Python, no framework, live-verified
│   ├── 03-tool-design-and-multi-step-reasoning.md                            ← what makes a tool good
│   ├── 04-memory-and-planning.md                                                ← short-term vs. long-term, honestly
│   ├── 05-model-context-protocol-mcp.md                                          ← current spec/SDK, a real server, live-verified
│   ├── 06-multi-agent-patterns-and-orchestration.md                                ← coordinator/worker, handoff, human-in-the-loop
│   ├── 07-agent-frameworks-overview.md                                               ← LangGraph, CrewAI, OpenAI Agents SDK, honestly
│   ├── 08-agent-safety-guardrails-and-evals.md                                        ← every real guardrail, and deterministic evals
│   ├── 09-ai-in-your-dev-workflow.md                                                    ← using AI well, reviewing it critically
│   ├── 10-building-questlogs-agent-backend.md                                             ← the capstone backend, explained
│   └── 11-building-questlogs-agent-frontend-and-going-live.md                               ← the capstone frontend + honest deploy walkthrough
├── exercises/
│   ├── 01-minimal-agent-loop/                                           ← easy
│   ├── 02-tool-design-and-multi-step-reasoning/                            ← guided
│   ├── 03-memory-and-planning/                                                ← guided
│   ├── 04-building-an-mcp-server/                                                ← guided -> independent (needs mcp[cli])
│   └── 05-guardrails-and-evals/                                                     ← independent
├── project/
│   ├── BRIEF.md                                                          ← the final capstone: verify, extend, reflect
│   └── questlog/                                                           ← QuestLog, copied forward from Module 14,
│       ├── backend/app/agent.py                                                ← NEW: the hand-built agent loop + 6 tools
│       ├── backend/app/routers/agent.py                                          ← NEW: POST /api/agent/chat
│       ├── backend/app/mcp_server.py                                               ← NEW: the optional, read-only MCP tie-back
│       ├── backend/requirements-mcp.txt                                              ← NEW: optional, for mcp_server.py only
│       ├── backend/tests/test_agent.py                                                ← NEW: 14 real tests, no external creds needed
│       ├── frontend/src/api/agentApi.ts                                                 ← NEW: SSE consumption for the agent
│       └── frontend/src/components/AgentChatPanel.tsx                                     ← NEW: the chat UI
└── CHECKLIST.md
```

Read the lessons in order — Lessons 10–11 assume every technique in
Lessons 00–09 without re-explaining any of them. Exercises 01–05 go from
"almost impossible to fail if you read Lesson 02" to "you're combining
three lessons' worth of judgment with far less scaffolding" — see each
exercise's own `INSTRUCTIONS.md` for its specific difficulty and hints.

## How to work through this module

Follow the workflow in the [root README](../README.md): read a lesson,
answer its self-check questions, do the matching exercise without looking
at its solution, ask for a review, revise if needed, then move on. Once
all five exercises are done, work through `project/BRIEF.md` — the final
capstone of the entire course.

## A note on the running project

See [`RUNNING_PROJECT.md`](../RUNNING_PROJECT.md) for the full picture of
how QuestLog evolves across modules, and its "Fixed technology decisions"
section for this module's own agent-tool-set, guardrail, and memory-scope
decisions, recorded there in full. This module's `project/questlog/` is
Module 14's finished QuestLog, copied forward, with `backend/app/` and
`frontend/src/` changed only for this module's own new, documented agent
feature — see Lessons 10–11 for the complete, file-by-file account of
exactly what changed and why.
