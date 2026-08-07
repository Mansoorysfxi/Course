# Notes on grading this yourself before asking for review

Run `python quest_roster.py` inside this `solution/` folder (or your own
completed `starter/quest_roster.py`) and compare the printed output against
what's described in `INSTRUCTIONS.md`'s acceptance criteria.

- **`format_quest`** — check the em dash (`—`) and exact spacing match:
  `"Slay the Dragon [Hard] — 0 gold"`. A common near-miss is using a
  regular hyphen `-` instead of the em dash, or missing a space.
- **`total_rewards()`** with zero arguments must return `0`, not `None` and
  not an error. If yours raises `TypeError: sum() ...`, you likely tried to
  call `sum(rewards, rewards)` or similar instead of the plain `sum(rewards)`
  — `rewards` is already the full tuple `*args` collected.
- **`filter_by_difficulty`** — the real check here is `quests is not
  hard_quests` printing `True`: this confirms a genuinely new list object
  was returned, not the same list object with items removed from it (which
  would also corrupt the caller's original data — exactly the mutability
  danger Lesson 03 warned about).
- **`unique_difficulties`** — must print as a `set` (curly braces, no
  guaranteed order, no duplicates) and `type(...)` must show
  `<class 'set'>` specifically, not `<class 'list'>`. If you used
  `list(set(...))` you've converted it back to a list — don't do that final
  conversion, the function should return the set itself.
- **`build_reward_lookup`** — the check here isn't just "does the right
  number come back," it's "did you build a dict for O(1) lookup" rather
  than looping through the list again inside a helper — re-read your own
  implementation and confirm there's no loop happening *at lookup time*,
  only once, when building the dict.
- **The one-sentence comment above `has_completed`** — this is graded like
  a real code review comment: does it correctly say *why* a set beats a
  list here (O(1) average membership check vs. O(n) scan, and that this
  matters because the check runs repeatedly, not once)? A comment that just
  restates "sets are faster" with no reasoning is a partial answer, not a
  full one.
