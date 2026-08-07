# Exercise 02 — Write a Cache-Friendly Dockerfile From Scratch (Guided)

**Concepts this exercise uses (all taught in
[`lessons/02-dockerfiles-layers-and-caching.md`](../../lessons/02-dockerfiles-layers-and-caching.md)):**
`FROM`, `WORKDIR`, `COPY`, `RUN`, `CMD`, image tags, `docker build -t`,
layer caching and instruction order, `.dockerignore`, `docker history`.

**Where to work:** `exercises/02-writing-a-dockerfile/starter/` — a
small, real Python app (`app.py`, `requirements.txt`) with **no
Dockerfile at all**. Your job is to write one.

## Setup

Confirm the app itself runs, outside Docker, first (so you know what
correct output looks like before containerizing anything):
```bash
cd exercises/02-writing-a-dockerfile/starter
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python app.py
```
**Expected:**
```
Quest of the Day: Slay the Dragon!
Reward: 100 gold, 1 legendary sword
```
Deactivate and remove this local venv when done confirming this (`rm -rf
.venv` — it isn't part of what you're submitting; it exists purely so
you can compare "runs correctly on my machine" against "runs correctly
in the container" in a moment).

## Your task

In this same `starter/` folder, write:

1. **A `Dockerfile`** that:
   - Uses `python:3.14-slim` as its base image.
   - Sets a `WORKDIR`.
   - Installs `requirements.txt`'s dependency **before** copying
     `app.py` in — ordered specifically so that editing `app.py` alone
     never forces `pip install` to re-run on a rebuild.
   - Runs `app.py` as its default command, using the exec form (a list
     of strings, not a bare shell string) — see Lesson 02's own example
     for the exact syntax.
2. **A `.dockerignore`** excluding at least `__pycache__/`, `*.pyc`, and
   any local venv folder you created while testing in Setup.

## Verify it yourself

```bash
docker build -t quest-of-the-day .
docker run --rm quest-of-the-day
```
**Expected:** the exact same two lines of output as the local run above.

Now prove your instruction ordering actually caches correctly. First,
touch only `app.py` (add a blank line, or change the reward's wording)
and rebuild:
```bash
docker build -t quest-of-the-day .
```
**Expected:** the build output should show your `RUN pip install ...`
step as `CACHED`, and only the `COPY` step touching `app.py` (plus the
final export step) actually re-running. If `pip install` re-runs every
single time regardless of what you changed, your instruction order is
wrong — revisit Lesson 02's own "why instruction order matters" section.

Confirm your image's actual layer history:
```bash
docker history quest-of-the-day
```
**Expected:** one row roughly corresponding to each instruction in your
Dockerfile, in order, each with a real size next to it (`0B` is fine for
instructions like `WORKDIR`/`CMD` that don't add files).

## Acceptance criteria

- [ ] `docker build -t quest-of-the-day .` succeeds with no errors.
- [ ] `docker run --rm quest-of-the-day` prints the exact same output as
      running `app.py` locally.
- [ ] Changing only `app.py` and rebuilding shows the `pip install` step
      as `CACHED`, not re-run.
- [ ] A `.dockerignore` file exists and excludes at least
      `__pycache__/`, `*.pyc`, and your local venv folder's name.
- [ ] You can explain, precisely, which line(s) of your Dockerfile would
      need to change if `requirements.txt` itself gained a new
      dependency, and confirm (by actually adding one, e.g. `colorama`,
      and rebuilding) that doing so correctly triggers a **fresh**
      `pip install`, not a cached one.

## Hints

<details>
<summary>Hint 1</summary>

Lesson 02's own worked example, in its "Why instruction order matters: a
real caching win" section, is structurally identical to what this
exercise wants — two `COPY` instructions, `requirements.txt` first, with
`RUN pip install` between them, `app.py`'s own `COPY` last.

</details>

<details>
<summary>Hint 2</summary>

If `docker build` can't find `app.py` or `requirements.txt` at all,
double check you're running `docker build` **from inside**
`starter/` (so `.` correctly refers to it as the build context) — not
from this module's own root folder.

</details>

<details>
<summary>Hint 3</summary>

The exec form of `CMD` looks like `CMD ["python", "app.py"]` — a JSON-
style list of strings, not `CMD python app.py` (the shell form, which
Lesson 02 explains loses direct signal forwarding).

</details>

A reference solution is in `solution/` — do not open it until you've
gotten your own version working, or have genuinely tried and want to
compare your approach afterward.
