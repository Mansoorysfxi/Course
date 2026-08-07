# Module 04 Capstone — QuestLog (web)

## What this is

Per [`RUNNING_PROJECT.md`](../../RUNNING_PROJECT.md), this is where
**QuestLog** — the course's running project — begins as real code for the
first time. (Module 01's QuestLog CLI was a separate, standalone codebase
that only established the *domain*; Module 03's capstone was deliberately
a different app, a weather dashboard. This one carries forward: Module 05
copies this exact codebase and adds a real FastAPI backend to it, Module
06 adds a database, and so on through the final capstone.)

You will build a React + TypeScript single-page app — a personal quest
(task) tracker with light RPG framing — using Vite, Tailwind CSS, and
React Router, with all data held in React state (no real backend yet;
that's Module 05).

**The finished reference solution lives at
[`project/questlog/`](./questlog/)** in this same folder, fully built,
and was actually run through `npm install` and `npm run build` (zero
TypeScript errors, a real production bundle) while writing this module —
read it once you've built your own version, not before.

## The domain model

```typescript
type Priority = "low" | "medium" | "high";

interface Quest {
  id: string;
  title: string;
  description: string;
  priority: Priority;
  done: boolean;
  questLine: string;   // a named group of related quests, e.g. "Main Story"
  createdAt: string;   // ISO 8601 timestamp
}
```

This is deliberately simple — per `RUNNING_PROJECT.md`, "nothing about the
business logic should ever be the hard part." Every module's added
complexity is about the *technology*, not the domain.

## Concepts this project uses

Every concept below has a dedicated lesson section — this project should
not require anything this module didn't already teach (Rule 1):

| Concept | Taught in |
|---|---|
| Vite + React + TS scaffold, Tailwind + React Router install | [Lesson 00](../lessons/00-setup.md) |
| Components, props, JSX, why a framework at all | [Lesson 01](../lessons/01-why-react-components-props-and-jsx.md) |
| `useState`, the rendering model, virtual DOM/reconciliation | [Lesson 02](../lessons/02-state-and-the-rendering-model.md) |
| `useEffect`, dependency arrays, cleanup functions (the fetch-on-mount pattern in `QuestsContext`) | [Lesson 03](../lessons/03-useeffect-the-dependency-array-in-depth.md) |
| Custom hooks (`useQuests`) | [Lesson 04](../lessons/04-useref-and-custom-hooks.md) |
| Controlled forms, lifting state up (`QuestForm`) | [Lesson 05](../lessons/05-forms-controlled-components-and-lifting-state.md) |
| Context (`QuestsContext`, avoiding prop-drilling across pages) | [Lesson 06](../lessons/06-context.md) |
| Data fetching, loading/error states, a mocked async API (`fetchQuests`) | [Lesson 07](../lessons/07-data-fetching-loading-and-error-states.md) |
| Multi-page routing, nested routes, dynamic segments, `useParams`/`useNavigate` | [Lesson 08](../lessons/08-react-router.md) |
| Utility-first CSS with Tailwind | [Lesson 10](../lessons/10-tailwind-and-utility-first-css.md) |
| TypeScript interfaces/unions for the domain model | Module 03, [Lesson 09](../../module-03-html-css-javascript/lessons/09-typescript-introduction.md) |
| `fetch`-shaped async/await, loading/error UI patterns in general | Module 03, [Lesson 07](../../module-03-html-css-javascript/lessons/07-fetch-promises-and-async-await.md) |

(Lesson 09, Next.js concepts, is conceptual only — QuestLog stays a Vite
SPA, per `RUNNING_PROJECT.md`.)

## What to build

Set this up as its own project, following
[`lessons/00-setup.md`](../lessons/00-setup.md):

```bash
cd module-04-react/project
npm create vite@latest questlog -- --template react-ts
cd questlog
npm install tailwindcss @tailwindcss/vite react-router
```

Then build:

### `src/types/quest.ts`
The `Quest`, `Priority`, `NewQuestInput`, and `QuestUpdate` types above.

### `src/api/fetchQuests.ts`
A mocked async "backend": a `fetchQuests()` function returning
`Promise<Quest[]>`, using `setTimeout` to simulate a real network delay
(several hundred milliseconds — long enough that a loading spinner is
genuinely visible), and able to reject — both **randomly** (a small
percentage of calls, so the error state gets exercised without anyone
doing anything special) and **on demand** (an option a caller can pass to
force a rejection, for deliberately testing error UI). This exact shape —
a Promise that can be made to fail — is what Module 05 replaces with a
real `fetch()` call to FastAPI, without any *caller* of `fetchQuests()`
needing to change.

### `src/context/QuestsContext.tsx`
A `QuestsProvider` + `useQuests()` custom hook that:
- Calls `fetchQuests()` once on mount (via `useEffect`), tracking
  `loading`/`error`/`quests` state correctly, with a cleanup guard against
  a stale request overwriting current state.
- Exposes `addQuest`, `updateQuest`, `deleteQuest`, `toggleDone`,
  `getQuest`, and `refetch` — all quest mutations happen here, once, so
  every page reads/writes through the same source of truth instead of
  passing quest data down through many layers of props.

### Pages (React Router)
- **`/`** — the Quest Board: lists all quests; correctly renders a loading
  state, an error state (with a way to retry), and the real list. Includes
  controls to **filter** (by quest line, priority, done/not-done) and
  **sort** (by newest, priority, or title) — these controls are local
  state to this page, not the context, since no other page needs them.
- **`/quests/new`** — a controlled form to add a quest.
- **`/quests/:id`** — view a single quest (read `:id` with `useParams`);
  toggle done; edit it (reusing the same form component used for
  creating); delete it (with a confirmation step).
- **A catch-all 404 page** for any unmatched route.

### Styling
Tailwind utility classes throughout, per Lesson 10 — no separate `.css`
files with your own custom class names for component styling (global
resets/fonts in `index.css` are fine).

## Acceptance criteria

- [ ] `npm install` then `npm run build` complete with zero TypeScript
  errors and a real production build.
- [ ] `npm run dev` starts a working dev server; visiting it shows a
  loading state briefly, then the quest list.
- [ ] Reloading the app repeatedly eventually shows the error state (the
  random failure) with a working "Try again" control — or you've
  confirmed this by temporarily forcing `forceError: true`.
- [ ] Filtering by quest line/priority/done and sorting all visibly,
  correctly change which quests are shown and in what order.
- [ ] Adding a quest through the form immediately shows it in the list
  (no page reload) and takes you back to the board.
- [ ] Clicking a quest goes to its own page; editing it and saving shows
  the updated data everywhere it appears; deleting it removes it and
  returns you to the board.
- [ ] Visiting a nonexistent quest ID, or a nonexistent path entirely,
  shows a real, styled page — not a blank screen or a crash.
- [ ] No component reaches into `QuestsContext`'s internals directly
  (everything goes through `useQuests()`).
- [ ] No prop is drilled through more than one layer just to reach a
  distant descendant — anything shared across pages goes through context.

## What to submit

Point your AI session at your `questlog/` folder and say *"check my
module"* — graded per
[GRADING_PROTOCOL.md](../../GRADING_PROTOCOL.md) alongside a re-check of
Exercises 01–05 as part of the full Module 04 module-end review.

## Why this project, specifically

This is the widest capstone yet — every concept this module taught, one
real app, and (unlike every capstone before it) not a one-off: this exact
codebase is what Module 05's agent is told to copy forward and wire up to
a real FastAPI backend. Getting the shape right here — a single source of
truth for quest data (`QuestsContext`), pages that read/write through it
rather than duplicating state, a mocked API isolated behind one function
so it can later be swapped for a real one — is what makes every future
module's "extend QuestLog" instructions land on solid ground instead of a
codebase that has to be partially rewritten first.
