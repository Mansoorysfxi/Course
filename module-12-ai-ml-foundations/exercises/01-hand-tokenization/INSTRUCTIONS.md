# Exercise 01 — Hand Tokenization Playground

**Difficulty:** Very easy — this should be nearly impossible to fail if
you've read
[`lessons/03-tokens-and-tokenization.md`](../../lessons/03-tokens-and-tokenization.md)
carefully. **Zero cost, zero account needed** — this exercise uses only
`tiktoken`, installed for free in [`lessons/00-setup.md`](../../lessons/00-setup.md).

**Concepts this exercise uses** (all taught in Lesson 03): what a token is,
what `tiktoken.get_encoding(...)` returns, `encode()` turning text into a
list of token IDs, `decode([token_id])` turning a single token ID back into
its text piece, and the general BPE idea that tokens are subword pieces,
not whole words.

## What to build

Open
[`starter/tokenize_playground.py`](starter/tokenize_playground.py) — it
already has every function's signature written for you, each with a
`# TODO` and a docstring describing exactly what it must do. Fill in each
function's body using `tiktoken`, exactly as Lesson 03 demonstrated. Do not
change any function's name or parameter list.

1. **`count_tokens(text, encoding_name="o200k_base")`** — return how many
   tokens `text` encodes into, using `tiktoken.get_encoding(encoding_name)`
   and `.encode(text)`.
2. **`show_token_pieces(text, encoding_name="o200k_base")`** — return a list
   of the actual decoded text for each token in `text`, in order (e.g. for
   `"QuestLog"` this should return `['Quest', 'Log']`, exactly matching
   Lesson 03's own worked example). Remember `decode()` expects a *list* of
   token IDs, even when decoding just one — `enc.decode([token_id])`, not
   `enc.decode(token_id)`.
3. **`compare_word_vs_token_count(text)`** — return a `(word_count,
   token_count)` tuple: `word_count` from a naive `text.split()`,
   `token_count` from calling your own `count_tokens(text)`.
4. **`estimate_input_cost(text, price_per_million=HAIKU_INPUT_PRICE_PER_MILLION)`**
   — return the estimated dollar cost of sending `text` as input to a model
   priced at `price_per_million` dollars per million tokens: get the token
   count, divide by 1,000,000, multiply by the price.

## Acceptance criteria

- [ ] All four functions are implemented, keep their original names/parameters, and match the exact behavior described above.
- [ ] `count_tokens("QuestLog")` returns `2` (verify with the real, actually-run value from Lesson 03: `'QuestLog'` tokenizes to `['Quest', 'Log']`).
- [ ] `show_token_pieces("QuestLog")` returns exactly `['Quest', 'Log']`.
- [ ] `compare_word_vs_token_count(...)` returns a tuple of two integers, and for most real sentences the two numbers are **not** equal (per Lesson 03, token count and word count are genuinely different things).
- [ ] `estimate_input_cost(...)` returns a small positive float, and doubling the input text's length roughly doubles the estimated cost (not exactly, since token counts don't scale perfectly linearly with character count, but roughly).
- [ ] Running `python tokenize_playground.py` directly (it has a demo block at the bottom under `if __name__ == "__main__":`) prints output with no errors, and the printed token count for the demo sentence matches what you get from independently running `tiktoken` yourself on the same text.

## What to submit

When you're ready for review, point your AI session at your completed
`starter/tokenize_playground.py` and say *"Review my solution for Module 12
Exercise 01."*

## Hints

- If `tiktoken.get_encoding("o200k_base")` fails with any kind of network
  or lookup error, re-check Lesson 00's setup — `tiktoken` should already
  have everything it needs bundled after installation, with no network
  access required at run time.
- Stuck on `decode()`'s list-wrapping requirement? Re-read Lesson 03's own
  `explore_tokens.py` example — it calls `enc.decode([token_id])` inside a
  loop, one token ID at a time, wrapped in a list each time.
- If your token counts don't match Lesson 03's worked examples exactly,
  double check you're using `"o200k_base"` and not a different encoding
  name — different encodings produce genuinely different token counts for
  the same text, exactly as Lesson 03 explained.
- If you've re-read the relevant section and are still stuck, ask your AI
  session for a hint — Level 1 first, per
  [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md).
