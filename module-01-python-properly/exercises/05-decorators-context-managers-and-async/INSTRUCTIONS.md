# Exercise 05 — Decorators, Context Managers, and Async (Independent)

**Difficulty:** Independent — this describes the *goal state*, not every
step. You decide the exact implementation, following the patterns from
Lessons 10 and 11.

**Concepts this exercise uses:**
- From [`lessons/10-decorators-and-context-managers.md`](../../lessons/10-decorators-and-context-managers.md): writing a decorator with `functools.wraps`, a decorator that takes its own arguments (the `repeat(times)` three-layer pattern), and a context manager via `@contextmanager`.
- From [`lessons/11-async-await-fundamentals.md`](../../lessons/11-async-await-fundamentals.md): `async def`, `await`, `asyncio.run()`, and `asyncio.gather()` for real concurrency.
- From [`lessons/06-error-handling.md`](../../lessons/06-error-handling.md): `try`/`except` inside the retry decorator below.

## What to build

Create a single file `starter/toolkit.py` (there's no pre-written skeleton
this time — build it from scratch) containing all five pieces below, then a
demo at the bottom under `if __name__ == "__main__":` that exercises all of
them together.

1. **`@log_command`** — a decorator (no arguments of its own) that, when
   applied to any function, prints the function's name and the arguments
   it was called with *before* calling it, then prints the function's
   name and its return value *after* calling it. Must use
   `functools.wraps` and must correctly support any function regardless of
   its specific parameters (via `*args, **kwargs`), per Lesson 10.
2. **`@retry(times)`** — a decorator *factory* (it takes an argument,
   `times`, and returns the real decorator — Lesson 10's three-layer
   `repeat(times)` pattern) that, when applied to a function, calls it and,
   if it raises **any** exception, retries up to `times` total attempts
   before finally letting the last exception propagate for real. Print a
   message each time a retry happens (e.g. `f"Attempt {n} failed: {e!r},
   retrying..."`).
3. **`timed_operation(label)`** — a context manager, written using
   `@contextmanager` from `contextlib` (Lesson 10's generator-based
   approach), that prints `f"Starting {label}..."` on entry and
   `f"Finished {label} in {elapsed:.4f}s"` on exit — using `try`/`finally`
   inside it so the elapsed-time message still prints even if the code
   inside the `with` block raises.
4. **`async def fetch_quest_data(quest_ids)`** — an async function that,
   for a list of quest IDs, "fetches" each one concurrently (use
   `asyncio.sleep(0.5)` — or any short delay — to simulate a slow network
   call per ID, and print a start/finish message per ID) using
   `asyncio.gather`, and returns a list of results (e.g. strings like
   `f"data-for-{quest_id}"`) **in the same order as the input `quest_ids`**,
   regardless of the (arbitrary/interleaved) order the start/finish
   messages actually print in.
5. **`async def main()`** — ties everything together:
   - Define a small flaky function (e.g. one that raises an exception the
     first one or two times it's called, using a counter, then succeeds)
     decorated with both `@log_command` and `@retry(times=3)` (yes, stack
     two decorators on the same function — order matters, think about
     which should run "closer" to the original function and why before
     picking an order), and call it.
   - Use `timed_operation("fetching quest data")` as a `with` block around
     an `await fetch_quest_data([...])` call for at least 3 quest IDs, and
     print the results.
   - Run `main()` via `asyncio.run(main())` at the bottom of the file.

## Acceptance criteria

- [ ] `@log_command` works correctly on functions with different numbers/kinds of parameters (test it on at least two different functions) and preserves `__name__` (verify with `.__name__` after decorating, per Lesson 10's `functools.wraps` check).
- [ ] `@retry(times=3)` actually retries — demonstrate with a function that fails exactly twice then succeeds, and confirm it succeeds overall without you needing more than 3 attempts. Also demonstrate the failure case: a function that *always* raises, decorated with `@retry(times=3)`, should still raise (after 3 attempts) rather than silently swallowing the error.
- [ ] `timed_operation` prints both its start and finish messages around a real block of code, and the finish message still prints even if you deliberately test it around code that raises (the exception should still propagate after the message prints — don't accidentally suppress it).
- [ ] `fetch_quest_data` genuinely runs concurrently — with 3+ IDs each "taking" the same simulated delay, total time should be close to *one* delay's worth, not the sum of all of them (mirror Lesson 11's own `asyncio.gather` timing proof).
- [ ] `fetch_quest_data`'s returned list is in the same order as the input `quest_ids`, even though the underlying prints may interleave.
- [ ] The stacked-decorator function (`@log_command` + `@retry`) runs correctly, and you can explain, in a comment, which decorator you put closer to the function definition and why (hint: think about whether you want retries to happen *inside* the logging, or logging to happen *inside* each retry attempt).

## What to submit

Point your AI session at your completed `starter/toolkit.py` and say
*"Review my solution for Exercise 05."*

## Hints

- Stuck on the retry decorator's three-layer shape? Re-read Lesson 10's
  `repeat(times)` example line by line — `retry(times)` is structurally
  almost identical, just with a `try`/`except` loop instead of a plain
  `for` loop.
- Stuck on where exactly to put the `try`/`except` inside `retry`? It goes
  *inside* `wrapper`, wrapping the call to the original function, inside a
  loop that runs up to `times` times — catch the exception, print a
  message, and only `raise` (re-raising the same exception) once you've
  exhausted every attempt.
- Stuck on decorator stacking order? `@a` then `@b` directly above `def
  f():` means `f = a(b(f))` — `b` runs "closer" to the real function,
  `a` wraps around the *result* of `b` wrapping `f`. Think about which
  order makes more sense for logging vs. retrying, and justify your choice
  in a comment — there's a genuinely defensible answer, and Lesson 10 gives
  you everything you need to reason it out, even though it doesn't state
  the answer directly for this specific combination.
- Stuck on `fetch_quest_data` preserving input order despite concurrent
  completion? `asyncio.gather(*coroutines)` already guarantees its
  returned list matches the order of the coroutines you passed in,
  regardless of which one actually finishes first internally — you don't
  need to sort anything yourself; re-read Lesson 11's own `asyncio.gather`
  example if the guarantee isn't clear.
- If you've re-read the relevant sections and are still stuck, ask your AI
  session for a Level 1 hint per [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md).
