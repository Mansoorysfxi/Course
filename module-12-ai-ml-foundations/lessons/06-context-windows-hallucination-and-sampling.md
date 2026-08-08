# Lesson 06 — Context Windows, Hallucination, and Sampling

**Verified against (August 2026), via live fetch of Anthropic's own current
documentation on August 8, 2026:**

| Fact | Verified value | Source |
|---|---|---|
| Claude Haiku 4.5 context window | 200,000 tokens | `platform.claude.com/docs/en/build-with-claude/context-windows` |
| Claude Opus 5, Sonnet 5, Opus 4.8/4.7/4.6, Sonnet 4.6 context window | 1,000,000 tokens, available by default at standard pricing (no beta header needed) | Same page |
| "Context rot" | Anthropic's own current documentation explicitly names this phenomenon: "as token count grows, accuracy and recall degrade" | Same page |
| Temperature parameter (Messages API) | Optional, range `0.0` to `1.0`, default `1.0`; explicitly documented: "even with temperature of 0.0, the results will not be fully deterministic" | `platform.claude.com/docs/en/api/messages`, fetched live |
| `top_p` (nucleus sampling) | A documented, optional alternative/complementary sampling control | Same page |

## What you'll learn

- What a **context window** practically limits, and why it isn't just "how
  much text fits" but also affects *how well* the model reasons about that
  text.
- What a **hallucination** actually is, mechanically — not "the AI makes
  things up" as an unexplained black box, but a direct, understandable
  consequence of how next-token prediction (Lesson 05) works.
- What **temperature** and other **sampling** settings actually control,
  with a real, runnable, local demonstration of the mechanism — no API key
  needed.

## Why this matters

These three ideas — context window, hallucination, sampling — are the ones
you'll bump into constantly, in exactly this form, starting in Module 13's
very first lines of real Anthropic API code. A context-window limit
error, a confidently-wrong factual claim in a response, or a `temperature`
parameter in a request body will all make immediate sense once you've
traced *why* each one exists, instead of being unexplained API surface
area you have to memorize.

## Prerequisites

- **Lesson 05 in full** — the context window and hallucination sections of
  this lesson are both direct consequences of the attention mechanism and
  the next-token-prediction framing that lesson built.
- **Lesson 00's setup** — this lesson's sampling demonstration uses
  `numpy`, already installed as a dependency of `sentence-transformers`.

## The concept, explained simply

Think of a context window the way you'd think about the amount of level
state and recent history an NPC's AI can actually hold in working memory at
once before older information starts falling out of consideration
entirely — a guard NPC who "forgets" it saw you sneak past ten minutes ago
because that event fell outside its perception/memory buffer, even though
the buffer is working exactly as designed. A context window is the same
idea for an LLM: everything within it (your messages, the model's prior
responses in the conversation, any documents you've included) is fully
available for attention (Lesson 05) to draw on when generating the next
token. Anything genuinely outside the window simply isn't there for the
model to consider at all — not "hard to recall," but mechanically absent
from the computation entirely.

Hallucination, by contrast, isn't about memory running out — it's about
what happens when the model's narrow, genuine job (predict the single most
statistically plausible next token, given everything in its context) has to
produce *something* even on a topic it has thin, contradictory, or no
strong training signal about. It's the equivalent of an NPC dialogue
generator that's been trained to always produce an in-character-sounding
line, being asked a question about lore the writers never actually
specified — it doesn't have a built-in "I genuinely don't know" fallback
unless something (training, prompting) has specifically taught it to
produce one; by default, it just generates the most plausible-*sounding*
continuation it can, and "plausible-sounding" and "actually true" are not
the same property, especially on obscure or genuinely uncertain topics.

## The details

### What a context window actually limits

The **context window** is the maximum number of tokens (Lesson 03) a model
can consider *at once* — every system prompt, every message in a
conversation, every document you've attached, and the response the model is
currently generating, all counted together, all measured in tokens, never
in words or characters. As of this lesson's verification (August 2026),
Claude Haiku 4.5's context window is **200,000 tokens**, while several
larger current Claude models (Opus 5, Sonnet 5, Opus 4.8, Opus 4.7, Opus
4.6, and Sonnet 4.6) support **1,000,000 tokens** by default. These exact
numbers are specific to this point in time and to these specific models —
treat any context-window number, including these, as something to
re-verify against current documentation whenever it actually matters for
real work, exactly as this lesson's own header table does, rather than
memorizing today's figures as permanent facts.

Mechanically, this limit exists largely *because of* attention (Lesson 05):
every token attending to every other token gets computationally more
expensive as the sequence gets longer (a token count of `N` means, roughly,
on the order of `N` × `N` comparisons happening inside attention — doubling
the sequence length roughly quadruples the attention computation), so there
is a genuine, real computational reason context windows can't simply be
unlimited, even setting aside training and engineering considerations.

**More context isn't automatically better**, and this is a real,
documented, current phenomenon Anthropic's own documentation names
explicitly: **"context rot"** — as the amount of text in the context window
grows, a model's accuracy and recall of specific details within that text
can measurably degrade, even when everything technically still "fits."
This is a genuinely important practical consequence: stuffing a context
window as full as it will technically allow is not a strategy for getting
the best possible response — curating *what* goes into the context matters
as much as how much space is technically available.

### What a hallucination actually is, mechanically

Here's the "open the hood" explanation the master plan specifically asks
for, not just "the AI makes things up": a trained LLM's actual, narrow job
(Lesson 05) is to output a probability distribution over what the next
token should be, given everything currently in its context. **There is no
separate, built-in step where the model checks a candidate answer against a
database of verified facts before committing to it.** When the model has
seen a topic covered clearly, consistently, and extensively during
training, the "correct" next tokens tend to have overwhelmingly higher
probability than incorrect alternatives, and the model reliably produces
accurate text. But when a topic is obscure, when the training data itself
was sparse, contradictory, or wrong on that specific point, or when a
question asks for something that was never true in the first place (a
fictional citation, a person who doesn't exist, a specific number nobody
ever actually measured), the model still has to output *some* next token —
there's no default "I don't know" token that automatically wins in that
situation unless training and prompting have specifically taught the model
to reach for uncertainty language instead of confident-sounding text.

This is why hallucinations are often stated with exactly the same fluent,
confident tone as accurate statements — **fluency and factual accuracy are
not the same property**, and next-token-prediction training, by itself,
optimizes directly for the former far more reliably than the latter. A
model that has learned "answers to date-and-name questions are usually
stated confidently, in this grammatical pattern" will reproduce that
confident *pattern* even when the specific facts filling it in are wrong,
because the pattern itself was genuinely, overwhelmingly common and correct
across its training data — it's the specific instance, not the pattern,
that's wrong.

### What sampling and temperature actually control

Given the model's computed probability distribution over the next token (a
real number for *every* possible token, all summing to 1.0), something has
to decide which one actually gets produced. The simplest option — always
pick the single highest-probability token, every time — is called **greedy
decoding**, and it's fully deterministic, but it tends to produce
noticeably repetitive, bland text over longer outputs, because it never
takes even a slightly less likely, more interesting continuation.

**Temperature** is the standard control for adjusting how "sharp" or "flat"
that probability distribution is before a token actually gets sampled from
it, and — per Anthropic's own current Messages API documentation, verified
above — it's a real, currently documented parameter on Claude models,
ranging from `0.0` to `1.0`, defaulting to `1.0`, explicitly documented as
not fully deterministic even at `0.0`. Lower temperature sharpens the
distribution toward the single most likely token (closer to greedy
decoding — good for tasks with one clearly-correct answer, like extracting
a specific fact or doing arithmetic); higher temperature flattens the
distribution, giving lower-probability tokens a genuinely higher chance of
being selected (better for tasks that benefit from variety, like creative
writing, where multiple different continuations could all be reasonable).

### A real, local, runnable demonstration

You don't need an API key to see exactly what temperature does — it's a
generic, well-defined piece of math, and the code below runs the real
computation on hand-picked example numbers ("logits," the raw scores a
model computes for each candidate next token, before they're turned into
probabilities). Create `temperature_demo.py`:

```python
# temperature_demo.py
# Real softmax-with-temperature math, run on hand-picked example "logits"
# for the next token after "The dragon breathed ___". These numbers are
# illustrative, not pulled from a real model, but the MATH applied to them
# is exactly the real mechanism.
import numpy as np

candidates = ["fire", "ice", "smoke", "words", "pizza"]
logits = np.array([4.0, 2.5, 2.0, 0.5, -1.0])  # higher = the model thinks this is more likely

def softmax_with_temperature(logits: np.ndarray, temperature: float) -> np.ndarray:
    scaled = logits / temperature       # dividing by temperature is the entire mechanism
    exp_scaled = np.exp(scaled - np.max(scaled))  # subtracting the max avoids overflow
    return exp_scaled / exp_scaled.sum()  # normalize so probabilities sum to 1.0

for temperature in [0.2, 1.0, 1.8]:
    probabilities = softmax_with_temperature(logits, temperature)
    print(f"temperature={temperature}")
    for candidate, probability in zip(candidates, probabilities):
        print(f"  {candidate:>6}: {probability:.4f}")
    print()
```

Run it:

```bash
python temperature_demo.py
```

**Actual output** (run for real while writing this lesson):

```
temperature=0.2
    fire: 0.9994
     ice: 0.0006
   smoke: 0.0000
   words: 0.0000
   pizza: 0.0000

temperature=1.0
    fire: 0.7166
     ice: 0.1599
   smoke: 0.0970
   words: 0.0216
   pizza: 0.0048

temperature=1.8
    fire: 0.5079
     ice: 0.2207
   smoke: 0.1672
   words: 0.0727
   pizza: 0.0316
```

This is exactly the effect temperature has, made completely concrete: at
`temperature=0.2`, `"fire"` captures essentially all of the probability
(99.94%) — sampling from this distribution would produce `"fire"` almost
every single time, very close to greedy decoding. At `temperature=1.0`
(the API default), `"fire"` is still clearly the most likely choice
(71.66%), but `"ice"`, `"smoke"`, and even `"words"` have genuine,
non-trivial chances of being selected. At `temperature=1.8`, the
distribution flattens substantially further — `"fire"` drops to about
50.79%, and even `"pizza"` (the least likely candidate) climbs from a
vanishing 0.05% (not shown above, but implied by the sharpness at 0.2) to a
real, non-negligible 3.16%. The exact same underlying model "logits" —
representing exactly the same underlying beliefs about what's likely —
produce meaningfully different actual output *behavior* depending only on
this one number.

**Try it yourself:** Add a `temperature=0.01` case to the loop and predict,
before running it, roughly what the probabilities will look like. Then
try `temperature=5.0` and predict the opposite extreme.

`top_p` (nucleus sampling), also a real, currently documented Anthropic API
parameter, works differently but toward a related goal: instead of scaling
the whole distribution the way temperature does, it restricts sampling to
only the smallest set of highest-probability tokens whose combined
probability reaches a target threshold (e.g., `top_p=0.9` means "only
consider tokens from the smallest group that together account for 90% of
the total probability, and ignore the long tail of extremely unlikely
tokens entirely"), which can prevent a high-temperature setting from
occasionally sampling something wildly implausible.

## Common mistakes & gotchas

- **Treating context-window size as the only thing that matters for a long
  conversation or document.** "Context rot" is real and documented — more
  tokens fitting doesn't mean more tokens are equally well *used*.
  Deliberately curating what's actually relevant, rather than dumping
  everything available into context "just in case," is a real, practically
  important skill Module 14's RAG work will build on directly.
- **Assuming `temperature=0` guarantees identical output every time.**
  Anthropic's own documentation, quoted above, explicitly states this isn't
  fully guaranteed even at `0.0` — small amounts of non-determinism can
  remain, for reasons related to how the underlying computation is actually
  executed on real hardware, not because the sampling math itself is
  ambiguous at `temperature=0`.
- **Believing a hallucination means "the model is broken" or "AI doesn't
  really understand anything."** Hallucination is a direct, predictable
  consequence of how next-token-prediction training works, not a sign of a
  malfunction — and it's precisely why prompt engineering (Lesson 07) and,
  later, RAG (Module 14) exist as real, serious techniques: giving the
  model relevant, verified information directly in its context measurably
  reduces hallucination, because the model can then draw on that specific,
  provided information via attention rather than relying purely on
  potentially-thin training-data patterns.
- **Confusing "low temperature" with "the model is more honest" or "high
  temperature" with "the model is more creative in some meaningful,
  intentional sense."** Temperature adjusts *randomness in token
  selection*, not the model's underlying knowledge, confidence, or
  reasoning quality. A low-temperature response can still hallucinate
  confidently; a high-temperature response isn't "trying harder" to be
  creative, it's just sampling from a flatter distribution.

## How this connects

Everything in Lessons 01-05 (weights, neurons, tokens, embeddings,
attention) explains *how the model computes a next-token probability
distribution at all*. This lesson explains what happens *around* that
computation — how much text it can consider at once (context window), what
happens when its confident-sounding output doesn't match reality
(hallucination), and how the final token actually gets chosen from the
distribution it computed (sampling/temperature). Lesson 07 is where all of
this becomes directly actionable: prompt engineering techniques like
system prompts, few-shot examples, and chain-of-thought all work, in large
part, by shaping what ends up in the context window (this lesson) so that
attention (Lesson 05) has better material to draw the next token's
probability distribution from — directly reducing the conditions that lead
to hallucination.

## Quick self-check

1. What specifically is "missing" from a model's computation when
   something falls outside its context window — is it "hard to recall" or
   mechanically absent? Why does that distinction matter?
2. What is "context rot," and why does it mean "more context" isn't always
   "better context"?
3. In your own words, mechanically, why does a hallucination often sound
   just as confident and fluent as an accurate statement?
4. Using `temperature_demo.py`'s real output, explain why `temperature=0.2`
   makes the model's output close to fully deterministic, while
   `temperature=1.8` gives even the least-likely candidate a real chance of
   being selected.
5. Why doesn't lowering temperature make a model less likely to
   hallucinate a specific wrong fact, even though it does make the output
   more deterministic?
