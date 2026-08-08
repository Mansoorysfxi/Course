# Lesson 05 — Attention and Transformers, at an Intuition Level

**Verified against (August 2026):** conceptual material in this lesson (what
attention computes, why transformers replaced earlier architectures) is
long-settled, well-documented territory in the field and hasn't changed —
this lesson does not depend on any fast-moving fact, version number, or
price. The one runnable example below uses plain `numpy` (already installed
as a dependency of `sentence-transformers` from Lesson 00) with entirely
hand-picked, illustrative numbers — explicitly **not** real learned
embeddings from any trained model — used only to make the *mechanism* of
attention concrete and traceable by hand.

## What you'll learn

- Why a language model needs a way for tokens to "look at" other tokens in
  a sequence, and why simpler, older architectures struggled with this.
- What **attention** actually computes, mechanically: a weighted lookup
  where each token decides how much to weigh every other token's
  information, using the dot-product-based similarity idea from Lessons
  01 and 04.
- What a **transformer** is, at the level of "attention plus the
  neural-network machinery from Lesson 02, stacked in a specific,
  repeated pattern" — enough to hold a real conversation about the
  architecture without needing to implement one.
- A real, hand-traceable, runnable toy example of the attention calculation
  itself.

## Why this matters

"Transformer" is the T in GPT, and it's the architecture behind every
frontier LLM in production today, including every Claude model this course
uses starting in Module 13. Attention specifically is the single
architectural idea that made today's LLMs possible — before transformers
existed (they were introduced in a 2017 paper, "Attention Is All You Need"),
language models processed text strictly in order, one token at a time, and
struggled badly to connect information across long stretches of text.
Understanding attention at an intuition level is what turns "the model
somehow understands language" from a black box into a specific, reasoned-
about mechanism — and it's a direct prerequisite for understanding *why*
context windows exist and have limits (Lesson 06) and why longer, messier
prompts can genuinely confuse a model even when it technically "fits."

## Prerequisites

- **Lesson 04 in full** — attention operates directly on the embedding
  vectors ("meaning as coordinates") that lesson introduced, and reuses
  the dot-product-based similarity idea from that lesson's cosine
  similarity calculation.
- **Lesson 02's neuron/layer vocabulary** — a transformer is built from
  the same weighted-sum-plus-activation neurons Lesson 02 covered, arranged
  in a specific repeating pattern this lesson describes.

## The concept, explained simply

Imagine reading a long, tangled sentence like: *"The dragon that had been
terrorizing the village for three years finally met its match when a young
knight, who had trained for a decade specifically for this encounter,
struck it down."* To understand what "it" refers to near the end, you have
to reach all the way back to "the dragon," ignoring a huge amount of
intervening text about the knight's training. Humans do this
effortlessly — we don't process language strictly left to right in an
isolated bubble; we hold the whole sentence's context available and
selectively focus on the parts that matter for understanding any given
word.

**Attention, at an intuition level, is exactly this: every token "looks
around" at every other token in the sequence and decides how much each one
matters for understanding it right now.** This is directly analogous to a
flocking (boids) algorithm in game AI, where each agent doesn't treat every
other agent in the simulation as equally relevant to its own movement —
each boid looks at its nearby neighbors and weighs their positions and
velocities more heavily than agents far away or moving in unrelated
directions. Attention does the computational equivalent for tokens in a
sentence: instead of "nearby in space," it's "relevant in meaning" (via the
embedding-space closeness from Lesson 04), and instead of a fixed
neighborhood radius, every token gets a *computed, weighted* say from every
other token, with the weights determined by how relevant each one actually
is.

## The details

### Why older architectures struggled

Before transformers, a common approach (recurrent neural networks, RNNs)
processed a sequence of tokens strictly one at a time, left to right,
carrying forward a single running summary ("hidden state") that got updated
at each step. The problem: by the time you reach the word "it" late in a
long sentence, the running summary has been overwritten and diluted many,
many times since it last touched "the dragon" — information from far back
in the sequence tends to fade, exactly the way a long chain of whispered
messages degrades the further it travels (the "telephone game" problem).
Longer sequences made this worse, not better.

Attention solves this by giving every token **direct, unmediated access to
every other token**, no matter how far apart they are in the sequence —
there's no "running summary" to dilute. The word "it" can attend directly
and strongly to "the dragon," skipping straight past the intervening
clause about the knight's training, regardless of how many tokens sit in
between.

### What attention actually computes

For every token in a sequence, attention computes a **weighted average of
every token's information**, where the weights are determined by how
relevant each token is to the one currently being processed. Mechanically,
each token's embedding gets used in three roles (this is the standard
terminology, worth knowing even at an intuition level): as a **query**
("what am I looking for?"), as a **key** ("what do I have to offer, for
comparison purposes?"), and as a **value** ("what information do I actually
contribute if selected?"). The similarity between a token's query and every
other token's key (computed via a dot product — the same operation from
Lessons 01 and 04) determines how much weight that other token's *value*
gets in the final weighted sum.

That's the entire mechanism: **compare (via dot product), turn the
comparisons into weights that sum to one (via a function called softmax),
then take a weighted sum of values using those weights.** Every "attention
head" in a real transformer does exactly this, many times over, at every
layer.

### A real, hand-traceable toy example

The numbers below are **entirely hand-picked for illustration** — not real
learned embeddings from any trained model — chosen specifically to make the
mechanism's output land somewhere intuitive, so you can trace *why* the
numbers come out the way they do. Create `toy_attention.py`:

```python
# toy_attention.py
# A minimal, hand-picked illustration of the attention mechanism.
# The vectors below are NOT real learned embeddings -- they're chosen by
# hand to make the output intuitive to trace, the same way Lesson 02's
# tiny_network.py used hand-picked weights rather than trained ones.
import numpy as np

np.set_printoptions(precision=4, suppress=True)

tokens = ["The", "dragon", "roared"]

# Toy 4-number "embeddings" -- 'dragon' and 'roared' point in a similar
# direction (both relate to the creature/action), 'The' is more neutral.
vectors = np.array([
    [0.1, 0.0, 0.2, 0.0],   # "The"
    [0.9, 0.1, 0.0, 0.8],   # "dragon"
    [0.8, 0.0, 0.1, 0.7],   # "roared"
])

def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - np.max(x))  # subtracting the max avoids overflow; doesn't change the result
    return e / e.sum()

# Compute attention FROM "roared" (the query) TO every token (the keys).
query = vectors[2]      # "roared" is asking the question
keys = vectors            # every token offers itself for comparison
values = vectors            # and also contributes its own information if selected

scores = keys @ query              # dot product: how relevant is each token to "roared"?
weights = softmax(scores)          # turn raw scores into weights that sum to 1

print("Raw similarity scores (roared vs each token):")
for token, score in zip(tokens, scores):
    print(f"  {token:>8}: {score:.4f}")

print("\nAttention weights after softmax (these sum to 1.0):")
for token, weight in zip(tokens, weights):
    print(f"  {token:>8}: {weight:.4f}")

context = weights @ values
print(f"\nResulting 'context' vector for \"roared\": {context}")
```

Run it:

```bash
python toy_attention.py
```

**Actual output** (run for real while writing this lesson):

```
Raw similarity scores (roared vs each token):
      The: 0.1000
   dragon: 1.2800
   roared: 1.1400

Attention weights after softmax (these sum to 1.0):
      The: 0.1412
   dragon: 0.4594
   roared: 0.3994

Resulting 'context' vector for "roared": [0.7471 0.0459 0.0682 0.6471]
```

Trace this by hand to confirm the mechanism: `"roared"`'s query vector was
compared against all three tokens' key vectors via a dot product. Because
this toy example's `"dragon"` and `"roared"` vectors were deliberately
chosen to point in a similar direction, `"dragon"` scored highest
(`1.28`), `"roared"` (comparing against itself) scored close behind
(`1.14`), and the more neutral `"The"` scored much lower (`0.10`). After
softmax, `"dragon"` ends up with the largest share of attention
(`0.4594`, or roughly 46%) when processing `"roared"` — exactly matching
the intuition that "roared" should care most about "who roared," which is
"dragon." The final `context` vector is a weighted blend of all three
tokens' information, weighted almost by that ~46/40/14 split.

**Try it yourself:** Change `"The"`'s toy vector from `[0.1, 0.0, 0.2, 0.0]`
to `[0.9, 0.1, 0.0, 0.8]` (identical to `"dragon"`'s) and predict, before
running it, how the attention weights will change. (Hint: two tokens with
identical vectors will always score identically against any query.)

### What a transformer actually is

A **transformer** is, at the architectural level: repeated "blocks," each
containing an attention step (exactly the mechanism above, computed
simultaneously for every token against every other token, and usually done
many times in parallel per block — called "multiple attention heads," each
free to learn to focus on a different kind of relationship between tokens)
followed by an ordinary feed-forward neural network (exactly Lesson 02's
neurons-and-layers, applied to each token's own vector independently, no
cross-token interaction in this step). Stack many of these attention +
feed-forward blocks on top of each other — modern frontier models stack
dozens of them — and you have a transformer. Every one of Lesson 02's
concepts (weights, biases, activation functions, loss, backpropagation)
still applies throughout: a transformer's attention mechanism itself has
trainable weights (the ones that convert a raw embedding into that token's
query, key, and value vectors), and training adjusts all of them, at every
layer, via exactly the same backpropagation-plus-gradient-descent process
from Lessons 01-02.

### Why next-token prediction produces coherent text at all

Here's the piece that feels like the most magic and deserves the most
demystifying: a trained LLM's actual job, at the lowest level, is
astonishingly narrow — given a sequence of tokens so far, predict a
probability distribution over what the *single next token* should be, then
(depending on sampling settings, covered in Lesson 06) pick one. That's the
entire task the model was trained on. There's no separate "planning" or
"reasoning" module bolted on top by default.

The reason this narrow task produces coherent, structured, even
apparently-reasoned text is that **predicting the next token well, over and
over, for genuinely varied and enormous amounts of real text, turns out to
require the model to build genuinely useful internal representations of
grammar, facts, relationships between concepts, and even some amount of
step-by-step reasoning** — because those internal representations are what
actually make next-token prediction accurate across billions of diverse
examples during training. Attention is the specific mechanism that lets the
model build and use those representations by letting every token draw on
relevant information from every other token, at every layer, rather than
being stuck with only a fixed nearby window or a fading running summary.
Coherent multi-sentence text emerges because the model predicts token 1,
then treats "everything so far, including the token I just produced" as
the new input for predicting token 2, and repeats — each new token is
generated with full attention access to everything that came before it,
including its own prior outputs.

## Common mistakes & gotchas

- **Thinking attention is a single, fixed lookup table.** It's computed
  fresh, from scratch, for every single input sequence, using that
  sequence's own actual embedding vectors — there's no pre-built table of
  "which words attend to which other words" sitting inside the model.
  The *weights that decide how to compute queries, keys, and values* are
  fixed after training, but the actual attention *pattern* for any given
  sentence is recomputed every time, based on that sentence's specific
  content.
- **Assuming more attention heads or more layers is unambiguously
  "smarter."** Scale genuinely correlates with capability in practice
  (this is a big part of why frontier models keep growing), but it's not a
  simple, guaranteed relationship, and enormous engineering effort goes
  into architecture and training-data quality alongside raw scale.
- **Confusing "the model predicts one token at a time" with "the model has
  no sense of the whole response it's building."** Because every new token
  is generated with attention access to the entire sequence so far
  (including tokens the model itself already produced earlier in this same
  response), the model effectively "sees" its own prior output as context
  for every subsequent token — which is exactly why a model can maintain a
  consistent train of thought across a long response, despite generating it
  one token at a time.
- **Treating this lesson's toy example as if its numbers were real,
  learned values.** They're not — `toy_attention.py`'s vectors were
  hand-picked specifically to make the mechanism's arithmetic land somewhere
  intuitive, exactly like Lesson 02's `tiny_network.py`. Real attention
  operates on real, trained embedding vectors (Lesson 04) with hundreds or
  thousands of dimensions, computed by real, trained query/key/value
  weight matrices — the mechanism is identical, the actual numbers are not
  something you'd hand-pick.

## How this connects

Lesson 04 gave you embeddings — meaning as coordinates. This lesson showed
you the specific mechanism (attention, inside the transformer architecture)
that real LLMs use to combine information across many tokens' embeddings at
once, using the same dot-product-based comparison idea from Lesson 04's
cosine similarity. Lesson 06 builds directly on this: the **context
window** is, mechanically, the maximum number of tokens attention can
operate across at once — every token attending to every other token gets
computationally expensive as the sequence gets longer, which is a large
part of *why* context windows have a hard limit rather than being
unlimited. Lesson 06 also covers *why* this narrow next-token-prediction
mechanism sometimes produces confident-sounding falsehoods (hallucination)
— a direct consequence of the fact that the model is always predicting
"what token is statistically likely to come next," not consulting a
built-in database of verified facts.

## Quick self-check

1. Using the boids/flocking analogy, explain in your own words what
   "attention" computes and why it's a useful analogy for the mechanism.
2. What specific problem with older, strictly-left-to-right architectures
   (like RNNs) does attention solve?
3. In `toy_attention.py`'s real output, why did `"dragon"` receive the
   highest attention weight when computing `"roared"`'s context vector?
4. What are "query," "key," and "value" in the attention mechanism, in your
   own words, and which operation from Lesson 01 does comparing a query to
   a key actually use?
5. Why does an LLM's genuinely narrow task — "predict the next token" —
   end up producing text that reads as coherent, structured, and even
   reasoned, rather than random plausible-sounding words strung together?
