# Exercise 03 — Mocking

**Difficulty:** Guided, more independent than Exercises 01–02 — you'll
need to decide *what* to mock and *why* for each test, not just follow a
template.

## Concepts this exercise uses (all taught in the lessons named)

- What a mock is, and `unittest.mock.patch` for replacing the real
  current date — `lessons/03-parametrize-and-mocking.md`'s "your first
  mock" and "the exact mock this module's real tests use" sections.
- `pytest`'s `monkeypatch` fixture, for replacing one specific function —
  same lesson, "`pytest`'s own `monkeypatch` fixture" section.
- Asserting a mock *was* (or was *not*) called, with what arguments
  (`mock.assert_called_once_with(...)`, `mock.assert_not_called()`) —
  same lesson's "the most important rule" section explains *why* this
  matters, though the exact assertion methods are new here — see the
  hints below if you get stuck on the exact method names.
- "Mock the boundary, not the thing you're testing" — same lesson.

## What you're given

`starter/quest_reminders.py` — four functions, no tests:
- `days_since_created(created_on: date) -> int` — depends on the real
  current date via `date.today()`.
- `is_overdue(created_on: date, deadline_days: int) -> bool`.
- `send_overdue_reminder(quest_title: str, owner_email: str) -> bool` —
  a stand-in for a real, slow, external notification call.
- `notify_if_overdue(quest_title, owner_email, created_on, deadline_days) -> bool`
  — calls `send_overdue_reminder` if, and only if, `is_overdue` says the
  quest is overdue.

## What to do

Write `starter/test_quest_reminders.py` covering:

1. **`days_since_created`** — at least two cases, each with the real
   current date mocked to a specific, known value (never relying on
   whatever today's real date happens to be when the test runs).
2. **`is_overdue`** — at least two cases: one where the number of days
   passed is exactly equal to `deadline_days` (read the function's own
   docstring carefully — is that overdue, or not?), and one where it's
   clearly past the deadline.
3. **`notify_if_overdue`** — two cases:
   - When the quest **is** overdue: confirm `send_overdue_reminder` was
     actually called, with the correct `quest_title` and `owner_email`
     arguments, and that `notify_if_overdue` itself returns `True`.
   - When the quest is **not** overdue: confirm `send_overdue_reminder`
     was **never called at all**, and that `notify_if_overdue` returns
     `False`.

For the `notify_if_overdue` tests, mock `is_overdue` itself (not the real
date) — you already fully tested `is_overdue`'s own date logic in step
2; re-testing it here would be redundant, and this lesson's "mock the
boundary" rule means these two tests should focus purely on
`notify_if_overdue`'s own decision logic.

## Acceptance criteria

- [ ] `python -m pytest -v` from `starter/` shows every test passing.
- [ ] No test actually depends on the real current date — every test
      still passes no matter what day you run it.
- [ ] No test's output actually prints the real `"[would send email]..."`
      line from `send_overdue_reminder` — if you see that line in your
      test output, `send_overdue_reminder` wasn't mocked in that test,
      and the real function ran instead.
- [ ] At least one test asserts a mock *was* called with specific
      arguments, and at least one asserts a mock was **not** called at
      all.

## What to submit

`starter/test_quest_reminders.py`.

## Hints

**Level 1:** Reuse this module's own `lessons/03-parametrize-and-mocking.md`
example almost directly for the date-mocking tests — the pattern
(`with patch("quest_reminders.date") as mock_date: mock_date.today.return_value
= date(...)`) is identical; only the module name and the specific dates
change.

**Level 2:** For asserting a mock was called with specific arguments,
the method is `mock_thing.assert_called_once_with(arg1, arg2)` — it
raises an `AssertionError` itself (failing your test) if the mock either
was never called, was called more than once, or was called with
different arguments than you specified.

**Level 3 (closer to the answer):** For asserting a mock was *not*
called at all, the method is `mock_thing.assert_not_called()` — no
arguments needed, since you're asserting it was never invoked in the
first place.
