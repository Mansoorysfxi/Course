# Grading Protocol

This is the exact rubric used every time you ask for an exercise review or a
module-end review. It is a direct copy of Rule 3 from
[MASTER_LEARNING_PLAN.md](MASTER_LEARNING_PLAN.md), kept here as its own file
so any session can be pointed at it directly: *"grade my exercise using
GRADING_PROTOCOL.md."*

## Single-exercise review

Triggered by: *"Review my solution for exercise X"* (or pasting/pointing at code).

The AI must:

1. **Run/read the solution carefully** — never skim. If it's runnable, run it. If it has tests, run them. Trace through the logic by hand for at least one non-trivial input.
2. **State what was done right**, specifically. Not "good job" — name the actual decision and why it was a good one (e.g., "using a set here instead of a list for `seen_ids` is correct because membership checks need to be O(1) once you're doing this for every request").
3. **State what was done wrong or is missing**, with the exact location — file, line number, function/class name — and an explanation of *why* it's wrong: what bug it causes, what security issue it opens, or what bad practice it reinforces.
4. **State what could be improved**, even if the code is technically correct — naming, structure, performance, more idiomatic style, unhandled edge cases.
5. **Give a score out of 10** with a short justification for that specific number (not just "8/10, nice work" — say what's keeping it from being a 10).
6. **Ask 2–3 follow-up comprehension questions** that verify understanding of *why* the code works, not just that it happens to work. Example style: "What would happen if two requests hit this endpoint at the same time?" or "Why did we need `await` on this line but not that one?"
7. **If the score is below 7**, tell the learner to revise and resubmit before moving on. Give hints first (see "Hint levels" below), not the full corrected solution — reveal the full solution only if the learner explicitly asks for it, or after two failed review rounds on the same exercise.

## Module-end review

Triggered by: *"Check my module"* / *"Review my progress"* (after the capstone project is done).

The AI must:

1. **Grade all of the module's exercises and the capstone** using the single-exercise protocol above — anything not yet reviewed, plus re-checking anything the learner revised.
2. **Look back at earlier modules.** Read [PROGRESS.md](PROGRESS.md) and the actual solution files from previous modules. Compare: are past weaknesses improving or repeating? Are old concepts still being applied correctly in new code, or fading? Cite specific evidence — e.g., "you handled errors well in exercises 03 and 05, but exercise 07 still has the same missing-validation issue flagged back in Module 04."
3. **Produce a module report** containing: an overall score, the strongest areas (with evidence), recurring weaknesses (with evidence across multiple exercises, not just this module's), and 2–3 concrete focus points to carry into the next module.
4. **Update PROGRESS.md** with this report — status table, exercise log, skills tracker, module reports, and focus points. This is the AI's responsibility, not the learner's.
5. **If recurring weaknesses are serious**, generate 1–2 small remedial exercises that target them directly, referencing the lesson material the learner needs, and ask the learner to complete those before starting the next module.

## Hint levels

When the learner asks for a hint instead of a review (typically mid-exercise, stuck for 30+ minutes):

- **Level 1 — Orientation.** Point at the general area/concept without touching the code. "Think about what happens to your loop variable after the exception is caught."
- **Level 2 — Narrowing.** Point at the specific function/line and name the category of the issue, still without giving the fix. "Look at line 42 — what's the lifetime of that variable relative to when the callback actually runs?"
- **Level 3 — Near-solution.** Describe the fix in words, or show a *similar but different* code snippet illustrating the pattern, without pasting the learner's exact fix.
- **Full solution** — only after level 3 hasn't resolved it, or the learner explicitly asks for the answer outright.

Always start at Level 1 unless the learner explicitly asks for a specific level.

## Scoring guide (for consistency across reviews)

- **9–10:** Correct, handles edge cases, idiomatic, well-named, no security or correctness issues. Nitpicks only.
- **7–8:** Correct and handles the main cases, but has minor issues — a missed edge case, a naming/style improvement, a small inefficiency. Safe to move on.
- **5–6:** Works for the happy path but has a real gap — a missing validation, an edge case that breaks it, a misunderstanding of a taught concept. Revise before moving on.
- **3–4:** Doesn't fully work, or works by accident (right output, wrong reasoning/mechanism). Needs a substantive redo, hints first.
- **0–2:** Doesn't run, or the core concept from the lesson is missing/misapplied entirely.

## Why this exists

Grading consistency matters more than any single grade. The point of scoring
and tracking recurring weaknesses in [PROGRESS.md](PROGRESS.md) is to catch
patterns a single review can't see — e.g., the same missing-error-handling
habit showing up in Modules 04, 07, and 09 is a real signal worth calling
out explicitly, even if each individual exercise "passed."
