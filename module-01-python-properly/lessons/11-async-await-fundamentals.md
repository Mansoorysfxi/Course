# Lesson 11 — Async/Await Fundamentals: The Event Loop, Explained Like a Game Loop

## What you'll learn

- The specific problem async/await solves, and why it exists as a *separate* concept from multithreading.
- What the **event loop** actually is, using an analogy to Unreal's own game loop/tick system.
- `async def`, `await`, and `asyncio.run()` — the minimum syntax to run real async code.
- Why `await` doesn't mean "runs in parallel," and what it actually means instead.
- Running things concurrently with `asyncio.gather()`, and the difference between I/O-bound and CPU-bound work.
- The most common beginner mistakes: forgetting `await`, and blocking the event loop by accident.

## Why this matters

Verified for this lesson (August 2026): modern async Python guidance still centers on exactly the model this lesson teaches — a single-threaded event loop, `asyncio.run()` as the standard entry point, and a hard rule against blocking that loop with slow synchronous code. This isn't a niche feature: FastAPI (Module 05 onward) is built around `async def` route handlers, and understanding *why* `async`/`await` exist — not just the syntax — is the difference between writing FastAPI code that's actually fast and writing FastAPI code that accidentally serializes everything anyway, silently defeating the entire point.

## Prerequisites

Lesson 04 (generators — async functions reuse that exact "pause, remember everything, resume later" mechanism, just triggered by `await` instead of `yield`, and driven by something other than manual `next()` calls).

## The concept, explained simply

Imagine your Unreal game's tick loop, running once per frame: it walks through every actor that needs updating and gives each one a small slice of time to do its thing, then moves to the next, then loops back to the start for the next frame. Nothing runs in genuine parallel inside that single loop — it's one thread, doing a little bit of many things, in rapid rotation, and the *illusion* of everything happening "at once" comes from how fast it cycles through them, not from actual simultaneous execution.

Python's **event loop** (the thing `asyncio` — Python's async standard library — actually runs) works on precisely the same principle, applied to a specific kind of task: **waiting on something slow that isn't the CPU itself** — a network request's response, a file finishing being read from a slow disk, a database query completing. Instead of your program sitting there frozen, doing absolutely nothing useful while it waits (which is what a normal, "synchronous" function call does), an `async` function can voluntarily say "I'm about to wait on something — go let someone else run in the meantime," hand control back to the event loop, and get resumed later, right where it left off, the moment what it was waiting for is actually ready. Exactly like a tick loop moving on to the next actor rather than freezing the whole game waiting on one actor's animation to finish playing.

**The single most important thing to understand, stated directly: `async`/`await` does not give you multiple threads, and does not make your CPU do more work simultaneously.** It's about *not wasting time waiting* — specifically for I/O (input/output: network, disk, database) — not about computing things faster. This distinction is the source of nearly every async misunderstanding, so it's worth re-reading before continuing.

## The details

### The problem, demonstrated synchronously first

```python
import time

def fetch_quest(quest_id):
    print(f"Starting fetch for quest {quest_id}...")
    time.sleep(1)   # pretend this is a slow network call, 1 second
    print(f"Finished fetch for quest {quest_id}")
    return f"Quest-{quest_id}"

start = time.perf_counter()
result1 = fetch_quest(1)
result2 = fetch_quest(2)
result3 = fetch_quest(3)
print(f"Total time: {time.perf_counter() - start:.2f}s")
```
**Run:** `python lesson11.py` → **Expected output:**
```
Starting fetch for quest 1...
Finished fetch for quest 1
Starting fetch for quest 2...
Finished fetch for quest 2
Starting fetch for quest 3...
Finished fetch for quest 3
Total time: 3.00s
```

Three "slow calls," run one after another, take roughly 3 seconds total — each one fully blocks the entire program until it personally finishes, exactly like a tick loop that freezes on one actor until its animation completes before moving to the next actor at all. `time.sleep()` here stands in for any real slow I/O operation (an actual network request behaves identically from your program's point of view: it sits there, doing nothing, until a response arrives).

### The same idea, written with async/await

```python
import asyncio
import time

async def fetch_quest(quest_id):
    print(f"Starting fetch for quest {quest_id}...")
    await asyncio.sleep(1)   # the async-aware version of a slow wait
    print(f"Finished fetch for quest {quest_id}")
    return f"Quest-{quest_id}"

async def main():
    start = time.perf_counter()
    result1 = await fetch_quest(1)
    result2 = await fetch_quest(2)
    result3 = await fetch_quest(3)
    print(f"Total time: {time.perf_counter() - start:.2f}s")

asyncio.run(main())
```
**Expected output:** identical timing to the synchronous version — still about 3 seconds, one after another. **This is deliberate and important:** simply adding `async`/`await` in front of things, while still `await`-ing each call one at a time in sequence, changes *nothing* about the timing — you haven't told the event loop it's allowed to run more than one of these at once, you've just described each individual wait as "interruptible" without actually taking advantage of that. The real payoff needs one more piece.

**Line by line of what's new here:**
- `async def fetch_quest(...)` — defines a **coroutine function**. Calling `fetch_quest(1)` does **not** run the function's body at all yet (exactly like calling a generator function from Lesson 04 didn't run its body) — it returns a **coroutine object**, a paused, not-yet-started task description.
- `await asyncio.sleep(1)` — this is the actual "pause and hand control back to the event loop" moment. `await` can only be used inside an `async def` function, and only in front of something itself awaitable (a coroutine, or certain other special objects). It means: "start this operation, and while genuinely waiting for it, let the event loop go run something else if there's anything else ready to run — then resume me, right here, the instant this is done."
- `asyncio.run(main())` — the standard entry point (verified current for this lesson, August 2026) that creates the event loop, runs your top-level coroutine (`main()`) to completion inside it, then cleanly shuts the loop down. You call this **once**, at the very top level of your program — never nested inside another `async` function.

### Actually getting the speedup — running things concurrently with `asyncio.gather`

```python
async def main():
    start = time.perf_counter()
    results = await asyncio.gather(
        fetch_quest(1),
        fetch_quest(2),
        fetch_quest(3),
    )
    print(results)
    print(f"Total time: {time.perf_counter() - start:.2f}s")

asyncio.run(main())
```
**Expected output:**
```
Starting fetch for quest 1...
Starting fetch for quest 2...
Starting fetch for quest 3...
Finished fetch for quest 1
Finished fetch for quest 2
Finished fetch for quest 3
['Quest-1', 'Quest-2', 'Quest-3']
Total time: 1.00s
```

**This is the actual payoff, and notice exactly what changed:** all three `"Starting fetch..."` lines print immediately, back to back — then, after roughly one second (not three), all three `"Finished fetch..."` lines print. `asyncio.gather(...)` hands all three coroutines to the event loop *at once* and says "run all of these, resuming each whenever it's ready, and give me all the results together when every one of them is done." Since each one's "slow part" (`asyncio.sleep(1)`) is just *waiting*, not actually using the CPU, the event loop can have all three "in flight," waiting simultaneously, and the total time is roughly the *longest single wait* (about 1 second), not the *sum* of all three waits (3 seconds) — exactly the improvement a synchronous, one-at-a-time approach could never achieve on a single thread.

**Connecting back to the game loop analogy directly:** this is precisely a tick loop managing three actors' independent animation timers simultaneously, checking in on each one every frame rather than fully blocking on actor 1's animation before even starting actor 2's. One thread, no true parallelism, but zero wasted idle time — the loop is always doing *something* useful across the whole set of waiting tasks, instead of babysitting one wait at a time.

### Why `await` is not "runs in parallel" — the crucial distinction, stated precisely

There is exactly **one** event loop, running on **one** thread, for a normal `asyncio` program. At any single instant, only one piece of your Python code is actually executing — never two lines "at the same time." What `async`/`await` buys you is that while one coroutine is genuinely *waiting* (not computing, just waiting — for a network response, a disk read, a timer), the event loop is free to let a *different* coroutine run during that idle gap, rather than sitting there doing nothing. This is why the earlier warning matters: **async gives you overlap during waiting, never simultaneous CPU computation.** For work that's genuinely CPU-heavy (crunching numbers, resizing an image, hashing a huge amount of data) rather than I/O-bound (waiting on something external), `async`/`await` provides **zero speedup** — the CPU is already the bottleneck, and there's no "idle waiting gap" for another coroutine to slip into. Genuinely parallel CPU work needs real multiple threads/processes, a separate topic outside this lesson's scope (you'll meet Python's approaches to that, and *when* you'd reach for them instead, later in the course, once real workloads justify it).

### The most common beginner mistake: forgetting `await`

```python
async def fetch_quest(quest_id):
    await asyncio.sleep(1)
    return f"Quest-{quest_id}"

async def main():
    result = fetch_quest(1)   # forgot `await`!
    print(result)

asyncio.run(main())
```
**Expected output:**
```
<coroutine object fetch_quest at 0x000001A2B3C4D5E6>
```
...often accompanied by a separate warning printed by Python itself: `RuntimeWarning: coroutine 'fetch_quest' was never awaited`.

**Why this happens:** calling `fetch_quest(1)` without `await` gives you back the *coroutine object itself* — the paused, not-yet-started description of the work — not the eventual result of running it. This is exactly like Lesson 04's generator functions not running their body until you actually pull a value from them: creating the coroutine object is not the same event as running it. Forgetting `await` is the single most common async bug beginners write, and Python's own `RuntimeWarning` exists specifically to catch it — if you ever see that warning, the fix is almost always "you forgot an `await` somewhere on that exact line."

### The other common mistake: blocking the event loop with synchronous slow code

```python
async def bad_fetch_quest(quest_id):
    print(f"Starting fetch for quest {quest_id}...")
    time.sleep(1)   # WRONG inside an async function — this is NOT awaitable, it blocks everything
    print(f"Finished fetch for quest {quest_id}")
    return f"Quest-{quest_id}"
```

Using the ordinary, synchronous `time.sleep(1)` (no `await`, because `time.sleep` isn't awaitable at all) inside an `async def` function does **not** hand control back to the event loop — it genuinely freezes the *entire* event loop, including every other coroutine that might otherwise have been ready to run during that second, defeating the entire purpose. This is the async equivalent of putting a hard, blocking wait directly inside your game's tick function and wondering why the whole game froze for a second instead of just one actor's animation pausing — verified current guidance (2026) is explicit on this exact point: never call blocking, synchronous code directly inside a coroutine; use the `async`-aware equivalent (`asyncio.sleep` instead of `time.sleep`, an async HTTP library instead of a synchronous one) or, if no async version exists, hand the blocking call off to a separate thread pool via `loop.run_in_executor(...)` — a more advanced technique you don't need for this module, but worth recognizing by name for when you meet it in a real FastAPI codebase.

## Common mistakes & gotchas

- **Forgetting `await` on a coroutine call.** Produces a `RuntimeWarning: coroutine '...' was never awaited` and a coroutine object where you expected a real result — always `await` a coroutine you intend to actually run and get a result from.
- **Believing `async`/`await` makes CPU-bound code faster.** It doesn't, and can't — there's no idle waiting gap in CPU-bound work for another coroutine to use. Async is for I/O-bound waiting specifically.
- **Calling a blocking, synchronous function (`time.sleep`, a synchronous HTTP request, heavy number-crunching) directly inside an `async def` function.** This freezes the entire event loop for everyone, not just that one coroutine — defeating the purpose entirely. Use the async-aware equivalent, or offload it (an advanced technique, not needed yet).
- **Calling `asyncio.run()` more than once, or nesting it inside another `async` function.** `asyncio.run()` is meant to be called exactly once, at your program's top level, to start and later cleanly tear down the event loop — nesting it raises a `RuntimeError`.
- **Awaiting things one at a time in sequence (`await a(); await b(); await c()`) when they don't actually depend on each other, and being surprised there's no speedup.** If the operations are independent, use `asyncio.gather(a(), b(), c())` to actually run them concurrently — sequential `await`s give you correctness but none of async's timing benefit.

## How this connects

You now understand the actual mechanism (event loop, single thread, cooperative pausing at `await` points, built on the same underlying pause/resume capability as Lesson 04's generators) rather than treating `async def`/`await` as syntax to imitate from examples. This module's capstone deliberately does **not** force async/await into a synchronous, local, JSON-file-based CLI tool — there's no genuine I/O-bound waiting there worth overlapping, and forcing it in would just be needless complexity (exactly the kind of "don't force it if it doesn't fit" judgment call this course wants you to develop, not "async because it's advanced"). Where this lesson pays off directly: Module 05's FastAPI route handlers are written `async def` specifically because a real web server juggles many simultaneous requests, each one waiting on I/O (a database query, another API call) — precisely the scenario this lesson's `asyncio.gather` example demonstrated in miniature.

## Quick self-check

1. In the game-loop analogy, what does "the event loop" correspond to, and what does a single `await` point correspond to?
2. Why did adding `async`/`await` to the three sequential `fetch_quest` calls, on its own, not speed anything up — what specifically was missing?
3. Why does `async`/`await` provide no benefit for CPU-bound work (like heavy number crunching), only for I/O-bound work?
4. What actually happens if you call an `async def` function without `await`-ing it, and what warning does Python print to help you catch this?
5. Why does calling ordinary, synchronous `time.sleep()` inside an `async def` function break the entire point of using async in the first place?
