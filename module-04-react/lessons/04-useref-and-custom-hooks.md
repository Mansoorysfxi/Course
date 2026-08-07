# Lesson 04 — useRef and Custom Hooks

## What you'll learn

- What **`useRef`** actually is: a mutable "box" that persists across re-renders, and exactly how it differs from `useState` — the single most important distinction in this lesson.
- Two concrete, real reasons to reach for a ref: (1) getting your hands on a real DOM node React normally manages for you, and (2) storing a value across renders that should *not* trigger a re-render when it changes.
- What a **custom hook** is: a plain function, name starting with `use`, that calls other hooks internally to package up reusable stateful behavior.
- The **Rules of Hooks** — the two non-negotiable rules every hook (built-in or custom) must follow, and *why* React enforces them.
- How to build your own custom hooks from scratch, ending with a hook shaped exactly like the real `useQuests()` hook this module's capstone (`project/questlog/src/context/QuestsContext.tsx`) uses.

## Why this matters

Right now, every stateful thing you know how to do in React — `useState`, `useEffect` — lives written out, longhand, inside whatever component needs it. That's fine for one component. It stops being fine the moment two *different* components need the exact same stateful logic (say, "fetch some data and track loading/error state") — without a way to package that logic up and reuse it, you'd end up copy-pasting the same `useState`/`useEffect` block into every component that needs it, and every future bug fix would need to be applied in every copy. Custom hooks are React's answer to that problem, and they're not a niche, advanced feature — the real QuestLog capstone's *entire* data layer (`useQuests()`) is a custom hook. `useRef` matters for a narrower but still essential reason: React's whole model is "describe what the UI should look like, and React handles the DOM for you" — but sometimes you genuinely need to reach past that abstraction (focus an input, measure an element, integrate a non-React library), and `useRef` is the one, deliberate escape hatch for exactly those cases.

## Prerequisites

Lesson 01 (components, props, and JSX) and Lesson 02 (state and re-rendering) — this lesson assumes you're comfortable with `useState` and the idea that calling a state setter schedules a re-render. Lesson 03 (`useEffect` and the dependency array, in depth) — this lesson uses `useEffect` as a building block without re-explaining the dependency array's rules; if any of this lesson's `useEffect` code looks unfamiliar, that's the lesson to revisit, not this one. Module 03, Lesson 06 (the DOM and events) — you already know what a real DOM node is and how `document.querySelector` grabs one by hand; this lesson's first `useRef` use case is React's own way of grabbing one. Module 01's discussion of functions and code reuse — custom hooks are that exact same "don't repeat yourself" idea, applied specifically to hook logic.

## The concept, explained simply

Think back to Lesson 02's core idea: **state** is a piece of data that belongs to a component, and calling its setter function (`setSomething(newValue)`) tells React "this component's data changed — please re-render it." That's exactly the right tool when a value needs to show up in the UI: a quest's `done` checkbox, a loading spinner, a form field's text.

But not every piece of data a component needs to remember is supposed to drive the UI. Imagine an Unreal Actor with two very different member variables: a `Health` property that's bound to a widget's health bar — every time `Health` changes, something visible must update — and a private bookkeeping variable like `TimesTickHasRunSinceSpawn`, used only internally by the Actor's own C++ logic to decide something, that no Blueprint, no widget, nothing visual ever reads. Changing `Health` needs to trigger a visual update. Changing `TimesTickHasRunSinceSpawn` does not — it's just the Actor's own scratch paper.

**`useRef`** gives a React component exactly that second kind of variable: a mutable "box" — conventionally called a **ref**, short for "reference" — whose current value lives at `ref.current`, persists across re-renders (React won't reset it back to some initial value the way a plain local variable inside the component function would be reset on every call), and, critically, **changing `ref.current` does not cause a re-render.** React doesn't even know it changed. Contrast that directly with `useState`: **changing state schedules a re-render; changing a ref's `.current` does not.** That's the entire distinction this lesson is built around — everything else follows from it.

## The details

### Creating a ref, and watching it *not* cause a re-render

```tsx
// src/RefVsState.tsx
import { useRef, useState } from "react";

export function RefVsState() {
  const [renderCount, setRenderCount] = useState(0);
  const clickCountRef = useRef(0);

  function handleClick() {
    clickCountRef.current = clickCountRef.current + 1;
    console.log("Ref value is now:", clickCountRef.current);
  }

  return (
    <div>
      <p>This component has rendered {renderCount} time(s).</p>
      <p>The ref's current value (check the console, not this line): {clickCountRef.current}</p>
      <button onClick={handleClick}>Bump the ref (no re-render)</button>
      <button onClick={() => setRenderCount((n) => n + 1)}>Bump state (re-render)</button>
    </div>
  );
}
```

**Line by line:**

- `const [renderCount, setRenderCount] = useState(0);` — familiar from Lesson 02: state that starts at `0`, with a setter that schedules a re-render.
- `const clickCountRef = useRef(0);` — `useRef(0)` creates a ref object with its `.current` property initialized to `0`. That object — `{ current: 0 }` — is the "box." React creates it once, on the component's first render, and hands you back the *exact same box* on every subsequent render of this component — it does not get recreated or reset.
- `clickCountRef.current = clickCountRef.current + 1;` — this is a **plain JavaScript mutation**, not a function call like `setSomething(...)`. There's no "setter" for a ref — you just assign directly to `.current`. Nothing about this line tells React anything happened.
- `console.log("Ref value is now:", clickCountRef.current);` — printed here specifically because, as the next paragraph explains, the value on the page itself will *not* update from this click alone.
- The line `The ref's current value (check the console, not this line): {clickCountRef.current}` — reads `clickCountRef.current` at render time, same as reading any other variable in JSX. It will show whatever the ref's value was *at the moment this component last rendered* — it will look "stuck" after clicking "Bump the ref," because that click didn't cause a new render, so this JSX never re-ran to pick up the new value.

**Try it yourself:** run this component, open the browser console, and click "Bump the ref (no re-render)" three times. **Expected:** the console logs `1`, `2`, `3` — the ref really is updating — but the number shown on the page next to "The ref's current value" does not change at all, and "This component has rendered N time(s)" stays put too. Now click "Bump state (re-render)" once. **Expected:** the page re-renders, `renderCount` goes up by one, *and* the ref's displayed value on the page suddenly jumps to whatever it had silently accumulated to (e.g. `3`) — because this new render is the first time the JSX has re-run and actually looked at `clickCountRef.current` since your three ref-only clicks. This is the whole lesson in one example: **the ref's real value was always correct and always up to date — React simply never repainted the screen to show it, because changing `.current` never asked React to.**

### Use case 1: reaching for a real DOM node (an escape hatch)

React normally handles creating, updating, and removing real DOM nodes for you — you never call `document.createElement` or `element.textContent = ...` yourself the way Module 03, Lesson 06 taught, because JSX and React's rendering describe *what* the DOM should look like and React takes care of *making it so*. But a few genuinely common things aren't expressible that way at all: focusing a specific `<input>`, reading an element's actual pixel size, scrolling to a position, or handing a DOM node to some non-React library that expects one directly. For all of these, you need **the real DOM node itself** — and `useRef`, wired up through a special `ref` prop, is exactly how you get it.

```tsx
// src/AutoFocusInput.tsx
import { useEffect, useRef } from "react";

export function AutoFocusInput() {
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return (
    <div>
      <label htmlFor="quest-title">Quest title</label>
      <input id="quest-title" ref={inputRef} type="text" placeholder="Slay the Dragon" />
    </div>
  );
}
```

**Line by line:**

- `const inputRef = useRef<HTMLInputElement | null>(null);` — this ref starts out holding `null`, and its type is `HTMLInputElement | null` (a **union type**, exactly as Module 03, Lesson 09 defined that term). It starts as `null` because, on the very first render, React hasn't created the actual `<input>` DOM element yet — JSX is only a *description* at that point, not yet a real element sitting in the page.
- `<input id="quest-title" ref={inputRef} type="text" ... />` — this is the wiring. `ref` is a special prop, built into every plain HTML-element JSX tag (`<input>`, `<div>`, `<button>`, and so on), that tells React: "once you create the real DOM node for this element, set `inputRef.current` to point at it." You never call `inputRef.current = ...` yourself for this — React does it for you, automatically, right after the DOM node exists.
- `useEffect(() => { inputRef.current?.focus(); }, []);` — recall from Lesson 03 that an effect with an empty dependency array (`[]`) runs exactly once, right after the component's first render completes and the real DOM has actually been created and inserted into the page. That timing is exactly why this line lives inside a `useEffect` and not directly in the component's body: during the render itself, the `<input>` doesn't exist as a real DOM node yet, so `inputRef.current` would still be `null` if you tried to call `.focus()` at that point. By the time this effect runs, React has finished creating the DOM node and set `inputRef.current` to point at it, so `.focus()` has a real element to act on.
- `inputRef.current?.focus();` — the `?.` (Module 03, Lesson 08's optional chaining) guards against the (unlikely, but type-checked-for) case where `inputRef.current` is still `null` — calling `.focus()` on `null` would throw a runtime error, and TypeScript's `HTMLInputElement | null` type is precisely what forces you to consider that case here at all, rather than letting you write `inputRef.current.focus()` and get a compile error.

**Try it yourself:** run this component and confirm the input is focused (cursor blinking in it) the instant the page loads, with no click needed. Then change the effect to `inputRef.current?.select();` instead of `.focus()` and give the input some default text (e.g. `<input id="quest-title" ref={inputRef} type="text" defaultValue="Slay the Dragon" />` — note `defaultValue`, not `value`; this input is deliberately *uncontrolled* here, a term Lesson 05 defines properly) — predict what you'll see before running it. **Expected:** the input's entire default text arrives already selected/highlighted, exactly like pressing Ctrl+A inside it yourself.

Why does React even need this escape hatch at all? Because React's declarative model — "here's what the UI should look like; you (React) figure out the DOM operations" — genuinely has no way to express instructions like "and also, put the text cursor inside this specific element" as a *description of what's on screen*. Focus, scroll position, and measured size are all facts about the *browser's own internal state*, not facts about what's rendered — so React gives you `ref` specifically to reach past its own abstraction for exactly these cases, without asking you to abandon that abstraction for everything else.

### Use case 2: a value that must persist across renders — but never redraw anything

The other core use for `useRef` has nothing to do with the DOM. Sometimes a component needs to remember something across multiple renders — genuinely across *separate calls* to the component function over time, not just within one function call's local variables — but that something is pure internal bookkeeping, never meant to appear on screen.

Recall Lesson 03's `cancelled` flag from inside a `useEffect`:

```tsx
useEffect(() => {
  let cancelled = false;
  // ... some async work checks `if (!cancelled) { ... }` before using its result
  return () => {
    cancelled = true;
  };
}, [/* deps */]);
```

That `cancelled` flag is a plain local variable, declared fresh *inside the effect function* — it lives and dies within one single run of that one effect. It works there because its whole job is "did the specific async operation started by *this* effect run get cancelled before it settled" — a question that only makes sense within that one effect run's own lifetime.

A ref is for the different situation where you need a value to survive **across multiple separate renders or multiple separate effect runs**, not just within one. The classic example is tracking whether this is a component's very first render:

```tsx
// src/FirstRenderTracker.tsx
import { useEffect, useRef, useState } from "react";

export function FirstRenderTracker() {
  const [count, setCount] = useState(0);
  const isFirstRender = useRef(true);

  useEffect(() => {
    if (isFirstRender.current) {
      console.log("First render — skipping the 'count changed' log.");
      isFirstRender.current = false;
    } else {
      console.log("Count changed to:", count);
    }
  }, [count]);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount((c) => c + 1)}>Increment</button>
    </div>
  );
}
```

**Line by line:**

- `const isFirstRender = useRef(true);` — created once, starts `true`, and — unlike a plain `let isFirstRender = true;` written directly in the component body — is **not** reset back to `true` on every re-render. A plain local variable would be recreated from scratch every single time this component function runs; the ref survives because React itself owns that box and hands you back the same one every render.
- Inside the effect (which, per its dependency array `[count]`, runs after the first render *and* after every render where `count` changed — Lesson 03's territory, not re-explained here): the `if (isFirstRender.current)` check reads whatever was left there by a *previous* render's effect run. On the very first run, it's still `true`. The line `isFirstRender.current = false;` flips it — and because it's a ref, not state, that flip does **not** trigger a re-render (nothing about "we're past the first render now" needs to be shown on screen) — it simply persists, silently, ready to be read by the *next* effect run, whenever that happens.
- On every later render where `count` changed, `isFirstRender.current` is now `false`, so the `else` branch runs instead.

This is exactly the situation where a ref is the right tool and a plain variable inside the effect closure (like Lesson 03's `cancelled`) is not: `cancelled` only ever needs to answer "was *this particular* effect run cancelled," a question fully answered within that one run. `isFirstRender` needs to answer "has *any* render before this one already happened," a question that only makes sense if the answer survives *between* separate effect runs — which requires storage that outlives any single render, i.e., a ref.

**Try it yourself:** add a second `useRef` that stores the *previous* value of `count` (e.g. `const previousCount = useRef(count);`, updated inside the effect after you've used it: `previousCount.current = count;`), and log both the previous and new value on every change after the first. This "compare against the previous render's value" pattern is common enough to have its own name in real-world React code: a "previous value ref."

### Custom hooks: packaging up reusable stateful logic

You already know, from Python, C++, or plain JavaScript, the basic motivation for writing a function: when the same logic shows up in more than one place, you extract it once and call it from everywhere, instead of maintaining N copies. **Custom hooks apply that exact same idea to hook logic specifically** — `useState`, `useEffect`, `useRef`, and so on.

Here's the wrinkle that makes this need its own concept, rather than "just write a normal helper function": a plain JavaScript/TypeScript function **cannot call `useState` or `useEffect` internally** and have it work correctly *unless that function itself follows a specific naming convention and a couple of rules* — because React needs to know, unambiguously, "this function is itself a hook, and it's safe to call other hooks from inside it."

A **custom hook** is simply: a plain function, whose name starts with `use` (by convention — `useCounter`, `useQuests`, `useWindowWidth`), that internally calls one or more other hooks. That's the entire definition. It's not a special syntax, a special file type, or a built-in React feature you import — it's a *naming convention* React (and its tooling) relies on to recognize which of your functions are hooks.

### The Rules of Hooks, and why they exist

Every hook — built-in (`useState`, `useEffect`, `useRef`) or custom (`useCounter`, `useQuests`) — must follow two rules:

1. **Only call hooks at the top level.** Never inside a condition (`if`), a loop (`for`), or a nested function defined inside your component.
2. **Only call hooks from React function components, or from other custom hooks.** Never from a plain regular function, and never from outside the render process (e.g., inside an event handler's callback body directly — call the hook in the component, and use the *value* it returned inside the handler instead).

Here's the concrete reason these rules exist, worth genuinely understanding rather than just memorizing: **React tracks each hook's own state by the order those hooks are called in, on every single render** — not by name, not by any explicit ID you provide. Internally, React keeps something like a numbered list: "hook call #1 on this component is this `useState`'s state; hook call #2 is this `useRef`'s box; hook call #3 is this `useEffect`'s bookkeeping," and so on, rebuilt fresh every render by walking through your component's code from top to bottom and counting hook calls as it goes. As long as your component calls hooks in the *exact same order, the exact same number of times*, on every single render, "hook call #2" reliably means the same state across every render, and React can correctly hand each hook call back its own previously-stored value.

Now imagine you wrote this instead:

```tsx
// DO NOT do this — a Rules of Hooks violation
function BrokenComponent({ showExtra }: { showExtra: boolean }) {
  const [count, setCount] = useState(0);

  if (showExtra) {
    const [extra, setExtra] = useState(""); // called conditionally!
  }

  const [name, setName] = useState("");
  // ...
}
```

On a render where `showExtra` is `true`, this component calls `useState` three times, in order: count, extra, name. On a render where `showExtra` is `false`, it calls `useState` only twice: count, name. React's numbered list now has "hook call #2" meaning `extra`'s state on one render and `name`'s state on the next — the mapping between "which call slot" and "which actual piece of your data" has silently shifted. React genuinely cannot recover from this reliably; in practice you'll see a real error at runtime, something like `Rendered fewer hooks than expected` or state values swapping between fields unpredictably, and React's own official ESLint plugin (`eslint-plugin-react-hooks`) is specifically built to catch this pattern in your editor before you ever run the code, flagging it as `React Hook "useState" is called conditionally`.

This is also exactly why the `use` naming convention matters practically, not just stylistically: that ESLint plugin (and React itself, informally) relies on the name starting with `use` to know "this function needs the Rules of Hooks checked against it." A helper function named `getQuestData` that secretly calls `useState` inside it would not get checked by the linter at all, and calling it conditionally would hit the exact same broken-order bug with no warning — the `use` prefix is what turns "a function that happens to call hooks" into "a hook the tooling actively protects you from misusing."

### Building your first custom hook: `useCounter`

Start with the simplest possible custom hook — wrapping exactly one `useState` and an increment function that several components could otherwise end up rewriting separately:

```tsx
// src/hooks/useCounter.ts
import { useState } from "react";

export function useCounter(initialValue: number = 0) {
  const [count, setCount] = useState(initialValue);

  function increment() {
    setCount((current) => current + 1);
  }

  function reset() {
    setCount(initialValue);
  }

  return { count, increment, reset };
}
```

**Line by line:**

- `export function useCounter(initialValue: number = 0) {` — a plain, exported function. `initialValue: number = 0` is a typed parameter with a default value (Module 03, Lesson 09's parameter typing, plus a familiar default-argument pattern from Python). The name starts with `use`, marking it as a hook to React's tooling and to any human reading it.
- `const [count, setCount] = useState(initialValue);` — this is the one hook call inside this custom hook. This is the entire reason `useCounter` *has* to follow the Rules of Hooks itself: it calls a real hook internally, so it's now subject to the same "top level only, called from a component or another hook" rules as `useState` itself.
- `increment` and `reset` are plain functions, closed over `setCount` — nothing new here versus any event handler you've already written.
- `return { count, increment, reset };` — the hook returns a plain object. This is the calling convention this course uses throughout: a custom hook returns whatever shape of data and functions its callers need, exactly like any other function's return value.

Using it:

```tsx
// src/QuestCounterDemo.tsx
import { useCounter } from "./hooks/useCounter";

export function QuestCounterDemo() {
  const { count, increment, reset } = useCounter(0);

  return (
    <div>
      <p>Quests completed today: {count}</p>
      <button onClick={increment}>+1</button>
      <button onClick={reset}>Reset</button>
    </div>
  );
}
```

Notice this component has **no `useState` of its own at all** — it never even sees `setCount`. All of that lives inside `useCounter`, entirely hidden from this component, which only sees the finished `{ count, increment, reset }` shape. That's the actual payoff: any other component that also needs "a number that goes up and can reset" can call `useCounter()` too, completely independently — each call to `useCounter()` creates its own separate `count` state, exactly the way calling `useState()` twice in two different components creates two independent pieces of state, never shared between them.

**Try it yourself:** add a `decrement` function to `useCounter` (guard it so `count` never goes below `0`), and add a second `<QuestCounterDemo />` instance to some parent component to confirm the two instances' counts are genuinely independent of each other.

### Building toward the real shape: a `{ data, loading, error }` custom hook

Now combine a custom hook with `useEffect`, building toward the exact shape this module's capstone actually uses. This is a **simplified, standalone version** — the full nuance of cleanup and cancellation is Lesson 07's job, not this one — but the point being demonstrated is real and identical:

```tsx
// src/hooks/useFakeQuestCount.ts
import { useEffect, useState } from "react";

interface UseFakeQuestCountResult {
  data: number | null;
  loading: boolean;
  error: string | null;
}

export function useFakeQuestCount(): UseFakeQuestCountResult {
  const [data, setData] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    const timeoutId = setTimeout(() => {
      const succeeded = Math.random() > 0.2;
      if (succeeded) {
        setData(5);
        setLoading(false);
      } else {
        setError("Simulated failure fetching quest count.");
        setLoading(false);
      }
    }, 800);

    return () => clearTimeout(timeoutId);
  }, []);

  return { data, loading, error };
}
```

**Line by line, briefly (Lesson 07 covers this shape's full correct version in depth):** three `useState` calls track exactly the three questions any async operation raises — "do we have a result yet" (`data`), "is it still in flight" (`loading`), "did it fail, and if so, with what message" (`error`). The `useEffect` (empty dependency array — run once, per Lesson 03) starts a fake, timed operation with `setTimeout` standing in for a real network request, and randomly succeeds or fails to exercise both outcomes. The cleanup function (`return () => clearTimeout(timeoutId)`) cancels the pending timeout if this hook's component ever unmounts before it fires — the same category of protection Lesson 03 taught for effects in general, just for a `setTimeout` instead of a fetch.

Any component using this hook gets to write remarkably little:

```tsx
// src/QuestCountBadge.tsx
import { useFakeQuestCount } from "./hooks/useFakeQuestCount";

export function QuestCountBadge() {
  const { data, loading, error } = useFakeQuestCount();

  if (loading) return <p>Loading quest count...</p>;
  if (error) return <p>Error: {error}</p>;
  return <p>You have {data} quests.</p>;
}
```

**This `{ data, loading, error }` return shape is exactly the shape the real capstone's `useQuests()` hook returns** (`project/questlog/src/context/QuestsContext.tsx`, though there it's `quests`/`loading`/`error` plus a handful of action functions like `addQuest`/`updateQuest`/`deleteQuest`/`toggleDone`/`refetch`). You've just built, in miniature, the exact pattern the real app's entire data layer is built on. Lesson 06 (Context) and Lesson 07 (data fetching) are what turn this simplified version into that real one — this lesson's job was making sure the custom-hook mechanics underneath it are no longer a mystery by the time you get there.

## Common mistakes & gotchas

- **Reading `ref.current` in JSX and expecting the screen to update when it changes.** It won't, ever, on its own — a ref changing never schedules a re-render. If a value needs to be visible and update live, it needs to be `useState`, not `useRef`. This is the single most common `useRef` mistake, and it comes directly from *not* internalizing "changing state schedules a re-render; changing a ref does not."
- **Accessing `ref.current` during render, before it's been attached.** For a DOM ref, `.current` is `null` until *after* React has created the real DOM node — which hasn't happened yet during the render itself. Only read a DOM ref's `.current` inside an event handler or a `useEffect` (which, per Lesson 03, runs *after* render completes), never directly in the component's returned JSX-building logic.
- **Calling a hook — built-in or custom — inside a condition, loop, or nested function.** This is a Rules of Hooks violation. Watch for it especially with early returns: `if (!quest) { return <NotFound />; }` followed *later* by more hook calls is fine (all hooks that ran, ran before the branch), but hooks called *after* a conditional return that sometimes fires and sometimes doesn't is not — every hook call must happen on every single render, unconditionally. (Note: `project/questlog/src/pages/QuestDetailPage.tsx`'s early `if (!quest)` return happens *before* any hooks are declared below it in that file precisely to sidestep this — it's not an accident.)
- **Forgetting the `use` prefix on a custom hook.** Nothing crashes immediately, but React's ESLint plugin can no longer verify the Rules of Hooks for that function at all, silently leaving you unprotected from exactly the bug the rules exist to prevent.
- **Mutating `ref.current` directly inside the component's render body (not inside an effect or a handler) as a way to "remember something."** This technically runs, but it's fighting React's own execution model — a component function can be called more than once for a single committed render in some circumstances (particularly under features this course doesn't cover yet), and mutating refs outside effects/handlers is considered unsafe, unpredictable practice. Keep ref mutations inside effects and event handlers, exactly as every example in this lesson does.

## How this connects

This lesson leaned on Lesson 03's `useEffect` and dependency-array vocabulary throughout — the DOM-focus example and the fake-fetch hook both run their real work inside effects, exactly as Lesson 03 taught. Custom hooks are also the exact mechanism the next three lessons build toward without saying so explicitly: Lesson 05's forms, Lesson 06's Context, and Lesson 07's data fetching all eventually get wrapped in custom hooks in the real capstone — most directly, `useQuests()` in `project/questlog/src/context/QuestsContext.tsx`, which is precisely this lesson's `{ data, loading, error }` pattern, extended with Context (Lesson 06) so it can be reached from anywhere in the app, and with the full correct fetch/cleanup pattern (Lesson 07). This is also, at bottom, the same code-reuse idea Module 01 taught you about writing functions in the first place — custom hooks are what "don't repeat yourself" looks like once the thing you're repeating is stateful React logic instead of a plain calculation.

## Quick self-check

1. In your own words: what's the one-sentence difference between what happens when you change a piece of `useState` state versus when you change a ref's `.current`?
2. Why does the auto-focus example call `.focus()` inside a `useEffect` instead of directly in the component's returned JSX-building code?
3. Give a concrete example (not from this lesson) of a value that should live in a ref rather than in state, and explain why state would be the wrong choice for it.
4. What are the two Rules of Hooks, and what specifically does React track, render to render, that breaks if you violate the "only call hooks at the top level" rule?
5. Why can't you just write a plain helper function (not named `use...`) that internally calls `useState`, and expect the Rules of Hooks tooling to protect you if you call it conditionally?
