# Notes on grading this yourself before asking for review

Run `python questline.py` and compare against `INSTRUCTIONS.md`'s
acceptance criteria.

- **`Quest.__repr__`** — check field order and the use of `!r` on string
  fields (`name`, `difficulty`) so they print with quotes, while
  `reward_gold` (an int) and `is_complete` (a bool) print without quotes.
  If your output shows `name=Slay the Dragon` (no quotes), you used `{self.name}` instead of `{self.name!r}`.
- **`TimedQuest.__repr__`** — the real check is that it calls
  `super().__repr__()` rather than duplicating every field itself. If you
  rewrote all the fields by hand inside `TimedQuest.__repr__`, it'll still
  probably produce correct-looking output, but it violates the "reuse the
  parent, don't duplicate it" point the exercise is checking — a real
  reviewer would flag this as a maintainability issue (if `Quest.__repr__`
  ever changes, your duplicated version silently drifts out of sync).
- **`__eq__`** — confirm it truly ignores `is_complete`. A common mistake
  is comparing the two `Quest` objects' entire `__dict__` instead of the
  three named fields, which would incorrectly make otherwise-identical
  quests with different `is_complete` values compare unequal.
- **List/dict comprehensions** — the instructions specifically require
  *single-line comprehensions*, not a `for` loop with `.append()` or manual
  dict assignment. If you wrote a loop instead, the output will likely
  still be correct, but re-read Lesson 04 and rewrite it as a genuine
  comprehension — that's specifically what's being practiced here.
- **`high_priority_quests` laziness** — the strongest self-check: put a
  `print(f"checking {quest.name}")` right before the `if` check inside the
  generator, create the generator, and call `next()` on it *once*. You
  should see exactly one `"checking ..."` line print, not all three
  quests' lines at once — proof the function body only advances as far as
  the next `next()` call demands, exactly Lesson 04's "pause and resume"
  mechanism.
