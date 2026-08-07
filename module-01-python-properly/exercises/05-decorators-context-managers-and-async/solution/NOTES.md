# Notes on grading this yourself before asking for review

Run `python toolkit.py` and compare against `INSTRUCTIONS.md`'s acceptance
criteria. Expected output shape (your exact timing will vary slightly):

```
Calling flaky_operation(args=(), kwargs={})
Attempt 1 failed: ValueError('Simulated failure #1'), retrying...
Attempt 2 failed: ValueError('Simulated failure #2'), retrying...
flaky_operation returned 'Success!'
Success!
---
Starting fetching quest data...
Starting fetch for q1
Starting fetch for q2
Starting fetch for q3
Finished fetch for q1
Finished fetch for q2
Finished fetch for q3
Finished fetching quest data in 0.50xxs
['data-for-q1', 'data-for-q2', 'data-for-q3']
```

- **The concurrency proof is the number, not the words.** If
  `fetch_quest_data`'s total elapsed time printed by `timed_operation` is
  close to **1.5 seconds** instead of **~0.5 seconds** for 3 IDs each
  "taking" 0.5s, your `fetch_one` calls are running sequentially (e.g. you
  wrote `for qid in quest_ids: await fetch_one(qid)` instead of collecting
  them and passing them all into one `asyncio.gather(...)` call) — this is
  the single most important thing to check, and the easiest thing to get
  subtly wrong while still producing "correct-looking" output.
- **Order preservation** — the returned list must read `['data-for-q1',
  'data-for-q2', 'data-for-q3']` in that exact order, even though the
  interleaved start/finish print statements don't prove anything about
  order on their own (in this specific solution they happen to also print
  in order, since all three delays are identical — try giving `q2` a
  longer simulated delay than the others and confirm the *returned list*
  still comes back in input order even though `q2`'s "Finished" message
  would now print last).
- **`retry`'s final failure case** — write a quick throwaway test:
  decorate a function that *always* raises with `@retry(times=3)` and
  confirm the exception still ultimately propagates (your program should
  still crash with that exception after exactly 3 "Attempt ... failed"
  messages) rather than the function silently returning `None`. A common
  bug: forgetting the final `raise last_error` after the loop, which would
  make the decorated function silently return `None` on total failure
  instead of surfacing the real problem.
- **`timed_operation` exception safety** — test it deliberately: put
  `raise ValueError("test")` inside a `with timed_operation("test"):`
  block. The `"Finished test in ...s"` message should still print (proving
  your `finally` is correctly placed), and the `ValueError` should still
  propagate out of the `with` block afterward (proving you didn't
  accidentally swallow it — re-check you didn't add a bare `except:` in
  there anywhere).
- **Stacking order comment** — the specific order chosen in this reference
  solution (`@log_command` outermost, `@retry` innermost) is not the only
  defensible choice — what matters is that your comment demonstrates real
  reasoning about *why* your chosen order produces the specific logging
  behavior it does, referencing how `@a @b def f()` means `f = a(b(f))`
  (Lesson 10).
