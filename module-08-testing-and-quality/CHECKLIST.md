# Module 08 — Checklist

Complete this after finishing all five exercises and the capstone
project, and after your module-end review ("Check my module"). This
module is the course's **Review Project milestone** — take the
spaced-repetition section below especially seriously; it's the whole
point of this checkpoint.

## Self-assessment

- [ ] I can explain, precisely, what makes a test "automated" (the three properties from Lesson 01), and why a `curl` command I typed and read myself doesn't count.
- [ ] I can draw the testing pyramid from memory and correctly classify any given test (including my own) as unit, integration, or end-to-end, with real reasoning.
- [ ] I can explain exactly how `pytest` resolves a fixture from a test function's parameter name, with no hand-waving about "magic."
- [ ] I can write a fixture that uses `yield` for cleanup, and explain precisely what runs before vs. after `yield`, and when.
- [ ] I can explain why `db_session` (this module's real fixture) uses function scope instead of a wider one, and what would go wrong if it didn't.
- [ ] I can use `@pytest.mark.parametrize` to run one test function against several inputs, and explain how `pytest` reports each case if only one of several fails.
- [ ] I can define "mock" from scratch, in my own words (not just recite this module's game-dev analogy), and I can name the broader term ("test double") it's one example of.
- [ ] I can explain the single most common `unittest.mock.patch` mistake (patching the wrong path) and why it happens.
- [ ] I can state, and actually apply, the rule "mock the boundary, not the thing you're testing."
- [ ] I can explain what ASGI is well enough to explain why `httpx.AsyncClient` + `ASGITransport` needs no real network connection to test a FastAPI app.
- [ ] I can explain what `app.dependency_overrides` does, mechanically, and why it lets this module's tests run without touching the real Postgres database.
- [ ] I can state, and justify with real trade-offs (not just "it's what the lesson said"), why this module's backend tests use in-memory SQLite instead of a dedicated Postgres test database — and I can name one future QuestLog feature that would force revisiting that choice.
- [ ] I can state React Testing Library's central philosophy ("test behavior, not implementation") and identify, in a real test, a query that honors it versus one that doesn't.
- [ ] I can explain the real difference between `getByText`, `queryByText`, and `findByText`, and when to use each.
- [ ] I have used `pytest -k`, `--lf`, and either `breakpoint()`/`pytest --pdb` or VS Code's graphical debugger for real, at least once, on a genuinely failing test — not just read about them.
- [ ] I can explain the difference between a linter and a formatter, and correctly say which of `ruff check`/`ruff format` is which.
- [ ] I can explain why this module's `pyproject.toml` uses an explicit `select = [...]` list instead of ruff's `ALL`.
- [ ] I can read `.pre-commit-config.yaml` and explain what every hook in it does, including why the frontend's own two hooks are `local`/`system` instead of a managed mirror repository.
- [ ] I have actually run this module's real backend test suite (31 tests) and real frontend test suite (17 tests) myself, on my own machine, and both passed.
- [ ] I have actually broken one real behavior on purpose (capstone step 7) and watched a specific, real test fail with a specific, readable message — then reverted the change.
- [ ] All five exercises were reviewed and scored 7/10 or higher (or revised until they were).

## Spaced-repetition review questions from earlier modules

This module is a review milestone — these five questions deliberately
span the *whole* course so far, not just recent modules.

1. **(Module 00 — Git & reading errors)** This module's Lesson 04 (debugging techniques) is a direct extension of Module 00's "reading docs and errors" lesson. What is the first thing you should identify in any Python traceback before trying to fix anything, and how does that same instinct apply to reading a failing `pytest` test's output?
2. **(Module 02 — Web Fundamentals)** This module's Lesson 05 tests QuestLog's API by sending real HTTP requests (`GET`, `POST`, `PATCH`, `DELETE`) through `httpx`. What does "HTTP is stateless" mean, and how does that same fact explain why every one of this module's protected-route tests has to send its own `Authorization` header on every single request, with nothing "remembered" between them?
3. **(Module 04 — React)** This module's `QuestListPage.test.tsx` mocks `useQuests()` instead of rendering a real `<QuestsProvider>`. What is a React "hook," in your own words, and why does mocking the *hook itself* (rather than the component using it) let this test check `QuestListPage`'s own rendering logic in isolation?
4. **(Module 06 — Databases)** Lesson 06 of this module explains why `db_session` uses `Base.metadata.create_all` instead of running real Alembic migrations. What is a migration, in your own words, and why does a brand-new, empty, in-memory test database have no real need for one — what would be different if that same database already had real rows in it?
5. **(Module 07 — Auth & Security)** This module's `test_one_user_cannot_get_another_users_quest_by_id` asserts a `404`, not a `403`. What is an IDOR (Insecure Direct Object Reference), and why does returning the *same* response for "doesn't exist" and "exists, but isn't yours" close off that specific vulnerability?

## Before you move on to Module 09

- [ ] You've said "check my module" and received a full module-end review — for this milestone module specifically, expect (and ask for, if it doesn't happen automatically) a comparison against your work in *every* earlier module, not just Module 07, per Rule 3's module-end review protocol.
- [ ] [PROGRESS.md](../PROGRESS.md) has been updated by the AI with your Module 08 report.
- [ ] Any remedial exercises the review generated (if any) are complete.
- [ ] You've read the Module 09 README to see what's coming next — QuestLog, exactly as it stands now (tested, linted, and ready), deployed manually to a real server for the first time.
