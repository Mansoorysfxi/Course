# Lesson 03 — useEffect: The Dependency Array In Depth

## What you'll learn

- What a **side effect** is, precisely, and why it's kept separate from a component's normal render body.
- What **`useEffect`** actually does, and why React gives you a dedicated, controlled place to run this kind of code instead of letting you run it directly while rendering.
- The **dependency array**, in full: no array at all, an empty array `[]`, and an array with values — exactly when each form runs, with runnable proof for each.
- **Stale closures**: what the term means precisely, why an effect with a missing dependency silently keeps seeing old data forever, and how to fix it.
- **Missing dependencies**: the "exhaustive deps" rule, as a convention to understand, not just a lint warning to silence.
- **Infinite loops**: the classic effect-triggers-itself bug, including the specific "a new object/array literal on every render is never equal to the last one" trap, and how to fix both.
- **Cleanup functions**: what returning a function from `useEffect` actually does, and the `cancelled`-flag pattern that stops a late-arriving async response from overwriting newer, correct state.
- Why React 19's `StrictMode` deliberately double-invokes effects in development, and why that's a feature, not a bug in your code.

## Why this matters

`useEffect` is, by a wide margin, the single most commonly *mis*used hook in React, and nearly every real-world React bug story that isn't "I mutated state directly" (Lesson 02) traces back to one of exactly three mistakes this lesson covers in full: a missing dependency causing stale data, a dependency that changes every render causing an infinite loop, or a missing cleanup function letting an old, no-longer-relevant async result overwrite newer state. This lesson is deliberately the most detailed one in this module because getting the dependency array right is a skill, not a fact you memorize once — you will make each of these three mistakes at least once regardless of how carefully you read this, and the goal here is that when you do, you'll recognize exactly which of these three sections you're looking at.

## Prerequisites

**Lesson 02** in full — you need state and the rendering model (what a render is, what triggers one) solid before adding a hook whose entire job is reacting to renders. **Module 03, Lesson 07** (fetch, Promises, async/await) — this lesson's examples use `fetch`-shaped async code, and leans directly on that lesson's Promise/`.then()`/`async`-`await` vocabulary without re-explaining it. **Module 03, Lesson 05** (the JavaScript event loop) — the reasoning for why side effects can't run directly during render connects to that lesson's explanation of JavaScript's single thread. **Module 01, Lesson 02** (functions and scope) — the stale closure section below leans directly on that lesson's definition of a closure.

## The concept, explained simply

A component's normal job, as Lessons 01 and 02 established, is: given the current props and state, return a description of UI. That's supposed to be a **pure**, self-contained calculation — the same inputs should always produce the same description, and nothing about *computing* that description should reach out and touch anything in the real world. A **side effect** is exactly that "reaching out to the real world" work: making a network request, starting or clearing a timer, subscribing to something (a WebSocket, a browser event, a third-party library), or manually reading/writing something outside React's own rendering (like the page's `document.title`). None of this belongs inside the plain body of a component function, and `useEffect` is the hook that gives this kind of code a specific, controlled place to run instead.

Here's a game-dev-shaped way to think about why the split exists at all: you wouldn't put a blocking network call directly inside an Actor's `Tick` function — `Tick` needs to run fast, deterministically, and potentially very often, and a slow network call sitting inside it would stall the whole frame. Instead, you'd kick the network call off separately and handle its result whenever it actually arrives, keeping `Tick` itself fast and side-effect-free. A React component's render body is that `Tick` function: it needs to be fast, predictable, and safe to call as often as React wants to call it (React 19 can, in some situations, start rendering and decide to discard or redo that work before it's ever shown to the user — you don't need the full mechanics of that to use `useEffect` correctly, only the consequence: **render must stay side-effect-free**, because you can't safely fire off "make a real network request" code from something that might run more than once, or get thrown away, without you asking for that). `useEffect` is React's answer to "where, then, do I put the side effect?" — it says: run this code **after** React has rendered and updated the real DOM for this render, and — this is the entire subject of this lesson — only when I tell you to, via the dependency array.

## The details

### Example 1 — no dependency array: runs after *every* render

```tsx
// src/components/RenderLogger.tsx
import { useState, useEffect } from "react";

export function RenderLogger() {
  const [count, setCount] = useState(0);
  const [unrelated, setUnrelated] = useState(0);

  useEffect(() => {
    console.log("effect ran");
  });

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment count</button>
      <button onClick={() => setUnrelated(unrelated + 1)}>Increment unrelated</button>
    </div>
  );
}
```

**Line by line:** `useEffect(() => { console.log("effect ran"); });` — `useEffect` takes a function (called the **effect function**) as its first argument. With **no second argument at all**, React runs this function after **every single render**, no matter what changed. Render `RenderLogger` for the first time, and it logs once. Click *either* button — even "Increment unrelated," which has nothing to do with `count` — and it logs again, every time, because *any* re-render of this component (Lesson 02: a state setter call schedules one) re-runs this effect.

**Run it:** render `<RenderLogger />` from `App.tsx`, open your browser's developer console, and click both buttons a few times.

**Expected output in the console:** `effect ran` once on load, then once more after *every single click of either button*, regardless of which one.

**Why this form is almost always wrong:** an effect with no dependency array re-runs for reasons that have nothing to do with what the effect actually cares about. If this effect were, instead, `fetch(...)`-ing data, you'd be firing a brand-new network request after literally every render of this component — including renders triggered by completely unrelated state changes elsewhere in the same component. This form has a real, narrow use (some kinds of debug logging, or syncing something on truly every render), but if you write `useEffect(() => { ... })` with no array while trying to fetch data or start a subscription, it is very likely a bug, not a choice.

**Try it yourself:** delete the "unrelated" button and its state entirely, leaving only `count`. Predict whether the effect still runs on every render before checking. **Expected:** yes — "no dependency array" genuinely means every render, full stop, regardless of how many or few state variables the component has.

### Example 2 — empty array `[]`: runs once, on mount

```tsx
// src/components/MountLogger.tsx
import { useState, useEffect } from "react";

export function MountLogger() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    console.log("MountLogger appeared on screen — this only prints once");
  }, []);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}
```

**Line by line:** the second argument, `[]`, is the **dependency array** — an empty one. An empty array means "this effect has no dependencies that ever change," so React runs it exactly once: after the very first render, when this component first appears — a moment with its own name, **mount**, meaning precisely "the first time this component is inserted into the page." No matter how many times you click the button afterward (each click triggers a normal re-render, per Lesson 02), the effect does **not** run again, because `[]` never changes.

**Run it:** render `<MountLogger />`, click the button several times.

**Expected output:** `MountLogger appeared on screen — this only prints once` exactly once, the moment the component first shows up — never again, no matter how many clicks follow.

This is the shape you'll use for "load this data once when the component first appears" — the exact shape QuestLog's real `QuestsContext.tsx` uses to fetch quests when the app first starts, though (foreshadowing this lesson's cleanup section) its actual dependency array isn't quite bare `[]`, for a reason you'll see shortly. Loading/error UI *states* around a fetch like this — what to show while waiting, what to show if it fails — are covered properly in this module's later data-fetching lesson; for now, focus only on *when* the effect itself runs.

**Try it yourself:** change `[]` to have no second argument at all (reverting to Example 1's form) and click the button a few times. Predict the console output before checking. **Expected:** the message now prints once per click, exactly like Example 1 — a direct, hands-on demonstration that the *presence* of `[]` versus *no array at all* is the entire difference between "once" and "every render."

### Example 3 — an array with values: runs on mount, and again whenever a listed value differs

```tsx
// src/components/QuestWatcher.tsx
import { useState, useEffect } from "react";

export function QuestWatcher() {
  const [questId, setQuestId] = useState("quest-001");
  const [unrelated, setUnrelated] = useState(0);

  useEffect(() => {
    console.log("Watching quest:", questId);
  }, [questId]);

  return (
    <div>
      <p>Currently watching: {questId}</p>
      <button onClick={() => setQuestId("quest-002")}>Switch to quest-002</button>
      <button onClick={() => setUnrelated(unrelated + 1)}>Increment unrelated ({unrelated})</button>
    </div>
  );
}
```

**Expected behavior:** on mount, logs `Watching quest: quest-001`. Click "Increment unrelated" as many times as you like — **nothing logs**, because `questId` didn't change, and it's the only thing listed in `[questId]`. Click "Switch to quest-002" once — logs `Watching quest: quest-002` — and clicking it again does nothing further, since `questId` is already `"quest-002"` and setting state to the same value it already holds doesn't trigger a new render at all.

**How React decides "did this value change":** for each value listed in the dependency array, React compares this render's value to the previous render's value using `Object.is` — for practical purposes here, behaving like JavaScript's `===`. For primitives (strings, numbers, booleans, like `questId` above), this is exactly "is it the same value," and it works exactly as you'd expect. **For objects and arrays, this comparison is by reference, not by contents** — two different object literals with identical-looking contents (`{ limit: 10 }` created twice) are **not** equal by `Object.is`/`===`, even though they'd look the same if you logged them side by side. This one fact is the seed of this lesson's infinite-loop section below — hold onto it.

### Stale closures: the effect that never sees updated state

This is the single most important trap in this entire lesson, and it's worth watching it break before you see the fix.

```tsx
// src/components/BrokenTicker.tsx
import { useState, useEffect } from "react";

export function BrokenTicker() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      console.log("count is:", count);
    }, 1000);

    return () => clearInterval(interval);
  }, []); // <-- empty array: this effect only ever runs once

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount((c) => c + 1)}>Increment</button>
    </div>
  );
}
```

**Run it:** render `<BrokenTicker />`. Immediately click "Increment" five or six times, watching the console the whole time.

**Expected (broken) output:** the console prints `count is: 0` once every second, **forever** — even after you've clicked the button many times and the on-screen "Count: 5" clearly shows the real value has changed. It never prints `1`, `2`, or anything but `0`.

**Exactly why this happens, using the closure vocabulary from Module 01, Lesson 02:** `useEffect`'s effect function — the arrow function passed as its first argument — is created **fresh, from scratch, every single render**, exactly like any other function or variable inside a component body. But this effect's dependency array is `[]`, so React only ever *calls* the version of that function that was created during the very first render, on mount, and never calls any of the newer versions created by later renders (each of which would have correctly closed over an updated `count`). The one function React did call, back on mount, is a **closure** — it "remembers" the variables from its enclosing scope at the exact moment it was created, per Module 01, Lesson 02's definition — and at that moment, `count` was `0`. That single frozen closure is what `setInterval` keeps calling, once a second, forever: it's not that React is somehow reading a "wrong" live value of `count` — it's that this exact closure, permanently, only ever knew about the `count` that existed the instant it was created. This is what **stale** means here: not "wrong" in some abstract sense, but specifically "old — from an earlier render that's since been superseded."

**The fix:** the effect reads `count`, so `count` belongs in the dependency array:

```tsx
useEffect(() => {
  const interval = setInterval(() => {
    console.log("count is:", count);
  }, 1000);

  return () => clearInterval(interval);
}, [count]); // <-- now the effect re-runs whenever count changes
```

**Run it again with this change.** Click "Increment" a few times, waiting a moment between clicks.

**Expected (fixed) output:** the console now prints the *current*, correct count each time — `count is: 0`, then, once you click and a new render happens, `count is: 1` starts appearing instead, then `count is: 2`, tracking whatever the button's actual on-screen count shows.

**What actually changed:** with `count` listed as a dependency, every render where `count` differs from last time causes React to run the cleanup function from the *previous* effect (clearing the old interval) and then run a brand-new effect function — one freshly created during *this* render, closing over *this* render's correct, current `count`. You're no longer running one permanently-frozen function forever; you're running a fresh, correctly-closed-over function every time `count` changes, which happens to also mean a new `setInterval` is created each time. (A real "count up every second, but never restart the interval" ticker needs one more tool — a `ref`, Lesson 04's territory — to read a value without needing it in the dependency array at all; the fix shown here is the *general* fix for stale closures, and it's the right one whenever restarting the effect on change is acceptable, which is most of the time.)

### Missing dependencies: the rule, stated plainly

The bug above happened because `count` was read inside the effect but not listed in the dependency array. The general rule — commonly enforced by an ESLint rule most real projects turn on, named `exhaustive-deps`, which this lesson doesn't ask you to configure, only to understand — is:

> **Every value from component scope (state, props, or anything derived from them) that your effect function reads must be listed in the dependency array.**

This isn't an arbitrary style rule. It's the direct, mechanical fix for exactly the stale-closure bug above: if an effect reads a value and that value isn't in the dependency array, the effect will keep running with whatever that value was on the render when the effect function currently in use was created — stale, by definition, the moment that value ever changes without the effect being told to re-run. When you see a lint warning naming a specific variable as a missing dependency, read it as: "this effect is reading a value that can go stale — either add it to the array, or you have a specific reason (like the `ref`-based fix mentioned above) that the warning doesn't know about."

### Infinite loops: when an effect keeps re-triggering itself

The dependency array can cause the opposite problem too — an effect that runs far too often, potentially forever.

**Case A — a dependency that's always "different," even though it looks the same:**

```tsx
// src/components/BrokenOptions.tsx
import { useState, useEffect } from "react";

export function BrokenOptions() {
  const [count, setCount] = useState(0);
  const options = { limit: 10 }; // a brand-new object, every single render

  useEffect(() => {
    console.log("effect ran, count is", count);
    setCount((c) => c + 1);
  }, [options]);

  return <p>Count: {count}</p>;
}
```

**Run it.** Do not walk away from your keyboard — this one genuinely runs away.

**Expected (broken) output:** the console fills with `effect ran, count is 0`, `effect ran, count is 1`, `effect ran, count is 2`... as fast as your machine can go, and the on-screen count climbs the same way, without you clicking anything at all.

**Exactly why:** `const options = { limit: 10 };` creates a **brand-new object literal every time `BrokenOptions` renders** — even though its *contents* (`{ limit: 10 }`) never actually change, its *reference* is different every single time, for the same reason two separately-written `{ ... }` literals are never `===` to each other in plain JavaScript. Recall from Example 3 above: React compares dependency-array values by reference, not contents. So on every render, `options` looks "different from last render" to React's comparison — even though nothing about it meaningfully changed — which means the effect runs again. This effect calls `setCount`, which schedules a new render. That new render creates a *new* `options` object again (same trap), so the *next* effect run also sees a "changed" dependency, runs again, calls `setCount` again... and the cycle never has a reason to stop.

**The fix — depend on the actual primitive value you care about, not the object wrapping it:**

```tsx
const options = { limit: 10 };

useEffect(() => {
  console.log("effect ran, limit is", options.limit);
}, [options.limit]); // a plain number — stable across renders unless it actually changes
```

`options.limit` is a plain `number`, compared by value, not by reference — it's genuinely the same `10` on every render until something actually changes it, so the effect correctly stops re-running once whatever it needed to do is done. (The other standard fix, for cases where you truly need the whole object as a dependency, is to only create that object once — outside the component, or with a tool called `useMemo` that this module doesn't cover in depth yet — rather than fresh on every render; naming the actual primitive fields you need, as shown here, is usually simpler and is the right default.)

**Case B — an effect's own setter feeds back into its own dependency, unconditionally:**

```tsx
// src/components/RunawayCounter.tsx
import { useState, useEffect } from "react";

export function RunawayCounter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    setCount(count + 1); // always bumps count, with no condition or exit
  }, [count]); // ...and count is exactly what this effect depends on

  return <p>Count: {count}</p>;
}
```

**Expected (broken) output:** the on-screen count climbs as fast as React can re-render, with no clicks, and never stops — `count` changes because the effect changed it, which re-runs the effect (since `count` is a dependency), which changes `count` again, forever. There's no bug in the reference-comparison sense here (`count` really is a different, genuinely-changed number each time) — the loop is simply the intended, correct behavior of "re-run when `count` changes" applied to an effect that itself unconditionally changes `count`, with nothing to ever stop it.

**The fix** is almost always to ask what this effect was actually trying to accomplish, since "always increment on every change, forever" is rarely the real goal — a genuinely one-time initialization becomes `[]`; a "only bump it in response to some *other* thing changing" becomes a dependency array naming that other thing instead of `count`; a "count up over time" ticker reaches for `setInterval` inside a mount-only effect (Example 2's shape) rather than a state-feedback loop inside the effect itself.

### Cleanup functions: preventing a stale async response from overwriting fresh state

Recall `BrokenTicker`'s fix above already returned a function from its effect (`return () => clearInterval(interval);`) without this lesson fully explaining what that does yet — here's the full explanation.

**Returning a function from an effect registers a cleanup function.** React calls it in exactly two situations: **right before running this effect again** (if its dependencies changed), and **when the component unmounts** (removed from the page entirely — the opposite of "mount" from Example 2). This is how you undo whatever the effect set up — clearing a timer/interval so old ones don't pile up, unsubscribing from something, and, critically for anything involving `fetch`, preventing a request that's no longer relevant from still being able to affect state once it finally resolves.

Here's the exact problem cleanup solves, with a runnable (simulated) example:

```tsx
// src/components/QuestDetailDemo.tsx
import { useState, useEffect } from "react";

function fakeFetchQuestTitle(questId: string): Promise<string> {
  const delay = 200 + Math.random() * 1800; // an unpredictable network delay
  return new Promise((resolve) => {
    setTimeout(() => resolve(`Title for ${questId}`), delay);
  });
}

export function QuestDetailDemo() {
  const [questId, setQuestId] = useState("quest-001");
  const [title, setTitle] = useState("Loading...");

  useEffect(() => {
    let cancelled = false;
    setTitle("Loading...");

    fakeFetchQuestTitle(questId).then((result) => {
      if (!cancelled) {
        setTitle(result);
      } else {
        console.log("Ignored a stale response for", questId);
      }
    });

    return () => {
      cancelled = true;
    };
  }, [questId]);

  return (
    <div>
      <p>{title}</p>
      <button onClick={() => setQuestId("quest-002")}>Switch to quest-002</button>
      <button onClick={() => setQuestId("quest-003")}>Switch to quest-003</button>
    </div>
  );
}
```

**Line by line, on the new parts:** `let cancelled = false;` — a plain local variable, created fresh inside the effect on every run, starting `false`. `fakeFetchQuestTitle(questId).then((result) => { if (!cancelled) { setTitle(result); } ... });` — when the simulated request finally resolves, it only calls `setTitle` **if `cancelled` is still `false`**. `return () => { cancelled = true; };` — the cleanup function: React calls this right before running the effect again (i.e., the moment `questId` changes) or on unmount, and all it does is flip this specific run's `cancelled` flag to `true`.

**Why this matters concretely:** click "Switch to quest-002" and then, before it's had time to resolve (the delay is random, up to nearly two seconds), immediately click "Switch to quest-003." Two requests are now in flight — one for `quest-002`, one for `quest-003` — and there's no guarantee they resolve in the order you started them; the `quest-002` request might genuinely finish *after* the `quest-003` one, purely because of network/timing randomness. **Without the cleanup/`cancelled` pattern**, whichever response happens to arrive last would win, overwriting the screen with an old quest's title even though you've since moved on to a different one — a real, user-visible bug where the UI shows the *wrong* data with total confidence. **With it**, the moment `questId` changes, React calls the previous run's cleanup, setting *that* run's `cancelled` to `true` — so if `quest-002`'s response arrives after you've already switched away, its `.then()` callback sees `cancelled === true` (its own run's flag, not the new run's) and correctly does nothing, logging `Ignored a stale response for quest-002` instead of clobbering the correct `quest-003` title that (hopefully) already arrived or is still loading.

One precise thing worth naming: **setting `cancelled = true` does not actually cancel the underlying request or timer** — the `setTimeout` in `fakeFetchQuestTitle` still fires, the Promise still resolves; a real `fetch` call, similarly, keeps running over the network. All the flag does is tell *this specific effect run's own callback* "don't act on your result anymore." (Genuinely aborting a real in-flight `fetch` is possible with a separate browser API, `AbortController` — out of scope here; the `cancelled`-flag pattern shown above is the simpler, extremely common approach that solves the actual bug — stale data overwriting fresh data — without needing that extra API.) This is, exactly, the same pattern used in this module's capstone, in `project/questlog/src/context/QuestsContext.tsx` — you haven't seen that file yet, but when you do, you'll recognize this `cancelled` flag immediately.

**Try it yourself:** comment out the `if (!cancelled)` check (call `setTitle(result)` unconditionally) and repeat the rapid double-click test a few times. You won't see it fail *every* time — timing has to line up unluckily — but occasionally you'll see the title briefly (or persistently) show the wrong quest's data, a flicker of exactly the bug the cleanup function exists to prevent.

### React 19's `StrictMode`: why effects run twice in development

If you look at `main.tsx` in a Vite-scaffolded project (yours from Lesson 00, or the capstone's), you'll find your app wrapped in `<StrictMode>`:

```tsx
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

**`StrictMode`** is a component that doesn't render anything itself — it exists purely to turn on extra development-only checks for everything inside it. One specific, relevant check for this lesson: **in development only**, React 19 deliberately runs each effect through mount → cleanup → mount again, immediately, the first time a component appears — you'll see an effect's setup code run, then its cleanup run, then its setup code run *again*, all before you've done anything at all. This is not a bug in your code, and it is not something that happens in a real production build (`npm run build`) — it's intentional, and it exists specifically to surface exactly the kind of missing- or broken-cleanup bugs this lesson just covered, by forcing them to happen immediately and visibly instead of only showing up later, rarely, in production, under exactly the kind of timing-dependent conditions the `QuestDetailDemo` example above relied on to demonstrate the bug at all.

Concretely: if `QuestDetailDemo`'s effect were missing its `cancelled` cleanup entirely, `StrictMode`'s double-invoke would make that far more likely to visibly misbehave even on a single, slow click, rather than requiring you to time two rapid clicks just right to notice. This is exactly why a correct cleanup function matters even for an effect that looks like it "only runs once" (an empty-array, mount-only effect) — `StrictMode` will still mount → clean up → mount it once, on purpose, specifically to check that your cleanup genuinely undoes whatever the setup did.

## Common mistakes & gotchas

- **Fetching data (or any other side effect) directly in the render body, with no `useEffect` at all.** This can fire the request on every single render, with no defined moment to know it's "done," and violates the "render must stay side-effect-free" rule this lesson opened with. If you're calling `fetch`, `setTimeout`, or subscribing to anything, that code belongs inside a `useEffect`.
- **A missing dependency causing a stale closure** — covered in full above. The tell: an effect that reads a state/prop value, appears to "work" once, and then keeps reporting/using an old value forever after that value changes elsewhere.
- **An object or array literal created fresh every render, used as a dependency.** Covered in full above under infinite loops — the tell: an effect that clearly *should* only run occasionally instead runs on every render, or spirals into a genuine infinite loop the moment it also happens to call a state setter.
- **Forgetting the cleanup function on an effect that starts a timer, subscription, or async request**, leading to a pile-up of running timers/subscriptions, or a stale response overwriting fresher state — covered in full above.
- **Trying to make `useEffect`'s effect function itself `async`** — `useEffect(async () => { await fetch(...); }, [])` is invalid; the function passed to `useEffect` must return either nothing or a cleanup function, and an `async` function always returns a Promise (Module 03, Lesson 07), which is neither. The fix is defining a normal `async` function *inside* the effect and calling it, without `await`-ing it directly in the effect body: `useEffect(() => { async function run() { ... } run(); }, [])`.
- **Confusing "runs twice in development because of `StrictMode`" with a real bug.** If your effect's setup and cleanup logic are correct, running mount → cleanup → mount once in development is expected and harmless — it does not happen in production, and it exists specifically to catch cleanup mistakes before they reach a real user.

## How this connects

You now have the full dependency-array picture: no array (every render), `[]` (mount only), and `[a, b]` (mount, plus whenever `a` or `b` genuinely differ by reference) — along with the three specific failure modes (stale closures, infinite loops, missing cleanup) that account for the overwhelming majority of real `useEffect` bugs. This connects directly back to Module 03, Lesson 07's Promises and `async`/`await`, and to Lesson 05's event loop — everything asynchronous you learned to write there is exactly what you're now learning to run at the *right moment*, in the *right place*, inside a React component. It connects back further still to Module 01, Lesson 02's closures — the stale-closure bug is that same concept, doing real damage in real code, not an abstract definition anymore. Looking forward: Lesson 04 introduces custom hooks, which very often exist specifically to wrap a `useEffect` (plus a `ref`, solving the exact "read a value without needing it as a dependency" limitation this lesson's `BrokenTicker` fix ran into) into a small, reusable, correctly-cleaned-up package. And this module's dedicated data-fetching lesson takes the `cancelled`-flag pattern from this lesson's `QuestDetailDemo` and builds the full, real loading/error UI treatment around it — everything mechanical about *when* and *how safely* the fetch runs, you've already learned here.

## Quick self-check

1. What specifically is a "side effect," and why can't this kind of code run directly inside a component's render body?
2. An effect reads a state variable but has `[]` as its dependency array. Explain, using the word "closure," exactly what value that effect will see for that variable, no matter how many times the component re-renders afterward — and why.
3. `useEffect(() => { ... }, [someObject])`, where `someObject` is created fresh with `{ ... }` inside the component body on every render. Why does this often cause the effect to run on every single render, even if `someObject`'s contents never actually change?
4. What does returning a function from `useEffect` actually cause React to do, and name the two specific moments it's called?
5. In the `cancelled`-flag pattern, does setting `cancelled = true` actually stop the underlying network request/timer? If not, what does it actually prevent?
