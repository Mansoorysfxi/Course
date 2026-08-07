# Exercise 03 — Error Handling, File I/O, and JSON (Guided)

**Difficulty:** Guided — the shapes of the functions and exceptions are
given; you decide the exact messages and some control-flow details.

**Concepts this exercise uses:**
- From [`lessons/06-error-handling.md`](../../lessons/06-error-handling.md): `try`/`except`/`finally`, raising exceptions with `raise`, and defining custom exception classes that inherit from `Exception` (and from each other).
- From [`lessons/08-file-io-and-json.md`](../../lessons/08-file-io-and-json.md): `with open(...)`, `json.dump`/`json.load`, and handling `FileNotFoundError`/`json.JSONDecodeError`.

## What to build

Open [`starter/save_system.py`](starter/save_system.py) and fill in every
TODO. This exercise builds a small, realistic save/load system — a direct
rehearsal for your capstone's persistence layer.

1. **Define three exception classes:**
   - `QuestLogError(Exception)` — the base class for everything in this file.
   - `QuestNotFoundError(QuestLogError)` — takes a `quest_name` in its
     `__init__`, stores it as `self.quest_name`, and calls
     `super().__init__(...)` with a message like
     `f"No quest named '{quest_name}' exists."` (Lesson 06's exact pattern).
   - `CorruptSaveFileError(QuestLogError)` — takes a `path` and an
     `original_error` in its `__init__`, stores both, and builds a message
     like `f"Save file at '{path}' is corrupted: {original_error}"`.
2. **`load_quest_log(path)`** — open and parse the JSON file at `path`.
   - If the file doesn't exist (`FileNotFoundError`), return an empty dict
     `{}` — a missing save file on first run is normal, not an error
     (Lesson 08's exact reasoning).
   - If the file exists but isn't valid JSON (`json.JSONDecodeError`),
     **raise** your own `CorruptSaveFileError(path, e)` instead of letting
     the original `json.JSONDecodeError` propagate — this is the point of
     defining a custom exception: callers of `load_quest_log` should only
     ever need to know about *your* exception types, not `json`'s.
3. **`save_quest_log(path, data)`** — write `data` (a dict) to `path` as
   JSON, using `with open(...) as f:` and `json.dump(data, f, indent=2)`.
4. **`get_quest(quests, quest_name)`** — given the loaded dict (assume its
   shape is `{quest_name: {"reward_gold": ..., "is_complete": ...}, ...}`),
   return the inner dict for `quest_name`. If it doesn't exist, **raise**
   `QuestNotFoundError(quest_name)` yourself rather than letting a raw
   `KeyError` propagate.
5. **`mark_complete(quests, quest_name)`** — use `get_quest` to fetch the
   quest (letting `QuestNotFoundError` propagate up if it's missing — don't
   catch it here, catch it at the call site instead, demonstrated in the
   `if __name__ == "__main__":` block), then set its `"is_complete"` key to
   `True`.
6. In the `if __name__ == "__main__":` block at the bottom (already
   partially written), wrap a call to `mark_complete` for a
   deliberately-missing quest name in a `try`/`except QuestNotFoundError`
   and print a friendly message instead of letting it crash — this is the
   "catch it at the boundary, not deep inside" pattern Lesson 06 discusses.

## Acceptance criteria

- [ ] `QuestNotFoundError` and `CorruptSaveFileError` both ultimately inherit from `Exception` via `QuestLogError`, and `except QuestLogError:` would catch either one.
- [ ] `load_quest_log("does_not_exist.json")` returns `{}` with no exception raised.
- [ ] Given a file containing deliberately broken JSON (e.g. `{not valid`), `load_quest_log` raises `CorruptSaveFileError`, not a raw `json.JSONDecodeError` — verify with `type(...)` or by catching each type separately in a quick test.
- [ ] `save_quest_log` followed immediately by `load_quest_log` on the same path returns data equal to what was saved (a genuine round trip).
- [ ] `get_quest` raises `QuestNotFoundError` (not `KeyError`) for a missing quest name, and returns the correct inner dict for an existing one.
- [ ] `mark_complete` correctly sets `is_complete` to `True` for an existing quest, and lets `QuestNotFoundError` propagate (uncaught, inside `mark_complete` itself) for a missing one.
- [ ] The demo block's deliberate missing-quest call is caught with `except QuestNotFoundError:` and prints a friendly message rather than crashing.

## What to submit

Point your AI session at your completed `starter/save_system.py` and say
*"Review my solution for Exercise 03."*

## Hints

- Stuck on the exception hierarchy? Re-read Lesson 06's
  "Custom exceptions" section — `QuestNotFoundError` and
  `CorruptSaveFileError` should each inherit from `QuestLogError`, not
  directly from `Exception`, exactly like that lesson's
  `QuestNotFoundError`/`QuestAlreadyCompleteError` both inheriting from
  `QuestError`.
- Stuck on converting a `json.JSONDecodeError` into your own
  `CorruptSaveFileError`? The pattern is: catch the specific built-in
  exception, then `raise YourOwnException(...)` from inside that `except`
  block — you're not fixing the problem, you're translating it into a
  vocabulary callers of your function should actually have to know about.
- Stuck on why `mark_complete` shouldn't catch `QuestNotFoundError` itself?
  Re-read Lesson 06's point about keeping `try` blocks small and specific —
  the *caller* of `mark_complete` is in a better position to decide what
  "quest not found" should mean for the user (retry? show a message? exit?)
  than `mark_complete` itself is.
- If you've re-read the relevant sections and are still stuck, ask your AI
  session for a Level 1 hint per [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md).
