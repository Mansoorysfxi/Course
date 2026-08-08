# Exercise 02 — Embedding Visualization

**Difficulty:** Guided — this builds directly on Exercise 01's pattern but
asks you to implement four functions instead of four simpler ones, and
introduces one genuinely new technique (2D projection via SVD). **Zero
cost, zero account needed** — this exercise uses only `sentence-transformers`,
installed for free in [`lessons/00-setup.md`](../../lessons/00-setup.md).
`matplotlib` is optional (see below).

**Concepts this exercise uses** (all taught in
[`lessons/04-embeddings-meaning-as-coordinates.md`](../../lessons/04-embeddings-meaning-as-coordinates.md)):
what an embedding is, `SentenceTransformer(...).encode(...)`, cosine
similarity and why it uses a dot product divided by vector lengths, and why
comparing many pairs of sentences reveals meaning-based clustering even
with no shared vocabulary. The 2D projection step uses `np.linalg.svd`,
which is briefly explained in the starter file's own docstring — you don't
need to understand SVD's full mathematics, only that it's a standard,
real technique for compressing many dimensions down to 2 for plotting,
while losing some information in the process.

## What to build

Open
[`starter/embedding_explorer.py`](starter/embedding_explorer.py) — it
already has the six sentences to work with, function signatures, and a
demo block. Fill in the four `# TODO` functions.

1. **`cosine_similarity(a, b)`** — exactly Lesson 04's formula: dot product
   of `a` and `b`, divided by the product of their lengths (norms).
2. **`most_similar_pair(embeddings, sentences)`** — loop over every unique
   pair of *different* sentences (by index, `i < j`), compute their cosine
   similarity using your own `cosine_similarity`, and return the pair with
   the highest score, along with that score.
3. **`project_to_2d(embeddings)`** — center the embeddings (subtract the
   mean of each column), run `np.linalg.svd` on the centered array, and
   project onto the top two directions of variance (`centered @ vt[:2].T`).
   The starter file's docstring spells out each step.
4. **`plot_embeddings(coords_2d, sentences, output_path)`** — try to
   import `matplotlib.pyplot`; if it's not installed, print a short message
   and return without error (this step is genuinely optional — see below).
   If it is installed, make a scatter plot of the 2D coordinates, label each
   point with its index, and save it to `output_path`.

**On matplotlib:** you do not need to install it to complete this exercise
— every acceptance criterion below can be satisfied purely from the printed
numeric output. If you'd like the visual plot too (recommended if you have
the disk space and a moment to spare — seeing the fantasy-themed sentences
cluster visually away from the grocery-themed ones is genuinely satisfying),
run `pip install matplotlib` first.

## Acceptance criteria

- [ ] All four functions are implemented, keep their original names/parameters, and match the exact behavior described above.
- [ ] `cosine_similarity(v, v)` (a vector compared against itself) returns very close to `1.0` for any non-zero vector `v` (a vector's angle with itself is always zero, and `cos(0) = 1`).
- [ ] `most_similar_pair(...)` returns a tuple of two *different* indices (never `i == j`), and the reported score is genuinely the maximum among all pairs — verify this by eye against the full printed list of pairwise scores.
- [ ] `project_to_2d(...)` returns an array of shape `(6, 2)` for this exercise's 6 sentences.
- [ ] Running `python embedding_explorer.py` prints all pairwise similarity scores, correctly identifies the two most-similar sentences, and prints 2D coordinates for all six sentences, with no errors — whether or not matplotlib is installed.
- [ ] In your own words (a one-sentence comment at the top of your file, or something you can explain out loud during review), explain *why* the two sentences your script identifies as most similar don't necessarily share many of the same words.

## What to submit

When you're ready for review, point your AI session at your completed
`starter/embedding_explorer.py` and say *"Review my solution for Module 12
Exercise 02."*

## Hints

- If your first run seems to hang for a while before printing anything,
  that's very likely the one-time model download from Hugging Face
  (Lesson 00's Step 4) — it should be much faster on every run after the
  first, since the model gets cached locally.
- Stuck on the SVD step? You don't need to derive or fully understand SVD's
  mathematics — copy the exact three-line recipe from the starter file's
  own docstring (center, `np.linalg.svd`, project onto `vt[:2].T`) and trust
  that it does what it says. This is exactly the kind of "use a standard,
  well-understood technique without re-deriving it from scratch" judgment
  call real ML-adjacent engineering work involves constantly.
- If your cosine similarity scores don't match the pattern Lesson 04
  described (semantically similar sentences scoring highest, despite little
  word overlap), double-check you're computing `np.dot(a, b)` and not
  accidentally summing element-wise differences or something else — a
  simple typo here is the most common way to get numbers that look
  plausible but are wrong.
- If you've re-read the relevant section and are still stuck, ask your AI
  session for a hint — Level 1 first, per
  [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md).
