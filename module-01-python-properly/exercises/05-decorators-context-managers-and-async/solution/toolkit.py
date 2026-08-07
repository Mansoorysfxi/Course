"""
Exercise 05 reference solution — Decorators, Context Managers, and Async.

Don't read this until you've made a genuine attempt at your own
starter/toolkit.py. There is more than one valid way to write several of
these (especially exact print wording) — this is *a* correct solution, not
*the only* correct one.
"""

import asyncio
import functools
import time
from contextlib import contextmanager


def log_command(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}(args={args}, kwargs={kwargs})")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    return wrapper


def retry(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    print(f"Attempt {attempt} failed: {e!r}, retrying...")
            raise last_error
        return wrapper
    return decorator


@contextmanager
def timed_operation(label):
    start = time.perf_counter()
    print(f"Starting {label}...")
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"Finished {label} in {elapsed:.4f}s")


async def fetch_quest_data(quest_ids):
    async def fetch_one(quest_id):
        print(f"Starting fetch for {quest_id}")
        await asyncio.sleep(0.5)
        print(f"Finished fetch for {quest_id}")
        return f"data-for-{quest_id}"

    results = await asyncio.gather(*(fetch_one(qid) for qid in quest_ids))
    return results


# --- Stacked-decorator demo ---
#
# @retry is placed closer to the real function (applied first), and
# @log_command wraps the result. This means each individual retry attempt
# is NOT separately logged by log_command — only the final outcome (the
# eventual return value, or the final exception once retries are
# exhausted) is logged once, at the outer layer. Retry's own "Attempt N
# failed..." prints already show what happened attempt by attempt, so
# logging the outer call once (rather than once per retry) avoids
# duplicate, redundant output. The opposite order (@log_command closer to
# the function, @retry outside) would instead log every single attempt
# individually, which is also a defensible choice — the point is knowing
# WHY you picked one, not that only one answer exists.
_attempt_counter = {"count": 0}


@log_command
@retry(times=3)
def flaky_operation():
    _attempt_counter["count"] += 1
    if _attempt_counter["count"] < 3:
        raise ValueError(f"Simulated failure #{_attempt_counter['count']}")
    return "Success!"


async def main():
    print(flaky_operation())

    print("---")

    with timed_operation("fetching quest data"):
        results = await fetch_quest_data(["q1", "q2", "q3"])
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
