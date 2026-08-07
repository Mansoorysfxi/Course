# Exercise 01 — Functions and Data Structures Warm-Up

**Difficulty:** Very easy — this should be nearly impossible to fail if you've
read [`lessons/01-variables-types-and-control-flow.md`](../../lessons/01-variables-types-and-control-flow.md),
[`lessons/02-functions-and-scope.md`](../../lessons/02-functions-and-scope.md),
and [`lessons/03-data-structures.md`](../../lessons/03-data-structures.md) carefully.

**Concepts this exercise uses** (all taught in the three lessons above):
defining functions, default arguments, `*args`, `**kwargs`, f-strings,
`if`/`elif`/`else`, lists, tuples, sets, dicts, `.append()`, `in` for
membership checks, `.get()`, and basic time-complexity intuition
(list scan vs. set/dict lookup).

## What to build

Open [`starter/quest_roster.py`](starter/quest_roster.py) — it already has
every function's signature written for you, each with a `# TODO` and a
docstring describing exactly what it must do. Fill in each function's body.
Do not change any function's name or parameter list — the acceptance
criteria below assume they stay exactly as given.

1. **`format_quest(name, difficulty, reward_gold=0)`** — return a string in
   the exact form `f"{name} [{difficulty}] — {reward_gold} gold"`. This
   practices a default argument (Lesson 02): calling `format_quest("Slay
   the Dragon", "Hard")` with no third argument should use `0`.
2. **`total_rewards(*rewards)`** — accept any number of reward amounts as
   separate positional arguments and return their sum using `*args`
   (Lesson 02). Calling it with zero arguments should return `0`, not error.
3. **`describe_player(**stats)`** — accept any number of keyword arguments
   describing a player (e.g. `name="Aria", level=12, hp=100`) and return a
   single string listing each `key: value` pair, comma-separated, using
   `**kwargs` (Lesson 02). The exact separator/format is up to you, as long
   as every key and value you were given appears somewhere in the string.
4. **`filter_by_difficulty(quests, difficulty)`** — given a list of quest
   dicts (each with at least a `"name"` and `"difficulty"` key) and a target
   difficulty string, return a **new list** containing only the quest dicts
   whose `"difficulty"` matches, using a plain `for` loop and `if` (not a
   comprehension — that's Lesson 04, not yet taught when you do this
   exercise). Do not mutate the input list.
5. **`unique_difficulties(quests)`** — given the same shape of list, return
   a **`set`** of every distinct `"difficulty"` value present, with no
   duplicates. This practices choosing a `set` specifically because
   duplicates should collapse automatically (Lesson 03).
6. **`build_reward_lookup(quests)`** — given the same shape of list, return
   a **`dict`** mapping each quest's `"name"` to its `"reward_gold"`, so
   that looking up any quest's reward by name afterward is an O(1) dict
   lookup rather than an O(n) list scan (Lesson 03's time-complexity
   intuition).
7. **`has_completed(completed_ids, quest_id)`** — given a `set` of already-
   completed quest IDs and a specific ID, return `True`/`False` using `in`.
   Answer, in a comment directly above this function in your file: *why is
   `completed_ids` typed as a `set` and not a `list` here?* (One sentence is
   enough — this is checked as part of the review, per Lesson 03's
   time-complexity section.)

## Acceptance criteria

- [ ] All seven functions are implemented, keep their original names/parameters, and match the exact behavior described above.
- [ ] `format_quest("Slay the Dragon", "Hard")` returns `"Slay the Dragon [Hard] — 0 gold"` (default argument used correctly).
- [ ] `total_rewards()` (no arguments) returns `0`, and `total_rewards(100, 250, 50)` returns `400`.
- [ ] `describe_player(name="Aria", level=12)` returns a string containing both `"Aria"` and `"12"`.
- [ ] `filter_by_difficulty` returns a **new** list — the original input list is unchanged after calling it.
- [ ] `unique_difficulties` returns a `set` (verify with `type(...)`), not a list, with no duplicate values.
- [ ] `build_reward_lookup` returns a `dict` where `lookup["Slay the Dragon"]` gives the correct reward directly, with no loop needed at lookup time.
- [ ] The one-sentence comment above `has_completed` correctly explains the O(1) vs. O(n) reasoning from Lesson 03.
- [ ] Running `python quest_roster.py` directly (it has a small demo block at the bottom under `if __name__ == "__main__":`) prints output with no errors.

## What to submit

When you're ready for review, point your AI session at your completed
`starter/quest_roster.py` (or copy it into a new file if you'd rather keep
the starter folder pristine) and say *"Review my solution for Exercise 01."*

## Hints

- If you're unsure how to test a function while writing it, add temporary
  `print(...)` calls under the `if __name__ == "__main__":` block at the
  bottom of the file (Lesson 07 explains exactly why that guard exists) and
  run `python quest_roster.py` repeatedly as you go — you don't need a
  separate test framework for this exercise.
- Stuck on `format_quest`'s default argument? Re-read Lesson 02's "Default
  arguments — the easy, safe case" section — this one is the safe,
  non-mutable case, not the mutable-default trap covered right after it.
- Stuck on `*rewards` summing to `0` for zero arguments? Recall from Lesson
  02 that `*args` always collects into a real (possibly empty) tuple, never
  `None` — `sum(())` is a completely normal expression.
- Stuck on why `filter_by_difficulty` must return a *new* list rather than
  modifying the input? Re-read Lesson 03's "Mutability in action" section —
  a function that silently mutates a list it was only supposed to *read*
  is a common source of bugs elsewhere in a program that still holds a
  reference to that same list.
- If you've re-read the relevant section and are still stuck, ask your AI
  session for a hint — Level 1 first, per [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md).
