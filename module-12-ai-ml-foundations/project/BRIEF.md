# Capstone Brief — The AI Foundations Toolkit

## What you're building

A single, standalone command-line Python script — `ai_foundations_toolkit.py`
— that combines everything from this module's three exercises into one
small, satisfying synthesis tool. This is **not** a QuestLog capstone —
per `RUNNING_PROJECT.md`'s own table, Module 12 makes no QuestLog code
changes at all, on purpose (Rule 1: concepts first). Think of this the way
Module 01's QuestLog CLI capstone combined that module's many small lessons
into one working program — same idea, scaled to this module's concept-only
scope.

## Before you start

- [ ] All three exercises in this module are done and reviewed.
- [ ] You've read Lessons 00-07 in full, in order.
- [ ] You have `tiktoken` and `sentence-transformers` installed and
      verified working (Lesson 00).
- [ ] You have, optionally, a real `ANTHROPIC_API_KEY` set (Lesson 00, Step
      5) — genuinely optional; a documented dry run is a fully accepted way
      to complete Part 3 below, exactly as Exercise 03 already established.

## What to actually build

Your script should do three things, in order, when run:

### Part 1 — Tokenize and estimate cost

Accept a piece of text (hardcoded as a variable at the top of your script is
fine — this doesn't need real command-line argument parsing) and report:

- Its token count, using `tiktoken` exactly as Exercise 01 taught.
- A comparison against a naive word count, showing the gap between the two.
- An estimated cost to send that text as input to Claude Haiku 4.5, using
  the pricing constants verified in Lesson 00's setup ($1.00 per million
  input tokens).

### Part 2 — Find the most similar pair among sample sentences

Using a small set of at least 5 sample sentences of your own choosing (they
don't have to be the exact ones from Exercise 02 — pick your own, ideally
ones where at least one pair is genuinely, meaningfully more similar than
the others, so your output has something interesting to show), compute
embeddings with `sentence-transformers` exactly as Exercise 02 taught, and
report:

- Every pairwise cosine similarity score.
- Which pair is most similar, and the actual score.
- One sentence, in your own words (a comment or printed line), explaining
  *why* that pair is more similar in meaning than the others, even if they
  don't share much vocabulary.

### Part 3 — A naive-vs-improved prompt comparison

Pick **one** prompt-engineering technique from Lesson 07 (system prompt,
few-shot, chain-of-thought, or structured output) and run a naive-vs-
improved comparison, exactly like Exercise 03's pattern:

- If you have a real API key: make it a genuine, live comparison — two real
  API calls, with the real responses and real token/cost numbers printed.
- If you don't: your script should still run cleanly end-to-end with no
  errors and no attempted network call (reuse Exercise 03's `get_client()`
  pattern — check for the environment variable, return `None` if it's
  missing, and print a clear dry-run notice), and your submission should
  include a short written explanation (in the script's own comments, or in
  a paragraph you tell your AI reviewer directly) of what you'd expect the
  real difference to be and why, citing the specific mechanism from Lesson
  07.

## Acceptance criteria (what "done" looks like)

- [ ] `ai_foundations_toolkit.py` runs end to end with `python
      ai_foundations_toolkit.py` and no errors, whether or not a real API
      key is set.
- [ ] Part 1's token count and cost estimate are real, computed values (not
      hardcoded numbers) — verify by changing the input text and confirming
      the printed numbers actually change.
- [ ] Part 2 correctly identifies the single highest-scoring pair among all
      pairwise comparisons of your chosen sentences (not just any two
      sentences that seem similar to you by eye).
- [ ] Part 3 either makes a real, live comparison (if you have a key) or
      cleanly dry-runs with a clear explanation of the expected difference
      (if you don't) — no silent failures, no crash if the key is missing.
- [ ] You can explain, without looking anything up, why each of the three
      parts works the way it does — which earlier lesson each part is
      built on, and why the specific numbers/results you got make sense
      given that lesson's explanation.
- [ ] No real money was spent unless you deliberately chose to run Part 3
      live — the free path (Parts 1-2 always free; Part 3's dry run) fully
      satisfies every criterion above.

## A note on scope

This capstone is intentionally small — a "concepts, not tools" module gets
a synthesis exercise, not a production system. There's no database, no web
framework, no deployment step. The entire point is proving to yourself (and
to whoever reviews it) that Lessons 03, 04, and 07's separate ideas —
tokenization, embeddings, and prompt engineering — are genuinely connected
pieces of the same underlying picture (a trained neural network predicting
tokens, one at a time, using attention over embedded context), not three
unrelated tricks you happened to learn back to back.

## What to submit

When you're ready for review, point your AI session at your completed
`ai_foundations_toolkit.py` and say *"Check my Module 12 capstone."* Mention
explicitly whether Part 3 was run live or as a dry run.
