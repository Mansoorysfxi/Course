# Exercise 02 — Comprehensions, Generators, and a Real Class Hierarchy (Guided)

**Difficulty:** Guided — more independent than Exercise 01, but the shape of
each piece is still spelled out. You decide some of the exact
implementation details yourself.

**Concepts this exercise uses:**
- From [`lessons/04-comprehensions-generators-and-iterators.md`](../../lessons/04-comprehensions-generators-and-iterators.md): list comprehensions, dict comprehensions, generator functions (`yield`), and making a custom class iterable via `__iter__`.
- From [`lessons/05-oop-classes-and-dunders.md`](../../lessons/05-oop-classes-and-dunders.md): class definitions, `__init__`, `__repr__`, `__eq__`, `__len__`, inheritance with `super()`, and composition.

## What to build

Open [`starter/questline.py`](starter/questline.py). It contains the same
kind of TODO-marked skeleton as Exercise 01. Work through it top to bottom —
later pieces depend on earlier ones.

1. **`Quest` class** — attributes `name`, `difficulty`, `reward_gold`,
   `is_complete` (default `False`). Implement `__repr__` so that
   `print(quest)` shows something like
   `Quest(name='Slay the Dragon', difficulty='Hard', reward_gold=500, is_complete=False)`
   (Lesson 05's `__repr__` section shows this exact pattern). Implement
   `__eq__` so two `Quest`s are equal if `name`, `difficulty`, and
   `reward_gold` all match (ignore `is_complete` in the comparison, same as
   Lesson 05's own example).
2. **`TimedQuest(Quest)`** — a subclass adding one extra attribute,
   `time_limit_minutes`. Its `__init__` must call `super().__init__(...)`
   (do not re-implement setting `name`/`difficulty`/`reward_gold` yourself —
   reuse the parent). Override `__repr__` so it includes
   `time_limit_minutes` too, ideally by calling `super().__repr__()` and
   extending its result rather than rewriting it from scratch.
3. **`QuestLine` class** — holds a list of `Quest` (or `TimedQuest`)
   instances internally (composition — a `QuestLine` *has* quests, it
   isn't one). Implement `__len__` (number of quests it holds) and
   `__iter__` (delegate to the internal list's own iterator, exactly
   Lesson 05's `QuestLine` example).
4. **`incomplete_quest_names(quest_line)`** — a **list comprehension**
   (one line) returning the `name` of every quest in `quest_line` where
   `is_complete` is `False`.
5. **`reward_lookup_over(quest_line, minimum_reward)`** — a **dict
   comprehension** (one line) mapping `name -> reward_gold` for every quest
   in `quest_line` whose `reward_gold` is `>= minimum_reward`.
6. **`high_priority_quests(quest_line, minimum_reward)`** — a **generator
   function** (uses `yield`, not `return`) that lazily yields each quest in
   `quest_line` whose `reward_gold` is `>= minimum_reward`, one at a time,
   without building an entire list first. Prove to yourself it's lazy: add
   a `print(f"checking {quest.name}")` line right before each `yield`
   check, then only call `next()` on it once or twice in your own testing
   and confirm it doesn't check *every* quest immediately.

## Acceptance criteria

- [ ] `Quest.__repr__` produces the exact field-by-field format shown above; `print(quest)` and `repr(quest)` both show it (Lesson 05 explains why defining `__repr__` alone covers both when `__str__` isn't separately defined).
- [ ] `Quest("A", "Hard", 100) == Quest("A", "Hard", 100)` is `True` even if `is_complete` differs between them; `Quest("A", "Hard", 100) == Quest("B", "Hard", 100)` is `False`.
- [ ] `TimedQuest`'s `__init__` calls `super().__init__(...)` — verify by confirming a `TimedQuest` instance has a correctly-set `name`/`difficulty`/`reward_gold` without `TimedQuest.__init__` setting them directly itself.
- [ ] `isinstance(some_timed_quest, Quest)` is `True`.
- [ ] `len(my_quest_line)` and `for q in my_quest_line:` both work correctly on a `QuestLine` instance.
- [ ] `incomplete_quest_names` and `reward_lookup_over` are each written as a single-line comprehension, not a `for` loop with `.append()`/manual dict-building.
- [ ] `high_priority_quests` is a generator function (uses `yield`) — confirm `type(high_priority_quests(line, 100))` prints `<class 'generator'>`, not `<class 'list'>`.
- [ ] Running `python questline.py` directly prints sensible output with no errors.

## What to submit

Point your AI session at your completed `starter/questline.py` and say
*"Review my solution for Exercise 02."*

## Hints

- Stuck on `__repr__`'s exact format? Re-read Lesson 05's dunder methods
  section — note the `!r` usage inside the f-string so string fields show
  their own quotes in the output.
- Stuck on why `TimedQuest.__init__` needs `super().__init__(...)`? Re-read
  Lesson 05's "genuine difference from C++" callout — Python does not call
  a parent's `__init__` automatically just because a subclass defines its
  own.
- Stuck on `QuestLine.__iter__`? It can be a one-line `return
  iter(self._quests)` — re-read Lesson 05's own `QuestLine` example, it's
  intentionally almost identical.
- Stuck on making `high_priority_quests` lazy rather than eager? Make sure
  you used `yield` and not `return` — a function with any `yield` anywhere
  in its body becomes a generator function, and calling it never runs the
  body immediately (Lesson 04).
- If you've re-read the relevant section and are still stuck, ask your AI
  session for a Level 1 hint per [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md).
