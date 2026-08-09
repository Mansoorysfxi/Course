# Lesson 03 — Tool Design and Multi-Step Reasoning

## What you'll learn

- What actually makes one tool definition better than another — concrete,
  checkable criteria, not vague advice.
- When a narrow, single-purpose tool beats a general one with a flag or
  parameter that does the same thing.
- How an agent chains several tool calls together to answer one question
  it couldn't answer from a single call — "multi-step reasoning," made
  concrete.
- What a *parallel* tool call is, and when the model uses one.

## Why this matters

Lesson 02's loop is dumb in exactly one useful way: it will faithfully do
whatever the model asks, using whatever tools you handed it. Everything
about whether an agent behaves *well* — whether it finds the right quest
on the first try, whether it asks for confirmation before something
risky, whether it wastes three tool calls doing what one well-designed
tool would have done in one — comes from the tools themselves, not from
the loop. A bad loop with great tools still mostly works. A great loop
with bad tools falls apart constantly, and the failure looks like "the
model is dumb," when the actual problem is upstream, in what you gave it
to work with.

## Prerequisites

- **Lesson 02, in full** — this lesson assumes the loop and its
  vocabulary (turn, iteration, tool call, observation) are second nature.
- **Module 13, Lesson 04's own tool-definition mechanics** (the JSON
  Schema shape) — this lesson is about *design decisions*, not the syntax
  those decisions get expressed in, which you already know.

## The concept, explained simply

Think about designing a public API for a class in a game engine — say,
an inventory system other programmers on your team will call into. You
wouldn't expose one giant `modifyInventory(action: string, ...)` function
that branches internally on a string like `"add"` or `"remove"` or
`"equip"` — you'd expose `addItem()`, `removeItem()`, `equipItem()`, each
with its own clear signature, because that's what lets a caller (and an
IDE's autocomplete) understand what's possible without reading your
implementation. Designing tools for an LLM agent is the *exact* same
discipline, with one twist: the "caller" reading your API surface isn't a
human programmer with access to your source code — it's a model deciding,
from nothing but each tool's name, description, and parameter schema,
which one (if any) fits what it's trying to do right now. A vague,
overloaded, or badly-described tool doesn't produce a compiler error the
way a bad API might for a human — it produces a *wrong tool call*, silently,
that you only notice when the agent's behavior looks off.

## The details

### What makes a tool description good

An LLM decides whether and when to call a tool almost entirely from its
`description` field — not from your own mental model of what the tool
does. Compare these two descriptions for the exact same underlying
function:

```python
# Weak -- describes only WHAT, never WHEN
{"name": "search", "description": "Searches quest notes."}

# Strong -- describes what, when, and what it returns
{
    "name": "search_quest_notes",
    "description": (
        "Search one specific quest's own notes for content relevant to a "
        "question. Returns the most relevant excerpts, each labeled with "
        "the note they came from. Use this before answering any question "
        "about what a quest's notes say."
    ),
}
```

The second version — the real one from this module's own
`app/agent.py` — earns its extra length. It tells the model three
separate things a name alone never could: *what* the tool does, *when*
to reach for it ("use this before answering any question about..."), and
*what shape* to expect back ("excerpts... labeled with the note they came
from"). Current guidance on tool design (this course's own research, live
as of August 2026) is explicit that being *prescriptive about when to
call a tool* — not just what it does — measurably improves whether a
model reaches for it at the right moment, especially on models that have
gotten more conservative about tool use over time. Under-describing a
tool is a far more common mistake than over-describing one.

### Narrow tool vs. a flag on a general one

Here's a real design decision this module's own `app/agent.py` makes,
worth understanding in full: QuestLog's agent has both `update_quest`
(a general tool: change any field) *and* `complete_quest` (a specific
tool: just mark it done). Why not fold "mark it done" into `update_quest`
as `{"done": true}`?

Two real reasons, not just taste:

1. **The common case should be the easy case.** "I finished this quest"
   is almost certainly the single most frequent thing a player will ever
   ask this agent to do. A dedicated `complete_quest(quest_id)` tool
   means the model only has to get one argument right, every time,
   instead of remembering that "done" is spelled `done`, is a boolean,
   and needs `true` rather than `"true"` — every extra degree of freedom
   in a tool's schema is one more way a call can go subtly wrong.
2. **Narrower tools are easier to reason about, log, and guard.** If you
   ever wanted to add a confirmation step before *any* quest gets marked
   complete (not something this module's own QuestLog does, but a
   realistic ask), a dedicated `complete_quest` tool gives you exactly
   one call site to gate. A generic `update_quest` would require
   inspecting *which fields changed* on every single call to tell
   "renamed a quest" apart from "marked it done" — solvable, but strictly
   harder, for no benefit once the dedicated tool exists.

The general rule: **promote an action to its own tool when it's common,
security-sensitive, or benefits from a narrower, harder-to-misuse
schema.** Keep a general tool (`update_quest`) around for the long tail of
"change some fields" work a dedicated tool for every single field
combination would be absurd to hand-enumerate.

### Multi-step reasoning: chaining tool calls to answer one question

"Multi-step reasoning" sounds like it needs some special technique. It
doesn't — it's simply what happens naturally when a question can't be
answered from one tool call alone, and the loop from Lesson 02 lets the
model ask for a second one once it has the first result. Concretely,
picture a player asking this module's own QuestLog agent: *"What should I
bring for the dragon fight?"*

The model has no `quest_id` for "the dragon fight" — it's a title, not an
id, and none of this agent's tools accept a title directly (a real,
deliberate design choice — see Lesson 10 for why). So a well-designed
agent, with a system prompt that says so (see this module's own
`app/agent.py`'s own `SYSTEM_PROMPT`), reasons in two steps:

1. **Iteration 1:** call `list_quests()` with no filter, to see what
   exists and find the id behind whichever quest's title matches "the
   dragon fight."
2. **Iteration 2:** now that it has a real `quest_id`, call
   `search_quest_notes(quest_id=..., question="What should I bring?")`.
3. **Iteration 3:** with the retrieved excerpts in hand, write the final,
   cited answer.

Three iterations, one user question, no special "multi-step" mode to
turn on — just the ordinary loop, given tools whose *inputs* naturally
chain (one tool's typical output, a quest id, is exactly what a later
tool needs as input). This is precisely why `list_quests` exists as its
own tool in this module's own agent, rather than being folded away:
without it, there would be no way for the model to go from "a title the
player typed" to "a real id another tool needs," and multi-step
reasoning like the example above simply couldn't happen.

**Try it yourself:** Using Lesson 02's own `minimal_agent.py`, add a
third tool, `get_weather(city: str)`, backed by a small hard-coded
dictionary of three cities. Script a fake conversation where the user
asks "What's 10 times the temperature in Paris?" — this needs the model
to call `get_weather` *first*, then `calculate` with whatever number came
back. Write the two scripted `final(...)` turns by hand before running
it, predicting exactly what each one should contain.

### Parallel tool calls

The model can also ask for **more than one tool in a single iteration** —
a single `response.content` list can contain several `tool_use` blocks at
once, if the model judges they're independent of each other (for
example, checking three separate quests' notes for the same question, or
creating two unrelated quests at once). Your own loop code already
handles this correctly if — like Lesson 02's `run_agent` — it iterates
over *every* `tool_use` block in `response.content` and collects *all*
their results into a single `tool_results` list before sending them back
in one user turn. The API's own rule (already covered in Module 13) is
strict about this: every `tool_use` block in one assistant turn needs a
matching `tool_result` in the very next user turn, all together — sending
them back split across multiple separate messages silently trains the
model to stop making parallel calls at all, since it looks to the model
like its own requests aren't all being honored together.

## Common mistakes & gotchas

- **A tool description that only restates its name.**
  `{"name": "get_weather", "description": "Gets the weather"}` tells the
  model nothing about *when* to use it versus not, or what shape the
  answer takes. If you can't think of at least one extra sentence beyond
  what the name already says, the tool probably needs a better name, a
  better description, or both.
- **One tool trying to do too many unrelated things.** A `manage_quest`
  tool that takes an `action` string (`"create"`, `"update"`, `"delete"`,
  `"complete"`) and branches internally is the exact overloaded-function
  anti-pattern this lesson opened with — split it into separate,
  named tools instead.
- **Too many tools, with heavy overlap.** If two tools do almost the same
  thing, the model has to guess which one you actually meant for a given
  situation — and it will guess wrong sometimes. Fewer, clearly-bounded
  tools consistently outperform many overlapping ones.
- **Assuming "multi-step" requires special prompting tricks.** It doesn't
  — it falls out for free from well-designed tools whose natural inputs
  and outputs chain, plus a system prompt that tells the model the order
  that chaining should usually happen in (see this module's own
  `app/agent.py`'s `SYSTEM_PROMPT`, which explicitly says to call
  `list_quests` first when a player refers to a quest by title).

## How this connects

Lesson 02 gave you the loop; this lesson gave you the judgment to decide
what goes *inside* it. Lesson 04 adds the next real ingredient — memory
and planning — because even a perfectly-designed tool surface needs
somewhere to keep track of what's already happened across more than one
turn. Lesson 10 shows you QuestLog's own six real tools
(`list_quests`, `create_quest`, `update_quest`, `complete_quest`,
`search_quest_notes`, `suggest_quest_breakdown`) applying every principle
from this lesson for real — including the deliberate absence of a
`delete_quest` tool at all, which Lesson 08 explains as a guardrail
decision, not an oversight.

## Quick self-check

1. Why does a tool's `description` field matter more than its `name` for
   getting a model to call it at the right moment?
2. Give the two real reasons this lesson gives for `complete_quest`
   existing as its own tool instead of being a flag on `update_quest`.
3. Walk through, step by step, how an agent with `list_quests` and
   `search_quest_notes` (but no tool that accepts a quest *title*
   directly) answers a question about a quest the player only referred to
   by name.
4. What API-level rule governs how tool results must be returned when the
   model requests more than one tool in a single iteration?
5. What's the concrete downside of having two tools that do almost the
   same thing, even if each one individually is well-designed?
