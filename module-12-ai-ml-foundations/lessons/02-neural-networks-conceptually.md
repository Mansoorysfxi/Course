# Lesson 02 — Neural Networks, Conceptually

## What you'll learn

- What an artificial **neuron** actually computes, mechanically — it's the
  dot product from Lesson 01 plus two small additions (a bias and an
  activation function), nothing more mysterious than that.
- Why neurons are arranged in **layers**, and what "hidden layer" means.
- What an **activation function** does and why a network of neurons needs
  one at all (why "just dot products, stacked" isn't enough).
- What **backpropagation** does at an intuition level: how "the output was
  wrong" gets turned into "here's how much to blame each individual weight,
  all the way back through the network."
- A real, hand-computed, runnable example of a tiny neural network's
  forward pass, so "neuron," "layer," and "activation" stop being words and
  become arithmetic you've actually watched run.

## Why this matters

An LLM like Claude is, underneath every bit of its apparent understanding
of language, an enormous neural network — many billions of the exact kind
of neuron this lesson describes, arranged in a specific, clever
architecture (the transformer, covered in Lesson 05). If Lesson 01 gave you
the *training loop* (try, measure wrongness, nudge), this lesson gives you
the *thing being trained* — the actual structure of weights and neurons
that training is adjusting. Without this, "attention" in Lesson 05 would
just be a word; with it, attention is a specific, well-motivated addition
to the neuron-and-layer structure this lesson builds.

## Prerequisites

- **Lesson 01 in full** — this lesson assumes you're comfortable with
  weights, dot products, loss, and gradient descent. Nothing here makes
  sense without that foundation.
- Module 01's Python fundamentals, same as Lesson 01.

## The concept, explained simply

Think of a single artificial neuron the way you'd think about one node in
a behavior tree's utility-scoring system: it takes several inputs (say,
"distance to enemy," "player's current health," "ammo remaining"), each
input gets multiplied by a **weight** that says how much that particular
input should matter for this neuron's decision, the weighted inputs get
summed up into one number, and then that number gets passed through a
simple rule that decides whether and how strongly this neuron "fires." That
firing rule is the **activation function** — the game-dev equivalent of a
utility curve that turns a raw weighted score into "this action's actual
priority," rather than passing the raw number through untouched.

A **neural network** is nothing more exotic than many of these neurons,
arranged in layers, where each neuron's output becomes an input to the next
layer's neurons. The first layer sees the network's raw input (in an LLM's
case, eventually, a sequence of tokens' embeddings — Lessons 03-04). The
last layer produces the network's final output. Everything in between is
called a **hidden layer** — "hidden" simply because you, as the person
using the network, never look at those intermediate numbers directly; they
exist purely to let earlier layers pass increasingly useful, increasingly
abstract signals forward to later ones.

## The details

### One neuron, mechanically

A single artificial neuron does exactly three things, in order:

1. **Weighted sum (a dot product, from Lesson 01):** multiply each input by
   its own weight, and add them all together.
2. **Add a bias:** one extra number, unique to this neuron, added after the
   weighted sum — think of it as the neuron's baseline "eagerness to fire"
   before it even looks at its inputs.
3. **Apply an activation function:** pass the result through a fixed,
   simple, non-linear function that decides the neuron's actual output.

In code, using one of the simplest and most common activation functions,
**ReLU** (Rectified Linear Unit — "if positive, pass it through unchanged;
if negative, output zero"):

```python
def relu(x):
    return max(0.0, x)

def neuron(inputs, weights, bias):
    total = sum(i * w for i, w in zip(inputs, weights)) + bias
    return relu(total)
```

Every line here maps directly onto the three steps above:
`sum(i * w for i, w in zip(inputs, weights))` is the weighted sum (dot
product), `+ bias` adds the neuron's own baseline, and `relu(total)` is the
activation function.

### Why you need an activation function at all

Here's the part that's easy to skip past but genuinely matters: if you
stacked layers of neurons *without* an activation function — just weighted
sums feeding into more weighted sums — the whole stack, no matter how many
layers deep, would mathematically collapse into being equivalent to a
*single* layer of weighted sums. Stacking purely linear operations produces
another linear operation; you gain nothing from depth. The activation
function's non-linearity (`ReLU`'s sudden "clip anything negative to zero"
behavior is exactly this kind of non-linearity) is what actually lets
depth matter — each additional layer can now represent genuinely new kinds
of patterns that a single layer couldn't, which is the entire reason "deep"
learning (many layers) works better than a single layer for hard problems
like understanding language.

### A real, tiny, hand-computed network

Here's a network with two inputs, one hidden layer of two neurons, and one
output neuron — small enough to trace completely by hand, and real enough
to show every concept in this lesson actually working.

Create `tiny_network.py`:

```python
# tiny_network.py
# A hand-built, 2-input -> 2-hidden-neurons -> 1-output network.
# The weights below are hand-picked for this demo, not learned by training
# (that's Lesson 01's job) -- this script only shows a forward pass (inference).

def relu(x: float) -> float:
    return max(0.0, x)

def neuron(inputs: list[float], weights: list[float], bias: float) -> float:
    total = sum(i * w for i, w in zip(inputs, weights)) + bias
    return relu(total)

# Two made-up input features, e.g. [quest_difficulty, player_level_normalized],
# both already scaled to roughly the 0-1 range (real networks almost always
# do this kind of input scaling; it's not covered further in this course).
inputs = [0.8, 0.3]

# Hidden layer: two neurons, each looking at BOTH inputs, each with its own
# weights and bias.
hidden1 = neuron(inputs, weights=[0.5, -0.2], bias=0.1)
hidden2 = neuron(inputs, weights=[-0.4, 0.9], bias=0.0)

print(f"hidden1 = {hidden1}")
print(f"hidden2 = {hidden2}")

# Output layer: one neuron, looking at BOTH hidden neurons' outputs.
output = neuron([hidden1, hidden2], weights=[0.6, 0.3], bias=-0.05)
print(f"output  = {output}")
```

Run it:

```bash
python tiny_network.py
```

**Actual output** (run for real while writing this lesson):

```
hidden1 = 0.44000000000000006
hidden2 = 0.0
output  = 0.21400000000000002
```

(The trailing digits like `...006` and `...002` are ordinary
floating-point rounding, not a bug — the "real" values are `0.44` and
`0.214`.)

Trace this by hand to confirm the mechanism, not just trust the printout:
`hidden1`'s weighted sum is `0.8 * 0.5 + 0.3 * -0.2 + 0.1 = 0.4 - 0.06 + 0.1
= 0.44`, and since `0.44` is already positive, ReLU passes it through
unchanged. `hidden2`'s weighted sum is `0.8 * -0.4 + 0.3 * 0.9 + 0.0 =
-0.32 + 0.27 + 0 = -0.05`, which is *negative* — so ReLU clips it to exactly
`0.0`. This is a real, common thing that happens inside real neural
networks: a neuron computes a negative weighted sum and simply outputs
zero, contributing nothing to whatever comes next, for this particular
input. (If a neuron does this for *every* input it ever sees during
training, it's sometimes called a "dead" neuron — worth knowing the term
exists, though this course doesn't go deeper into diagnosing it.)

**Try it yourself:** Change `hidden2`'s bias from `0.0` to `0.1` and predict,
before running it, whether `hidden2` will still be clipped to zero. (Hint:
recompute the weighted sum with the new bias and check its sign.)

### What backpropagation actually does

Lesson 01 showed gradient descent for a single weight. A real network has
millions or billions of weights, spread across many layers, all
contributing to one final output and one final loss value. **Backpropagation**
is the algorithm that efficiently computes the gradient for *every single
weight in the network at once*, by working backward from the output.

The intuition, using a game-dev-flavored analogy: imagine a boss fight
where your team wiped, and you're doing a post-mortem to figure out whose
fault it was — not to blame anyone personally, but to know precisely which
build decisions to adjust before the next attempt. You start from the
outcome (the wipe — analogous to the loss) and work backward: the healer
ran out of mana too early, which happened because the tank pulled too many
adds at once, which happened because the scout under-reported enemy count.
Each step back assigns a share of "responsibility for the bad outcome" to
an earlier decision. Backpropagation does exactly this, mathematically and
automatically: starting from the loss, it works backward layer by layer,
computing exactly how much each weight in each layer contributed to the
final error, using the chain rule from calculus (you don't need to know
calculus to understand *what* it accomplishes, only that it exists and is
this "assign blame backward through the chain of computations" mechanism).

Once every weight's gradient is known (via backpropagation), gradient
descent (Lesson 01) does the actual nudging — same mechanism as the
single-weight toy example, just applied simultaneously to every weight in
every layer.

### Why this matters for LLMs specifically

An LLM's neural network has an enormous number of layers and an enormous
number of neurons per layer — orders of magnitude beyond this lesson's
2-neuron toy example — and a specific, additional architectural idea layered
on top (attention, Lesson 05) that lets information flow between tokens in
a sequence, not just straight through stacked layers. But the fundamental
unit — weighted sum, bias, non-linear activation — and the fundamental
training mechanism — backpropagation computing gradients, gradient descent
using them to nudge weights — are exactly what you just traced by hand
above, just repeated at a scale that requires enormous specialized computer
hardware (GPUs, and the TPUs/custom chips major labs use) to actually run.

## Common mistakes & gotchas

- **Thinking "neural network" implies something biologically brain-like.**
  The name is historical (loosely inspired by biological neurons decades
  ago), but a real artificial neuron, as this lesson showed, is just a
  weighted sum plus a bias plus a simple function — closer to a spreadsheet
  formula than to actual brain tissue. Don't let the name imply more than
  the mechanism actually is.
- **Assuming more layers is always better.** More layers (more "depth")
  can represent more complex patterns, but also makes training harder in
  practice (a real, well-studied problem — worth knowing it exists, though
  this course doesn't dig into the specific failure modes or fixes).
- **Forgetting that a forward pass and a training step are different
  things.** `tiny_network.py` above only does a *forward pass* (inference —
  compute the output from fixed, hand-picked weights). It does not do any
  training at all — the weights `[0.5, -0.2]` etc. were chosen by hand for
  this demo, not learned. Lesson 01's `learning_rate_demo.py` is the
  training half; this lesson's `tiny_network.py` is the "what's actually
  being trained" half. Real systems always do forward passes many, many
  times during training (once per example, to compute the current loss)
  before backpropagation and gradient descent get a chance to improve the
  weights.
- **Expecting backpropagation to be something you need to implement.** You
  will never write backpropagation by hand in this course, and very few
  working ML engineers do either — libraries like PyTorch (which you just
  installed as a dependency of `sentence-transformers` in Lesson 00's
  setup) compute it automatically. What matters for this course is
  understanding *what it accomplishes* (efficiently getting every weight's
  gradient) well enough that "the model was trained via backpropagation and
  gradient descent" is a meaningful sentence rather than jargon.

## How this connects

Lesson 01 gave you the training loop (try, measure loss, compute gradients,
nudge weights); this lesson gave you the structure being trained (neurons,
layers, activation functions) and the mechanism (backpropagation) that
makes computing every weight's gradient efficient even at enormous scale.
Lesson 03 shifts from "how a network computes" to "what actually goes
*into* the network in the first place" when the input is text rather than
neat numeric features like this lesson's toy `[0.8, 0.3]` — starting with
tokens.

## Quick self-check

1. What three steps does a single artificial neuron perform, in order, on
   its inputs?
2. Why does stacking layers of *purely linear* operations (no activation
   function) fail to gain anything over a single layer, no matter how many
   layers you stack?
3. In `tiny_network.py`'s actual run, why did `hidden2` output exactly
   `0.0` instead of a small negative number?
4. Using the boss-fight "assign blame backward" analogy, explain in your
   own words what backpropagation computes and why working backward from
   the loss (rather than forward from the inputs) is the natural direction
   for that computation.
5. What's the difference between a "forward pass" and a "training step,"
   and which one did `tiny_network.py` actually perform?
