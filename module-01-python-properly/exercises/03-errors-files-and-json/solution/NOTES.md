# Notes on grading this yourself before asking for review

Run `python save_system.py` and compare against `INSTRUCTIONS.md`'s
acceptance criteria. Clean up `demo_quests.json` and `broken_demo.json`
afterward (or add them to a local `.gitignore` if you're tracking this
folder with Git) — they're generated, throwaway output.

- **Exception hierarchy** — confirm with `issubclass(QuestNotFoundError,
  QuestLogError)` and `issubclass(CorruptSaveFileError, QuestLogError)`,
  both `True`. If you made either inherit directly from `Exception`
  instead of `QuestLogError`, `except QuestLogError:` at a call site
  wouldn't catch it — a real behavioral difference, not just a style nit.
- **`load_quest_log`'s two except branches** — the corrupt-file branch's
  real point is *translation*: your function should never let a raw
  `json.JSONDecodeError` escape to its caller. If your `except
  json.JSONDecodeError:` block just re-raised the same exception, or
  printed something and returned `None`, that's a gap — it should
  specifically `raise CorruptSaveFileError(path, e)`.
- **`get_quest` raising `QuestNotFoundError` instead of a raw `KeyError`**
  — this is the single most important behavior in this exercise. Test it
  directly: `get_quest({}, "nope")` should raise `QuestNotFoundError`, and
  `type` of the raised exception should not be `KeyError`.
- **`mark_complete` NOT catching `QuestNotFoundError` itself** — read your
  own implementation. If `mark_complete` has a `try`/`except
  QuestNotFoundError` inside it (rather than in the `if __name__ ==
  "__main__":` block, where the instructions asked for it), that's a
  design mismatch against the exercise's explicit instruction, even if the
  end-to-end behavior looks similar — the point being practiced is
  deciding *where* in a call chain an exception should actually be
  handled.
