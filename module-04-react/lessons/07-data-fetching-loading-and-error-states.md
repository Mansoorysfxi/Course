# Lesson 07 — Data Fetching, Loading, and Error States

## What you'll learn

- That this lesson teaches **no new asynchronous JavaScript at all** — only what changes about placement and state management when you do async work you already understand *inside* a React component.
- The core React data-fetching pattern: `data`/`loading`/`error` state, set from inside a `useEffect`.
- Why the naive version of that pattern has a real bug — the exact "stale response overwrites newer state" problem Lesson 03 already warned about — and the full, correct version that fixes it, matching the real capstone's actual code almost line for line.
- A **fake fetch** pattern: a function that returns a genuinely delayed, occasionally-failing Promise, used to practice loading/error UI against something that behaves like a real network call, without needing a real backend yet.
- How to render three distinct UI states — loading, error (with a working retry), and success — using early returns, matching the real `QuestListPage.tsx`.
- The **reload token** pattern: an incrementing piece of state whose only job is to be a `useEffect` dependency, used to deliberately re-trigger a fetch on demand (a "Try again" button).

## Why this matters

You already know what a Promise, `fetch`, `async`/`await`, `try`/`catch`, and the loading → success/error DOM-update pattern are — all of that is Module 03, Lesson 07. This lesson is entirely about what changes when you do the exact same thing inside a React component instead of by hand with the DOM: nothing here is new async JavaScript, it's new **placement** and **state management** for async work you already understand. This matters because it's the single most common thing a real frontend does — every page in QuestLog, and every future module's frontend work, needs data from somewhere, and has to correctly show "it's loading," "it worked," or "it failed" as three genuinely distinct states, never leaving a user staring at a blank or frozen screen.

## Prerequisites

Module 03, Lesson 07 (fetch, Promises, and async/await) — required, and not re-taught here; if `.then()`, `await`, or `try`/`catch` feel unfamiliar, that's the lesson to revisit. Lesson 03 (`useEffect` and the dependency array, in depth) — this lesson builds directly on the cleanup-function and `cancelled`-flag pattern that lesson taught; it is not re-explained from scratch here. Lesson 02 (state and re-rendering) — you already know what calling a `useState` setter does. Lesson 06 (Context) — this lesson's final version of the pattern is the data-fetching half of the real `QuestsContext.tsx`, which Lesson 06 already introduced the Context/custom-hook half of.

## The concept, explained simply

Recall Module 03, Lesson 07's DOM-based pattern: set some `statusEl.textContent = "Loading..."`, `await fetch(...)`, then either update the DOM with real data or catch an error and update the DOM with a message instead. Every single piece of that is still exactly correct, conceptually, in React. What changes is *where* "the current state" lives and *how* the UI reacts to it changing: instead of directly writing to `element.textContent`, you write to `useState` variables, and instead of manually calling a DOM-update function at each step, you describe, in JSX, what the UI should look like for each possible state — loading, error, success — and let React's own re-rendering (Lesson 02) handle actually updating the screen the moment that state changes.

The other genuinely new piece is *when* the fetch itself should run. In Module 03, you called `showWeather(lat, lon)` in response to something — a button click, a page load. In a React component, "when the component first appears (and, sometimes, when something specific about it changes)" is exactly what `useEffect` exists to express (Lesson 03) — so the fetch call itself moves inside a `useEffect`, and the loading/success/error handling wraps around it using state instead of direct DOM writes.

## The details

### The core pattern, naive version first — and its real bug

Start with the simplest version that "works," in the sense that it runs without crashing:

```tsx
// src/QuestCountNaive.tsx
import { useEffect, useState } from "react";
import { fetchQuestCount } from "./fakeApi"; // built below

export function QuestCountNaive() {
  const [count, setCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetchQuestCount()
      .then((result) => setCount(result))
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Unknown error"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  return <p>You have {count} quests.</p>;
}
```

**Line by line:** three `useState` calls track exactly the three questions any async call raises, the same shape Lesson 04 already previewed — `count` (the actual result, `null` until it arrives), `loading` (are we still waiting), `error` (did it fail, and with what message). The `useEffect` (empty dependency array, so it runs once, right after this component's first render — Lesson 03's territory) sets `loading` to `true` and clears any old `error` *before* starting the fetch, then calls `fetchQuestCount()` and reacts to its two possible outcomes with `.then()`/`.catch()` (Module 03, Lesson 07's exact vocabulary), plus a `.finally()` (also standard Promise API — runs regardless of success or failure, exactly once) to turn `loading` back off either way. Finally, three early returns render one of three completely distinct pieces of JSX depending on which state is currently true.

This genuinely works, the first time you run it. Here's the bug, and it is *exactly* the bug Lesson 03 warned about with the `cancelled`-flag pattern: imagine this same fetch is retriggerable — say, a "refresh" button that calls the same effect again (this lesson builds exactly that below), or the component can unmount before the fetch settles. If a *first* fetch is started, and before it resolves, a *second* fetch is started (say, the user clicked refresh twice quickly), both fetches are now in flight simultaneously. There's nothing here stopping the *first* (older, "stale") fetch's `.then()` from resolving *after* the second one, and silently overwriting the second fetch's fresher result with its own older data — the exact "stale response overwrites newer state" bug Lesson 03 named directly. This naive version has no protection against that at all.

### The full, correct version — matching the real capstone almost exactly

```tsx
// src/QuestCountCorrect.tsx
import { useEffect, useState } from "react";
import { fetchQuestCount } from "./fakeApi";

export function QuestCountCorrect() {
  const [count, setCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    setError(null);

    fetchQuestCount()
      .then((result) => {
        if (!cancelled) {
          setCount(result);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unknown error");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [reloadToken]);

  function refetch() {
    setReloadToken((token) => token + 1);
  }

  if (loading) return <p>Loading...</p>;
  if (error)
    return (
      <div>
        <p>Error: {error}</p>
        <button onClick={refetch}>Try again</button>
      </div>
    );
  return <p>You have {count} quests.</p>;
}
```

**Line by line, since by this point you have the full vocabulary (Lesson 03) to understand every piece of this:**

- `let cancelled = false;` — declared fresh, inside the effect function, on every run of the effect. This is a plain local variable, not a ref (Lesson 04 drew that exact distinction: this value only needs to answer a question about *this one specific effect run*, so a plain closure variable, not a ref, is the right tool here — contrast with Lesson 04's `isFirstRender`, which needed to persist *across* multiple separate effect runs, a genuinely different requirement).
- `setLoading(true); setError(null);` — placed *before* the fetch starts, so the UI immediately reflects "we're loading" the instant this effect runs, exactly matching Module 03, Lesson 07's reasoning for setting a loading indicator before an `await`.
- `.then((result) => { if (!cancelled) { setCount(result); } })` — this is the actual fix for the naive version's bug. Before trusting this fetch's result enough to store it in state, check whether *this specific effect run* has since been marked cancelled. If a newer effect run has already started (because `reloadToken` changed again before this older one settled), the cleanup function below will have already set this run's own `cancelled` to `true`, and this stale `.then()` callback's result gets silently discarded instead of overwriting fresher state.
- The `.catch()` and `.finally()` callbacks repeat the exact same `if (!cancelled)` guard, for the same reason — a stale run shouldn't get to set `error` or clear `loading` either, once a newer run is already in charge.
- `return () => { cancelled = true; };` — the cleanup function. Recall from Lesson 03 exactly when this runs: right *before* the effect runs again (because a dependency changed) and also when the component unmounts entirely. Both cases matter here: if `reloadToken` changes again before the current fetch settles, this closure's own `cancelled` flips to `true`, defusing its own two callbacks above the moment they eventually run; if the whole component disappears from the screen before the fetch finishes, this same cleanup stops a `setCount`/`setError`/`setLoading` call from ever firing against a component that no longer exists.
- `const [reloadToken, setReloadToken] = useState(0);` and `[reloadToken]` as the effect's dependency — `reloadToken`'s actual numeric value is never read or displayed anywhere; its entire job is to exist as a dependency so that *changing* it (Lesson 03's rule: a changed dependency re-runs the effect) is a deliberate, on-demand way to say "run this fetch again," with no other meaning attached to the number itself.
- `function refetch() { setReloadToken((token) => token + 1); }` — the actual trigger. Calling this bumps `reloadToken` by one, which is a genuine change to a dependency of the effect, which is exactly what makes the effect run again, from the top, starting a brand-new fetch with its own brand-new `cancelled` flag.

**This is, almost line for line, exactly what the real `project/questlog/src/context/QuestsContext.tsx` does** — same `cancelled` flag, same `if (!cancelled)` guards in `.then()`/`.catch()`/`.finally()`, same `reloadToken`/`refetch` pattern, just fetching `quests` instead of a single `count`, and living inside a Context provider (Lesson 06) instead of a standalone component.

### The fake fetch pattern, and why the course builds one

Notice both examples above call `fetchQuestCount()`, a function you haven't seen the inside of yet. RUNNING_PROJECT.md is explicit about why: QuestLog has no real backend at all yet — that arrives in Module 05 — but practicing loading and error UI honestly requires something *genuinely* asynchronous and *occasionally failing*, not a function that resolves instantly and never fails (against which your loading spinner would never actually be visible, and your error banner would never actually be exercised). The real `project/questlog/src/api/fetchQuests.ts` solves this with a function that returns a Promise via `setTimeout`, with a real, tunable chance of randomly rejecting. Build a simplified version of the same idea yourself:

```tsx
// src/fakeApi.ts
const SIMULATED_DELAY_MS = 800;
const DEFAULT_FAIL_RATE = 0.2;

export function fetchQuestCount(options: { forceError?: boolean; failRate?: number } = {}): Promise<number> {
  const { forceError = false, failRate = DEFAULT_FAIL_RATE } = options;

  return new Promise<number>((resolve, reject) => {
    setTimeout(() => {
      const shouldFail = forceError || Math.random() < failRate;
      if (shouldFail) {
        reject(new Error("Could not reach the quest server. (Simulated failure — try again.)"));
        return;
      }
      resolve(5);
    }, SIMULATED_DELAY_MS);
  });
}
```

**Line by line:** `new Promise<number>((resolve, reject) => { ... })` builds a Promise **by hand**, using the same underlying constructor `fetch` itself uses internally — this is worth pausing on, since Module 03, Lesson 07 only ever showed you Promises that *fetch* had already created for you. `resolve` and `reject` are two functions this constructor hands you; calling `resolve(value)` settles the Promise as fulfilled with `value`, calling `reject(error)` settles it as rejected with `error` — exactly the two outcomes Module 03, Lesson 07 already taught you how to react to with `.then()`/`.catch()`, just now you're the one deciding which happens. `setTimeout(() => { ... }, SIMULATED_DELAY_MS)` delays *when* `resolve`/`reject` gets called by `SIMULATED_DELAY_MS` milliseconds — this is what makes the Promise genuinely take a moment to settle, instead of resolving synchronously and instantly, so a loading state actually has time to be visible on screen. `Math.random() < failRate` gives this fake API a real, tunable chance of failing on its own, exactly matching the real `fetchQuests.ts`'s `DEFAULT_FAIL_RATE` — this exists specifically so the error UI gets exercised sometimes without anyone having to force it, and `forceError` exists for the times you *do* want to force it deliberately (testing, or a lesson example).

**Try it yourself:** call `fetchQuestCount({ forceError: true })` from the naive example above, confirm the error path renders, then switch back to the default options and reload the page a handful of times until you see the ~20% chance of a random failure trigger on its own.

### Rendering three states with early returns

Look again at the return statements in `QuestCountCorrect` above:

```tsx
if (loading) return <p>Loading...</p>;
if (error) return ( /* error UI */ );
return <p>You have {count} quests.</p>;
```

This is deliberately **not** one big conditional expression trying to squeeze all three states into a single JSX tree (something like `{loading ? <Spinner /> : error ? <ErrorBanner /> : <RealContent />}`, nested inline). Early-returning for the loading and error cases keeps the **happy path** — the actual success-case UI, which is usually the largest and most complex part of a component — completely un-nested and readable on its own, as if the loading/error cases didn't exist at all by the time you're reading that final `return`. This is exactly the structure the real `project/questlog/src/pages/QuestListPage.tsx` uses:

```tsx
// project/questlog/src/pages/QuestListPage.tsx (structure, simplified)
export function QuestListPage() {
  const { quests, loading, error, refetch, toggleDone } = useQuests();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorBanner message={error} onRetry={refetch} />;
  }

  // Everything below here can safely assume: not loading, no error,
  // and `quests` is real, current data. No nested conditionals needed
  // anywhere in the rest of this function.
  const visibleQuests = quests.filter(/* ... */).sort(/* ... */);
  return (
    <div>
      {/* the actual quest board UI */}
    </div>
  );
}
```

`useQuests()` (Lesson 06) hands this page `quests`, `loading`, `error`, and `refetch` in one call — no separate `useEffect` in this component at all, because all of that already lives inside `QuestsProvider`. `<LoadingSpinner />` and `<ErrorBanner message={error} onRetry={refetch} />` (`project/questlog/src/components/LoadingSpinner.tsx` and `ErrorBanner.tsx`) are small, focused components — `ErrorBanner` specifically takes an `onRetry` function and renders a real "Try again" button wired directly to it, so passing `refetch` (Lesson 06's Context-provided function, built on this lesson's reload-token pattern) into it is all that's needed to give the user a genuine way to recover from a failed fetch, not just a dead-end error message.

**Try it yourself:** in your own `QuestCountCorrect` example, replace the three early returns with a single nested ternary expression squeezing all three states into one `return`, and compare readability once the "success" JSX grows to, say, five or six lines instead of one. This is a good moment to feel directly why early returns win as a component's real content grows.

## Common mistakes & gotchas

- **Skipping the `cancelled` flag "because it works fine without it."** It does work fine, right up until a fetch is retriggerable (a refetch button, or a dependency the effect depends on changing) — the stale-overwrites-fresh bug is invisible until you actually trigger it twice in quick succession, which makes it easy to ship and only discover later, in production, from a confusing user report of "the count is wrong sometimes."
- **Setting `loading`/`error` state, or calling any state setter, from inside a `.then()`/`.catch()` without the `if (!cancelled)` guard**, once a fetch is retriggerable at all. Every single state-setting call inside the Promise chain needs the same guard — missing even one (e.g., guarding `.then()` but forgetting `.finally()`) reopens the exact bug the other guards were meant to close.
- **Forgetting `setLoading(true)` (and clearing any old `error`) at the *start* of the effect, before the fetch begins**, especially on a refetch — without it, clicking "Try again" after a failure can leave the old error message showing on screen for the entire duration of the new fetch, instead of immediately switching back to a loading state.
- **Reaching for a nested ternary instead of early returns as a component's states grow more complex.** It's not wrong, syntactically, but it makes the actual success-path JSX harder to read the larger it gets, exactly backwards from what you want in the most important, most-visited state of the component.
- **Building a fake API that resolves instantly and never fails**, purely to "get something on screen quickly." This defeats the entire purpose of practicing loading/error UI — a fetch that always succeeds immediately never actually exercises your loading spinner or your error banner at all, and bugs in either will go unnoticed until a real, slower, occasionally-failing backend arrives.

## How this connects

This lesson is explicitly a continuation of Module 03, Lesson 07 — no new async JavaScript, only new placement (inside `useEffect`) and new state management (`useState` instead of direct DOM writes) for exactly the Promise/`fetch`/`async`-`await`/`try`-`catch` vocabulary that lesson already taught. It leaned on Lesson 03's cleanup-function and dependency-array rules throughout, without re-explaining either. It also directly completes Lesson 06's `QuestsContext.tsx`: Lesson 06 taught the `createContext`/`Provider`/custom-hook half of that file; this lesson is the `useEffect`/`cancelled`/`reloadToken` half — put together, you now understand every single line of the real file. Forward, Lesson 08 (React Router) is what actually causes different pages to mount and unmount as the user navigates, making the `cancelled`-flag/cleanup discipline this lesson doubled down on not just theoretical but something a real navigating user will actually trigger.

## Quick self-check

1. In one sentence, what is this lesson teaching that Module 03, Lesson 07 did not already cover?
2. Describe the exact bug the naive version of the data-fetching pattern has, and the specific line(s) added in the correct version that fix it.
3. What is `reloadToken`'s actual value ever used for, besides being an effect dependency — and why does changing it re-run the effect at all?
4. Why does the course's fake `fetchQuestCount`/`fetchQuests` deliberately take time and deliberately sometimes fail, instead of resolving instantly and always succeeding?
5. Why does `QuestListPage.tsx` use two early returns (`if (loading) return ...`, `if (error) return ...`) instead of one large conditional expression covering all three states?
