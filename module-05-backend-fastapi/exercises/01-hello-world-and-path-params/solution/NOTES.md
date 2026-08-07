# Notes on the reference solution

- All three routes use plain `def`, not `async def` — correct per Lesson 01: none of them
  await anything I/O-bound, so `async def` would buy nothing here.
- `power`'s two path parameters are matched to the function's parameters **by name**
  (`base`, `exponent`), not by position — renaming either one in only one of the two places
  (the decorator string or the function signature) breaks the match, per Lesson 02.
- Both `base` and `exponent` are hinted `int`, so `2 ** 10` is real integer exponentiation,
  returning `1024` as a real JSON number — if either were left as `str`, `base ** exponent`
  would raise a `TypeError` at runtime (strings don't support `**`), and FastAPI's own
  automatic `422` for a non-numeric path segment would never even get a chance to help,
  since the bug would only show up for *some* otherwise-valid-looking requests.

**Verified:** this exact file was run with `uvicorn main:app --reload` and every
acceptance-criteria `curl` command in `INSTRUCTIONS.md` while writing this exercise.
