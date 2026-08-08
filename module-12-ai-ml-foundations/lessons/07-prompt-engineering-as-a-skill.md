# Lesson 07 — Prompt Engineering as a Real Skill

**Verified against (August 2026), via live fetch of Anthropic's own current
documentation and PyPI on August 8, 2026:**

| Fact | Verified value | Source |
|---|---|---|
| `anthropic` Python SDK version | `0.121.0`, released August 7, 2026 | PyPI project page |
| Model used in this lesson's examples | `claude-haiku-4-5` — Anthropic's cheapest current model | `platform.claude.com/docs/en/about-claude/pricing`, fetched live |
| Claude Haiku 4.5 pricing | $1.00 / million input tokens, $5.00 / million output tokens | Same page |
| Basic `client.messages.create(...)` call shape shown below | Confirmed current via Anthropic's own Messages API documentation | `platform.claude.com/docs/en/api/messages`, fetched live |

**An important, honest note before you read any further:** every example
response shown in this lesson is written as **"a response along these
lines"** — a realistic, carefully-considered illustration of what asking
Claude Haiku 4.5 this specific prompt would produce, based on how these
well-documented prompting techniques are known to change model behavior —
**not text this course's generation process personally observed from a
live API call.** No real Anthropic API key was available while writing this
specific lesson. Exercise 03 and this module's capstone both tell you,
explicitly, how to run these exact prompts for real yourself if you have a
key from Lesson 00's optional setup, and both treat a careful, honest
"dry run" — reading every example, predicting the real model's behavior,
and explaining *why* each technique should change the output the way this
lesson describes — as a completely legitimate way to complete this module,
exactly like Module 09 and Module 11 accepted dry runs for real
infrastructure they couldn't guarantee every learner would pay for.

## What you'll learn

- Why prompt engineering is a real, teachable skill with real technique —
  not "just typing the right magic words" — and *why* each technique below
  works, tied directly back to Lessons 05-06's next-token-prediction and
  sampling framing.
- What a **system prompt** is and how it differs from a regular user
  message.
- What **few-shot prompting** is, and why showing examples changes model
  behavior more reliably than describing what you want in the abstract.
- What **chain-of-thought (CoT) prompting** is, and why asking a model to
  "think step by step" measurably improves its accuracy on harder problems
  — mechanically, not magically.
- How to ask a model for **structured output** (like JSON) and why that's
  useful for real applications, previewing exactly the kind of thing
  Module 13 builds a whole AI feature around.
- The real, current, basic shape of an Anthropic API call in Python, so
  Module 13's much deeper API material starts from something familiar.

## Why this matters

This is the payoff lesson for the entire module. Everything from Lessons
01-06 — training, weights, tokens, embeddings, attention, context windows,
sampling — explains *why* an LLM behaves the way it does. Prompt
engineering is where that understanding becomes a *skill you can practice
and improve at*, rather than trivia. Module 13 assumes you already know
why a system prompt is different from a user message, why showing examples
works, and why asking a model to reason step by step helps — this lesson
is where all of that gets taught, before Module 13 needs it for QuestLog's
real AI assistant feature.

## Prerequisites

- **Lesson 06 in full** — every technique in this lesson is explained in
  terms of context windows, next-token prediction, and sampling from that
  lesson. Chain-of-thought specifically only makes sense once you
  understand that generated tokens become part of the context for later
  tokens (Lesson 05/06).
- **Lesson 00's setup** — if you're running any of this lesson's examples
  for real (fully optional), you'll need the Anthropic API key and SDK
  from that lesson's Steps 5-6.

## The concept, explained simply

A prompt isn't a magic incantation — it's the entire content of the context
window (Lesson 06) that the model's attention mechanism (Lesson 05) has
available when it starts predicting the response, token by token. Every
technique in this lesson works by deliberately shaping *what's actually in
that context* — adding instructions, adding examples, adding intermediate
reasoning space — so that the model's next-token predictions have better
material to draw on. This is exactly analogous to briefing an NPC's
utility-AI system before it makes a decision: the AI doesn't get smarter
just because you asked nicely, but if you give it richer, better-organized
input state to evaluate against (more relevant context, worked examples of
the kind of decision you want, room to "show its work" before committing),
its actual decisions measurably improve — not through magic, but because
you gave the exact same decision-making machinery better material to work
with.

## The details

### The basic shape of a real API call

Before diving into techniques, here's the real, current, minimal shape of
an Anthropic API call in Python — confirmed against Anthropic's own current
documentation (verified above). You'll see every technique below expressed
as variations on this same basic shape.

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=300,
    system="You are a helpful assistant.",     # the system prompt (optional)
    messages=[
        {"role": "user", "content": "Break down this quest into three steps: Defeat the dragon guarding the old mine."},
    ],
)
print(response.content[0].text)
```

Every line matters: `client = anthropic.Anthropic()` creates a client that
automatically reads your `ANTHROPIC_API_KEY` environment variable (Lesson
00, Step 5) — never hardcode a real key directly in a Python file. `model`
names exactly which model to run inference on (Lesson 01's "inference,"
made concrete). `max_tokens` caps how many tokens (Lesson 03) the response
is allowed to use — a hard ceiling, not a target. `system` is a special,
separate slot for instructions about *how the model should behave*,
distinct from the actual conversation (explained fully below). `messages`
is the actual conversation, as a list of `{"role": ..., "content": ...}`
dictionaries — `"user"` for things you say, `"assistant"` for things the
model said in an earlier turn (useful for multi-turn conversations, not
needed for a single request). `response.content[0].text` pulls the actual
generated text back out of the response object.

Module 13 goes much deeper into this API (streaming, tool use, error
handling, cost tracking) — this lesson only needs enough of it to run real
prompt-engineering experiments.

### System prompts

A **system prompt** is a single, separate instruction slot (the `system`
parameter above) that shapes the model's overall behavior, tone, and
persona for the entire conversation, distinct from anything the user
actually asks. Mechanically, it's still just text that ends up in the
context window before the actual conversation — but by convention (and by
how models are specifically trained), text placed in the `system` slot is
treated as higher-priority, more persistent instruction than a regular user
message, and it applies across every turn of a conversation rather than
needing to be repeated.

**Naive prompt (no system prompt at all):**
```python
messages=[{"role": "user", "content": "Break down this quest into steps: Defeat the dragon guarding the old mine."}]
```
*A response along these lines:* a reasonably generic breakdown — something
like "1. Gather information about the dragon's weaknesses. 2. Prepare
appropriate weapons and armor. 3. Travel to the old mine. 4. Confront and
defeat the dragon." — competent, but generic, with no particular voice or
format, because nothing in the context told the model what kind of
breakdown, tone, or format was actually wanted.

**With a system prompt:**
```python
system="You are QuestLog's quest-breakdown assistant. Break every quest into 3-5 short, actionable steps a player could actually check off. Use a slightly playful, RPG-flavored tone. Never break a quest into more than 5 steps."
messages=[{"role": "user", "content": "Break down this quest into steps: Defeat the dragon guarding the old mine."}]
```
*A response along these lines:* a response that actually follows the
step-count constraint and adopts the requested tone — something like "1.
Scout the old mine's entrance and note the dragon's patrol pattern. 2.
Stock up on fire-resistant gear before you go anywhere near its breath
weapon. 3. Bait the dragon into the open, away from the tunnels where its
tail can wreck you. 4. Land the killing blow while it's recovering from an
attack." — noticeably more specific, on-brand, and reliably bounded to the
requested step count, precisely because the system prompt's constraints are
now genuinely present in the context every single turn.

**Try it yourself (with or without a real API key):** Predict, before
reading either "a response along these lines" above, what a *third* version
would produce if the system prompt instead said "You are a terse, no-nonsense
drill sergeant. Never use more than 10 words total." Then compare your
prediction against how the earlier two differ.

### Few-shot prompting

**Few-shot prompting** means including a small number of worked examples of
the exact input-output pattern you want, directly in the prompt, before
asking the model to handle a new case. This works because you're not
*describing* the desired output format in the abstract — you're putting a
concrete, literal example of it directly into the context window, which
attention (Lesson 05) can directly draw on when predicting the new case's
tokens, rather than the model having to infer your intent from a
description alone. ("Zero-shot" is the term for the opposite — no examples
at all, just an instruction, exactly what every example earlier in this
lesson has been until now.)

```python
messages=[{
    "role": "user",
    "content": """Classify each quest's difficulty as Easy, Medium, or Hard.

Quest: "Fetch 5 herbs from the meadow." -> Easy
Quest: "Defeat the bandit captain and his lieutenant." -> Medium
Quest: "Slay the ancient dragon terrorizing the kingdom." -> Hard

Quest: "Deliver a letter to the next village over." ->"""
}]
```
*A response along these lines:* `Easy` — and, importantly, in exactly that
bare format, with no extra explanation or preamble, because the three
worked examples established both the *classification logic* (low-risk
errand vs. multi-enemy combat vs. legendary threat) and the *exact output
format* (just the label, nothing else) that the model then reliably
continues. A zero-shot version of the same request ("Classify this quest's
difficulty: Deliver a letter...") would likely still get the difficulty
roughly right, but with much less certainty about matching your exact
desired output format, since nothing in the context demonstrated it.

### Chain-of-thought (CoT) prompting

**Chain-of-thought prompting** means explicitly asking the model to reason
through a problem step by step *before* stating its final answer, rather
than jumping straight to a conclusion. This directly exploits the
next-token-prediction mechanism from Lesson 05: **every token the model
generates becomes part of the context for every subsequent token**, so if
you make the model generate genuine intermediate reasoning steps first,
those steps are then available as real, attended-to context when it goes to
generate the final answer — effectively giving the model "more thinking
material" to draw its final answer from, rather than forcing it to jump
straight from the question to a single answer token with no intermediate
work.

**Naive prompt:**
```python
messages=[{"role": "user", "content": "A player has completed 7 out of 12 quests in the 'Dragon's Bane' questline, each worth 150 XP, and has 340 XP already banked from other questlines. How much total XP does the player have?"}]
```
*A response along these lines:* a plausible-looking final number, but with
real risk of a silent arithmetic slip on a multi-step calculation like this
one, since nothing forced the model to lay out the intermediate steps
explicitly before committing to a final digit.

**With chain-of-thought:**
```python
messages=[{"role": "user", "content": "A player has completed 7 out of 12 quests in the 'Dragon's Bane' questline, each worth 150 XP, and has 340 XP already banked from other questlines. How much total XP does the player have? Think through this step by step before giving your final answer."}]
```
*A response along these lines:* something like "Step 1: 7 completed quests
× 150 XP each = 1,050 XP from this questline. Step 2: add the 340 XP
already banked: 1,050 + 340 = 1,390 XP total. **Final answer: 1,390 XP.**"
— the explicit intermediate multiplication and addition, laid out as real
generated tokens, is now sitting in the context by the time the model
generates the final answer, making an arithmetic slip meaningfully less
likely than jumping straight to a final number with no visible working.

This is precisely why "think step by step" reliably helps on multi-step
math, logic, and multi-constraint problems, and precisely why it helps far
less on simple factual lookups or purely creative tasks that don't benefit
from visible intermediate reasoning.

### Structured outputs

Real applications (like Module 13's QuestLog AI assistant feature) almost
never want a free-form paragraph back — they want data in a specific,
predictable shape they can parse and use in code. **Structured-output
prompting** means explicitly asking the model to respond in a specific
format, most commonly JSON, and being explicit about the exact shape.

```python
messages=[{
    "role": "user",
    "content": """Break down this quest into steps and respond with ONLY valid JSON, no other text, in exactly this shape:
{"quest": "<quest name>", "steps": ["<step 1>", "<step 2>", ...], "estimated_difficulty": "Easy" | "Medium" | "Hard"}

Quest: Defeat the dragon guarding the old mine."""
}]
```
*A response along these lines:*
```json
{"quest": "Defeat the dragon guarding the old mine", "steps": ["Scout the mine entrance and observe the dragon's patrol pattern", "Gather fire-resistant gear and healing supplies", "Lure the dragon into open ground away from narrow tunnels", "Strike during an opening after it exhales fire"], "estimated_difficulty": "Hard"}
```
Being explicit about the exact JSON shape (key names, whether a field is a
string or a list, an explicit enum of allowed values for
`estimated_difficulty`) is what makes this reliable enough to actually
`json.loads()` in real code — a vague "respond in JSON" without a concrete
shape example produces far less consistent results.

**A brief, honest preview of what's coming in Module 13:** prompting the
model to produce JSON, as shown above, is a real, useful, and genuinely
common technique — but it isn't *guaranteed* valid JSON every single time,
since the model is still just predicting tokens, one at a time, and a
sufficiently unusual case could still produce malformed output. The
Anthropic API also offers a dedicated structured-output feature that
constrains the model's output to strictly match a schema you provide,
guaranteeing parseable output — this module doesn't teach that feature's
exact syntax (that's genuinely Module 13's job, where QuestLog's real AI
feature needs it for real), but knowing it exists, and knowing *why* you'd
eventually want it over plain prompting for a production feature, is useful
now.

## Common mistakes & gotchas

- **Treating prompt engineering as trial-and-error guessing rather than
  applying a specific, named technique for a specific, understood reason.**
  Every technique above has a mechanical explanation for *why* it works,
  tied to context windows, attention, and next-token prediction — reach for
  the technique that matches the actual problem (few-shot for format
  consistency, chain-of-thought for multi-step reasoning, structured
  output for parseable data) rather than randomly rewording a prompt and
  hoping.
- **Writing a system prompt so long and over-specified that it eats a
  large share of the context window (Lesson 06) for very little benefit.**
  System prompts are powerful, but they're still just tokens competing for
  space and attention with everything else in the conversation.
- **Assuming few-shot examples need to be numerous.** Two or three
  well-chosen, clearly-formatted examples reliably outperform ten
  inconsistent or redundant ones — quality and format-consistency of the
  examples matters far more than sheer quantity.
- **Forgetting that chain-of-thought only helps because the reasoning
  tokens become real context for the final-answer tokens.** Asking a model
  to "think step by step" but then discarding everything except a
  requested one-word final answer (e.g., forcing pure structured output
  with no room for reasoning first) can actually remove the benefit, since
  there's no visible intermediate reasoning left in context by the time the
  final token is generated. When you need both structured output *and*
  reliable reasoning, a common real pattern is asking for reasoning first,
  then the structured answer, in that order, within the same response.
- **Assuming a JSON-shaped prompt request guarantees parseable JSON back.**
  As noted above, plain prompting for JSON is a strong technique, not an
  ironclad guarantee — real production code that needs guaranteed-valid
  structured output should validate what comes back (and, eventually, use
  the API's dedicated structured-output feature, Module 13's territory)
  rather than blindly trusting every response will parse.

## How this connects

This lesson is where Lessons 01-06's entire conceptual buildup — training,
weights, tokens, embeddings, attention, context windows, hallucination,
sampling — becomes a genuinely usable, practiced skill. Every technique
here works by shaping context (Lesson 06) that attention (Lesson 05) draws
on to predict better next tokens (Lesson 05) with a more favorable sampling
outcome (Lesson 06), reducing the conditions that produce hallucination
(Lesson 06). Module 13 picks up directly from here: it teaches the full
Anthropic API (streaming, tool use, structured-output syntax, error
handling, cost management) and has you build QuestLog's first real AI
feature — an assistant that suggests a quest breakdown — using exactly the
system-prompt, few-shot, and structured-output techniques you just
practiced, for real, against QuestLog's real data.

## Quick self-check

1. Mechanically, why does putting instructions in the `system` parameter
   tend to have a more persistent effect across a conversation than putting
   the same instructions in a single user message?
2. Why does few-shot prompting tend to produce more *consistently
   formatted* output than a purely zero-shot instruction describing the
   desired format in words?
3. Using Lesson 05's "every generated token becomes context for the next
   token" idea, explain mechanically why chain-of-thought prompting helps
   on multi-step arithmetic but helps much less on a simple factual lookup.
4. Why is being explicit about the exact JSON shape (key names, types, an
   enum of allowed values) more reliable than just saying "respond in
   JSON"?
5. If you have a real Anthropic API key, what's the exact `model` string
   this lesson used for every example, and roughly how much would running
   every example in this lesson once, for real, actually cost, given the
   pricing verified at the top of this lesson?
