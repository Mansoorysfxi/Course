# Notes on grading this yourself before asking for review

Compare your project against `questpkg-project/` in this same `solution/`
folder (the actual working reference implementation, alongside the example
`MY_SUBMISSION.md`).

- **Type hints on everything** — check every parameter and return type
  across `models.py` and `formatting.py`. A common near-miss: hinting
  parameters but forgetting the `-> None` on `__init__`, or forgetting to
  hint `format_quest`'s return type.
- **`__init__.py` re-export** — confirm `from questpkg import Quest` works
  from `main.py` *without* `main.py` needing to know `Quest` actually lives
  in `questpkg/models.py`. If `main.py` had to write
  `from questpkg.models import Quest` instead, the re-export step is
  missing from `__init__.py`.
- **The relative-import gotcha** — this is the single most instructive
  part of this exercise. If you never actually *tried* running
  `python questpkg/formatting.py` directly (only ever used
  `python -m questpkg.formatting`), you may not have hit — and therefore
  not really understood — the exact error this exercise is built around.
  Worth deliberately triggering it once, even after everything else works,
  just to see it for yourself.
- **`requirements.txt` reproducibility** — the real test: delete `.venv/`
  entirely, create a brand new one, and run `pip install -r
  requirements.txt`. If that fully restores a working environment with no
  manual `pip install` commands needed afterward, the file is doing its
  job correctly.
- **`.venv/` not submitted** — if you find a `.venv/` folder anywhere
  inside what you're about to share for review, that's a real, if harmless,
  mistake — per Lesson 00, it should never be committed/shared; only
  `requirements.txt` should represent it.
