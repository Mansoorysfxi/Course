# Lesson 04 — Embeddings: Meaning as Coordinates

**Verified against (August 2026):** `sentence-transformers` `5.7.0` (PyPI,
released August 6, 2026), using the `all-MiniLM-L6-v2` model — a small,
free, openly-licensed embedding model (confirmed current and actively
maintained via its Hugging Face model card, fetched live August 8, 2026).
Every number in this lesson's worked example is **real, actually-computed
output** from running this exact model while writing this lesson — not
invented or estimated.

## What you'll learn

- What an **embedding** is: a list of numbers that represents a piece of
  text's *meaning* as a point (a "coordinate") in a high-dimensional space.
- Why "meaning as coordinates" is a genuinely deep, load-bearing idea, not
  just a metaphor — and what it actually buys you.
- What **cosine similarity** measures, and how to compute and interpret it
  yourself, with real numbers from a real model.
- Why an embedding model is itself a trained neural network (tying directly
  back to Lessons 01-02), specifically trained so that semantically similar
  text ends up *close together* in this coordinate space.

## Why this matters

Embeddings are the single idea that makes Module 14's entire RAG
(retrieval-augmented generation) capstone possible — "search by meaning
instead of by exact keyword match" only works because embeddings exist.
They're also the concept underneath *why* attention (Lesson 05) is even
possible: attention works by comparing tokens' vector representations to
each other, and understanding what a vector representation of meaning
actually is, concretely, makes attention's mechanism click instead of
feeling like magic. This is arguably the single most important concept in
this entire module.

## Prerequisites

- Lesson 03's concept of a token — an embedding, at the lowest level,
  starts from tokens (or, as this lesson's exercise uses, from a whole
  sentence at once via a model specifically trained to embed full
  sentences).
- Lesson 00's setup — this lesson's example uses `sentence-transformers`,
  installed there, entirely free and local, no API key.
- Lessons 01-02's neuron/weight/training vocabulary — an embedding model is
  a trained neural network, and this lesson assumes you're comfortable with
  what that means.

## The concept, explained simply

Imagine every word, sentence, or document you could ever write got assigned
a specific point in space — not physical space, but a space with hundreds
of numeric dimensions instead of the usual three. Now imagine that this
space was built so that things with *similar meaning* end up *physically
close together* in it, and things with *unrelated meaning* end up far
apart — regardless of whether they share any of the same actual words.
"The dragon guards the castle" and "A fierce lizard watches over the
fortress" would land near each other, even though they share almost no
vocabulary, because they mean almost the same thing. "The dragon guards the
castle" and "I need to buy milk" would land far apart, because they don't.

That's an **embedding**: a list of numbers (a **vector**) that represents a
specific piece of text's meaning as a location in this space. "Meaning as
coordinates" is not a loose metaphor here — it's a literal description of
what the numbers are. Two pieces of text with similar meaning genuinely
have numerically close vectors, in a mathematically precise, measurable
sense you'll compute yourself below.

## The details

### Turning a sentence into coordinates

Here's real, runnable code that computes an actual embedding for a real
sentence. Create `explore_embeddings.py`:

```python
# explore_embeddings.py
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

sentence = "QuestLog helps you track your daily quests."
embedding = model.encode(sentence)

print(f"Sentence: {sentence!r}")
print(f"Embedding shape: {embedding.shape}")
print(f"First 10 numbers of the embedding: {embedding[:10]}")
```

Run it:

```bash
python explore_embeddings.py
```

**Actual output** (run for real while writing this lesson):

```
Sentence: 'QuestLog helps you track your daily quests.'
Embedding shape: (384,)
First 10 numbers of the embedding: [-0.02466939  0.03018171  0.03925782 -0.02798483  0.02798948 -0.09553427
  0.06576081  0.01361226 -0.02298306  0.03014459]
```

That single sentence just became a list of **384 numbers** — a point in
384-dimensional space. Nobody can visualize 384 dimensions directly, but
you can shrink many dimensions down to just 2 or 3 for a plot, on purpose,
using a technique called **dimensionality reduction** — deliberately
throwing away the dimensions that carry the least information while
keeping the ones that carry the most, so the result is a genuine (if lossy)
2D approximation of the original space rather than an arbitrary slice of
it. Exercise 02 uses one standard, real dimensionality-reduction technique
(SVD, Singular Value Decomposition) to do exactly this — you don't need to
understand SVD's underlying mathematics for this course, only that "shrink
384 numbers down to 2, keeping as much of the real structure as possible"
is a well-defined, legitimate thing to do, not a hack. The model itself
never needs this step — it works directly with the full 384 numbers; the
projection only exists so a human can look at a picture, which is exactly
what the next section's cosine similarity calculation does instead,
working with the full, un-shrunk vectors.

### Comparing meaning with cosine similarity

Given two embedding vectors, how do you measure "how similar are these in
meaning"? The standard tool is **cosine similarity** — a single number
between roughly -1 and 1 that measures the angle between two vectors,
ignoring their length entirely. A cosine similarity near `1.0` means the
two vectors point in almost the same direction (very similar meaning); near
`0.0` means they're roughly unrelated; negative values mean they point in
genuinely opposite directions (rare in practice for normal text, but
possible).

```python
import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
```

Notice the **dot product** from Lesson 01 sitting right in the middle of
this formula (`np.dot(a, b)`) — cosine similarity is, mechanically, "the dot
product of two vectors, divided by their lengths so only *direction*
matters, not magnitude." The same operation that combined weighted inputs
inside a single neuron in Lesson 02 is exactly the operation used to
compare two pieces of meaning here. This is not a coincidence — the dot
product is genuinely one of the small number of core operations that shows
up constantly throughout machine learning.

### A real, six-sentence worked example

Here's the payoff — six real sentences, embedded and compared for real, with
every number below being genuine output from running this code:

```python
sentences = [
    "The dragon guards the ancient castle.",
    "A fierce lizard watches over the old fortress.",
    "I need to buy milk and eggs from the store.",
    "Remember to pick up groceries after work.",
    "QuestLog helps you track your daily quests.",
    "The wizard cast a powerful fireball spell.",
]

embeddings = model.encode(sentences)

n = len(sentences)
for i in range(n):
    for j in range(i + 1, n):
        score = cosine_similarity(embeddings[i], embeddings[j])
        print(f"[{i}] vs [{j}]: {score:.4f}")
```

**Actual output** (run for real while writing this lesson):

```
[0] vs [1]: 0.4282
[0] vs [2]: 0.0024
[0] vs [3]: 0.0218
[0] vs [4]: 0.0483
[0] vs [5]: 0.2795
[1] vs [2]: -0.0716
[1] vs [3]: -0.0185
[1] vs [4]: -0.0026
[1] vs [5]: 0.0886
[2] vs [3]: 0.3467
[2] vs [4]: 0.0707
[2] vs [5]: 0.0346
[3] vs [4]: 0.1172
[3] vs [5]: 0.0282
[4] vs [5]: 0.0630
```

Read this like real evidence, because it is:

- **The single highest similarity is `[0]` vs `[1]`, at `0.4282`** — "The
  dragon guards the ancient castle" and "A fierce lizard watches over the
  old fortress." These two sentences share almost **no** actual words in
  common (`the` is the only overlap), and yet the model places them closer
  together than any other pair, because they describe the *same kind of
  situation*: a mythical creature guarding a fortified structure. This is
  the entire point of embeddings — they capture meaning, not vocabulary
  overlap.
- **The second highest is `[2]` vs `[3]`, at `0.3467`** — "I need to buy
  milk and eggs from the store" and "Remember to pick up groceries after
  work." Again, almost no shared vocabulary, but both are mundane
  grocery-errand sentences, and the model correctly groups them.
- **`[0]` vs `[5]`, at `0.2795`**, is the third-highest — "The dragon
  guards the ancient castle" and "The wizard cast a powerful fireball
  spell" are both fantasy-themed, and land meaningfully closer together
  than either does to the grocery sentences, even without being as close as
  the top pair.
- **Sentence `[4]`, the QuestLog one, is the least similar to everything
  else** — its highest similarity to any other sentence is only `0.1172`
  (against the grocery-reminder sentence `[3]`). It's a sentence about an
  app feature, genuinely somewhat unlike either the fantasy sentences or the
  grocery sentences, and the numbers reflect that.

**Try it yourself:** Before running the code, predict which pair of these
six sentences you'd expect to have the *lowest* (most negative or closest
to zero) similarity score, and why. Then check your prediction against the
real output above.

## Common mistakes & gotchas

- **Assuming similar-sounding words guarantee high similarity, or that
  shared words guarantee it.** As the `[0]` vs `[1]` example directly
  demonstrates, an embedding model can correctly rate two sentences as
  highly similar *despite* almost no shared vocabulary — and, just as
  importantly, two sentences that happen to share a common word (like "the"
  appearing in nearly every sentence above) are not thereby rated as
  similar. Embeddings compare meaning, not string overlap.
- **Treating cosine similarity scores as if they had a universal
  "similarity meter" scale (like 0-100%).** A `0.4282` doesn't mean "43%
  similar" in any human-interpretable sense — it's a relative measure, most
  useful for *comparing* several candidate pairs against each other (as
  this lesson's worked example does) rather than for judging a single score
  in isolation.
- **Forgetting that embeddings are themselves the output of a trained
  neural network.** `all-MiniLM-L6-v2` didn't get its "similar meaning →
  nearby vectors" property for free — it was trained (Lesson 01's whole
  training loop: forward pass, loss, backpropagation, gradient descent) on
  a large number of example sentence pairs, with a loss function
  specifically designed to reward the model for placing genuinely similar
  sentences close together and dissimilar ones far apart. The "meaning as
  coordinates" property is a *result* of training, not an inherent property
  of text.
- **Confusing an embedding vector with a token ID from Lesson 03.** A token
  ID (like `37831` for `'Quest'` in Lesson 03) is just an arbitrary lookup
  number for a specific subword piece — it carries no meaning by itself. An
  embedding (a list of 384 floating-point numbers, in this lesson's model)
  is the actual, meaning-carrying representation. Inside a real LLM, every
  token ID gets converted into an embedding vector as one of the very first
  steps of processing — this is the bridge between Lesson 03's "text is
  chopped into tokens" and this lesson's "meaning is coordinates in space."

## How this connects

Every token an LLM processes gets converted into an embedding vector before
anything else happens to it — this is the literal first step inside a real
transformer (Lesson 05). The "meaning as coordinates" idea you just
verified with real cosine-similarity numbers is exactly what Lesson 05's
**attention** mechanism operates on: attention decides how much each
token should "pay attention to" every other token by comparing their vector
representations to each other — using, again, a dot-product-based
similarity calculation very close in spirit to the cosine similarity you
just computed by hand. Module 14's entire RAG capstone is also a direct,
scaled-up application of exactly this lesson: "chat with your documents"
works by embedding a user's question, embedding many candidate document
chunks, and finding the chunks whose embeddings are closest (by cosine
similarity) to the question's embedding — precisely Exercise 02's
"most similar pair" logic, just searching across many more candidates.

## Quick self-check

1. What does "meaning as coordinates" mean literally, not just as a loose
   figure of speech?
2. In the six-sentence worked example, why did `[0]` and `[1]` score
   highest in similarity despite sharing almost no words?
3. What does cosine similarity actually measure, and why does it divide out
   each vector's length (magnitude) rather than just using a plain dot
   product?
4. Why is an embedding model itself a trained neural network, and what
   would its loss function need to reward it for doing, to end up with the
   "similar meaning → nearby vectors" property?
5. What's the difference between a token ID (Lesson 03) and an embedding
   vector (this lesson), and at what point does a real LLM convert one into
   the other?
