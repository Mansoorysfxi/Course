# Exercise 03 — Prompt Engineering Experiments

**Difficulty:** Independent — this is the module's last exercise, and it
asks you to add a genuinely new experiment of your own, not just fill in
provided logic. **Optional-but-recommended real cost** — see below; a
zero-cost dry run is a fully legitimate way to complete every acceptance
criterion.

**Concepts this exercise uses** (all taught in
[`lessons/07-prompt-engineering-as-a-skill.md`](../../lessons/07-prompt-engineering-as-a-skill.md)):
system prompts, few-shot prompting, chain-of-thought prompting, structured
(JSON) output requests, and the real, current `client.messages.create(...)`
call shape.

## On cost — read this first

This exercise is the one place in this module that genuinely benefits from
a real API key (Lesson 00, Step 5) — seeing an actual model's actual
response change based on a prompting technique is a better teacher than
any written description. **It is still entirely optional.** The script you'll
complete automatically detects whether `ANTHROPIC_API_KEY` is set and runs
in a completely safe, zero-cost "dry run" mode if it isn't — printing every
prompt clearly so you can read Lesson 07's own worked examples alongside
it and reason about what each real response would look like. If you do have
a key, running every experiment in this exercise once costs, per Lesson
00's verified pricing, well under a cent total.

## What to build

Open
[`starter/prompt_lab.py`](starter/prompt_lab.py) — it already has four
complete experiments defined (one per technique from Lesson 07), a working
`run_experiment` function that handles both the live and dry-run paths, and
two `# TODO` functions for you to fill in.

1. **`get_client()`** — return `None` if `ANTHROPIC_API_KEY` isn't set in
   the environment (triggering dry-run mode everywhere else in the script);
   otherwise, import `anthropic` **inside the function** (so the import
   never happens at all in dry-run mode) and return `anthropic.Anthropic()`.
2. **`estimate_cost(input_tokens, output_tokens)`** — using the pricing
   constants already defined at the top of the file, compute and return the
   combined input + output cost in dollars.
3. **(Independent step) Add a fifth experiment** to the `EXPERIMENTS` list,
   following the exact same `{"name": ..., "naive": {...}, "improved":
   {...}}` shape as the four already there. Apply any technique — or
   combination of techniques — from Lesson 07 to a QuestLog-flavored prompt
   you write yourself. It does not need to be complicated; it needs to
   genuinely demonstrate one real prompting technique changing the model's
   likely output in a specific, explainable way.

## Acceptance criteria

- [ ] `get_client()` and `estimate_cost(...)` are both implemented, keep their original names/parameters, and match the exact behavior described above.
- [ ] Running `python prompt_lab.py` with **no** `ANTHROPIC_API_KEY` set completes with no errors, no network calls, and prints a clear "DRY RUN" message for every experiment (including your new fifth one).
- [ ] `EXPERIMENTS` now has **five** entries, and your fifth one has a distinct `"name"`, a real `"naive"`/`"improved"` prompt pair, and applies a technique genuinely taught in Lesson 07.
- [ ] If you have a real API key and choose to run it live: `estimate_cost(...)` returns a small positive number for each real response, and you can point to the real, printed differences between at least two of your naive/improved response pairs and explain, in your own words, why the improved version changed the way it did.
- [ ] If you do **not** run it live: you can still explain, for your own fifth experiment specifically, *why* you'd expect the improved prompt to produce a better or more reliable response than the naive one — citing the specific mechanism from Lesson 07 (context shaping, few-shot pattern-matching, visible intermediate reasoning, or explicit output-shape constraints).

## What to submit

When you're ready for review, point your AI session at your completed
`starter/prompt_lab.py` and say *"Review my solution for Module 12 Exercise
03."* Mention explicitly whether you ran it live (and if so, roughly what
it cost) or completed it as a dry run — both are fully acceptable, and
your reviewer should grade the reasoning either way, not just live output.

## Hints

- If `get_client()` raises `ModuleNotFoundError: No module named
  'anthropic'` even when you have no key set, you've put the `import
  anthropic` line in the wrong place — it must be *inside* the `if` branch
  that only runs once a key is confirmed present, per the docstring's
  Step 2.
- Stuck on what makes a good fifth experiment? Re-read Lesson 07's own
  four worked examples for inspiration — a good fifth experiment usually
  starts from "which one of these four techniques would help most with a
  QuestLog feature I can imagine," then writes one naive prompt and one
  improved prompt that isolates exactly that technique's effect.
- If you're running this live and a response doesn't look like what Lesson
  07's illustrative example predicted, that's genuinely fine and expected —
  Lesson 07 was explicit that its own examples were reasoned illustrations,
  not guaranteed exact wording. What matters is whether the *general
  effect* of the technique (more specific tone from a system prompt, more
  consistent format from few-shot examples, more careful arithmetic from
  chain-of-thought, valid JSON from a structured-output request) shows up.
- If you've re-read the relevant section and are still stuck, ask your AI
  session for a hint — Level 1 first, per
  [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md).
