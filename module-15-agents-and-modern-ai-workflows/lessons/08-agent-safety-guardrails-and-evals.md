# Lesson 08 — Agent Safety: Guardrails and Evals

**Verified August 9, 2026, via live web research, cross-checking multiple
2026 sources on agentic-system safety and evaluation practice:** current
guardrail guidance treats cost/loop limits and tool-execution boundaries
as structural controls that must be enforced in code, not left to system
prompt instructions alone (a prompt-only rule is not a guardrail — a
sufficiently adversarial or confused model can talk its way around
prose). Current agent-evaluation guidance has moved decisively toward
**multi-level evaluation** — end-to-end (did the task succeed?),
trajectory-level (was the path taken sound — right tools, right order,
no wasted steps?), and component-level (which specific piece broke?) —
with **deterministic checks preferred over an LLM judge specifically for
tool-call correctness** (exact tool names, required arguments, and
expected call order can be checked in plain code, with no ambiguity an
LLM judge would need to resolve).

## What you'll learn

- Why a guardrail has to live in code your agent's own loop enforces, not
  in a system-prompt instruction the model might or might not follow.
- The concrete guardrails this course's own QuestLog capstone actually
  implements, and the real reasoning behind each one — including the
  guardrail that's simply *not building a tool at all*.
- What "evaluating an agent" means once "did it get the right answer?"
  stops being a sufficient question — trajectory-level and tool-call
  correctness evals, and how to write a simple one yourself, with no LLM
  judge required.

## Why this matters

An agent that can take real actions (create a database row, send a
message, spend money) is categorically riskier than a chatbot that only
produces text — a wrong tool call has a real effect, not just a wrong
sentence. This lesson is where "build an agent" and "build a *responsible*
agent" stop being the same sentence. Every guardrail here is something
this course's own capstone (Lesson 10) actually implements, for real
reasons stated plainly — not a checklist item added for appearances.

## Prerequisites

- **Lessons 01–06, in full** — this lesson assumes the loop, tool design,
  memory scope, and human-in-the-loop pattern are all already familiar;
  every guardrail below is something you insert *into* that loop, not a
  new mechanism.
- **Module 13, Lesson 05 (error handling, retries, and cost management)**
  — the idea that a runaway loop is a real cost risk, not just a
  correctness one, is assumed from there.

## The concept, explained simply

A guardrail for an agent is the exact same idea as a **maximum recursion
depth**, or a hard **tick budget**, you'd put on any recursive or
self-scheduling behavior in a game to stop a bad state from freezing the
whole simulation. You wouldn't trust an NPC's own AI to "know when to
stop" recursing through a pathfinding search — you'd cap the recursion
depth in code, as a hard, unconditional limit, precisely because the bug
that causes infinite recursion is exactly the bug that would also make an
NPC's own internal logic *think* it should keep going. A guardrail on an
LLM agent works the same way, for the same reason: you can't trust the
model's own judgment to reliably self-limit, because the exact situations
where a limit matters most (a confused model, an adversarial user, a
genuinely ambiguous task) are also the situations where the model's own
judgment is least reliable.

## The details

### Guardrail 1: a hard iteration cap, enforced in code

You've already seen this in every loop this module has built —
`MAX_ITERATIONS` (Lesson 02), `MAX_AGENT_ITERATIONS` (QuestLog's own
`app/agent.py`, Lesson 10). The mechanism is a plain `for` loop with a
fixed range, not a "please don't loop more than N times" instruction in
the system prompt — because a prompt instruction is advisory, and this
guardrail's entire job is to hold even when the model doesn't follow
advice. **Why 8, for QuestLog specifically?** This module's own agent has
six tools and a genuinely open-ended job, so a realistic worst-case chain
(find the quest, check its notes, suggest a breakdown, then create two or
three quests from the result) can legitimately need five or six
iterations before a final answer — 8 gives real headroom above that
without being large enough that a truly stuck loop burns an unreasonable
number of calls before the cap bites. This is a **judgment call, stated
honestly**, not a value derived from a formula — Lesson 00's own cost
math shows you exactly what the worst case costs in dollars if you want
to sanity-check a different number for your own project.

### Guardrail 2: not every action gets a tool

The single most effective guardrail against a destructive action is
**never exposing it as a tool at all.** This course's own QuestLog agent
can create, read, update, and mark quests complete — it has **no**
`delete_quest` tool, full stop. This is a real, considered decision, not
an oversight: QuestLog's own `delete_quest` in `app/repository.py` is a
genuine, permanent `DELETE`, with no trash or undo. Rather than building
a whole confirmation-flow (Lesson 06's human-in-the-loop pattern) just
for this one destructive action, this course's own honest answer is
simpler: the capability doesn't exist for the agent at all. A player who
wants to delete a quest still can, from QuestLog's own existing UI —
nothing about the agent removes that ability, it just isn't something the
*agent itself* can do on a player's behalf.

**The general judgment call, stated plainly:** before adding any tool,
ask whether the action is easily reversible (creating a quest is — you
can delete it) or not (deleting one isn't). For reversible actions, let
the agent act freely. For irreversible ones, you have three real options,
in ascending order of engineering cost: **don't build the tool at all**
(QuestLog's own choice here); **gate it behind human-in-the-loop
approval** (Lesson 06); or **build a genuine undo/soft-delete path** so
the action becomes reversible after all, removing the need for a gate.
Pick the cheapest option that's honestly sufficient for your own
product's real stakes — don't reach for the most elaborate one by
default.

### Guardrail 3: ownership scoping, on every tool, with no exceptions

Every QuestLog agent tool that touches a specific quest resolves it
through the exact same "combine the existence check and the ownership
check in one query" function every other route in this app has used
since Module 07 — a quest that exists but belongs to someone else
produces the same "not found" result a nonexistent quest would, the same
404-not-403 information-leak reasoning from that module, now applied to
a tool result instead of an HTTP response. This matters *more* for an
agent than for an ordinary route, not less: a tool's `quest_id` argument
is supplied by the *model*, which is itself influenced by whatever the
player typed — a well-designed agent should never be one bad or
manipulated tool call away from touching a quest it has no business
touching, and the fix is exactly the authorization discipline you already
know from Module 07, applied consistently.

### Guardrail 4: structured, validated tool inputs

A tool's arguments arrive as whatever JSON the model decided to send —
untrusted in exactly the same sense any HTTP request body is untrusted
(Module 05's own Pydantic-validation lesson). QuestLog's own
`create_quest` and `update_quest` tools validate their arguments through
the **same** `QuestCreate`/`QuestUpdate` Pydantic models the real HTTP
routes already validate request bodies against — not a second,
independent validation path, the *same* one, reused. A model that omits
a required field, or supplies an out-of-range `priority`, produces a
clear, recoverable validation error the agent can react to (Lesson 03's
own "defense in depth" reasoning, applied to a tool's input instead of a
structured output).

### Guardrail 5: sandboxing tool execution

Not every guardrail is about *which* actions exist — some are about
*how* an action executes once it's allowed. Two concrete, current
practices worth knowing:

- **Never pass model-supplied text directly to something that executes
  it** — `eval()`, a raw shell command, an unvalidated file path. Lesson
  02's own calculator tool used a narrow character allowlist specifically
  because a real tool must never trust that "the model wouldn't ask for
  something dangerous" — the same discipline as never trusting raw user
  input in a web form, applied to model output instead, because model
  output is itself downstream of untrusted user input.
- **Run genuinely risky tool execution (arbitrary code, shell access) in
  an isolated environment** — a container, a restricted user account,
  or a sandboxed process — never directly in your main application's own
  process or with its own full privileges. This course's own QuestLog
  tools never execute arbitrary code at all (every tool is a specific,
  narrow, pre-written Python function — Lesson 03's own "promote to a
  dedicated tool" principle, taken to its logical conclusion), which is
  itself a form of sandboxing: there's no general-purpose "run this code"
  capability to sandbox in the first place.

### Guardrail 6: cost transparency, surfaced to the person paying for it

A cap that only lives in a server log isn't a guardrail a *user* can
reason about. QuestLog's own agent sends a `usage` event — how many
turns and tool calls the current conversation turn actually took — right
before its final answer, every single time, so cost is a visible number
in the UI, not a hidden one a player has to trust exists. This is a
small, low-effort addition with real value: it makes the guardrail's own
existence *legible*, not just enforced.

### Evaluating an agent: beyond "did it get the right answer?"

Module 13 already taught you a simple eval harness for a single-call
feature: give it inputs, check the outputs match expectations. An agent
needs more, because two agents can produce the *same correct final
answer* while one of them took a sensible path and the other flailed,
called the wrong tool twice, or got lucky. Current practice evaluates
three separate things, not one:

1. **End-to-end** — did the task actually succeed?
2. **Trajectory-level** — was the *path* sound? Right tools, in a sensible
   order, no wasted or redundant steps?
3. **Component-level** — if something failed, which specific piece (a
   particular tool, a particular retrieval step) is responsible?

**Tool-call correctness deserves its own, deterministic check — no LLM
judge needed.** Whether the right tool was called, with valid arguments,
in a sensible order, is a fact you can check in plain code, exactly like
any other assertion in a test:

```python
"""A tiny, deterministic trajectory eval -- checks WHICH tools an agent
called and in what order, not just whether its final answer sounds right."""

def eval_finds_quest_before_searching_notes():
    """For a question that names a quest only by TITLE (never an id),
    the agent MUST call list_quests before search_quest_notes -- calling
    search_quest_notes first would mean it invented a quest_id, a real,
    checkable failure mode."""
    fake = FakeClient(turns=[
        final([tool_use("t1", "list_quests", {})], "tool_use"),
        final([tool_use("t2", "search_quest_notes", {"quest_id": "q1", "question": "armor?"})], "tool_use"),
        final([text_block("Bring fire armor.")], "end_turn"),
    ])

    def run_tool(name, tool_input):
        if name == "list_quests":
            return '[{"id": "q1", "title": "Defeat the dragon"}]'
        if name == "search_quest_notes":
            return "Bring fire resistant armor."
        return "unknown"

    _, tool_call_log = run_agent_recording_tool_calls(
        fake, "What armor should I bring for the dragon fight?", run_tool
    )

    assert tool_call_log == ["list_quests", "search_quest_notes"], tool_call_log
    print("PASS: tool_call_log =", tool_call_log)
```

(`run_agent_recording_tool_calls` is the same loop shape you already
know, extended to append every tool name it calls, in order, to a plain
list — the only new piece here is *recording* the trajectory, not
running it differently.)

**Live-verified, August 9, 2026:**

```
PASS: tool_call_log = ['list_quests', 'search_quest_notes']
```

This is exactly the same principle this module's own capstone test suite
(`tests/test_agent.py`, Lesson 10) already applies for real — several of
its own tests assert on the *sequence and content* of `tool_call` events
a scripted fake conversation produces, not just the final answer text.
You've now seen, in miniature, why those assertions exist: they're
trajectory-level evals, the same idea this lesson just named.

**Try it yourself:** Write a second eval that would **fail** the same
assertion style — script a fake conversation where the agent calls
`search_quest_notes` with a guessed `quest_id` *before* ever calling
`list_quests`. Run your eval and confirm it correctly reports the failure
(this is proving your eval actually checks something, not just that it
prints "PASS" unconditionally).

## Common mistakes & gotchas

- **Writing a guardrail as a system-prompt instruction only** ("never
  call this tool more than 3 times") instead of enforcing it in code. A
  model can, and eventually will, fail to follow prose instructions
  exactly — a real guardrail has to hold even then.
- **Believing a loop cap alone is "safety."** It bounds *how long* a bad
  interaction can run — it says nothing about whether an individual
  action, taken once, is itself safe. Guardrails 2–5 above are what
  actually constrain *what* a single iteration can do; the loop cap only
  constrains *how many* iterations there can be.
- **Using an LLM judge for something a deterministic check would answer
  more reliably and more cheaply.** "Did it call the right tool with the
  right arguments?" has one correct answer you can check with plain
  Python — reaching for an LLM judge here adds cost, latency, and its own
  potential for error, for a question that doesn't need any of that.
- **Treating "no delete tool" as a limitation to work around** rather
  than the guardrail it actually is. If a real product genuinely needs
  agent-driven deletion later, the honest next step is human-in-the-loop
  approval (Lesson 06) or a real undo path — not quietly adding the tool
  back without either.

## How this connects

Every earlier lesson in this module built the mechanism (the loop, tool
design, memory, MCP, multi-agent patterns, frameworks); this lesson gave
you the judgment to build it *responsibly*, and a real way to check
whether it's working correctly beyond "the final answer looked fine."
Lesson 09 shifts focus one more time — from AI you're *building* to AI
you use *while* building, which turns out to need a very similar kind of
judgment (review critically, don't take output on faith). Lessons 10–11
apply every guardrail from this lesson for real, inside QuestLog, and you
already know, in advance, exactly why each one is there.

## Quick self-check

1. Why isn't a system-prompt instruction like "never call this tool more
   than 3 times" a real guardrail, on its own?
2. What is QuestLog's own agent's guardrail against a destructive
   `delete_quest` action — and why does this lesson call it the "cheapest
   sufficient option," compared to the alternatives?
3. Name the three levels current practice evaluates an agent at, and give
   one concrete question each level is meant to answer.
4. Why does this lesson recommend a deterministic check, not an LLM
   judge, specifically for tool-call correctness?
5. Walk through, in your own words, why `MAX_AGENT_ITERATIONS = 8` is
   described as a judgment call rather than a value derived from a
   formula — what real trade-off is it balancing?
