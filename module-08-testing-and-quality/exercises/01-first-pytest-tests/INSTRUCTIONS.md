# Exercise 01 — Your First pytest Tests

**Difficulty:** Easy — the first exercise of this module. If you've read
`lessons/02-pytest-fundamentals-and-fixtures.md` in full, this exercise
should be very close to impossible to fail.

## Concepts this exercise uses (all taught in the lesson named)

- Writing a `test_*.py` file and `test_*` functions so `pytest` discovers
  them at all — `lessons/02-pytest-fundamentals-and-fixtures.md`, Steps 1–2.
- Plain `assert` statements, including how `pytest` reports a failure —
  same lesson, Step 1.
- `pytest.raises(...)` for testing that a function correctly raises an
  exception for bad input — same lesson, Step 3.

No fixtures, no parametrize, no mocking, and no database/HTTP are needed
for this exercise — those come in Exercises 02–04.

## What you're given

`starter/quest_utils.py` — four small, pure functions with **no tests at
all yet**:
- `is_valid_priority(value: str) -> bool`
- `priority_weight(priority: Priority) -> int`
- `format_quest_title(title: str) -> str` — raises `ValueError` on empty
  (or whitespace-only) input.
- `count_completed(done_flags: list[bool]) -> int`

Read `quest_utils.py` first — every function has a docstring explaining
exactly what it should do.

## What to do

Create a new file, `starter/test_quest_utils.py`, and write tests that
check **every one of the four functions above**, covering at least:

1. `is_valid_priority` — at least one input that should return `True`,
   and at least one that should return `False`.
2. `priority_weight` — confirm the actual ordering the docstring promises
   ("lower number = more urgent").
3. `format_quest_title` — a normal case, **and** a case that confirms it
   raises `ValueError` for bad input (empty string).
4. `count_completed` — at least the empty-list case and one case with a
   real mix of `True`/`False`.

## Acceptance criteria

- [ ] Running `python -m pytest -v` from inside `starter/` shows **every
      test passing**, with no errors.
- [ ] Every one of the four functions in `quest_utils.py` has at least
      one test.
- [ ] `format_quest_title`'s exception-raising behavior is tested using
      `pytest.raises`, not by manually calling the function inside a
      `try`/`except` yourself.
- [ ] Test names are descriptive (`test_is_valid_priority_rejects_unknown_value`,
      not `test_1` or `test_case_2`) — a future reader (including you, in
      six months) should understand what broke from the test's name
      alone, without reading its body.

## What to submit

`starter/test_quest_utils.py` (do not modify `quest_utils.py` itself —
this exercise is purely about writing tests against already-correct
code).

## Hints

**Level 1:** Start with `is_valid_priority` — it's the simplest function
here. Write one test, run `pytest -v`, confirm it passes, then add the
next one.

**Level 2:** For `format_quest_title`'s exception case, the shape is:
```python
def test_format_quest_title_raises_on_empty_string():
    with pytest.raises(ValueError):
        format_quest_title("")
```

**Level 3 (closer to the answer):** You need roughly 10–14 individual
test functions to cover all four functions reasonably — if you have
fewer than 6, you're likely missing an edge case (an empty list for
`count_completed`, or the case-sensitivity of `is_valid_priority`).
