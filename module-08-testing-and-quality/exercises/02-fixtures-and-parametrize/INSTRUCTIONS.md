# Exercise 02 — Fixtures and Parametrize

**Difficulty:** Guided — builds directly on Exercise 01, adding fixtures
and parametrize on top of the same kind of plain, dependency-free code.

## Concepts this exercise uses (all taught in the lessons named)

- `@pytest.fixture`, and using one fixture from another —
  `lessons/02-pytest-fundamentals-and-fixtures.md`, Steps 4 and (the
  "fixture depending on another fixture" gotcha) the Common Mistakes
  section.
- `conftest.py`, so fixtures are available with no import —
  same lesson, Step 6.
- `pytest.raises` — same lesson, Step 3.
- `@pytest.mark.parametrize` — `lessons/03-parametrize-and-mocking.md`.

## What you're given

`starter/quest_board.py` — a `QuestBoard` class (an in-memory collection
of `Quest` objects) with **no tests at all yet**:
- `add_quest(title, priority) -> Quest`
- `mark_done(title) -> None` — raises `KeyError` if no quest has that title.
- `count_by_priority(priority) -> int`
- `all_done() -> bool` — read its docstring carefully; the empty-board
  case is easy to get backwards.

## What to do

1. Create `starter/conftest.py` with **two fixtures**:
   - `empty_board` — returns a fresh `QuestBoard()` with nothing on it.
   - `stocked_board` — depends on `empty_board` (take it as a parameter,
     the same way a test would) and adds **three** quests of three
     **different** priorities to it before returning it.
2. Create `starter/test_quest_board.py` with tests that use both
   fixtures, covering:
   - A board with no quests: `all_done()` is `True` (the vacuous-truth
     case named in the docstring), and every `count_by_priority` call
     returns `0`.
   - `mark_done` on a title that doesn't exist raises `KeyError`
     (`pytest.raises`).
   - Marking every quest on the stocked board done makes `all_done()`
     `True`; marking only *one* of them done does **not** affect the
     other quests' `done` status.
   - Using `@pytest.mark.parametrize`, confirm `count_by_priority`
     returns the right count for **each** of the three priorities on the
     stocked board, as one parametrized test (not three separate,
     near-identical test functions).

## Acceptance criteria

- [ ] `python -m pytest -v` from `starter/` shows every test passing.
- [ ] `conftest.py` has both fixtures, and `stocked_board` genuinely
      takes `empty_board` as its own parameter rather than creating a
      second, separate `QuestBoard()` itself.
- [ ] At least one test uses `@pytest.mark.parametrize` to check all
      three priorities, and `pytest -v`'s output shows three separately
      reported, named test cases from that one parametrized function.
- [ ] The empty-board `all_done()` case has its own dedicated test —
      don't skip it just because it feels like an edge case; it's exactly
      the kind of thing a fixture-driven test suite makes cheap to check
      properly.

## What to submit

`starter/conftest.py` and `starter/test_quest_board.py`.

## Hints

**Level 1:** `stocked_board`'s fixture function signature looks like
`def stocked_board(empty_board):` — the parameter name must exactly
match the other fixture's name, the same rule that applies to a test
function asking for a fixture.

**Level 2:** For the parametrize case, the tuple list only needs the
priority string itself if the expected count is always the same (1, on a
board with exactly one quest of each priority) — you don't need a second
column in that case; `@pytest.mark.parametrize("priority", ["low",
"medium", "high"])` is enough.

**Level 3 (closer to the answer):** If `test_marking_one_quest_done_does_not_affect_the_others`
is tricky to write, remember `stocked_board.quests` is just a plain
Python list — use a loop, or a generator expression with `next(...)`, to
find the specific `Quest` object you want to check by its `title`.
