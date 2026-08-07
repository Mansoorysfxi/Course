# Lesson 02 — State and the Rendering Model

## What you'll learn

- What **state** is, precisely: data a component owns that, when changed, should cause the UI to update — and why a plain variable can't do this job.
- **`useState`**: what it actually returns, how to read and update it, and why it's the mechanism that makes React aware something changed.
- What a **render** actually is, in exact terms — not "the page redraws," but "React calls your component function again."
- What specifically **triggers** a render: a state update, a parent re-rendering, props changing.
- What the **Virtual DOM** is (a plain JS object tree, not the real browser DOM) and what **reconciliation**/diffing means — and why React works this way instead of just rebuilding the whole page every time something changes.
- The single most common beginner trap with `useState`: why a `console.log` placed right after calling the setter still shows the *old* value.
- How to update state that's an array of objects (toggling one item's flag) without mutating the original array — and why that rule exists.

## Why this matters

Every interactive thing you build from here forward — a checkbox, a counter, a form field, a filter — is state. Get the mental model in this lesson solid, and hooks, forms, and data fetching in the rest of this module will feel like small variations on one idea you already understand deeply. Get it fuzzy, and you'll spend the rest of the module fighting bugs that all trace back to the same two misunderstandings this lesson exists to prevent: expecting a state update to happen instantly, and mutating data in place instead of replacing it.

## Prerequisites

**Lesson 01** in full — you need components, props, and JSX comfortable before adding a fourth moving piece. **Module 03, Lesson 08** (ES6+ features) — this lesson uses array destructuring (`const [a, b] = ...`) constantly, and you'll see `.map()` used to build a new array rather than mutate an old one. **Module 01, Lesson 02** (functions and scope) — this lesson's explanation of *why* `console.log` shows a stale value after a state update leans directly on the closure concept that lesson introduced.

## The concept, explained simply

Picture an Actor in Unreal with a `Health` property, and a HUD widget with a health bar bound to it. In the engine's own terms, changing `Health` doesn't, by itself, magically repaint the health bar — *something* has to notice the change and act on it. Depending on how you built it, that might be an explicit call from your damage-handling code to update the widget, or a Blueprint's construction script re-running, or a "health changed" event you wired up yourself. The point is: **you, the developer, are responsible for connecting "this property changed" to "therefore, update this specific piece of UI."**

React's **state** is a component's own version of that `Health` property — a piece of data a component owns, that's expected to change over time, and that should cause the UI to update when it does. The difference from the Unreal picture above is the entire point of React: **you don't wire up the "notice the change, then update the UI" step yourself.** You declare a piece of state, and whenever you update it through the mechanism React gives you, React handles noticing the change and updating the UI, automatically, every time, for every component that depends on it. That mechanism is a **hook** called `useState` — a **hook** being nothing more mysterious than "a specially-named function, starting with `use`, that lets a component tap into React features like state" (you'll meet several more hooks later this module; `useState` is the first).

Here's the concrete reason you can't just use a plain variable for this. Say you tried:

```tsx
function Counter() {
  let count = 0;

  function handleClick() {
    count = count + 1;
    console.log(count); // this part works fine
  }

  return <button onClick={handleClick}>Count: {count}</button>;
}
```

Click the button, and `count` really does become `1`, then `2`, then `3` — the `console.log` proves it. But the button's displayed text never changes from "Count: 0." Why? Because **nothing about reassigning a plain JavaScript variable tells React "hey, re-run this component function and update the page."** `count` living inside `Counter`'s function body is just a regular local variable; React has no way to observe that it changed, because nothing about a plain assignment (`count = count + 1`) is visible to anything outside that one function call. The only way the text on the button would ever update is if `Counter` itself got called again — and nothing here causes that to happen. `useState` exists precisely to fix this: it's the specific mechanism that tells React "something changed, please re-run this component and update what depends on it."

## The details

### `useState`: what it returns and how to use it

```tsx
// src/components/Counter.tsx
import { useState } from "react";

export function Counter() {
  const [count, setCount] = useState(0);

  function handleClick() {
    setCount(count + 1);
  }

  return <button onClick={handleClick}>Count: {count}</button>;
}
```

**Line by line:** `import { useState } from "react";` — `useState` is a function exported directly by the `react` package itself, not something you write. `const [count, setCount] = useState(0);` — this is the one line worth slowing all the way down for:
- `useState(0)` — the argument, `0`, is the **initial value** this state starts at, used only the very first time this component renders.
- `useState` returns **a pair**: a two-element array, always in this order — `[currentValue, setterFunction]`. `const [count, setCount] = ...` is ordinary array destructuring (Module 03, Lesson 08), pulling those two elements out into two named variables in one line. You choose the names; `count`/`setCount` is a strong, near-universal convention (`value`/`setValue` for the state itself, `set` + the same name for its setter), not a required one.
- `count` is the **current value** of this state, for *this* render only — read it like any other variable.
- `setCount` is a function whose entire job is: **call it with a new value, and it tells React "this state changed — please re-render this component with the new value."** This is the missing piece the plain-variable version above didn't have.

`function handleClick() { setCount(count + 1); }` — clicking the button calls `setCount`, handing it `count + 1` (the current value plus one). This does two distinct things, worth naming separately: it records the new value for React to use, and it **schedules a re-render** of `Counter` — it does not, itself, immediately change what's on screen; the re-render (covered next) is what actually does that.

**Run it:** render `<Counter />` from `App.tsx` exactly as you rendered `<Greeting />` in Lesson 01, save, and click the button in the browser repeatedly.

**Expected output:** the button's text updates, "Count: 0" → "Count: 1" → "Count: 2", once per click — unlike the plain-`let` version above, which was frozen at "Count: 0" forever no matter how many times `count` itself actually changed underneath.

**Try it yourself:** add a second, completely unrelated `<Counter />` instance next to the first one in `App.tsx`. Click one of them several times. Predict, before checking, whether the *other* counter's number changes too. **Expected:** no — each `<Counter />` instance has its **own, independent** call to `useState(0)` and its own independent `count`. This is worth sitting with: two instances of the same component do not share state, exactly as two instances of the same Blueprint have their own independent property values, even though they share the same underlying design.

### What a "render" actually is

This is worth being extremely precise about, because "re-render" gets thrown around loosely elsewhere and it's easy to import a vague, wrong mental model from it.

**A render is React calling your component function, from the top, and getting back a new description of what the UI should look like** — the exact plain-object tree Lesson 01 showed JSX compiling down to. That's the entire definition. It is *not* "the browser redraws the screen" (that's a separate, later step, and often doesn't even happen if nothing actually changed) — it's specifically "your function, the one you wrote (`Counter`, `Greeting`, `App`), gets called again, and whatever it returns this time is the new description."

**What specifically triggers a render:**
- **Calling a state setter** (`setCount(...)`) on a component that's currently on screen. This is the one you've now seen directly.
- **A parent re-rendering.** When a component re-renders, React re-renders its children too by default — if `App` re-renders, every component `App` returns (directly or indirectly) gets called again too, whether or not *their* own props actually changed. (There are ways to avoid this for performance in bigger apps, not needed yet — filed away for later.)
- **Props changing.** If a parent passes a *different* prop value down (say, `App`'s own state changed and it now passes `priority="low"` instead of `"high""` to a child), that child re-renders with the new prop — though notice this is really a special case of the previous bullet: the parent re-rendered (because *its* state changed), and re-rendering it re-renders its children, one of which happens to now receive a different prop value.

### The Virtual DOM and reconciliation — what happens after a render

Here's the part the master plan insists on being minute about, because "React only updates what changed" sounds like magic until you see the actual two-step process underneath.

Recall from Module 03: the **real DOM** is the browser's own live representation of your page — actual objects, created with things like `document.createElement`, that carry an enormous amount of machinery with them (layout calculation, paint, accessibility tree entries, event listener wiring, and much more). Touching the real DOM — even just changing one element's text — is comparatively **expensive**: the browser has to potentially recalculate layout for surrounding elements, repaint pixels, and more, depending on what changed. This is exactly why, in Module 03's DOM exercise, doing that carefully and only where truly needed was your job in the first place.

React does not touch the real DOM directly every time your component function runs. Instead:

1. **Every render produces a Virtual DOM tree** — a plain, lightweight JavaScript object tree (exactly the `{ type: ..., props: ... }`-shaped objects from Lesson 01's "opening the hood" section), describing what the UI *should* look like right now. Creating and comparing plain JS objects in memory is comparatively very cheap — nothing here has touched the browser's actual page yet.
2. **Reconciliation**: React compares this new Virtual DOM tree against the previous one (the tree from the last time this part of the UI rendered), element by element, and computes the **minimal set of actual changes** needed to make the real DOM match the new description — "this text node's content needs to change from '0' to '1'," for instance, and nothing else, if that's genuinely the only difference.
3. Only *that* minimal set of changes gets applied to the real, expensive-to-touch DOM. Everything in the new Virtual DOM tree that's identical to the previous one is left completely alone.

The reason this two-step "diff in cheap memory first, then patch only what's different in the expensive real DOM" approach exists is almost exactly the same reasoning behind a rendering engine only redrawing the specific "dirty" regions of a screen that actually changed this frame, instead of blindly re-rendering every pixel of every object from scratch every single frame regardless of whether it moved. A naive render loop that repaints everything every frame works, but wastes enormous effort repainting things that didn't change; React's reconciliation is that same optimization, applied to a UI tree instead of a framebuffer — recompute the cheap in-memory description every time (that part *is* "redraw everything" from your code's point of view — your whole component function reruns), but only ever spend the expensive real-DOM-touching work on the parts that reconciliation actually found to be different.

This is also, concretely, *why* `Counter`'s button click only updates the number's text and nothing else on the page, even though `Counter` returned a whole new description of a `<button>` from scratch: reconciliation compared the new description to the old one, found that only the text content inside differed, and touched only that one real text node.

### The trap: state doesn't update *inside the same render* that scheduled it

This is the single most common beginner surprise with `useState`, and it's worth seeing broken before it makes sense:

```tsx
function Counter() {
  const [count, setCount] = useState(0);

  function handleClick() {
    setCount(count + 1);
    console.log(count); // <-- what does this print?
  }

  return <button onClick={handleClick}>Count: {count}</button>;
}
```

Click the button once, starting from `count = 0`. **Expected (and genuinely correct) output in the console:** `0` — **not** `1`.

Here's exactly why, and it directly uses the closure concept from Module 01, Lesson 02: every time `Counter` renders, React calls the `Counter` function fresh, and everything inside that one function call — including `count`, and including the `handleClick` function itself — is a **closure** over the values `count` had *at the moment this particular render started*. `count` inside this specific call to `handleClick` is a fixed, frozen snapshot — literally `0` — for the entire rest of that function call, no matter what happens afterward. Calling `setCount(count + 1)` does not reach back in time and change that snapshot; it only tells React "please schedule a new render, and when it happens, start that new render's `count` at `1`." The `console.log(count)` line, still running inside the *current, already-in-progress* render's `handleClick`, has no way to see a value that won't exist until the *next* render even begins.

This is exactly the same idea as a closure "remembering" the variables from its enclosing scope at the time it was created, which Module 01, Lesson 02 defined for Python — here it's a JavaScript function (`handleClick`) closing over a JavaScript variable (`count`), captured fresh on every render. Click the button a second time, and you're now inside an entirely new render, with a brand-new `handleClick` closing over a brand-new `count` — which now really does start at `1` — and *that* click's `console.log` will correctly print `1`, then `2` on the third click, and so on: always one render "behind" the value you just set, because it's reporting the snapshot it captured at the start of its own render, not the future one you just scheduled.

**Try it yourself:** change the log line to `console.log("count will become", count + 1)` and predict what it prints on the first click before checking. **Expected:** `count will become 1` — because `count + 1` is computed *right now*, from the correct current snapshot (`0`), the same computation `setCount` itself was handed; there's nothing wrong with reading `count` itself mid-render, only with expecting `count` to have already become the *new* value before the next render has happened.

### Updating an array of objects in state without mutating it

Most real state isn't a single number — QuestLog's real state is an array of quest objects. Here's a small, standalone version of exactly the pattern the capstone's `toggleDone` function uses:

```tsx
// src/components/MiniQuestList.tsx
import { useState } from "react";

interface MiniQuest {
  id: string;
  title: string;
  done: boolean;
}

const initialQuests: MiniQuest[] = [
  { id: "1", title: "Slay the Dragon", done: false },
  { id: "2", title: "Gather Herbs", done: true },
];

export function MiniQuestList() {
  const [quests, setQuests] = useState<MiniQuest[]>(initialQuests);

  function handleToggle(id: string) {
    setQuests((current) =>
      current.map((quest) =>
        quest.id === id ? { ...quest, done: !quest.done } : quest
      )
    );
  }

  return (
    <ul>
      {quests.map((quest) => (
        <li key={quest.id}>
          <label>
            <input
              type="checkbox"
              checked={quest.done}
              onChange={() => handleToggle(quest.id)}
            />
            {quest.title}
          </label>
        </li>
      ))}
    </ul>
  );
}
```

**Line by line, focusing on the new pieces:** `useState<MiniQuest[]>(initialQuests)` — the `<MiniQuest[]>` is an explicit type argument (TypeScript can usually infer this from `initialQuests`, but it's shown here to be unambiguous): this state is, and will only ever be, an array of `MiniQuest` objects. `function handleToggle(id: string) { setQuests((current) => ...); }` — instead of handing `setQuests` a brand-new array value directly, this hands it a **function**, called an updater function, which React calls with the current state (`current`) as its argument, and whose return value becomes the new state. This form matters here because reading `quests` directly from the outer closure (exactly like the `count` snapshot problem above) could be stale if multiple updates happened in quick succession; the updater form always receives the true, latest value at the moment React actually applies it.

`current.map((quest) => quest.id === id ? { ...quest, done: !quest.done } : quest)` — this is the core of the pattern, worth reading very slowly:
- `.map(...)` (Module 01's comprehension-adjacent concept, JavaScript's array-transforming method) builds and returns a **brand new array**, the same length as `current`, by running this function on every element.
- For the one quest whose `id` matches, it returns `{ ...quest, done: !quest.done }` — a **new object**, created by spreading (`...quest`, Module 03, Lesson 08) every existing field of the old quest into a new object literal, then overwriting just `done` with its flipped value.
- For every other quest, it returns `quest` completely unchanged — the exact same object reference as before.
- The result: a new array, containing one new object (the toggled quest) and several old, untouched object references (everything else).

**Why not just mutate the original**, e.g. `quest.done = !quest.done; setQuests(quests);`? Two concrete reasons, both worth understanding rather than memorizing:
1. **React wouldn't necessarily notice the change even if it worked.** If you handed `setQuests` back the exact same array reference you started with (because you mutated it in place instead of creating a new one), some of React's own internal bail-out checks compare old and new state by reference — and in some situations, would conclude "this is the same array as before, nothing to do," skipping the re-render you wanted, even though the contents changed underneath.
2. **It quietly breaks reconciliation's assumptions.** Reconciliation (covered above) works by comparing a new Virtual DOM tree against a snapshot of the previous one — and that comparison, at every level, leans on being able to tell "is this the same object as last time, or a different one?" by reference. Handing React data you've mutated in place muddies exactly the distinction reconciliation depends on to know what genuinely changed.

The fix, universally, is: **never mutate state directly — always produce and set a brand-new value** (a new array from `.map()`/`.filter()`/spread, a new object from `{ ...old, changed: newValue }`), even when only one small piece of it actually changed. `key={quest.id}` on the `<li>` (Module 03 never needed this — it's new here) is a related idea worth flagging now and returning to properly in a later lesson: it's how React tells *which* item in a list is which, across renders, so reconciliation can match old list items to new ones correctly instead of guessing by position.

**Try it yourself:** temporarily change `handleToggle` to mutate directly — `const quest = current.find(q => q.id === id); quest!.done = !quest!.done; return current;` — and click a checkbox. Predict what you'll see before running. **Expected:** the checkbox visually appears not to update at all (or updates inconsistently), even though the underlying data really did change — a direct, hands-on demonstration of the bail-out problem described above. Revert back to the `.map()` version afterward.

### Multiple state variables vs. one state object

You can call `useState` as many times as you need inside one component:

```tsx
const [title, setTitle] = useState("");
const [priority, setPriority] = useState<Priority>("medium");
```

...or group related fields into a single state object:

```tsx
const [form, setForm] = useState({ title: "", priority: "medium" as Priority });
// updating one field still means spreading the rest:
setForm((current) => ({ ...current, title: "New title" }));
```

Both are legitimate; this course generally reaches for separate variables when fields are genuinely independent (a `loading` flag and a list of items rarely need to change together), and a single object when fields are always edited and read together as one logical unit — you'll see the single-object form again when this module covers forms in depth. Neither choice affects anything this lesson taught about renders or reconciliation — it's purely about what's easier to read and update correctly in your own code.

## Common mistakes & gotchas

- **Expecting a variable read right after a setter call to reflect the new value.** Covered in full above — the fix is either computing the value you need directly (`count + 1`, not `count` after calling `setCount`), or using a `useEffect` (Lesson 03) to react to the value *after* the next render actually happens.
- **Mutating state directly** — `quests.push(newQuest)`, `quest.done = true`, `array[0] = x` — instead of producing a new array/object and calling the setter with it. This is the single most common real bug in early React code, and it often *appears* to half-work (the data really did change in memory) while the UI stubbornly doesn't reflect it, which is a uniquely confusing failure mode the first time you hit it.
- **Calling `useState` conditionally, or inside a loop/`if`.** Hooks (of which `useState` is the first you've met) must always be called in the exact same order on every single render of a given component — React tracks *which* state belongs to *which* `useState` call by the order they're called in, not by name. Wrapping `useState(...)` in an `if` is invalid and React will warn/error about it loudly; if you need conditional behavior, put the condition *inside* the component (after all hooks are called), never around a hook call itself.
- **Forgetting that two instances of the same component have independent state.** Demonstrated in this lesson's first "Try it yourself" — a very common source of "why isn't my other counter updating too?" confusion early on.
- **Assuming a render means "the browser repainted the screen."** A render is your function being called again and a new description being produced; reconciliation may well conclude nothing real-DOM-visible actually needs to change, in which case the browser paints nothing new at all, even though your component genuinely re-rendered.

## How this connects

You now have the full local picture: components describe UI (Lesson 01), props configure a component from outside, and state is what a component owns and can change from the inside, with React handling the "notice the change, update the UI" step automatically via the render → Virtual DOM → reconciliation → real-DOM-patch pipeline this lesson walked through in detail. The closure-based "stale snapshot" idea you just saw with `count` is exactly the same mechanism — a function remembering the values from its enclosing scope at creation time — that Module 01, Lesson 02 introduced for Python, now doing real work in a language you're using every day. State changing is very often the moment you need to reach *outside* React's own rendering to do something in the real world — fetch fresh data when a filter changes, start a timer, subscribe to something — and React deliberately does not let you do that directly inside a component's render body. That controlled "do this extra thing, but only after rendering, and only when specific things changed" mechanism is `useEffect`, and it's the entirety of Lesson 03 — in extreme detail, because it is the single easiest hook in this module to get subtly wrong.

## Quick self-check

1. Why doesn't reassigning a plain `let` variable inside a component cause the UI to update, even though the variable's actual value really did change?
2. Precisely define what a "render" is in React. Is "the browser repaints the page" part of that definition?
3. What is the Virtual DOM, in plain terms, and why does React compare two Virtual DOM trees before touching the real DOM at all, instead of just re-creating the whole real DOM from scratch on every render?
4. Given `setCount(count + 1); console.log(count);`, explain — using the word "closure" correctly — exactly why the `console.log` still shows the old value.
5. Why does `quests.map(q => q.id === id ? { ...q, done: !q.done } : q)` return a brand-new array instead of modifying `quests` in place, and what specifically goes wrong if you mutate the array/object directly instead?
