# Exercise 05 — A Real Eval Harness for a Quest-Breakdown Function

## What you'll build

A script, `eval_breakdown.py`, that combines this module's own final two
skills: generating a structured quest breakdown (Lesson 03) and running a
small golden-set eval harness against the results (Lesson 06) — runnable
in two modes: **mocked** (no API key needed, fully deterministic — the
default) and **live** (a real, small number of calls against Claude
Haiku 4.5, if you pass `--live` and have a key set).

This is this module's most independent exercise — you're given the
scenario and the acceptance criteria, not a near-complete script or a
worked example to adapt line by line.

## Concepts this exercise uses

- Structured output with a JSON Schema and Pydantic validation (Lesson
  03)
- A golden set of hand-picked test cases, and plain, deterministic
  checks against each one's result (Lesson 06)
- Basic error handling: what to do if a live call refuses or gets cut off
  (Lesson 05) — needed only in `--live` mode

## Requirements

Write `eval_breakdown.py` that:

1. Defines `generate_breakdown(quest_title: str, quest_description: str,
   existing_titles: list[str]) -> list[str]` — a **non-streamed, no-tool-use**
   function using `output_config.format` (Lesson 03) to get a
   schema-conformant list of 2-4 sub-quest titles, validated with a
   Pydantic model before returning. Mention the player's existing titles
   directly in the prompt text (a plain instruction, e.g. "the player
   already has these quests: ...; don't suggest a duplicate") — this
   exercise does not require the tool-use round-trip from Lesson 04 or
   Exercise 04; a plain prompt is a legitimate, simpler alternative for a
   standalone script like this one.
2. Defines a golden set of **at least 3** cases (`GoldenCase` — see
   Lesson 06's own example for the shape), each with a `quest_title`,
   `quest_description`, and `existing_titles`, chosen deliberately to
   exercise something different from each other (an ordinary case, a
   case with an existing near-duplicate title, and at least one more of
   your own choosing).
3. Defines `check_result(case, sub_quests) -> list[str]`, following
   Lesson 06's own pattern: checks the count is 2-4, no title is empty or
   over 12 words, no title duplicates an existing title, and no title is
   a verbatim restatement of the original quest.
4. Supports two modes, chosen by a command-line flag:
   - **Default (mocked):** runs the harness against a small,
     hand-written `CANNED_RESULTS` dict (one entry per golden case) —
     exactly Lesson 06's own demonstration pattern — so the whole script
     runs instantly with **no API key required at all**.
   - **`--live`:** calls your real `generate_breakdown` function once per
     golden case instead of using canned data. Wrap each live call in a
     `try`/`except` that handles `anthropic.APIError` and a
     `stop_reason == "refusal"` result gracefully (print a clear message
     and treat that case as inconclusive rather than crashing the whole
     run).
5. Prints a `PASS`/`FAIL` line per case (with the specific problems
   listed for any failure), and a final summary line with the total
   problem count — matching Lesson 06's own demonstrated output format.

## Acceptance criteria

- [ ] `python eval_breakdown.py` (no flags) runs to completion with
      **no API key set at all**, and produces the same output every time
      you run it (fully deterministic, since it's using canned data).
- [ ] `python eval_breakdown.py --live` (with a real key set) makes real
      API calls and evaluates the genuine responses — this run's exact
      PASS/FAIL results may vary between runs, which is expected and
      fine (Module 12, Lesson 06's sampling material) — but the script
      itself should never crash, even if one case's live response
      happens to fail a check.
- [ ] At least one of your golden cases' canned result is written to
      deliberately **fail** at least one check, so you can see your
      harness actually catching a real problem, not just always passing.
- [ ] `check_result` contains zero hardcoded references to any specific
      golden case's data — it's a general function that works against
      any `GoldenCase` and any list of sub-quest title strings.

## Hints

1. **Level 1:** Lesson 06's own worked example is almost this entire
   exercise's harness half already — the new work is writing
   `generate_breakdown` (Lesson 03's own pattern) and the `--live` mode.
2. **Level 2:** `sys.argv` (Exercise 02 already used this) is the
   simplest way to check for a `--live` flag:
   `live_mode = "--live" in sys.argv`.
3. **Level 3:** For the refusal check in `--live` mode, remember
   `stop_reason == "refusal"` is a normal, successful response, not an
   exception — your `try`/`except` around the API call itself is for
   catching things like `anthropic.RateLimitError`, while the refusal
   check is a plain `if` on the response you already got back
   successfully.

This exercise has **no `solution/` file for the golden-set contents or
the exact prompt wording** on purpose — those are genuine design
decisions with more than one reasonable answer. `solution/eval_breakdown.py`
shows one complete, working reference implementation; if yours differs in
its exact wording or golden-set choices but meets every acceptance
criterion above, it's correct.
