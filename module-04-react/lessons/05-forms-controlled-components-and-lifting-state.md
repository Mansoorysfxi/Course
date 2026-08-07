# Lesson 05 — Forms, Controlled Components, and Lifting State Up

## What you'll learn

- What a **controlled component** is: an input whose current value lives in React state, not in the browser's own hidden internal state.
- What an **uncontrolled component** is, by contrast, and why you'd deliberately choose one over the other.
- How to build a multi-field form the React way, one field at a time, ending in the same shape as this module's real `QuestForm.tsx`.
- Why `event.preventDefault()` is still needed on a form submission inside React, even though it's the exact same DOM API you already used in Module 03.
- **Lifting state up**: the specific pattern for letting two components that don't otherwise talk to each other share and coordinate a single piece of state.
- Why a form component is often better off *not* deciding what happens when it's submitted — and how to hand that decision to its parent instead.

## Why this matters

Every real app has forms — QuestLog's "add a quest" and "edit a quest" screens are both, at their core, a form. Doing forms "the React way" (controlled components) is what lets you validate input as the user types, disable a submit button until a field is filled in, reset a field programmatically, or show a live character count — none of which a plain, un-managed HTML input lets you do without manually reaching into the DOM, the exact way Module 03 taught before React existed. Lifting state up matters for a broader reason: it's the first, simplest answer to "how do two components share data," and it's deliberately the *default* answer you should reach for before anything fancier — Lesson 06 (Context) exists specifically for the cases where lifting state up alone stops being practical, and you can't appreciate why Context exists until you've felt lifting state's own limits first.

## Prerequisites

Lesson 02 (state and re-rendering) — this lesson assumes you're comfortable with `useState` and calling a setter to update a value. Lesson 01 (components, props, and JSX) — you already know a component receives data via props and that a function passed as a prop is just a value like any other. Module 03, Lesson 01 (HTML structure, forms, and accessibility) — you already know what a `<form>`, `<label>`, `<input>`, and `<select>` are and why `<label htmlFor="...">` pairs with an input's `id`; this lesson doesn't re-teach any of that. Module 03, Lesson 06 (the DOM and events) — you already know what `event.preventDefault()` does and when you need it for a plain HTML form; this lesson uses the exact same method, just inside a React event handler.

## The concept, explained simply

Think about a completely plain HTML `<input>`, with no React involved at all, the way Module 03 taught it: the browser itself keeps track of whatever the user has typed into it. If you want to know what's currently in the box, you go ask the DOM element directly — `document.querySelector("#title").value` — the way Module 03, Lesson 06 taught. The input manages its own value internally; your JavaScript is a visitor that can peek at it or set it, but the *source of truth* for "what's really in this field right now" lives inside the browser's own DOM node, not in any variable you wrote.

A **controlled component** flips that arrangement around entirely: the input's current value lives in **React state** — a `useState` variable your component owns — and the input is wired up so that (a) its displayed value always comes from that state (`value={someState}`) and (b) every keystroke immediately updates that same state (`onChange={e => setSomeState(e.target.value)}`). The input itself becomes, in a real sense, just a visual mirror of a value React already has — React is now the single source of truth for "what's really in this field," not the DOM node.

An **uncontrolled component**, by contrast, is the plain-HTML-style input: it manages its own value internally, the React way of even acknowledging it exists (if you need to at all) is a `ref` (Lesson 04) pointed at the real DOM node, read only when you actually need it — e.g., at the moment of form submission — rather than tracked on every keystroke. Lesson 04's `AutoFocusInput` example used an uncontrolled input (with `defaultValue` instead of `value`) precisely because that example only needed to *focus* the input, never to track or react to its value.

Why prefer controlled? Because once React state is holding the "real" value of a field, you can do things a plain uncontrolled input structurally cannot support without you writing manual DOM-reading code:

- **Validate or transform on every keystroke** — e.g., strip whitespace, enforce a max length, or reject non-numeric characters, live, as the user types.
- **React to every keystroke elsewhere in the UI** — e.g., a live character counter or a "this quest line already exists" warning that updates as you type, not just at submit time.
- **Let some *other* part of the UI read or reset the field's value programmatically** — e.g., a "clear form" button that resets every field to empty by just calling `setValues(emptyValues)`, with no DOM lookups involved at all.

## The details

### One controlled input

```tsx
// src/QuestTitleInput.tsx
import { useState } from "react";

export function QuestTitleInput() {
  const [title, setTitle] = useState("");

  return (
    <div>
      <label htmlFor="title">Quest title</label>
      <input
        id="title"
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <p>You've typed: {title}</p>
    </div>
  );
}
```

**Line by line:**

- `const [title, setTitle] = useState("");` — plain state, starting as an empty string. This is the single source of truth this input will mirror.
- `<label htmlFor="title">Quest title</label>` — exactly the accessible label/input pairing Module 03, Lesson 01 taught; nothing about controlled components changes accessibility requirements.
- `value={title}` — this is the "controlled" half of the wiring. The input's displayed text is *always* set to whatever `title` currently is. Try to type into this input with only this line (no `onChange`) and you'd find you *can't* — every keystroke would render the input back to showing `title` (still `""`), because nothing is updating `title` when you type. React actually warns about exactly this in the console if you forget `onChange`: `Warning: You provided a 'value' prop to a form field without an 'onChange' handler.`
- `onChange={(e) => setTitle(e.target.value)}` — the other half. `onChange` fires on every keystroke (technically, on every change to the input's value — familiar from Module 03, Lesson 06's event-handling vocabulary, just written as a JSX prop instead of `addEventListener`). `e.target` is the real DOM `<input>` element the event happened on, and `.value` is its current text — reading `e.target.value` here is the *one* place this component still reaches into the DOM directly, and it's reading the value the browser just updated a split second before this handler ran, not writing it. `setTitle(e.target.value)` takes that fresh value and stores it in React state, which schedules a re-render — and that re-render is what feeds the new value right back into `value={title}` above, completing the loop. This "type a key → onChange fires → state updates → re-render → value prop reflects the new state" cycle happens on every single keystroke, and it's fast enough that it feels completely instant to the user.
- `<p>You've typed: {title}</p>` — proof that some *other* part of the UI can read this same state live, on every keystroke, with zero DOM queries — exactly the kind of thing an uncontrolled input can't offer without manual work.

**Try it yourself:** add a line above the input showing `title.length`, live, as a character count (e.g. `<p>{title.length} / 40 characters</p>`), and then add a check inside `onChange` that refuses to update state if the new value is longer than 40 characters (`if (e.target.value.length <= 40) setTitle(e.target.value);`). Notice the input itself now visibly stops accepting new characters past the limit — proof that React state, not the browser, is genuinely deciding what the field's value is allowed to be.

### Building a multi-field form, one field at a time

A form with several fields doesn't need several separate `useState` calls — it's usually cleaner to hold all of a form's fields in **one object**, mirroring the real `QuestForm.tsx`'s approach. Build it up incrementally.

**Step 1 — two fields:**

```tsx
// src/QuestFormStep1.tsx
import { useState } from "react";

interface QuestDraft {
  title: string;
  description: string;
}

export function QuestFormStep1() {
  const [values, setValues] = useState<QuestDraft>({ title: "", description: "" });

  return (
    <form>
      <div>
        <label htmlFor="title">Title</label>
        <input
          id="title"
          type="text"
          value={values.title}
          onChange={(e) => setValues({ ...values, title: e.target.value })}
        />
      </div>
      <div>
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          value={values.description}
          onChange={(e) => setValues({ ...values, description: e.target.value })}
        />
      </div>
    </form>
  );
}
```

**Line by line — the one genuinely new idea here:** `setValues({ ...values, title: e.target.value })`. Recall the spread operator (`...`) from Module 03, Lesson 08: `{ ...values, title: e.target.value }` builds a **brand-new object** that copies every property from `values`, then overwrites `title` specifically with the input's new value — `description` comes along unchanged because the spread copied it first. This matters for a genuinely important reason, not just style: React state must always be updated by *replacing* it with a new value, never by mutating the old one in place (e.g. `values.title = e.target.value; setValues(values);` looks like it should work, and often visibly doesn't, or works by accident today and breaks later — React compares state by reference to decide whether a re-render is needed, and handing back the *same* object reference it already had, even with a mutated property inside it, can cause React to skip the re-render entirely). Each field's `onChange` in this pattern spreads the *whole* current object and overwrites just its one field.

**Step 2 — add priority (a `<select>`) and questLine, matching the real `QuestForm.tsx`'s exact four fields:**

```tsx
// src/QuestFormStep2.tsx
import { useState } from "react";

type Priority = "low" | "medium" | "high";

interface QuestDraft {
  title: string;
  description: string;
  priority: Priority;
  questLine: string;
}

const emptyDraft: QuestDraft = { title: "", description: "", priority: "medium", questLine: "" };

export function QuestFormStep2() {
  const [values, setValues] = useState<QuestDraft>(emptyDraft);

  return (
    <form>
      <div>
        <label htmlFor="title">Title</label>
        <input
          id="title"
          type="text"
          value={values.title}
          onChange={(e) => setValues({ ...values, title: e.target.value })}
        />
      </div>
      <div>
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          value={values.description}
          onChange={(e) => setValues({ ...values, description: e.target.value })}
        />
      </div>
      <div>
        <label htmlFor="priority">Priority</label>
        <select
          id="priority"
          value={values.priority}
          onChange={(e) => setValues({ ...values, priority: e.target.value as Priority })}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>
      <div>
        <label htmlFor="questLine">Quest line</label>
        <input
          id="questLine"
          type="text"
          value={values.questLine}
          onChange={(e) => setValues({ ...values, questLine: e.target.value })}
        />
      </div>
    </form>
  );
}
```

**What's new here:** a `<select>` is controlled exactly like an `<input>` — `value={values.priority}` and `onChange` — even though visually it's a dropdown, not a text box; React treats every form element (`input`, `textarea`, `select`) through the same controlled pattern. `e.target.value as Priority` uses a **type assertion** (Module 03, Lesson 09's term) because `e.target.value` is always typed as a plain `string` (every DOM value is text — recall Module 03, Lesson 09's ISO-date-string discussion), but you, the developer, know this particular `<select>`'s `<option>` values are constrained to exactly `"low" | "medium" | "high"`, so you assert that narrower type rather than widening `priority`'s own type to a plain `string`.

**Try it yourself:** compare this component field-by-field against the real `project/questlog/src/components/QuestForm.tsx` — it's the same four fields (`title`, `description`, `priority`, `questLine`), the same spread-based `onChange` pattern, just without the `required` attributes, styling classes, and the `PRIORITIES` array-driven `<option>` list the real file uses to avoid hardcoding three `<option>` tags by hand. Try rewriting your `<select>`'s options using a `.map()` over `["low", "medium", "high"] as const` the way the real file does over its `PRIORITIES` constant.

### Submitting the form: `event.preventDefault()`, again

```tsx
// src/QuestFormStep3.tsx (continuing from Step 2's state)
import { type FormEvent } from "react";

function handleSubmit(event: FormEvent<HTMLFormElement>) {
  event.preventDefault();
  console.log("Submitting:", /* values */ "...");
}

// <form onSubmit={handleSubmit}> ... </form>
```

**Line by line:** `FormEvent<HTMLFormElement>` is React's typed wrapper around a form submission event — the generic `<HTMLFormElement>` (Module 03, Lesson 09's generic-type vocabulary) tells TypeScript specifically which kind of DOM element this event came from, the same way `Promise<number>` told TypeScript what a Promise would eventually resolve to. `event.preventDefault()` is **the exact same DOM API Module 03, Lesson 06 already taught you** for plain HTML forms — nothing new about the method itself. What *is* worth re-stating precisely: a `<form>`'s default browser behavior, with or without React anywhere in the picture, is to perform a full page navigation/reload and submit its fields as a traditional HTTP request the instant its submit button is clicked or Enter is pressed inside a text field — a behavior that predates JavaScript entirely and has nothing to do with React. Skip `event.preventDefault()` in a React app and the browser will still try to do that full-page reload, wiping out your entire React application (all its state, instantly gone) and, on QuestLog specifically, attempting to navigate to a URL that doesn't correspond to any real backend endpoint at all yet. You call `preventDefault()` inside `onSubmit` for exactly the same reason, and via exactly the same method call, you would have inside a plain `addEventListener("submit", ...)` handler in Module 03 — React changes *where* you attach the handler (a JSX prop instead of `addEventListener`), not what the handler needs to do once it runs.

### Lifting state up: sharing state between siblings

Now for a different problem. Imagine two sibling components — components with a shared parent, but no direct relationship to each other — that each need access to the *same* piece of data. Here's a concrete before/after.

**Before — broken, because each component owns its own separate state:**

```tsx
// src/QuestLineFilterBroken.tsx
import { useState } from "react";

function FilterControl() {
  const [selectedLine, setSelectedLine] = useState("all");
  return (
    <select value={selectedLine} onChange={(e) => setSelectedLine(e.target.value)}>
      <option value="all">All quest lines</option>
      <option value="Main Story">Main Story</option>
    </select>
  );
}

function FilterSummary() {
  const [selectedLine] = useState("all"); // this is a SEPARATE piece of state!
  return <p>Currently showing: {selectedLine}</p>;
}

export function QuestLineFilterBroken() {
  return (
    <div>
      <FilterControl />
      <FilterSummary />
    </div>
  );
}
```

Run this and change the dropdown in `FilterControl` — `FilterSummary`'s text never updates. This isn't a bug in the sense of broken syntax; it's a structural problem: `FilterControl`'s `selectedLine` and `FilterSummary`'s `selectedLine` are two entirely separate `useState` calls, each managing its own private box of state, with zero connection between them, despite having the same variable name. Two components, each with their own state, simply cannot see or affect each other's state — no matter how similarly you name things.

**After — the state is lifted to their shared parent:**

```tsx
// src/QuestLineFilterFixed.tsx
import { useState } from "react";

function FilterControl({
  selectedLine,
  onSelectedLineChange,
}: {
  selectedLine: string;
  onSelectedLineChange: (line: string) => void;
}) {
  return (
    <select value={selectedLine} onChange={(e) => onSelectedLineChange(e.target.value)}>
      <option value="all">All quest lines</option>
      <option value="Main Story">Main Story</option>
    </select>
  );
}

function FilterSummary({ selectedLine }: { selectedLine: string }) {
  return <p>Currently showing: {selectedLine}</p>;
}

export function QuestLineFilterFixed() {
  const [selectedLine, setSelectedLine] = useState("all");

  return (
    <div>
      <FilterControl selectedLine={selectedLine} onSelectedLineChange={setSelectedLine} />
      <FilterSummary selectedLine={selectedLine} />
    </div>
  );
}
```

**Line by line — this is the actual "lifting" step:** the `useState` call itself moved out of both `FilterControl` and `FilterSummary` and now lives only in their shared parent, `QuestLineFilterFixed`. Neither child has any state of its own anymore for this value at all. The parent then passes the current value *down* as a prop (`selectedLine={selectedLine}` — this is the "data down" half) to both children, so they both read the exact same single value. The parent also passes a way to *change* that value down as a prop (`onSelectedLineChange={setSelectedLine}` — this is the "events up" half): `FilterControl` doesn't call `setSelectedLine` directly (it doesn't even know that function's real name — it just calls whatever function it received, named generically `onSelectedLineChange` from its own point of view), but calling it still ultimately runs the *parent's* real `setSelectedLine`, because a function passed as a prop is still, underneath, the very same function object — calling it from inside a child runs the parent's actual code, updates the parent's actual state, and triggers a re-render of the parent and everything below it, including both children, which is exactly why `FilterSummary` now updates too.

This is **lifting state up**: when two (or more) components need to share or coordinate a piece of state, move that state to their nearest common parent, and have that parent hand it down as props — the actual value going *down* to children who need to display it, and update functions going *down* to children who need to change it, with events technically "bubbling up" only in the sense that calling a passed-down function runs code that lives up in the parent.

**Try it yourself:** add a third sibling, `FilterClearButton`, that receives `onSelectedLineChange` and renders a single button calling `onSelectedLineChange("all")`. Confirm clicking it resets both the dropdown *and* the summary text — proof this is genuinely one shared value, not three separately-synced copies.

**The limit of this pattern, honestly stated:** lifting state up works cleanly when the components that need to share state have a reasonably close common parent. If a value needs to reach a component four or five layers deep, through several intermediate components that don't themselves care about that value at all — just accepting it as a prop and immediately passing it further down, layer after layer, purely so it can reach something far below them — that specific pain has its own name, **prop drilling**, and it's exactly the problem Lesson 06 (Context) exists to solve. This lesson's pattern is still the right *first* choice even once you know Context exists — reach for lifting state up by default, and reach for Context specifically when lifting genuinely becomes unwieldy across real distance, not before.

### A form that doesn't decide what submitting means

One more application of this same idea, directly matching the real `QuestForm.tsx`: a form component can receive its submission handler as a prop, rather than deciding for itself what happens with the data once it's valid.

```tsx
// src/hooks-free sketch, mirroring the real QuestForm.tsx's shape
interface QuestFormProps {
  submitLabel: string;
  onSubmit: (values: QuestDraft) => void;
}

function QuestForm({ submitLabel, onSubmit }: QuestFormProps) {
  const [values, setValues] = useState<QuestDraft>(emptyDraft);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(values);
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* fields, as built above */}
      <button type="submit">{submitLabel}</button>
    </form>
  );
}
```

Notice `QuestForm` itself never mentions `addQuest`, `updateQuest`, an API call, or navigation to another page — it collects field values into its own local state (that part *is* its job) and, on submit, simply hands the finished object to whatever function it was given via the `onSubmit` prop. `QuestForm` doesn't know or care whether `onSubmit` will create a brand-new quest, save changes to an existing one, or something else entirely — that decision belongs to whichever page rendered it. In the real capstone, `project/questlog/src/pages/NewQuestPage.tsx` renders `<QuestForm submitLabel="Add Quest" onSubmit={handleSubmit} />` where `handleSubmit` calls `addQuest(values)` and then navigates back to the quest board, while `project/questlog/src/pages/QuestDetailPage.tsx` renders the *exact same* `QuestForm` component with a *different* `onSubmit` that calls `updateQuest` instead. This is lifting state up applied one level further than the sibling example above: instead of lifting a piece of *data*, you're lifting the *decision of what submission means* — the form owns its own fields' values, but hands the finished result, and the choice of what to do with it, up to its parent via a prop, exactly the same "data/functions flow through props, not sideways between components" idea.

## Common mistakes & gotchas

- **Passing `value` without `onChange`.** React logs a real console warning (`a form field without an 'onChange' handler`) and the field becomes impossible to type into, because nothing ever updates the state feeding `value` back into the input.
- **Mutating state directly instead of replacing it**, e.g. `values.title = e.target.value; setValues(values);`. This can silently fail to re-render (React may see the same object reference and skip updating), or work by accident today and fail later once other parts of the app start relying on state actually being a fresh object each time. Always build a *new* object (`{ ...values, title: ... }`) instead.
- **Forgetting `event.preventDefault()` in `onSubmit`.** The browser's default full-page-reload/navigate behavior fires, wiping out all React state instantly and often producing a confusing "page reloaded and now everything is blank" bug that has nothing to do with your form's logic being wrong.
- **Trying to lift state into a component that isn't actually a common ancestor of everything that needs it.** If two components that need to share state don't have a reasonably close shared parent, you'll find yourself passing the same prop down through several layers that don't use it themselves — a sign you've hit prop drilling, and a preview of exactly what Lesson 06 addresses.
- **Making a form component "smart" (deciding what submitting means) instead of "dumb" (just collecting values and calling `onSubmit`).** This works for a single-purpose form, but it makes the component impossible to reuse the moment you need the same fields for a second purpose (like QuestLog's shared create/edit form) — you'd end up either duplicating the whole form or bolting an awkward "mode" prop onto it instead of simply lifting the decision to the caller.

## How this connects

This lesson is built entirely on Lesson 02's state model — every controlled input is just `useState` plus two specific wiring props (`value`, `onChange`). It reused Module 03, Lesson 01's forms/accessibility knowledge (labels, input types) and Module 03, Lesson 06's `event.preventDefault()` without re-teaching either — same concepts, new placement. Lifting state up is the direct setup for Lesson 06: the moment lifting requires threading a value down through components that don't use it, purely to reach something several layers below, you've hit prop drilling, and Context is the tool built specifically for that case. The `QuestForm`'s `onSubmit`-as-a-prop pattern is exactly what you'll see, unchanged, in the real `project/questlog/src/components/QuestForm.tsx`, `NewQuestPage.tsx`, and `QuestDetailPage.tsx`.

## Quick self-check

1. In one sentence, what makes an input "controlled" versus "uncontrolled" — what's the precise difference in where its value lives?
2. Name two things a controlled input lets you do that a plain uncontrolled HTML input does not, without manual DOM code.
3. Why does `setValues({ ...values, title: newTitle })` work correctly while `values.title = newTitle; setValues(values);` is a mistake, even though both "end up" changing `title`?
4. In the "lifting state up" before/after example, precisely what moved, and what stayed the same, between the broken and fixed versions?
5. Explain, in your own words, why `QuestForm` receiving `onSubmit` as a prop rather than calling `addQuest` directly is the same underlying idea as lifting state up, even though no state is being "lifted" in the literal sense.
