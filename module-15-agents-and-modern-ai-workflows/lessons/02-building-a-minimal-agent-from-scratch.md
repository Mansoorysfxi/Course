# Lesson 02 — Building a Minimal Agent from Scratch

## What you'll learn

- How to write a complete, working agent loop in raw Python — no
  LangChain, no CrewAI, no Anthropic SDK "tool runner" helper, just the
  `anthropic` client and a `for` loop.
- How to structure tool definitions, dispatch a tool call to real Python
  code, and feed the result back to the model.
- How to run this loop with **zero cost and zero API key**, so you can
  watch every mechanical step before you ever spend a cent — and then
  run the identical code path against the real API once you're ready.

## Why this matters

The master plan for this course is explicit: build one of these by hand,
with no framework, so nothing about "an agent" is ever magic to you.
Every framework covered later in this module (Lesson 07) — LangGraph,
CrewAI, the OpenAI Agents SDK — is, underneath its own abstractions,
running a loop shaped exactly like the one you're about to write. Once
you've built it yourself, you'll be able to look at any framework's docs
and immediately recognize which part of *this* loop each piece of its API
maps to, instead of taking the framework's word for what it's doing.

## Prerequisites

- **Lesson 01, in full** — this lesson writes the exact loop that one
  described in prose.
- **Module 13, Lesson 04 (tool use)** — the tool-definition JSON shape
  (`name`, `description`, `input_schema`) and the `tool_result` shape are
  assumed, not re-taught.

## The concept, explained simply

You're about to write the same four-step loop from Lesson 01 —
observe → decide → act → observe — as an actual Python `for` loop that
calls `client.messages.create(...)` once per iteration, checks
`response.stop_reason`, and either runs a tool or returns the model's
final answer. Nothing here is different in kind from the tool-use round
trip Module 13 already taught; this lesson's whole contribution is
letting that round trip *repeat*, capped at a small, fixed number of
iterations, instead of running exactly once.

## The details

### Step 1 — Define the tools

Two small, self-contained tools: a calculator, and a clock. Neither
touches a database or the network — kept deliberately simple so this
lesson is about the *loop*, not about any particular tool's own
complexity (Lesson 03 covers what makes a tool well-designed).

```python
TOOLS = [
    {
        "name": "calculate",
        "description": "Evaluate a basic arithmetic expression, e.g. '2 + 2 * 10'.",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    },
    {
        "name": "get_current_time",
        "description": "Get the current UTC time as an ISO-8601 string.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]
```

This is the exact same shape (`name`/`description`/`input_schema`) every
tool definition in this entire course has used since Module 13 — nothing
new here.

### Step 2 — Write the code that actually runs a tool

The model can only ever *ask* for a tool to run (Lesson 01's own "the
model can't touch the real world" point) — this function is the one place
that request turns into a real action:

```python
def run_tool(name: str, tool_input: dict) -> str:
    if name == "calculate":
        # A real production tool would never use eval() on arbitrary,
        # model-supplied text -- see Lesson 08's own sandboxing section.
        # This is a teaching example with a narrow, hand-checked allowlist.
        allowed = set("0123456789+-*/(). ")
        expr = tool_input["expression"]
        if not set(expr) <= allowed:
            return "Error: expression contains disallowed characters."
        return str(eval(expr, {"__builtins__": {}}, {}))
    if name == "get_current_time":
        import datetime
        return datetime.datetime.now(datetime.UTC).isoformat()
    return f"Error: unknown tool '{name}'"
```

**Try it yourself, before running the full agent:** call
`run_tool("calculate", {"expression": "3 + 4 * 2"})` directly in a Python
shell. Predict the output (order of operations matters!) before running
it.

### Step 3 — The loop itself

This is the entire agent. Read it line by line before running anything:

```python
MAX_ITERATIONS = 5

def run_agent(client, user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    for iteration in range(1, MAX_ITERATIONS + 1):
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            tools=TOOLS,
            messages=messages,
        )
        print(f"-- iteration {iteration}: stop_reason={response.stop_reason}")

        if response.stop_reason != "tool_use":
            # Decide step said "I'm done" -- no more tools requested.
            return next(b.text for b in response.content if b.type == "text")

        # Act: echo the assistant's own turn back into history first --
        # the API needs to see exactly what it asked for, matched up with
        # exactly what you're about to tell it happened.
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"   tool call: {block.name}({block.input})")
                result = run_tool(block.name, block.input)
                print(f"   tool result: {result}")
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": result}
                )
        # Observe: the tool results go back in as a user turn.
        messages.append({"role": "user", "content": tool_results})

    return "Gave up after too many steps."
```

Every line here maps to one of Lesson 01's four steps:

- `client.messages.create(...)` — **observe** the current `messages` list
  (everything that's happened so far), and let the model **decide**.
- `if response.stop_reason != "tool_use": return ...` — the model decided
  it's done. This is the loop's "good" termination condition.
- The `for block in response.content` loop — **act**: for every tool the
  model asked for, actually run it.
- `messages.append({"role": "user", "content": tool_results})` —
  **observe** again: the tool's real output becomes the next thing the
  model sees.
- `for iteration in range(1, MAX_ITERATIONS + 1)` and the final
  `return "Gave up..."` — the loop's "bad" termination condition, a real
  guardrail (Lesson 08 goes deep on exactly this pattern).

### Step 4 — Run it, with or without a real API key

**Live-verified in this course's own environment on August 9, 2026** (no
`ANTHROPIC_API_KEY` was available while writing this lesson): the fake
client below, and everything from `run_agent` up, ran exactly as printed.
The *loop mechanics* you're about to watch are the real thing — only the
model's responses are scripted, standing in for what a real Claude call
would return.

```python
# ---- A tiny fake client, so this script runs with no API key at all ----
from types import SimpleNamespace

class FakeMessages:
    def __init__(self, turns):
        self._turns = iter(turns)
    def create(self, **kwargs):
        return next(self._turns)

class FakeClient:
    def __init__(self, turns):
        self.messages = FakeMessages(turns)

def text_block(text):
    return SimpleNamespace(type="text", text=text)

def tool_use_block(id_, name, input_):
    return SimpleNamespace(type="tool_use", id=id_, name=name, input=input_)

def final(content, stop_reason):
    return SimpleNamespace(content=content, stop_reason=stop_reason)


if __name__ == "__main__":
    import os

    if os.environ.get("ANTHROPIC_API_KEY"):
        import anthropic
        client = anthropic.Anthropic()
    else:
        print("No ANTHROPIC_API_KEY set -- running against a scripted fake client instead.\n")
        client = FakeClient(turns=[
            final(
                [tool_use_block("t1", "calculate", {"expression": "12 * (3 + 4)"})],
                stop_reason="tool_use",
            ),
            final([text_block("12 * (3 + 4) is 84.")], stop_reason="end_turn"),
        ])

    answer = run_agent(client, "What is 12 times the sum of 3 and 4?")
    print("\nFinal answer:", answer)
```

Save the whole file (Steps 1–4, in order) as `minimal_agent.py` and run:

```bash
python minimal_agent.py
```

**Expected output, live-verified exactly as shown (with no
`ANTHROPIC_API_KEY` set):**

```
No ANTHROPIC_API_KEY set -- running against a scripted fake client instead.

-- iteration 1: stop_reason=tool_use
   tool call: calculate({'expression': '12 * (3 + 4)'})
   tool result: 84
-- iteration 2: stop_reason=end_turn

Final answer: 12 * (3 + 4) is 84.
```

**If you do have a real `ANTHROPIC_API_KEY` set**, the exact same
`run_agent` function runs against `anthropic.Anthropic()` instead of
`FakeClient` — nothing about the loop changes, only where the "decide"
step's answer is actually coming from. This course could not verify that
live path in the environment it was written in (no key was available) —
label any output you get from the real path in your own notes as
something *you* observed, since this lesson's own printed output above is
the fake-client path only.

**Try it yourself:** Ask it `"What is 12 times the sum of 3 and 4, and
what time is it right now?"` — a question needing *two* different tools.
If you're using the fake client, you'll need to script two `tool_use`
blocks in one `final(...)` turn (the model can request more than one tool
at once — Lesson 03 covers this "parallel tool calls" pattern). Predict
how many iterations it takes before writing the fake turns.

## Common mistakes & gotchas

- **Forgetting to append the assistant's own turn to `messages` before
  appending the tool results.** The Anthropic API validates that every
  `tool_use` block has a matching `tool_result` in the very next turn —
  skip the assistant append and you'll get a 400 error complaining about
  mismatched or missing tool results.
- **Returning the tool result as a raw Python object instead of a string.**
  `content` in a `tool_result` block must be a string (or a specific
  content-block structure) — `run_tool` above always returns `str`,
  deliberately, even for a numeric answer.
- **No cap on iterations.** Delete `MAX_ITERATIONS` (or set it absurdly
  high) and a model that gets stuck calling the same tool repeatedly — a
  real, documented failure mode, not a hypothetical — will run until it
  hits the API's own hard limits or your patience, whichever comes first,
  and you'll be billed for every one of those calls. This is not a
  contrived worry; it's exactly why Lesson 08 treats a loop cap as
  non-negotiable.
- **`eval()` in a real tool.** The calculator tool above uses `eval()`
  with a narrow character allowlist purely so this lesson's own example
  stays short — it is not a pattern to reuse for anything a real user (or
  a real model, which is influenced by whatever a user or an attacker
  puts in front of it via prompt injection) can influence with untrusted
  input. Lesson 08 covers real tool-execution sandboxing.

## How this connects

You've now built, by hand, the exact mechanism every tool-using AI
product in this course (and most of the industry) runs on. Lesson 03
asks the next real question: given that a tool's own definition shapes
how well an agent uses this loop, what makes a *good* tool? Lesson 04
adds memory and planning on top of this same loop. By Lesson 10, you'll
recognize QuestLog's own `app/agent.py` as this exact same shape, with
six tools instead of two and a real database and a real Claude
connection behind it — not a new thing to learn, an application of what
you just built.

## Quick self-check

1. Walk through `run_agent`'s loop body line by line, in your own words,
   naming which of Lesson 01's four steps each line belongs to.
2. Why must the assistant's own turn (`response.content`) be appended to
   `messages` before the tool results are appended?
3. What would happen — mechanically, not just "it would fail" — if
   `MAX_ITERATIONS` didn't exist and a tool's own implementation had a bug
   that made the model call it again every single time, forever?
4. Why is `run_tool`'s calculator implementation explicitly called out as
   unsafe for a real production tool, even though it works correctly in
   this lesson's own example?
5. If you swapped `client` for a *different* fake object whose
   `.messages.create(...)` always returned a `tool_use` response, no
   matter what, what would `run_agent` eventually print, and why?
