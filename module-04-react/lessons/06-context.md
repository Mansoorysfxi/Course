# Lesson 06 — Context

## What you'll learn

- What **prop drilling** is, concretely — the specific pain that shows up when a value needs to reach a deeply nested component through several layers that don't themselves use it.
- What **Context** actually is: a way to make a value available to any descendant component, at any depth, without manually passing it through every intermediate layer's props.
- `createContext`, `<SomeContext.Provider value={...}>`, and `useContext(SomeContext)` — the three pieces that make Context work, built up one at a time.
- The full real pattern this module's capstone uses: `createContext<T | undefined>(undefined)` plus a custom hook wrapper (`useQuests()`) that throws a clear error if there's no provider above it — and exactly why that's the standard, idiomatic way most real React codebases use Context.
- When to reach for Context, and — just as importantly — when *not* to, and the honest trade-off Context makes against plain props.

## Why this matters

Lesson 05 taught you the right *default* tool for sharing state between components: lift it to their common parent, pass it down as props. That tool has a real limit, though, and this lesson exists because you're about to feel it directly. QuestLog's quest data needs to be read and changed from the quest board, the quest detail page, the "add a quest" page, and individual quest cards — components that are not siblings with one convenient shared parent a few lines up; they're separate *pages*, each rendered by the router (Lesson 08) at different times, several component layers removed from any single obvious common ancestor. Threading `quests`, `addQuest`, `updateQuest`, `deleteQuest`, and `toggleDone` down through props at every one of those layers would be unworkable. Context is React's built-in answer, and it's exactly what the real `QuestsContext.tsx` in this module's capstone is built on.

## Prerequisites

Lesson 05 (lifting state up) — this lesson assumes you've felt that pattern work, and you understand it as the thing Context is an alternative *to*, not a replacement for by default. Lesson 04 (custom hooks) — the standard Context pattern this lesson teaches wraps `useContext` inside a custom hook, so you need to already be comfortable with what a custom hook is and why it must follow the Rules of Hooks. Lesson 01 (components, props, and JSX) — you already know how a value gets passed from a parent to a child via props; this lesson is about what happens when that path gets too long to be practical.

## The concept, explained simply

### First, feel the actual pain: prop drilling

Here's a genuinely runnable example of the exact problem Context solves — four layers of components, where only the top and the very bottom actually care about a `questCount` value, and the three in between are forced to accept and immediately re-pass it purely because it has to travel through them to get where it's needed:

```tsx
// src/PropDrillingDemo.tsx
function QuestCountDisplay({ questCount }: { questCount: number }) {
  return <p>You have {questCount} quests.</p>;
}

function Sidebar({ questCount }: { questCount: number }) {
  // Sidebar itself never reads questCount -- it only exists to hand it
  // further down to whatever it renders.
  return (
    <aside>
      <QuestCountDisplay questCount={questCount} />
    </aside>
  );
}

function PageLayout({ questCount }: { questCount: number }) {
  // Same story here -- PageLayout doesn't care about questCount either.
  return (
    <div>
      <Sidebar questCount={questCount} />
    </div>
  );
}

function AppShell({ questCount }: { questCount: number }) {
  // ...and again here.
  return <PageLayout questCount={questCount} />;
}

export function PropDrillingDemo() {
  const questCount = 5; // imagine this is real state, from Lesson 05's pattern
  return <AppShell questCount={questCount} />;
}
```

**Line by line, and notice the shape of the problem specifically:** `PropDrillingDemo` is the only component that actually *has* `questCount` as a real value (here hardcoded, but imagine it as `useState` in a real app). `QuestCountDisplay`, at the bottom, is the only component that actually *reads* `questCount` to show it on screen. Everything in between — `AppShell`, `PageLayout`, `Sidebar` — has to accept `questCount` as a prop and immediately, mechanically, pass it straight through to whatever it renders, without ever touching, reading, or caring about the value itself. This is **prop drilling**: passing a prop down through one or more intermediate components solely because something further below needs it, not because those intermediate components have any actual use for it themselves.

**Try it yourself:** rename `questCount` to `totalQuests` everywhere. Notice you had to touch *five* separate function signatures and JSX prop-passing sites to rename one value that only two of those five components actually care about. Now imagine `AppShell`, `PageLayout`, and `Sidebar` are real components in a real app, written by different contributors, each already juggling a dozen other props of their own — every one of them now also has to know about, type, and forward `questCount`, purely as plumbing.

This gets worse, not better, in a real app for two concrete reasons: first, the actual distance is usually much greater than four layers (QuestLog's real component tree runs `App` → `Layout` → a routed page → possibly a shared component like `QuestCard`); second, in a real app, `Sidebar` and `PageLayout` are typically reused all over the place for many different things, and every one of their other call sites that has nothing to do with quest counts still has to satisfy the prop's TypeScript type, even if it never uses it — bloating every intermediate component's props interface with data it's merely forwarding.

### What Context actually is

**Context** is a built-in React feature for making a value available to *any* descendant component, at *any* depth below wherever you set it up, without manually passing that value through every intermediate component's props. It has three moving pieces, and it's worth learning them in the order you'd actually use them:

1. **`createContext(defaultValue)`** — creates a **Context object**. Think of it as a labeled "channel" — a named slot a value can be broadcast into, and later tuned into, from anywhere below.
2. **`<SomeContext.Provider value={...}>`** — a component you wrap around some part of your tree. Everything rendered *inside* it — no matter how many layers deep — can now tune into this channel and read whatever `value` currently is.
3. **`useContext(SomeContext)`** — the hook any descendant component calls to actually read the current value being broadcast on that channel, with zero props involved at all.

Here's the prop-drilling example above, fixed with Context:

```tsx
// src/ContextDemo.tsx
import { createContext, useContext } from "react";

const QuestCountContext = createContext<number>(0);

function QuestCountDisplay() {
  const questCount = useContext(QuestCountContext);
  return <p>You have {questCount} quests.</p>;
}

function Sidebar() {
  // No questCount prop at all -- Sidebar doesn't need to know it exists.
  return (
    <aside>
      <QuestCountDisplay />
    </aside>
  );
}

function PageLayout() {
  return (
    <div>
      <Sidebar />
    </div>
  );
}

function AppShell() {
  return <PageLayout />;
}

export function ContextDemo() {
  const questCount = 5;
  return (
    <QuestCountContext.Provider value={questCount}>
      <AppShell />
    </QuestCountContext.Provider>
  );
}
```

**Line by line:** `createContext<number>(0)` creates the channel, typed to carry a `number`, with `0` as the value anything reading it would get *if no Provider exists above it at all* — this default is a fallback for that specific "nobody's broadcasting" case, not a value you'll normally rely on in a real app, as the next section explains. `<QuestCountContext.Provider value={questCount}>` — every Context object automatically comes with a matching `.Provider` component; wrapping it around `<AppShell />` means "for `AppShell` and literally everything it renders, at any depth, `useContext(QuestCountContext)` will return `questCount`'s current value." `useContext(QuestCountContext)` inside `QuestCountDisplay` reaches straight through `AppShell`, `PageLayout`, and `Sidebar` — none of which mention `QuestCountContext` at all — and gets the value directly. Notice `AppShell`, `PageLayout`, and `Sidebar` are now back to having *zero* props related to this value — the plumbing is gone entirely.

**Try it yourself:** add a second consumer, a `<QuestCountDoubled />` component that also calls `useContext(QuestCountContext)` and renders `questCount * 2`, rendered somewhere else inside `AppShell`. Confirm it reads the *same* current value with no props passed to it either — any number of descendants, at any depths, can all tune into the same Provider.

## The details

### The real pattern: `createContext<T | undefined>(undefined)` plus a custom hook

The example above works, but it has a real weakness worth exposing on purpose: what if someone renders `<QuestCountDisplay />` *without* wrapping it in a `<QuestCountContext.Provider>` anywhere above it — say, in a test, or a part of the app that was refactored and lost its provider by accident? With `createContext<number>(0)`, that mistake is invisible: `useContext` just quietly returns `0`, the default, and the bug shows up later as "why does this always say zero quests" instead of immediately, at the actual site of the mistake.

This is exactly the problem the real `project/questlog/src/context/QuestsContext.tsx` is built to avoid, and it does it with a specific, deliberate pattern:

```tsx
// project/questlog/src/context/QuestsContext.tsx (the Context-specific parts)
import { createContext, useContext, type ReactNode } from "react";
import type { Quest, NewQuestInput, QuestUpdate } from "../types/quest";

interface QuestsContextValue {
  quests: Quest[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
  addQuest: (input: NewQuestInput) => void;
  updateQuest: (id: string, changes: QuestUpdate) => void;
  deleteQuest: (id: string) => void;
  toggleDone: (id: string) => void;
  getQuest: (id: string) => Quest | undefined;
}

const QuestsContext = createContext<QuestsContextValue | undefined>(undefined);

export function QuestsProvider({ children }: { children: ReactNode }) {
  // ... quests/loading/error state and addQuest/updateQuest/etc. functions
  // (the full data-fetching part of this is Lesson 07's job) ...
  const value: QuestsContextValue = {
    /* quests, loading, error, refetch, addQuest, updateQuest, deleteQuest, toggleDone, getQuest */
  } as QuestsContextValue;

  return <QuestsContext.Provider value={value}>{children}</QuestsContext.Provider>;
}

export function useQuests(): QuestsContextValue {
  const context = useContext(QuestsContext);
  if (context === undefined) {
    throw new Error("useQuests() must be called from inside a <QuestsProvider>.");
  }
  return context;
}
```

**Line by line, piece by piece:**

- `interface QuestsContextValue { ... }` describes the complete shape of everything this Context will ever broadcast — the actual quest data, the loading/error flags, and every function a consumer might need to change that data. This is exactly Module 03, Lesson 09's `interface` idea, applied to "the shape of what a Context provides" instead of "the shape of an API response."
- `createContext<QuestsContextValue | undefined>(undefined)` — here's the deliberate choice this lesson is built around. Instead of inventing some fake placeholder `QuestsContextValue` to use as a default (which would require fabricating fake versions of `quests`, `addQuest`, and every other field just to satisfy the type), the default value is genuinely `undefined`, and the type is explicitly the union `QuestsContextValue | undefined` — meaning "either a real value, or the literal absence of one." This makes the "no provider above me" case a real, distinct, type-checked possibility, rather than something quietly hidden behind a fake default or an `as QuestsContextValue` type assertion (Module 03, Lesson 09's term) that would just tell TypeScript to trust you and stop checking.
- `export function QuestsProvider({ children }: { children: ReactNode })` — this is the component you'll actually wrap around part of your app (in `main.tsx` or `App.tsx`) to make quest data available below it. `children: ReactNode` (a type meaning "anything React can render" — components, strings, numbers, more JSX) is exactly how this component can wrap *any* content and pass it straight through, unchanged, inside the `<QuestsContext.Provider>` at the bottom.
- `export function useQuests(): QuestsContextValue { const context = useContext(QuestsContext); if (context === undefined) { throw new Error(...); } return context; }` — this is the custom hook (Lesson 04's territory) that every real component in the app actually calls, instead of importing `QuestsContext` directly and calling `useContext(QuestsContext)` itself everywhere. Read the `if` check carefully: if `useContext(QuestsContext)` returns `undefined`, that can only mean one thing — this component was rendered somewhere *without* a `<QuestsProvider>` above it — and rather than silently returning `undefined` and letting every single caller of `useQuests()` remember to separately check for that themselves (`const value = useQuests(); if (!value) return null;`, repeated everywhere, easy to forget even once), this hook throws a clear, specific error message immediately, right at the point of the actual mistake. After that check, TypeScript itself is satisfied that `context` can only be `QuestsContextValue` from this point on (never `undefined`) — the `if` block is a **type narrowing** check (Module 03, Lesson 09's vocabulary), so the function's declared return type `QuestsContextValue` (no `| undefined`) is genuinely, correctly guaranteed, not just asserted.

**Why this is better developer experience than every consumer checking for `undefined` itself:** imagine instead that `useContext(QuestsContext)` could quietly return `undefined` and every component using it had to write `const questsValue = useContext(QuestsContext); if (!questsValue) return null;` (or worse, forgot to, and crashed later on `questsValue.quests.map(...)` with a confusing "Cannot read properties of undefined" error pointing at the wrong line). Centralizing that one check inside `useQuests()` means the check happens exactly once, in exactly one place, with a message that names the actual problem (`"useQuests() must be called from inside a <QuestsProvider>."`) instead of a generic runtime crash — and every other component in the app gets to write `const { quests, addQuest } = useQuests();` and trust, completely, that it received real data. **This exact combination — a Context plus a custom hook wrapping `useContext` and validating it — is the standard, idiomatic way most real React codebases use Context.** You will rarely see production code call `useContext(SomeRawContext)` directly outside of the one hook file that defines it.

### When to reach for Context — and when not to

Context is genuinely useful, but it is not a default reach for "any time two components need to share something." Ask one honest question before using it: **does more than one, meaningfully distant part of the component tree actually need this value?**

- If a piece of state is only used by one component, and maybe that component's own direct children — plain `useState` plus props (Lesson 02 and Lesson 05's lifting pattern) is simpler, more explicit, and should be preferred. Look at `project/questlog/src/pages/QuestListPage.tsx`'s own filter/sort controls (`questLineFilter`, `priorityFilter`, `doneFilter`, `sortField`) — these live in plain `useState` inside that one page component, *not* in `QuestsContext`, precisely because nothing else in the app needs them. Putting them in Context "just in case" would be reaching for a bigger tool than the actual problem calls for.
- Context earns its place when a value is genuinely needed across real distance — QuestLog's `quests` array and its `addQuest`/`updateQuest`/`deleteQuest`/`toggleDone`/`refetch` functions are needed by the quest board, the quest detail page, the new-quest page, and individual quest cards — separate pages and components with no convenient shared parent a few lines up, exactly the prop-drilling scenario this lesson opened with.

**Name the trade-off honestly, because it is a real trade-off, not a strict improvement:** plain props make data flow **explicit and traceable** — you can look at any component's function signature and see, in one place, everything it depends on, and you can trace exactly where each prop came from by reading upward through the JSX tree. Context trades that traceability away in exchange for **convenience across distance** — a component calling `useQuests()` gives you no visual indication, just from reading that one file, of *where* the data it's returning actually comes from, or how far away the `<QuestsProvider>` supplying it lives; you have to go looking. Context isn't "better" than props in some absolute sense — it's the right tool specifically when the distance problem is real and props alone have become genuinely unwieldy, not a default upgrade to reach for out of habit.

### The real cost of overusing Context, briefly

One common mistake, worth being aware of even though deep performance work is out of scope for this lesson: putting *everything* into one giant, shared Context "just in case something needs it later." The concrete cost is this — **any component that consumes a Context re-renders whenever *any* value inside that Context changes, even parts of it that component never actually reads.** If `QuestsContextValue` held, say, `quests` *and* some unrelated `currentUser` value all in one giant object, a component that only ever reads `quests` would still re-render every single time `currentUser` changed, for no benefit to that component at all. This is exactly why `project/questlog/src/pages/QuestListPage.tsx` keeps its own filter/sort state local instead of folding it into `QuestsContext` — doing so would mean *every* consumer of `QuestsContext` across the whole app re-renders every time a filter dropdown changes, even components that have nothing to do with filtering at all. This lesson isn't asking you to solve that problem (that's real performance-optimization territory, out of scope here) — just to know it's a real, named cost of "one context to hold everything," so you have a genuine reason, beyond "it felt tidy," to keep Context scoped to what actually needs to be widely shared.

## Common mistakes & gotchas

- **Calling `useContext(SomeContext)` directly all over the app instead of writing a custom hook wrapper.** It works, syntactically, but you lose the centralized `undefined`-check this lesson built, and every consumer has to remember to handle the "no provider" case (or, more likely, forgets to, and gets a confusing crash later at the point of *use*, not the point of the actual mistake).
- **Rendering a component that calls `useQuests()` (or any Context-wrapping hook) outside its matching Provider.** With the real pattern (`| undefined` plus the explicit throw), you get an immediate, clearly-worded error naming the exact problem. Without that pattern — say, if you'd used a fake default value instead — you'd instead get silently wrong behavior (fake/default data rendering as if it were real) that's far harder to trace back to its actual cause.
- **Forgetting to actually wrap part of the tree in the Provider at all**, e.g. defining `QuestsProvider` and `useQuests` correctly but never rendering `<QuestsProvider>` anywhere in `main.tsx` or `App.tsx`. Every consumer will hit the "must be called from inside a `<QuestsProvider>`" error the instant it renders — a strong hint to go check exactly this.
- **Reaching for Context as the very first tool for any shared state**, before checking whether the components involved actually have a reasonably close common parent where Lesson 05's lifting pattern would work fine. Context adds a layer of indirection (you can no longer trace a value's origin just by reading props) that's only worth paying for when the distance genuinely justifies it.
- **Putting unrelated pieces of state into one shared Context "for convenience,"** and then being surprised when a component re-renders in response to a change it never reads at all — the real cost named above, not a bug in React, just a consequence of how Context notifies its consumers.

## How this connects

This lesson is the direct sequel to Lesson 05's lifting-state-up pattern — Context is what you reach for once lifting alone stops being practical across real distance, not a replacement for it in general. It also depends on Lesson 04's custom-hook vocabulary: the standard Context pattern *is* a custom hook (`useQuests`) wrapping a built-in one (`useContext`). Forward, this lesson connects directly to Lesson 07: the real `QuestsContext.tsx` combines everything this lesson taught — `createContext`, a Provider, and a custom hook — with the full data-fetching pattern (loading/error state, cleanup, refetch) Lesson 07 covers, all in one file. It also connects to Lesson 08 (React Router): once QuestLog has multiple routed pages, every one of them will reach quest data the exact same way, by calling `useQuests()`, regardless of which page component is currently rendered by the router.

## Quick self-check

1. In your own words, what specifically is "prop drilling," and what distinguishes it from a normal, reasonable case of passing a prop from a parent to a direct child?
2. Name the three pieces involved in using Context, in the order you'd typically set them up.
3. Why does the real `QuestsContext.tsx` use `createContext<QuestsContextValue | undefined>(undefined)` instead of inventing a fake default `QuestsContextValue` to satisfy the type?
4. Why is a custom hook like `useQuests()` — that throws if the context is `undefined` — considered better practice than having every component call `useContext(QuestsContext)` directly and check for `undefined` itself?
5. Give a concrete reason QuestLog's filter/sort state (in `QuestListPage.tsx`) should stay as local `useState` rather than being added to `QuestsContext` — what's the actual cost if it were moved there?
