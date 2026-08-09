# Lesson 03 — Structured Outputs with Pydantic

**Verified against (August 2026), via live fetch of official Anthropic
documentation on August 9, 2026:**

| Fact | Verified value | Source |
|---|---|---|
| Native, schema-constrained JSON output exists | Yes — `output_config.format` on `messages.create()`/`messages.stream()`, or the higher-level `messages.parse()` helper | `platform.claude.com/docs/en/build-with-claude/structured-outputs` |
| Models supporting it (as of this lesson) | Claude Fable 5, Mythos 5, Opus 5, Opus 4.8/4.7/4.6, Sonnet 5, Sonnet 4.6, Opus 4.5, and **Claude Haiku 4.5** (`claude-haiku-4-5-20251001`) | Same page, fetched live |
| Works with streaming | Yes | Same page |
| Works with tool use in the same request | Yes — a documented, combined example exists | Same page |
| Does **not** work with | Citations, or an assistant-turn prefill | Same page |
| Unsupported JSON Schema features | `minLength`/`maxLength`, numeric `minimum`/`maximum`/`multipleOf`, array constraints beyond `minItems` of 0 or 1, recursive schemas, `additionalProperties` set to anything but `false` | Same page |

## What you'll learn

- Why "ask nicely for JSON" (Module 12, Lesson 07's own technique) isn't
  a guarantee, and what a *guarantee* actually looks like at the API
  level.
- How to constrain a Messages API response to a JSON Schema you define,
  using `output_config.format`.
- Why this backend still validates that JSON with a Pydantic model
  afterward, even though the API already promised it would match — and
  why that isn't redundant paranoia.
- Exactly which JSON Schema features are and aren't supported, so you
  design a schema that actually works the first time.

## Why this matters

Module 12, Lesson 07 ended with an honest caveat: prompting for JSON
("respond with ONLY valid JSON...") is a real, useful technique, but it's
still just the model predicting tokens one at a time — a sufficiently
unusual input could still produce something that doesn't parse. QuestLog's
real AI feature (Lessons 07-08) can't tolerate that: a quest-breakdown
response that fails to parse means a broken feature, not a slightly-off
answer. Structured outputs are the actual, production-grade answer to
that problem, and this lesson is where you learn them properly, before
QuestLog's capstone needs them for real.

## Prerequisites

- **Lesson 01 in full** — this lesson adds one new parameter,
  `output_config`, to the exact same request shape.
- **Module 12, Lesson 07's "structured outputs" section** — read it again
  if it's been a while; this lesson picks up exactly where that one's
  honest caveat left off.
- **Module 05's Pydantic lesson** — `BaseModel`, field types, and
  validation. This lesson assumes you're comfortable with Pydantic from
  building QuestLog's own request/response models in that module.

## The concept, explained simply

Think of `output_config.format` the way you'd think about a save-game
deserializer that validates a save file's structure the instant it's
loaded, rather than one that blindly trusts whatever bytes are on disk
and only discovers a corrupted field when your game crashes three minutes
later trying to read it. Prompting a model to "please respond in JSON" is
like *asking* a save file to be well-formed — usually it is, because the
model is generally good at this, but there's no hard guarantee. Structured
outputs are the API-level equivalent of a deserializer with a strict
schema: the response is *constrained*, during generation itself, to match
a shape you specify — Claude cannot produce a response that violates it,
the same way a well-designed save format cannot be loaded if its
structure doesn't match what the loader expects.

## The details

### The problem, demonstrated

Before the fix, here's a real illustration of exactly the gap Module 12,
Lesson 07 warned about. Plain prompting for JSON:

```python
# plain_json_prompt.py (illustrative -- do not need to run this)
messages = [{
    "role": "user",
    "content": (
        'Respond with ONLY valid JSON: {"sub_quests": ["...", "..."]}. '
        "Break down: Defeat the dragon guarding the old mine."
    ),
}]
```

This works the overwhelming majority of the time — but "the overwhelming
majority of the time" is not a number you can build a real feature's
error handling around. `output_config.format`, below, changes "usually
valid JSON" into "guaranteed to match this exact schema, or the request
tells you clearly why not" (Lesson 05 covers exactly which non-schema
outcomes — like a refusal — can still occur).

### Constraining the response with a raw JSON Schema

```python
# structured_raw_schema.py
import json
import anthropic

client = anthropic.Anthropic()

schema = {
    "type": "object",
    "properties": {
        "sub_quests": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"title": {"type": "string"}},
                "required": ["title"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["sub_quests"],
    "additionalProperties": False,
}

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=300,
    system="Break the quest into 2-4 short, actionable sub-quests.",
    output_config={"format": {"type": "json_schema", "schema": schema}},
    messages=[
        {"role": "user", "content": "Quest: Defeat the dragon guarding the old mine."},
    ],
)

text = response.content[0].text
print(text)
data = json.loads(text)
print(data["sub_quests"])
```

What's new versus Lesson 01: `output_config={"format": {"type":
"json_schema", "schema": schema}}`. `type: "json_schema"` tells the API
this response must conform to a schema you're providing (as opposed to
free-form text, the default); `schema` is a standard JSON Schema object,
the same vocabulary Module 05's own Pydantic/OpenAPI material already
introduced you to (`type`, `properties`, `required`) — this is not a
new, Anthropic-specific format to learn.

*A response along these lines:*

```
{"sub_quests":[{"title":"Scout the mine entrance and note patrol timing"},{"title":"Gather fire-resistant gear"},{"title":"Lure the dragon into the open"},{"title":"Strike during its recovery window"}]}
```

Notice: **no preamble, no "Here is the JSON you requested," no markdown
code fences** — just the raw JSON, because the schema constraint applies
to the entire text content, not just part of it. `json.loads(text)` on
this response is safe to call without a `try`/`except` guarding against
malformed output the way plain-prompted JSON genuinely would need — the
API's own guarantee already ruled that failure mode out (Lesson 05 covers
the failure modes that remain, like a refusal, which structured output
does *not* eliminate).

### The higher-level way: `messages.parse()` with a Pydantic model

Writing a raw JSON Schema by hand, then manually `json.loads()`-ing the
result, works but duplicates a shape you'd usually rather define once, as
a Pydantic model — exactly the way Module 05 defined request/response
shapes for QuestLog's own API. The SDK's `messages.parse()` helper does
both steps for you:

```python
# structured_parse_helper.py
from pydantic import BaseModel
import anthropic


class SubQuest(BaseModel):
    title: str


class QuestBreakdown(BaseModel):
    sub_quests: list[SubQuest]


client = anthropic.Anthropic()

response = client.messages.parse(
    model="claude-haiku-4-5",
    max_tokens=300,
    system="Break the quest into 2-4 short, actionable sub-quests.",
    messages=[
        {"role": "user", "content": "Quest: Defeat the dragon guarding the old mine."},
    ],
    output_format=QuestBreakdown,
)

breakdown = response.parsed_output  # a real QuestBreakdown instance, not a dict
for sub_quest in breakdown.sub_quests:
    print(sub_quest.title)
```

The SDK derives the JSON Schema from `QuestBreakdown` itself (the same
Pydantic model your application code already uses everywhere else) and
hands back `response.parsed_output` as an actual, typed `QuestBreakdown`
instance — not a raw dict you'd still have to validate by hand. This is
the pattern to reach for whenever your application already has (or
should have) a Pydantic model for the shape you want; the raw-schema
version from the previous section is what you reach for when you need
finer control than a plain Pydantic model conveniently gives you, or
you're calling `.stream()` directly (see below) rather than the
non-streaming `.parse()` helper, which does not have a streaming
equivalent as of this lesson.

### Why validate with Pydantic *again*, when the API already promised?

QuestLog's real backend (Lesson 07) uses the raw-schema approach above
*and* still runs the parsed result through a Pydantic model before
trusting it anywhere else in the code. This is not redundant — it's
**defense in depth**, the same principle Module 07's security lessons
taught for input validation in general: `output_config.format`
guarantees the response *matches the JSON Schema*, but a JSON Schema (per
the limitations table at the top of this lesson) cannot express every
constraint your application actually cares about — a minimum/maximum
count of sub-quests, a maximum title length, anything Pydantic's own
richer validation vocabulary (`Field(min_length=..., max_length=...)`)
handles that raw JSON Schema, in this API's currently-supported subset,
does not. There's also a second, more structural reason: a refusal or a
`max_tokens` truncation (Lesson 05) can still produce text that isn't
the schema-conformant JSON you expected at all — your own code needs to
handle that regardless of what the schema constraint promises for the
*normal* case.

```python
from pydantic import BaseModel, Field, ValidationError


class SubQuest(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class QuestBreakdown(BaseModel):
    # min_length/max_length here are real Pydantic validation, enforced
    # in this backend's own Python code -- NOT expressible in the raw
    # JSON Schema sent to the API (see this lesson's own limitations
    # table: "array constraints beyond minItems of 0 or 1" aren't
    # supported there).
    sub_quests: list[SubQuest] = Field(min_length=2, max_length=4)


try:
    breakdown = QuestBreakdown.model_validate_json(text)
except ValidationError as exc:
    print("Claude's response didn't meet this app's own requirements:", exc)
```

**Try it yourself:** Change `QuestBreakdown`'s `Field(min_length=2, max_length=4)`
to `Field(min_length=5)`, then run the validation above against this
lesson's own earlier four-sub-quest example response. Predict, before
running it, what the `ValidationError` message will say — then check
your prediction. This is the concrete proof that Pydantic's validation is
doing real, independent work here, not just re-checking what the schema
already guaranteed.

## Common mistakes & gotchas

- **Writing a JSON Schema with `minLength`, `maxLength`, `minimum`,
  `maximum`, or numeric array-size constraints and expecting the API to
  enforce them.** This lesson's own header table lists these as
  unsupported — the request won't error, but those constraints are
  silently ignored by the schema constraint itself. Enforce them in your
  own Pydantic model afterward instead, exactly as this lesson's last
  example does.
- **Forgetting `additionalProperties: false` on every object in the
  schema.** Anthropic's documented support requires it; leaving it off
  (or setting it to anything else) is one of the unsupported shapes.
- **Trying to combine structured output with citations or an
  assistant-turn prefill.** Both are explicitly documented as
  incompatible with `output_config.format` — this lesson's header table
  lists both. Reach for a system-prompt instruction instead of a prefill,
  the same replacement Module 12, Lesson 07 already hinted at.
- **Assuming a schema-conformant response means Claude's *content* is
  good, not just its *shape*.** Structured output guarantees the JSON
  parses and matches your schema — it says nothing about whether the
  suggestions inside it are actually sensible. That's a different
  problem, and it's exactly what Lesson 06's evaluation material exists
  to check.
- **Skipping the second, application-level Pydantic validation because
  "the API already guarantees it."** As this lesson's own explanation
  shows, the API's guarantee and your application's actual requirements
  are not the same thing — always validate what you actually need,
  separately.

## How this connects

Structured outputs solve the "is this response the shape my code
expects" problem the same way tool use (Lesson 04, next) solves a
different problem: "can the model get real, current information it
doesn't already have." QuestLog's capstone (Lesson 07) needs *both* at
once — a structured final answer, informed by a tool-use round-trip that
checks the player's existing quests first — and the Anthropic API
supports combining them in a single request, as this lesson's header
table confirms. Lesson 04 teaches tool use minutely, from scratch, before
Lesson 07 asks you to combine it with everything this lesson just taught.

## Quick self-check

1. What specifically does `output_config.format` guarantee about a
   response, and what does it *not* guarantee?
2. Name two JSON Schema features you might reasonably want (e.g. "between
   2 and 4 items in this array") that this API's structured-output
   support currently does not enforce, and say where you'd enforce them
   instead.
3. What's the difference between the raw-schema approach
   (`output_config={"format": {"type": "json_schema", "schema": ...}}`)
   and `messages.parse(..., output_format=SomePydanticModel)`? When would
   you reach for each?
4. Why does QuestLog's backend still run a Pydantic validation pass on a
   response that already came back schema-conformant from the API?
5. Name one thing structured output is explicitly documented as
   incompatible with, and what you'd use instead to get a similar effect.
