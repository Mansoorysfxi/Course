# Module 12 — AI/ML Foundations

**Phase:** 4 — AI Engineering & Agents (opening module)
**Estimated time:** 10-14 hours (lighter on setup than recent modules, but the
lessons are dense conceptual material — read slowly, especially Lessons 03-06)
**Verified against (August 2026):** `tiktoken` `0.13.0` (PyPI, released May 15,
2026), `sentence-transformers` `5.7.0` (PyPI, released August 6, 2026) with
the `all-MiniLM-L6-v2` model, `anthropic` Python SDK `0.121.0` (PyPI, released
August 7, 2026), current Claude model pricing/context-window figures fetched
live from `platform.claude.com/docs/en/about-claude/pricing` and
`.../build-with-claude/context-windows` on August 8, 2026. Every fact carrying
a specific number or version string in this module was checked against a live
source that day — see each lesson's own header for exactly what was verified
and where.

## What this module is

Modules 00-11 built and shipped a real full-stack application. This module
does something different on purpose: it stops touching QuestLog entirely and
spends its full attention on the concepts underneath everything Modules
13-15 are about to build. `RUNNING_PROJECT.md`'s own table says it plainly —
this module is standalone exercises, no QuestLog code, concepts before
tools. That's not a placeholder note; it's the master plan's Rule 1 in
action. Module 13 has you wire an AI assistant feature into QuestLog's
FastAPI backend and React frontend. If you learn the Anthropic API's request
shape without first understanding what a token is, why an embedding
represents "meaning" as a location in space, why attention lets a model
weigh some words more than others, why a model can state a confident-sounding
falsehood, and what "temperature" actually does to next-token selection —
you'll be memorizing API calls instead of understanding the tool you're
calling. This module is the "why" underneath everything from here to the
end of the course.

In Unreal terms: think of this the way you'd think about spending a week
reading about how a physics engine's constraint solver actually works before
you start scripting gameplay against it. You could skip straight to calling
`AddImpulse` and `SetPhysicsLinearVelocity` and get something moving. But
when the constraint solver does something you didn't expect — an object
tunnels through a wall, a joint explodes, a stack of boxes jitters forever —
understanding the solver's actual mechanics is the difference between a
five-minute fix and an afternoon of guessing. LLMs are the same: you can
call `client.messages.create(...)` without understanding tokens or attention
and get useful output most of the time. The moment something surprising
happens — a hallucinated fact stated with total confidence, a response that
gets cut off mid-sentence, a prompt that works differently than you expected
— the concepts in this module are what let you diagnose it instead of
shrugging and retrying.

## What you'll be able to do after this module

- Explain, with a game-dev analogy, the actual difference between training a
  model and running inference on an already-trained model — and explain
  gradient descent and a loss function well enough to reason about why a
  model's weights change the way they do during training, without needing
  calculus.
- Explain a neural network from a single artificial neuron up to a full
  network: what a weight is, what a loss function measures, and what
  "backpropagation" actually does at an intuitive level.
- Hand-tokenize a piece of real text using the same class of algorithm
  (byte-pair encoding) that real LLM tokenizers use, using a real, free,
  fully local Python library — with zero API key and zero cost.
- Explain what an embedding is using the "meaning as coordinates" analogy
  in enough depth to compute and interpret real cosine-similarity scores
  between sentence embeddings yourself, with a real, free, local embedding
  model — again zero API key, zero cost.
- Explain attention and the transformer architecture at an intuition level:
  why a model needs a mechanism for tokens to "look at" other tokens, and
  why this replaced older architectures that read text strictly left to
  right.
- Explain, mechanically (not just "the AI makes things up"), what a
  hallucination actually is, what a context window practically limits, and
  what temperature/sampling parameters do to next-token selection.
- Write and systematically compare prompts using real prompt-engineering
  techniques — system prompts, few-shot examples, chain-of-thought, and
  structured-output requests — and explain why each one changes the model's
  output the way it does.
- Decide, for yourself, when a real LLM API call is worth its (small, known,
  optional) cost versus when a free local tool or a careful reading of this
  module's own worked examples gets you just as far.

## Prerequisites

- **Module 01's Python material in full** — this module's exercises are
  plain Python scripts (no FastAPI, no React). You'll write functions, use
  lists/dicts, read files, and run scripts from the command line exactly as
  Module 01 taught. If any of that feels shaky, revisit Module 01 before
  starting here — this module does not re-teach basic Python.
- **Nothing whatsoever from Modules 02-11.** This module doesn't touch
  QuestLog, the web, databases, Docker, or deployment. That's deliberate.
- **No prior AI/ML knowledge assumed at all.** Rule 2 applies at full
  strength here: every term is defined the first time it's used, and this
  module treats you as a total beginner to machine learning specifically,
  even though you're already a strong programmer.

## A note on cost — read this before you worry about it

This module follows the exact same pattern Modules 09 and 11 already
established for real infrastructure: **reading and understanding every
single lesson, and completing the large majority of this module's work,
requires zero spending and zero paid account.** The two hands-on Python
libraries this module uses (`tiktoken` for tokenization, `sentence-
transformers` for embeddings) are free, open-source, and run entirely on
your own machine with no API key of any kind — verified in
`lessons/00-setup.md`. The one place this module touches a paid service is
Lesson 07's prompt-engineering exercises, which genuinely need a real LLM to
experiment against — and even there, the cost is measured in fractions of a
cent per experiment (a real, current price is quoted in `00-setup.md`), it's
explicitly optional, and getting an Anthropic API key now is useful
groundwork for Module 13 rather than wasted effort, since Module 13 requires
one anyway.

## Module structure

```
module-12-ai-ml-foundations/
├── README.md                                                        ← you are here
├── lessons/
│   ├── 00-setup.md                                                  ← free tools, optional API key, verification
│   ├── 01-what-machine-learning-actually-is.md                        ← training vs inference, minimal math
│   ├── 02-neural-networks-conceptually.md                               ← neurons, weights, loss, backprop
│   ├── 03-tokens-and-tokenization.md                                       ← what tokens are, hands-on with tiktoken
│   ├── 04-embeddings-meaning-as-coordinates.md                               ← embeddings in depth
│   ├── 05-attention-and-transformers-intuition.md                              ← how an LLM actually reads text
│   ├── 06-context-windows-hallucination-and-sampling.md                          ← context limits, hallucination, temperature
│   └── 07-prompt-engineering-as-a-skill.md                                          ← system prompts, few-shot, CoT, structured output
├── exercises/
│   ├── 01-hand-tokenization/                                        ← very easy, zero cost
│   ├── 02-embedding-visualization/                                    ← guided, zero cost
│   └── 03-prompt-engineering-experiments/                               ← independent, optional real API cost
├── project/
│   └── BRIEF.md                                                     ← standalone capstone script (no QuestLog this module)
└── CHECKLIST.md
```

Read the lessons in numeric order — Lesson 03 (tokens) needs Lesson 01's
"what is inference" framing, Lesson 04 (embeddings) needs Lesson 03's
concept of a token, Lesson 05 (attention) needs Lesson 04's embedding
concept, and Lesson 06 (context/hallucination/sampling) needs everything
before it. Lesson 07 (prompting) is the payoff lesson — it's where all six
earlier lessons stop being abstract and start explaining why specific
prompting techniques work.

## How to work through this module

Follow the workflow in the [root README](../README.md): read a lesson
fully, answer its self-check questions, do the matching exercise without
looking at its solution, ask your AI session for a review, revise if
needed, then move on. Once all three exercises are done, work through
`project/BRIEF.md`.

## A note on the running project

See [`RUNNING_PROJECT.md`](../RUNNING_PROJECT.md) for the full picture of
how QuestLog evolves across modules. This module's row is explicit:
*"standalone exercises — tokenization, embeddings, prompting — No QuestLog
code yet — concepts first, per Rule 1."* There is no `project/questlog/`
folder in this module, and that's intentional, not an oversight — Module
13 is where QuestLog gains its first AI feature, built on top of
everything this module teaches.
