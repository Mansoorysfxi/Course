# Lesson 04 — Tool Use and Function Calling: The Full Round-Trip, Minutely

**Verified against (August 2026), via live fetch of official Anthropic
documentation on August 9, 2026:**

| Fact | Verified value | Source |
|---|---|---|
| Tool definition shape | `{"name": ..., "description": ..., "input_schema": <JSON Schema>}` inside the `tools` list | Anthropic's own Messages API tool-use reference |
| Round-trip content block types | `tool_use` (in a response) and `tool_result` (in a follow-up request) | Same |
| `stop_reason` when Claude wants to call a tool | `"tool_use"` | Same |
| Multiple tool calls in one turn | Supported — the API may return several `tool_use` blocks in one response; all their `tool_result`s must be returned together, in a single follow-up user message | Same |
| A beta convenience helper exists | Yes — `client.beta.messages.tool_runner(...)` automates the loop this lesson teaches manually | Anthropic's own Python SDK tool-use reference |

This lesson teaches the **manual loop**, not the beta `tool_runner`
helper, on purpose: QuestLog's own capstone (Lesson 07) combines tool use
with streaming and structured output in one custom loop, and the
clearest way to understand *why* that loop is shaped the way it is, is to
have built the plain version yourself first. The beta helper is
mentioned at the end of this lesson so you know it exists for simpler,
non-streamed cases.

## What you'll learn

- What "tool use" actually is: a real mechanism for a model to request
  that *your code* do something and hand the result back — not the model
  executing anything itself.
- The complete, real round-trip, step by step: how Claude asks for a
  tool, what your code has to do with that request, and how the result
  gets back to Claude so it can continue.
- How to define a tool's schema, run it, and hand results back correctly
  — including when Claude asks for more than one tool at once.
- Why a manual loop needs a hard iteration cap, and what happens if a
  tool itself fails.

## Why this matters

Every LLM's actual knowledge is frozen at training time and limited to
whatever's in its context window (Module 12, Lesson 06). It cannot look
up today's date, check a real database, or know what quests a specific
QuestLog player already has — unless something *gives* it that
information. Tool use is the real, general mechanism for that: Claude
decides, mid-conversation, that it needs a specific piece of outside
information or wants a specific action performed, asks for it in a
structured way, and continues once it has an answer. QuestLog's own AI
assistant (Lesson 07) uses this for real: before suggesting sub-quests,
it can ask to see the player's other quest titles, so it doesn't suggest
a duplicate.

## Prerequisites

- **Lesson 01 in full** — tool use adds one new parameter, `tools`, to
  the exact same request shape everything else in this module builds on.
- **Module 05's Pydantic/JSON Schema material** — a tool's `input_schema`
  is a JSON Schema, the same vocabulary Lesson 03 just used for structured
  outputs.
- **Module 01's function/dict fundamentals** — this lesson's loop passes
  plain Python dicts and lists around; nothing exotic, but you should be
  comfortable reading and building nested dict/list structures quickly.

## The concept, explained simply

Think of tool use the way you'd think about an NPC's utility-AI system
pausing its own decision-making to call out to the actual game world for
real data it doesn't already have — "what's the player's current
inventory?" — rather than guessing or hallucinating an answer from
whatever it happens to remember. The NPC's AI doesn't *become* the
inventory system; it asks a specific, well-defined question, waits for
the game world's real answer, and then resumes its own reasoning with
that answer folded in. Tool use works exactly the same way: Claude
doesn't gain the ability to run code, query a database, or check a file
system by itself — it only gains the ability to say, in a precise,
structured way, "I need you (your application code) to run this specific
function with these specific arguments, and tell me what it returns."
Your code is the one and only thing that actually *executes* anything.
Claude's role is deciding *when* to ask and *what* to do with the answer.

## The details

### Step 1 — Define a tool

A tool definition has exactly three parts: a `name`, a `description`, and
an `input_schema` — the same JSON Schema vocabulary Lesson 03 used for
structured outputs, describing what arguments this tool needs.

```python
GET_QUEST_LINE_COUNT_TOOL = {
    "name": "get_quest_line_count",
    "description": (
        "Returns how many quests currently exist in a given quest line "
        "(e.g. 'Main Story', 'Side Quests'). Call this when you need to "
        "know how large a quest line already is before suggesting whether "
        "to add more quests to it."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "quest_line": {"type": "string", "description": "The exact quest line name."},
        },
        "required": ["quest_line"],
    },
}
```

**The `description` field matters far more than it looks like it should.**
Claude decides *whether* and *when* to call a tool almost entirely based
on this text — a vague description ("looks up quest info") gets called
inconsistently or at the wrong moments; a specific one, stating exactly
when to use it, gets called reliably. This is the single highest-leverage
thing to get right when writing a tool.

### Step 2 — Pass it in, and see Claude ask for it

```python
# tool_round_trip.py
import anthropic

client = anthropic.Anthropic()

messages = [
    {"role": "user", "content": "Is the Side Quests line getting too big? It has room for a few more."},
]

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=300,
    tools=[GET_QUEST_LINE_COUNT_TOOL],
    messages=messages,
)

print(f"Stop reason: {response.stop_reason}")
for block in response.content:
    print(block.type)
```

*A response along these lines:*

```
Stop reason: tool_use
text
tool_use
```

Two content blocks came back: a short `text` block (Claude sometimes
narrates briefly before calling a tool — "Let me check how many quests
are already in that line.") and a `tool_use` block. `response.stop_reason`
is `"tool_use"` — this is the API's own, explicit signal that Claude
isn't finished; it's paused, waiting on information only your code can
provide.

### Step 3 — Inspect exactly what Claude is asking for

```python
tool_use_block = next(block for block in response.content if block.type == "tool_use")
print(tool_use_block.id)      # e.g. "toolu_01A2b3C4..."
print(tool_use_block.name)    # "get_quest_line_count"
print(tool_use_block.input)   # {"quest_line": "Side Quests"} -- already a parsed dict
```

Three fields, and all three matter for what comes next: `.id` is a unique
identifier for *this specific* tool call — you'll need to echo it back
exactly, unchanged, when you reply. `.name` tells you *which* tool Claude
wants (you may have several tools available at once; a real application
branches on this). `.input` is the arguments Claude decided on, already
parsed into a real Python dict — never a raw JSON string you have to
`json.loads()` yourself.

### Step 4 — Actually run it, and send the result back

This is the step that makes tool use real rather than theoretical: **your
code**, not Claude, executes the actual logic.

```python
def get_quest_line_count(quest_line: str) -> int:
    # A stand-in for a real database query (app/repository.py, in
    # QuestLog's real backend) -- this is exactly the kind of real,
    # external information Claude cannot know on its own.
    fake_data = {"Main Story": 3, "Side Quests": 7, "Village Errands": 2}
    return fake_data.get(quest_line, 0)


result = get_quest_line_count(**tool_use_block.input)
print(result)  # 7
```

The result now has to go back to Claude, as a **new message with role
`"user"`**, containing a `tool_result` block that names, via
`tool_use_id`, exactly which tool call this answers:

```python
messages.append({"role": "assistant", "content": response.content})
messages.append({
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": tool_use_block.id,
            "content": str(result),
        }
    ],
})
```

**Both of these appends matter, and in this order.** The first line
echoes Claude's *own* turn — including the `tool_use` block itself — back
into the conversation history exactly as it came, because the API needs
to see, in the history, that a tool was requested before it can make
sense of a `tool_result` answering it. The second line is the actual
answer, as a `user`-role message (from the API's point of view, "the
outside world responding" is modeled as a user turn, the same way a
person typing a reply is). `tool_use_id` must match `tool_use_block.id`
**exactly** — this is how Claude (and the API) know which of possibly
several pending tool calls this particular result belongs to.

### Step 5 — Send the follow-up request, and get the real final answer

```python
response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=300,
    tools=[GET_QUEST_LINE_COUNT_TOOL],
    messages=messages,
)

print(f"Stop reason: {response.stop_reason}")
print(response.content[0].text)
```

*A response along these lines:*

```
Stop reason: end_turn
Side Quests already has 7 quests -- that's a healthy-sized line already,
so I'd suggest starting a new quest line rather than adding more here.
```

`stop_reason` is now `"end_turn"` — Claude has everything it needs and
has produced its real, final answer, one that genuinely reflects the
real number your tool returned (7), not a guess.

### The full round-trip, as one loop

Steps 2 through 5 above are really one repeatable pattern: keep calling
the API and responding to tool requests until `stop_reason` is no longer
`"tool_use"`. Here's the same conversation as a proper loop, handling
**any** number of tool calls Claude might make, including more than one
at once:

```python
# tool_round_trip_loop.py
import anthropic

client = anthropic.Anthropic()
tools = [GET_QUEST_LINE_COUNT_TOOL]
messages = [
    {"role": "user", "content": "Compare how full 'Side Quests' and 'Main Story' are."},
]

MAX_ITERATIONS = 5

for _ in range(MAX_ITERATIONS):
    response = client.messages.create(
        model="claude-haiku-4-5", max_tokens=300, tools=tools, messages=messages,
    )

    if response.stop_reason != "tool_use":
        break  # Claude has its final answer

    messages.append({"role": "assistant", "content": response.content})

    # A single turn can contain MULTIPLE tool_use blocks -- e.g. Claude
    # decided to check both quest lines' counts before answering. Every
    # single one needs its own tool_result, and ALL of them go back
    # together, in ONE user message -- never split across several.
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = get_quest_line_count(**block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(result),
            })
    messages.append({"role": "user", "content": tool_results})
else:
    print("Gave up after too many tool-use iterations.")

print(response.content[0].text if response.stop_reason != "tool_use" else "(no final answer)")
```

**Why `MAX_ITERATIONS` exists at all:** every iteration of this loop is a
real, billed API call. A model that (unusually) keeps requesting tools
without ever settling on a final answer would otherwise turn one user
request into an unbounded number of paid calls. Capping the loop —
QuestLog's real backend (Lesson 07) uses the exact same pattern, as
`MAX_TOOL_ITERATIONS` — is a cost-safety measure as much as a
correctness one; Lesson 05 covers cost management in more depth.

### When a tool itself fails

Real tools can fail — a database query errors, an external lookup times
out. Tell Claude about it explicitly, using `is_error: True`, rather than
silently returning nothing or crashing your own code:

```python
tool_results.append({
    "type": "tool_result",
    "tool_use_id": block.id,
    "content": "Error: no quest line named 'Bandit Camp' exists.",
    "is_error": True,
})
```

Claude reliably adapts to an error result — trying a different approach,
asking a clarifying question, or apologizing and moving on — precisely
*because* it was told plainly that something went wrong, instead of
receiving a result that looks superficially valid but is actually
garbage or empty.

**Try it yourself:** Change the `tool_results.append(...)` call above to
omit `is_error: True` on a genuine error case (just return the plain
error string as if it were a normal, successful result). Ask a question
that should trigger this exact failure and compare Claude's two
responses side by side — with and without the flag. The difference is
usually visible: without it, Claude tends to treat the error string as if
it were real, valid data.

### Controlling *whether* Claude uses a tool: `tool_choice`

By default (`tool_choice: {"type": "auto"}`, which you never have to
write explicitly since it's already the default), Claude decides for
itself whether a tool is needed. Three other values exist for less common
cases: `{"type": "any"}` forces it to use *some* tool; `{"type": "tool",
"name": "..."}` forces one specific tool; `{"type": "none"}` disables
tool use for this request even though `tools` is still provided (useful
if you want the schema/definitions available for a later turn in the same
conversation, but not this one).

## Common mistakes & gotchas

- **Forgetting to echo the assistant's `tool_use` turn back into
  `messages` before appending the `tool_result`.** The follow-up request
  fails validation (or, worse, silently confuses the model) if the
  history doesn't show a tool being requested before it shows one being
  answered.
- **Mismatched or missing `tool_use_id`.** If a turn has multiple
  `tool_use` blocks, every single one needs its own `tool_result` with
  the *exact* matching id — dropping one, or answering the wrong one, is
  a real and common bug in a hand-written loop.
- **Splitting multiple `tool_result`s across separate messages** instead
  of one single `user` message containing all of them. The API expects
  every result answering one turn's tool calls to arrive together.
- **Writing a vague tool `description`** and being surprised the model
  either never calls it or calls it at the wrong moments. Revisit this
  lesson's "Step 1" note — the description is doing almost all of the
  work of teaching Claude *when* to reach for the tool.
- **No iteration cap on a manual loop.** Even though it's rare in
  practice for a model to loop forever, an uncapped `while True:` loop
  with no `MAX_ITERATIONS` is a real, if unlikely, cost and correctness
  risk — always bound it, as this lesson's loop example does.
- **Assuming Claude "runs" the tool.** It never does. If your code has a
  bug in `get_quest_line_count` above, or never actually calls it at all
  after seeing a `tool_use` block, Claude has no way to know or fix
  that — from its side, it's still just waiting for a `tool_result` that
  may never come.

## How this connects

This lesson's manual loop — call, check `stop_reason`, execute, respond,
repeat — is exactly the shape QuestLog's real backend uses in Lesson 07,
with two things added on top: every turn is opened with `.stream()`
(Lesson 02) instead of a plain call, and the *final*, non-tool-use turn
also carries `output_config.format` (Lesson 03), so the answer Claude
eventually settles on is guaranteed to match a schema. Nothing about the
round-trip itself changes — you're combining three lessons' worth of
parameters on the same underlying request/response cycle, not learning a
fourth, different mechanism. Lesson 05 is next: what happens when a call
in this loop — or any call in this module — fails outright (a rate limit,
a timeout, an overloaded server), and how to handle that honestly instead
of letting one bad request take down a whole feature.

## Quick self-check

1. Walk through the full round-trip from memory, in order: what does
   Claude send when it wants a tool, what does your code do with that,
   and what does your code send back?
2. Why must both the assistant's `tool_use` turn *and* your
   `tool_result` response both be appended to `messages`, in that order,
   before the next request?
3. If Claude's response contains two `tool_use` blocks in the same turn,
   how many `tool_result` blocks do you need to send back, and in how
   many separate messages?
4. Why does a manual tool-use loop need a hard iteration cap, even though
   it's unusual for a model to actually hit it?
5. What does `is_error: True` on a `tool_result` actually do, and why is
   it better than silently returning an empty or fake-looking result when
   a tool genuinely fails?
