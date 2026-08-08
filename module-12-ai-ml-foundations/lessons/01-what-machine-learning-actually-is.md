# Lesson 01 — What Machine Learning Actually Is

## What you'll learn

- What "training" and "inference" actually mean, as two genuinely separate
  phases of a machine learning system's life, and why confusing them is one
  of the most common beginner mistakes.
- What a "model" is, stripped of hype: a pile of numbers (weights) plus a
  fixed procedure for turning an input into an output using those numbers.
- What a **loss function** is and why it's the single number that training
  is entirely organized around minimizing.
- What a **gradient** is, at an intuition level, and why "gradient descent"
  is just a systematic way of nudging weights in the direction that reduces
  loss — with a real, tiny, runnable example you'll trace by hand and by
  code.
- What a **dot product** is and why it shows up constantly in neural
  networks (previewing Lesson 02).

## Why this matters

Every single thing this course does with AI from here through Module 15 —
calling the Anthropic API, building a RAG pipeline, writing an agent — is
built on top of a *trained* model that someone else (Anthropic) already
spent enormous computing resources training. You will never train a model
like Claude yourself in this course, and that's fine — almost nobody who
uses LLMs professionally trains their own from scratch. But if you don't
understand what training actually did to produce the weights sitting behind
that API call, words like "hallucination," "context window," and
"temperature" (all coming in Lessons 03-06) will feel like arbitrary rules
to memorize instead of direct consequences of how the thing was built. This
lesson is the foundation everything else in the module stands on.

## Prerequisites

- Module 01's Python fundamentals — functions, variables, basic loops. This
  lesson includes one small, real, runnable Python script; nothing beyond
  what Module 01 taught is needed to read it.
- Nothing else. This is the first lesson of the module and assumes zero
  prior ML knowledge, per Rule 2.

## The concept, explained simply

Imagine you're tuning a physics material in Unreal — say, a bouncy ball's
restitution (how much energy it keeps on a bounce) and friction. You don't
know the "right" values up front. So you do something very mechanical: drop
the ball, watch how it actually bounces, compare that to how you *wanted*
it to bounce, and nudge the restitution and friction values a little in
whichever direction makes the next drop look more like what you wanted.
Drop it again. Compare again. Nudge again. Repeat hundreds of times, and
the values converge on something that produces the behavior you're after.

That entire repeated process — try, measure how wrong you were, nudge the
numbers in the direction that reduces the wrongness, repeat — **is
training**, and it is not a metaphor for how machine learning works, it is
almost literally how it works. The "numbers you're nudging" are called
**weights**. The "how wrong you were" number is called the **loss**. The
systematic way of deciding which direction to nudge each weight is called
**gradient descent**, and the "which direction" signal itself is called a
**gradient**. Once you've nudged the weights enough times that the loss
gets acceptably small, you stop. Training is over. The weights are now
frozen.

**Inference** is what happens afterward, every single time you actually
*use* the trained thing. Once your bouncy-ball material's restitution and
friction are dialed in, every ball you spawn afterward just uses those
fixed numbers to bounce — no more comparing, no more nudging, no more
measuring wrongness. It just runs the physics forward, once, using the
values training already found. That's inference: running a *fixed,
already-trained* model forward, once, on a new input, to get an output.

Every time you send a message to Claude, that's inference. Claude's weights
were fixed months before you typed anything — your message doesn't change
them at all. Training happened once (an enormous, expensive, one-time
process Anthropic ran); you are doing inference, over and over, forever
afterward, against those same frozen weights.

## The details

### A model is just numbers plus a procedure

Strip away every bit of AI mystique for a second: a trained model is
**a big list of numbers (the weights) plus a fixed sequence of arithmetic
operations that uses those numbers to turn an input into an output.** That's
genuinely all it is at the mechanical level. A tiny (deliberately
unrealistic) example: suppose your "model" is just `output = weight * input`,
and you've decided (via training) that `weight = 4`. Given `input = 3`,
inference is: run the arithmetic, get `output = 12`. No thinking, no
memory of past inputs, no updating — just fixed arithmetic on the fixed
weight.

Real models like Claude have billions of weights and much more elaborate
arithmetic (Lessons 02 and 05 build that up piece by piece), but the shape
of the idea never changes: fixed numbers, fixed procedure, new input in,
output out.

### Training vs. inference, side by side

| | Training | Inference |
|---|---|---|
| **When it happens** | Once (or occasionally, when a new model version is released) | Every single time the model is used |
| **What changes** | The weights themselves get updated, repeatedly | Nothing about the model changes — only the input changes |
| **What it needs** | Massive amounts of example data, a loss function, and enormous compute | Just the already-trained weights and one input |
| **Who does it, for Claude** | Anthropic, before you ever see the model | You, every time you call the API or use claude.ai |
| **Cost, roughly** | Extremely expensive (this is why frontier models are built by well-funded labs) | Comparatively cheap per use (this is exactly what the pricing in Lesson 00's setup table reflects — you're paying for inference, never for training) |

**Try it yourself:** Before reading further, answer this in your own
words: when you send a chat message to Claude and it responds, are you
doing training or inference? What would have to be true for it to be
training instead?

### What a loss function actually measures

A **loss function** is a single number that says "how wrong is the model's
current output, compared to what it should have been." It's exactly the
scoring function you'd write for an AI behavior tree evaluator, or a
fitness function in a genetic algorithm — one number, lower is better,
computed automatically from the current state. For the toy bouncy-ball
example: if you wanted the ball to reach a height of 2 meters on its first
bounce and it actually reached 1.5 meters, a simple loss might be
`(2 - 1.5) ** 2 = 0.25` — squaring the difference is a common, deliberate
choice, because it makes the loss always positive (being too high and too
low are both "wrong," not cancel out) and it punishes being *very* wrong
much more than being *slightly* wrong.

For the tiny code example below, the model is `y_pred = w * x` (predict
`y` by multiplying input `x` by a single weight `w`), and the loss is the
squared difference between the prediction and the true target:
`loss = (y_pred - y_true) ** 2`.

### What a gradient actually is

Here's the one piece of "minimal math" this lesson needs, and it's genuinely
minimal: a **gradient** is just a number that tells you two things at once
— *which direction* to nudge a weight to reduce the loss, and *roughly how
much* that nudge should matter. If the gradient for a weight is a large
positive number, increasing that weight would make the loss go up a lot —
so you should decrease the weight. If the gradient is negative, the
opposite. If it's close to zero, the loss barely cares about that weight
right now.

You do not need to be able to derive a gradient by hand with calculus for
this course — you need to trust that it exists, that it's a real,
computable number for every weight in the model, and that "gradient
descent" just means: **repeatedly nudge each weight a small step in the
opposite direction of its gradient, because that's the direction that
reduces loss.** The size of that "small step" is called the **learning
rate** — too large a learning rate and you overshoot past the best value
and bounce around; too small and training crawls.

### A real, tiny, runnable example

This is the entire mechanism of training, reduced to the smallest possible
working example: a model with exactly one weight, learning to predict
`y = 12` given `x = 3` (so the "correct" weight is `w = 4`, since
`4 * 3 = 12` — but the code below never gets told that directly; it has to
find it via gradient descent, the same way real training never gets told
the "right" weights directly).

Create `learning_rate_demo.py`:

```python
# learning_rate_demo.py
# The entire mechanism of gradient descent, reduced to one weight.

w = 0.0            # start with a random-ish guess (real training starts truly random)
x = 3.0             # a fixed input
y_true = 12.0       # the correct output we want the model to learn to produce
learning_rate = 0.02  # how big a step to take on each nudge

for step in range(8):
    y_pred = w * x                                # inference: run the model forward
    loss = (y_pred - y_true) ** 2                 # how wrong was that prediction?
    gradient = 2 * (y_pred - y_true) * x          # which way, and how hard, to nudge w
    print(f"step {step}: w={w:.4f}  y_pred={y_pred:.4f}  loss={loss:.4f}  gradient={gradient:.4f}")
    w = w - learning_rate * gradient              # the actual "nudge" — gradient DEscent

print(f"final: w={w:.4f}")
```

Run it:

```bash
python learning_rate_demo.py
```

**Actual output** (run for real while writing this lesson, August 2026,
plain CPython, no libraries needed):

```
step 0: w=0.0000  y_pred=0.0000  loss=144.0000  gradient=-72.0000
step 1: w=1.4400  y_pred=4.3200  loss=58.9824  gradient=-46.0800
step 2: w=2.3616  y_pred=7.0848  loss=24.1592  gradient=-29.4912
step 3: w=2.9514  y_pred=8.8543  loss=9.8956  gradient=-18.8744
step 4: w=3.3289  y_pred=9.9867  loss=4.0532  gradient=-12.0796
step 5: w=3.5705  y_pred=10.7115  loss=1.6602  gradient=-7.7309
step 6: w=3.7251  y_pred=11.1754  loss=0.6800  gradient=-4.9478
step 7: w=3.8241  y_pred=11.4722  loss=0.2785  gradient=-3.1666
final: w=3.8874
```

Read this output line by line: `w` starts at `0`, so the initial prediction
is `0` — very wrong (`loss=144`). The gradient is a large negative number,
which — through the `w = w - learning_rate * gradient` line — pushes `w`
*up* (subtracting a negative number increases `w`). Every step, the loss
gets smaller, and `w` creeps closer to the true answer, `4`. This is every
single training run of every neural network that has ever existed,
mechanically, at the smallest possible scale — real training just does this
across billions of weights simultaneously, using far more sophisticated
math to compute each gradient efficiently (that efficient computation
across many weights at once is called **backpropagation**, which Lesson 02
covers).

**Try it yourself:** Change `learning_rate = 0.02` to `learning_rate = 0.1`
and predict what will happen before running it again. (Hint: a learning
rate that's too large can cause the weight to overshoot past the correct
value and oscillate back and forth instead of smoothly converging — this is
a real, common training failure mode, not just a toy-example quirk.)

### Where the dot product comes in

The toy example above has exactly one weight and one input, so "multiply
weight by input" is the whole computation. Real neural networks have many
inputs feeding into each neuron at once (Lesson 02), and the natural way to
combine "many inputs, each multiplied by its own weight, then summed" is
called a **dot product**: given inputs `[x1, x2, x3]` and weights
`[w1, w2, w3]`, the dot product is `x1*w1 + x2*w2 + x3*w3` — one number, out
of many. This single operation, repeated at enormous scale, is the
computational heart of every neural network, including the one behind
Claude. You'll see it again explicitly in Lesson 02.

## Common mistakes & gotchas

- **Thinking the model "learns" from your conversation with it.** It
  doesn't — not in the training sense. When you chat with Claude, that's
  pure inference; the weights behind the model do not change based on what
  you type. (Some products build a *separate* memory system on top of a
  model to simulate "remembering" you between sessions — Module 15 touches
  on memory patterns for agents — but that's not the same thing as the
  model's weights actually updating, and it's not what's happening by
  default.)
- **Confusing "the loss went down" with "the model is now correct."** A
  decreasing loss means the model is getting better at the *specific
  examples it trained on*. Whether that improvement generalizes to new
  inputs it's never seen is a separate, harder question (real ML
  engineering spends enormous effort on exactly this problem, called
  overfitting — worth knowing the term exists, though this course doesn't
  go deeper into it).
- **Assuming a bigger learning rate always trains faster.** As the "try it
  yourself" above demonstrates, too large a learning rate can make training
  *worse* — the weight overshoots the target and oscillates instead of
  smoothly converging. Real training pipelines spend real effort tuning
  this value.
- **Thinking you need to understand calculus to reason about gradients.**
  You don't, for this course's purposes. You need the intuition ("a number
  telling you which way and how hard to nudge each weight to reduce loss")
  and the trust that it's a real, well-defined, computable quantity —
  exactly what this lesson gave you.

## How this connects

This lesson's "weights, loss, gradient descent" trio is the vocabulary
Lesson 02 builds directly on top of, scaling from one weight to a whole
network of artificial neurons. Everything from Lesson 03 onward (tokens,
embeddings, attention) describes the *architecture* of one specific,
enormously scaled-up kind of trained model — a transformer-based large
language model — but every one of those pieces is still, underneath,
weights that were set by exactly this training-vs-inference process, just
at a scale involving billions of weights instead of one.

## Quick self-check

1. In your own words, what is the actual difference between training and
   inference — not just "one happens first," but what specifically is
   different about what's happening computationally in each?
2. What does a loss function measure, and why does the toy example square
   the difference between `y_pred` and `y_true` instead of just using the
   plain difference?
3. If a weight's gradient is a large positive number, should you increase
   or decrease that weight to reduce the loss? Why?
4. What would happen to the `learning_rate_demo.py` example if you set
   `learning_rate = 0.0`? Would `w` ever change?
5. Why is a dot product a natural way to combine multiple weighted inputs
   into a neuron, rather than, say, adding all the inputs together with no
   weights at all?
