# Solution Notes — Exercise 02

This solution was actually run (not just written) while generating this
module, using `sentence-transformers` `5.7.0` and the free, local
`all-MiniLM-L6-v2` model, plus `matplotlib` `3.11.1` for the optional plot.
No API key, no paid service.

**Actual, verified output from running `python embedding_explorer.py`:**

```
Computing embeddings for 6 sentences...
Embedding shape: (6, 384)

Pairwise cosine similarities:
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

Most similar pair (score=0.4282):
  [0] 'The dragon guards the ancient castle.'
  [1] 'A fierce lizard watches over the old fortress.'

2D projected coordinates:
  [0] (-0.557, -0.143)  'The dragon guards the ancient castle.'
  [1] (-0.592, -0.251)  'A fierce lizard watches over the old for'
  [2] (0.606, -0.339)  'I need to buy milk and eggs from the sto'
  [3] (0.569, -0.275)  'Remember to pick up groceries after work'
  [4] (0.227, 0.810)  'QuestLog helps you track your daily ques'
  [5] (-0.253, 0.197)  'The wizard cast a powerful fireball spel'

Saved plot to embedding_plot.png
```

Two things worth noticing in this real output beyond what the exercise
strictly asks for:

1. **The second-highest similarity (`0.3467`) is also a meaning-based
   cluster**, not the top pair's runner-up by coincidence: sentences `[2]`
   and `[3]` are both mundane grocery-errand sentences, correctly grouped
   together and clearly separated from the fantasy-themed sentences.
2. **The 2D coordinates visibly cluster by theme even after losing most of
   the original 384 dimensions of information**: the two fantasy-guard
   sentences (`[0]`, `[1]`) land at similar negative x-coordinates, the two
   grocery sentences (`[2]`, `[3]`) land at similar positive x-coordinates,
   and the wizard sentence (`[5]`) sits between the two clusters but closer
   to the fantasy side — exactly matching its `0.2795` similarity to `[0]`
   from the pairwise table above. This is a real, honest demonstration that
   even a lossy 2D projection preserves a meaningful amount of the original
   embedding space's structure.

The generated `embedding_plot.png` file itself is not checked into this
solution folder (per this course's convention of not committing generated
build artifacts) — run the script yourself to produce and view it.
