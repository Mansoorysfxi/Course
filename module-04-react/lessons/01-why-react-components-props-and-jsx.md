# Lesson 01 — Why React, Components, Props, and JSX

## What you'll learn

- The specific, concrete pain that shows up once a hand-built, vanilla-JS app grows past a handful of interactive elements — the exact pain React exists to remove.
- What a **component** actually is: not a UI widget in the abstract, but a specific kind of JavaScript/TypeScript function.
- What a **prop** is, why it's read-only from the receiving component's side, and why that restriction is a feature, not a limitation.
- What **JSX** really is under the hood — it is not HTML, and this lesson opens the hood on exactly what it compiles down to.
- How to build a component from zero props, to one prop, to multiple typed props described with a TypeScript `interface`.
- How to scaffold, write, and run your first real React component, end to end, in the browser.

## Why this matters

Every single thing this module teaches from here on — state, hooks, forms, routing, data fetching — is something you attach *to* a component, written *in* JSX, configured *with* props. If any one of those three ideas is fuzzy, everything downstream feels like memorized incantations instead of a system you understand. This lesson exists so that by the end of it, a file full of `<QuestCard title="..." priority="high" />`-shaped code reads as plain, explainable function calls — because that is exactly what it is.

## Prerequisites

**Lesson 00** in full — you need a scaffolded Vite + React + TypeScript project (this lesson's examples assume you can run `npm create vite@latest ... -- --template react-ts`, `npm install`, and `npm run dev` and get a working dev server, exactly as Lesson 00 walked through). **Module 03, Lesson 06** (the DOM and events) — this lesson's opening section refers directly to the `03-dom-manipulation-and-events` exercise you already completed; if the details of `querySelector`, `addEventListener`, and `textContent` are fuzzy, a quick re-read of that lesson will make this one land harder. **Module 03, Lesson 09** (TypeScript introduction) — you'll need `interface` again here, exactly as you used it there.

## The concept, explained simply

Think back to Module 03's DOM manipulation exercise. You had a page with, say, a list of items, an "add" button, and a few filters. To make any of it work, you had to: `querySelector` the specific elements you cared about, `addEventListener` on the button, and inside that handler, manually figure out which piece of the page needed to change and update it yourself — `element.textContent = ...`, `element.classList.toggle(...)`, maybe building a whole new `<li>` with `document.createElement` and `appendChild`-ing it into the list. You, the programmer, were the thing keeping the page's *displayed* state in sync with your *data*. Every time the data changed, you had to remember every single place on the page that depended on that data and update each one by hand.

That's manageable for one list and one button. It stops being manageable once your app has a dozen pieces of data that all affect each other — a quest that's "done" needs its checkbox checked, its title struck through, its count in a filter dropdown updated, and maybe a "quests remaining" counter somewhere else, all from one click. Miss updating even one of those places and you get a bug where the screen is lying about the actual data — a checkbox says done, but the counter still thinks it isn't. This is not a hypothetical: it is *the* single most common category of real bug in hand-written interactive web pages, and it gets worse, not better, as an app grows. This bookkeeping burden — keeping a mental map of "if X changes, I must remember to update A, B, and C" — is exactly the pain React exists to remove.

React's whole pitch is: **you describe what the UI should look like for a given set of data, and React figures out what actually needs to change on the page and does it for you.** You stop manually pushing updates to specific elements. Instead, you write a description ("here's what a quest card looks like, given a quest") and hand React your data; React re-runs that description whenever the data changes and updates the real page to match. Lesson 02 covers exactly *how* React decides what changed and updates only that — for this lesson, the important shift is: you write descriptions, not step-by-step DOM instructions.

A **component** is the unit that description comes in. A component is simply **a JavaScript/TypeScript function that returns a description of some UI** — nothing more mystical than that. If you've built a reusable Widget Blueprint in Unreal — say, a health bar you can drop into any HUD, configure with a "max health" value, and instance as many times as you need — a component is that same idea, translated to a function: a self-contained, reusable *definition* of a piece of UI that you can call ("instance") as many times as you want, each time configured a little differently.

That configuration — the inputs you hand a component each time you use it, the same way you'd set exposed variables on a Blueprint instance in its construction script — is what React calls a **prop** (short for "property"). Props are just function parameters, given to the component from the outside, each time it's used.

## The details

### Step 0 — set up a place to work

Reuse the scaffold from Lesson 00, or create a fresh one for this lesson's practice:

```bash
npm create vite@latest react-practice -- --template react-ts
cd react-practice
npm install
npm run dev
```

Leave `npm run dev` running in one terminal for the rest of this lesson — Vite's Hot Module Replacement (Lesson 00) means every file you save below will show up in the browser at `http://localhost:5173/` automatically, no manual refresh needed.

### Step 1 — a component with zero props

Create a new file:

```tsx
// src/components/Greeting.tsx
export function Greeting() {
  return <h1>Hello, adventurer!</h1>;
}
```

**Line by line:** `export function Greeting() { ... }` — this is a completely ordinary, named JavaScript function, made available to other files with `export`. There is nothing React-specific about the word `function` or `export` here; the only unusual-looking part is what's inside the `return`. `return <h1>Hello, adventurer!</h1>;` — this is **JSX**, which this lesson opens the hood on fully in a moment; for now, read it as "this function returns a description of an `<h1>` element containing this text," not as literal HTML being handed to a browser.

By convention, a component's function name is capitalized (`Greeting`, not `greeting`) — this isn't cosmetic. JSX uses the capitalization to decide whether a tag refers to a plain HTML element (`<h1>`, `<div>`, lowercase, built into the browser) or a component you wrote (`<Greeting />`, capitalized, a function call in disguise). Naming your own component starting with a lowercase letter is a real bug: React/JSX will treat `<greeting />` as an attempt to render an unknown HTML tag, not a call to your function.

Now render it. Open `src/App.tsx` (already created by the Vite scaffold) and replace its contents:

```tsx
// src/App.tsx
import { Greeting } from "./components/Greeting";

function App() {
  return (
    <div>
      <Greeting />
    </div>
  );
}

export default App;
```

**Line by line:** `import { Greeting } from "./components/Greeting";` — an ordinary ES module import (Module 03, Lesson 08), pulling in the function you just wrote; note the file has no `.tsx` extension in the import path — Vite's tooling resolves that for you. `<Greeting />` — this is the component **instance**: exactly like dragging a Widget Blueprint into a HUD and it appearing on screen, writing `<Greeting />` anywhere inside another component's returned JSX causes React to call your `Greeting` function and slot whatever it returns into that spot in the page.

**Run it:** with `npm run dev` already running, save both files and look at `http://localhost:5173/` in your browser.

**Expected output:** the page shows, as its only content, the text **"Hello, adventurer!"** styled as a large heading (an `<h1>`'s default browser styling — no custom CSS has been added yet).

**Try it yourself:** add a second `<Greeting />` right below the first one inside `App.tsx`'s `<div>`. Predict what you'll see before saving. **Expected:** the exact same heading, twice — because `<Greeting />` is a function call, and calling the same function twice with the same (in this case, no) input produces the same result twice. This is the "instance a Blueprint twice" idea made concrete: one definition, called as many times as you like.

### Step 2 — add one prop

A component with zero props can only ever show one thing. Configure it like you'd configure a Blueprint instance's exposed variables — with a prop:

```tsx
// src/components/Greeting.tsx
interface GreetingProps {
  name: string;
}

export function Greeting({ name }: GreetingProps) {
  return <h1>Hello, {name}!</h1>;
}
```

**Line by line:** `interface GreetingProps { name: string; }` — exactly the same `interface` syntax you used in Module 03, Lesson 09 to describe an object's shape; here it describes the shape of the single argument every React component receives: an object holding all of its props. `export function Greeting({ name }: GreetingProps)` — this is a function with one parameter, an object, whose shape is annotated as `GreetingProps`; `{ name }` is ordinary JavaScript **destructuring** (Module 03, Lesson 08) pulling the `name` field straight out of that props object instead of writing `props.name` everywhere inside the function. `<h1>Hello, {name}!</h1>` — the curly braces `{ }` inside JSX are how you **embed a JavaScript expression** in otherwise-static markup; anything between `{` and `}` is evaluated as plain JS/TS, and its result is inserted into the output. `{name}` here means "put the actual value of the `name` variable here," not the literal five characters `n`, `a`, `m`, `e`.

Update `App.tsx` to pass the prop, and to try several instances with different values — exactly like configuring several instances of the same Blueprint differently:

```tsx
// src/App.tsx
import { Greeting } from "./components/Greeting";

function App() {
  return (
    <div>
      <Greeting name="Rowan" />
      <Greeting name="Mira" />
    </div>
  );
}

export default App;
```

**Line by line:** `<Greeting name="Rowan" />` — `name="Rowan"` is an **attribute-looking syntax that is actually how you pass a prop**; it's read as "call `Greeting` with a props object `{ name: "Rowan" }`." The second `<Greeting name="Mira" />` calls the exact same function again, with a different props object.

**Expected output:** two headings, "Hello, Rowan!" and "Hello, Mira!" — one component definition, two differently-configured instances, exactly like two Widget Blueprint instances with different exposed-variable values producing two different results from the same underlying design.

**Try it yourself:** delete the `name="Mira"` attribute from the second `<Greeting />` entirely (leave `<Greeting />` with no props at all) and predict the error before saving. **Expected:** TypeScript refuses to compile, with an error naming that `name` is missing — because `GreetingProps` declared `name: string` as required, with no `?`. This is the exact same "missing required field" checking Module 03, Lesson 09 showed you for a plain `interface`, now applied to a component's props.

### Step 3 — multiple, typed props (building toward the capstone's `QuestCard`)

Real components almost always need more than one prop. Here's a small, presentational "quest card" — deliberately similar to, but simpler than, the `QuestCard` component you'll build in this module's capstone later:

```tsx
// src/types/quest.ts
export type Priority = "low" | "medium" | "high";
```

**Line by line:** `export type Priority = "low" | "medium" | "high";` — a **union type** made of specific string literals, exactly as Module 03, Lesson 09 covered: `Priority` isn't "any string," it's exactly one of these three values, checked at compile time. This is the actual type QuestLog's real `Priority` type uses later in this module.

```tsx
// src/components/QuestCardLite.tsx
import type { Priority } from "../types/quest";

interface QuestCardLiteProps {
  title: string;
  priority: Priority;
}

export function QuestCardLite({ title, priority }: QuestCardLiteProps) {
  return (
    <div className="quest-card">
      <h2>{title}</h2>
      <span>Priority: {priority}</span>
    </div>
  );
}
```

**Line by line:** `import type { Priority } from "../types/quest";` — `import type` is a TypeScript-specific form of `import` that pulls in only a *type* (erased entirely at compile time, per Module 03, Lesson 09) rather than any actual runtime value; there is no JavaScript object called `Priority` to import, only a compile-time shape, so this form makes that explicit. `interface QuestCardLiteProps { title: string; priority: Priority; }` — two required props this time, one a plain `string`, one your own named union type. `className="quest-card"` — **this, not `class="quest-card"`, is how you set a CSS class in JSX**, and it's worth knowing exactly why: `class` is a **reserved word** in JavaScript — it's the actual keyword used to declare a JS class (`class Foo { ... }`) — so JSX cannot use the literal word `class` as a prop name without colliding with the language's own syntax. React instead uses `className`, matching the exact same name the real DOM's own JavaScript API already used for this (`element.className`, which you almost certainly touched in Module 03's DOM lesson) — so this isn't an arbitrary React invention, it's React reusing a name the DOM itself already had.

Render a few, with different data:

```tsx
// src/App.tsx
import { QuestCardLite } from "./components/QuestCardLite";

function App() {
  return (
    <div>
      <QuestCardLite title="Slay the Dragon" priority="high" />
      <QuestCardLite title="Gather Herbs" priority="low" />
    </div>
  );
}

export default App;
```

**Expected output:** two stacked blocks, each with a bold-ish heading (an `<h2>`'s default styling) and a "Priority: high"/"Priority: low" line beneath it.

**Try it yourself:** change one instance's `priority="high"` to `priority="urgent"` and predict what `tsc`/your editor does before saving. **Expected:** a compile error — `"urgent"` isn't one of `Priority`'s three allowed literal strings, exactly the same kind of check Module 03, Lesson 09 demonstrated for `status: "open" | "closed"`. This is a bug a plain JavaScript version of this component would never have caught until it silently rendered "Priority: urgent" in production.

### Props are read-only — and why

Inside `QuestCardLite`, `title` and `priority` are ordinary local variables (destructured out of the props object) — but React's rule, enforced by convention and by React itself refusing to make this work sensibly, is: **a component must never reassign or mutate the props it receives.** Writing `priority = "high";` (an outright reassignment) inside `QuestCardLite`'s body wouldn't even do anything useful — it would only change QuestCardLite's own local copy of that variable for the rest of *this* function call; the parent (`App`, here) that actually owns and passed in `priority` would never see or know about the change, and the very next render would hand `QuestCardLite` the real, original value again as if nothing happened.

This is precisely the same discipline as a well-written function in any language not mutating its own arguments behind the caller's back: a caller passing a value into a function reasonably expects that value to still mean what it meant *after* the call, unless the function's contract explicitly says otherwise. React leans on this rule hard — every part of how React decides what to re-render (Lesson 02) assumes a parent component is the single source of truth for what it hands down, and a child silently mutating that would make it impossible for React (or you, reading the code later) to reason about where a given value actually came from. If a piece of data needs to change over time from *inside* a component, that's not a job for a prop — that's exactly the job of **state**, which is where Lesson 02 picks up.

### Opening the hood: what JSX actually compiles to

Here is the fact worth sitting with for the rest of this module: **JSX is not HTML.** It looks like HTML on purpose, so it's readable, but it is a syntax extension to JavaScript/TypeScript that a build tool (here, Vite's React plugin, already wired into `vite.config.ts` since Lesson 00) transforms into **plain function calls** before your code ever reaches a browser. No browser anywhere understands JSX natively — by the time your code runs, JSX is gone.

Take this line from `Greeting.tsx`:

```tsx
<h1>Hello, {name}!</h1>
```

Historically (and still conceptually accurate today), JSX like this compiles down to a call to React's own `createElement` function:

```js
React.createElement("h1", null, "Hello, ", name, "!")
```

The exact call your tooling emits today looks slightly different — React 19.2.8, via Vite's React plugin, uses what's called the "automatic" JSX runtime, which compiles the same line to a call to a function named `jsx` (or `jsxs` for elements with multiple children), auto-imported from a package called `react/jsx-runtime` that you never write or see yourself:

```js
import { jsx as _jsx } from "react/jsx-runtime";
_jsx("h1", { children: ["Hello, ", name, "!"] })
```

The exact function name and argument shape changed between React versions; the essential fact did not: **JSX compiles to an ordinary JavaScript function call**, passed a description of what to render — a tag or component, its props, and its children — and that call **returns a plain JavaScript object**, not a real DOM node. Something roughly shaped like:

```js
{ type: "h1", props: { children: ["Hello, ", name, "!"] } }
```

This lightweight object — a description of "an `<h1>` should exist here, with this content," not an actual browser element — is what people mean when they say a React element, and it's the raw material Lesson 02's Virtual DOM and reconciliation process is built from. Nothing about `<Greeting name="Rowan" />` calling your `Greeting` function, or that function's `<h1>` calling `React.createElement`/`jsx` under the hood, involves any magic beyond "JSX is sugar for function calls that build a description object" — the same category of "opening the hood" you did in Module 03, Lesson 09 for `tsc` erasing type annotations.

### JSX syntax rules worth knowing now

A handful of JSX-specific rules will otherwise cost you a confusing error the first time you hit them:

- **Self-closing tags are mandatory when there's no children.** `<Greeting />` (with the trailing `/>`) — not `<Greeting>` left unclosed. Unlike HTML, where a browser will forgivingly guess what you meant with a stray unclosed tag, JSX is compiled, and an unclosed tag with no matching close is a compile error, full stop.
- **A component must return exactly one root element.** `return <h1>A</h1><p>B</p>;` is a compile error ("JSX expressions must have one parent element") — two sibling elements with nothing wrapping them isn't a single description JSX/`createElement` can represent in one call. Wrap them: `return <div><h1>A</h1><p>B</p></div>;`.
- **If you don't want an extra wrapping `<div>` in your actual page** (say, because it would break a CSS layout expecting specific siblings), use a **Fragment** — `<>` and `</>` — which groups multiple elements into one return value without adding any real element to the page at all: `return <><h1>A</h1><p>B</p></>;`.
- **`{}` embeds *any* JavaScript expression**, not just variables — `{name.toUpperCase()}`, `{1 + 1}`, `{someCondition ? "Yes" : "No"}` are all valid. It cannot embed a *statement* (an `if` block, a `for` loop) directly — only expressions that produce a value. This exact limitation is why you'll see conditional rendering written with the ternary operator (`? :`) or `&&` rather than an `if` statement inline in JSX — a pattern later lessons use often.

## Common mistakes & gotchas

- **Using `class` instead of `className`.** The browser's console/TypeScript won't always shout loudly about this the way a missing prop does — a stray `class="..."` attribute is technically valid JSX (React just silently passes it through as an unrecognized DOM attribute in some cases, or your editor flags it) but the styling described by that class will not reliably apply the way `className` does. Get in the habit now: it's always `className` in JSX.
- **Forgetting to wrap multiple sibling elements in one root element or Fragment.** The error message — "JSX expressions must have one parent element" — is exact and points straight at the fix.
- **Naming your own component starting with a lowercase letter.** `<questCard />` is parsed as an attempt to render an unknown lowercase HTML tag, not a call to your function — the bug here is silent-ish (React/your browser won't render your intended content, and you'll get a confusing "does not exist" or nothing-rendered-here result) rather than a loud compile error. Always capitalize component names.
- **Trying to mutate a prop and expecting the parent to notice.** As covered above: reassigning a destructured prop only changes a local copy for the rest of that one function call; it does not, and cannot, flow back up to whoever passed the prop in. If you find yourself wanting to do this, you almost always actually want state (Lesson 02).
- **Passing the wrong type to a prop and not noticing until it renders oddly.** `<QuestCardLite title={42} priority="high" />` (a number where `title: string` was declared) is a compile error, not a silent bug — this is one of TypeScript's most direct payoffs in a component-heavy codebase: a typo'd or wrong-shaped prop is caught before you ever look at the browser, exactly as Module 03, Lesson 09 argued in the abstract.

## How this connects

You now have the three ideas everything else in this module is built from: components (functions returning UI descriptions), props (read-only configuration passed in from outside, exactly like a Blueprint's exposed construction-script variables), and JSX (sugar for plain function calls producing description objects — not HTML). This directly automates the exact bookkeeping you did by hand in Module 03's DOM manipulation exercise — instead of you tracking "if this data changes, remember to update these three DOM spots," you'll write one description, and Lesson 02 explains precisely how React decides what changed and updates only that. The one thing missing so far is data that changes *from inside* a component over time, in response to something like a click — props alone can't do that, since they only ever come from outside. That's **state**, and it's the entirety of Lesson 02.

## Quick self-check

1. In your own words, using the `03-dom-manipulation-and-events` exercise as the example: what specific bookkeeping burden grows as a hand-written vanilla-JS app adds more interactive pieces, and what does React do differently that removes it?
2. What is a prop, in terms of an ordinary JavaScript function — and what's the single closest Unreal/Blueprint concept to compare it to?
3. Why can't a component reassign a prop it receives and expect the change to be visible to its parent?
4. `<h1>Hello, {name}!</h1>` is JSX. What does this actually compile to, and what kind of object does that compiled call return — is it a real DOM node?
5. Why does JSX use `className` instead of `class`, specifically — what would go wrong with `class` if JSX allowed it directly?
