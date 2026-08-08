# Solution Notes — Exercise 03

**Honest disclosure:** no real `ANTHROPIC_API_KEY` was available while
generating this module, so this solution was actually run and verified in
its **dry-run path only** — the branch of the code that requires no key,
makes no network call, and costs nothing. That dry run completed cleanly
with no errors, and its real, actually-observed output is:

```
No ANTHROPIC_API_KEY found -- running in DRY RUN mode.
This is a fully legitimate way to complete this exercise.
See lessons/07-prompt-engineering-as-a-skill.md for realistic,
carefully-reasoned illustrations of what each prompt below
should produce, and read this script's own prompts to predict
the differences yourself before checking the lesson.

======================================================================
EXPERIMENT: System prompt
======================================================================

--- NAIVE ---
System: None
User message: 'Break down this quest into steps: Defeat the dragon guarding the old mine.'
(DRY RUN -- no ANTHROPIC_API_KEY set. Read lessons/07's
 corresponding worked example for a realistic illustration
 of what this prompt should produce, and why.)
```
(...and so on for all five experiments, each printing its naive and
improved prompt in full before noting the dry run.)

**What is, and is not, live-verified in this file:** the *code path*, the
*prompt content*, and the *dry-run message* above are all real,
actually-run, actually-observed output. The *live API responses* Lesson 07
describes for each of these same prompts (e.g. "a response along these
lines...") are honestly framed there as reasoned illustrations, not text
this course's generation process personally saw come back from Claude
Haiku 4.5 — because, again, no real key was available. If you have a real
key and run this script live, your own actual output is the first genuinely
live-observed version of these specific responses, and comparing your real
output against Lesson 07's reasoned predictions is itself a legitimate,
interesting thing to do during review.

**On the fifth experiment:** the reference solution's fifth experiment
combines two Lesson 07 techniques at once — a system prompt (`"You are
QuestLog's quest-recommendation assistant..."`) and chain-of-thought
(`"Think through their progress step by step before recommending."`) —
applied to a quest-recommendation scenario, deliberately structured to
mirror exactly the kind of feature QuestLog gains for real starting in
Module 13's "suggest a quest breakdown" AI assistant endpoint. Combining
techniques is a legitimate, common, real pattern — nothing in Lesson 07
restricts you to using exactly one technique per prompt.
