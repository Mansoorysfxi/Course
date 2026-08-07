# Exercise 02 — State and a Controlled Form

**Lessons:**
- [`lessons/02-state-and-the-rendering-model.md`](../../lessons/02-state-and-the-rendering-model.md) — `useState`, immutable updates with `.map()`/spread.
- [`lessons/05-forms-controlled-components-and-lifting-state.md`](../../lessons/05-forms-controlled-components-and-lifting-state.md) — controlled inputs, lifting state up.

Read both fully before starting.

**Difficulty:** Guided. More is provided than Exercise 01, but the actual state-management logic and the form are left for you to write, following the exact patterns the lessons teach.

## Concepts this exercise uses

- `useState` for a list of items and for individual form fields.
- Updating state **immutably** — producing a new array/object instead of mutating the old one.
- A **controlled** text input and a controlled `<select>`.
- **Lifting state up**: the form doesn't decide what happens when a quest is added — it calls a function passed down from its parent (`onAddQuest`), exactly like `QuestListItem` (already built for you) calls `onToggleDone`.

## What's already done for you

- `src/types.ts` — the `Priority` and `Quest` types (complete).
- `src/components/QuestListItem.tsx` — renders one quest with a checkbox that calls `onToggleDone(quest.id)` (complete — read it, since your `QuestForm` will follow the same "receive a callback prop, call it" shape).
- `src/App.tsx` — has `quests` state, seed data, and renders the list and form. Two functions inside it, `addQuest` and `toggleDone`, are stubbed with `console.log("TODO: ...")` placeholders you must replace.

Run `npm install && npm run dev` now — it will fail to compile (unused-variable errors pointing at exactly the pieces you need to finish). That's expected.

## What to build

### Step 1 — `addQuest` in `src/App.tsx`

Given a `title` and `priority`, create a new `Quest` object (generate its `id` with `crypto.randomUUID()`, it starts `done: false`) and add it to the FRONT of the `quests` array, using `setQuests` with a **new** array (don't call `.push()` on the existing one).

### Step 2 — `toggleDone` in `src/App.tsx`

Given an `id`, flip that one quest's `done` value. Use `.map()` to build a new array where every quest keeps its existing reference except the one matching `id`, which gets a new object with `done` flipped.

### Step 3 — `src/components/QuestForm.tsx`

Build a controlled form with a text input (title) and a `<select>` (priority), each backed by its own `useState`. On submit: `preventDefault()`, ignore an empty (post-`.trim()`) title, call `onAddQuest(title, priority)`, then clear the title field.

## Acceptance criteria

- [ ] `npm run dev` runs with zero TypeScript errors once you're done.
- [ ] Typing a title, picking a priority, and clicking "Add Quest" immediately shows the new quest in the list — no page reload, no console errors.
- [ ] Submitting with an empty title does nothing (no blank quest gets added).
- [ ] Clicking a quest's checkbox toggles its done state (and its strikethrough styling) without affecting any other quest.
- [ ] After adding a quest, the title field is empty again; the priority field is unchanged (this is intentional, not a bug — see the solution's comment on why).
- [ ] `quests` is never mutated directly (no `.push()`, no `quest.done = ...` outside of producing a new object). `npm run build` completes with zero errors.

## What to submit

Point your AI session at your completed folder and say *"Review my solution for exercise 02."*

## Hints

**Level 1:** For `toggleDone`, re-read Lesson 02's example of flipping one boolean flag inside an array of objects with `.map()` — this exercise's `toggleDone` is that exact example with different field names.

**Level 2:** `addQuest`'s new-array pattern: `setQuests([newQuest, ...quests])` (spread the existing array after the new item). `toggleDone`'s pattern: `setQuests(quests.map(q => q.id === id ? { ...q, done: !q.done } : q))`.

**Level 3 (near-answer):** `QuestForm`'s submit handler needs, in order: `event.preventDefault()`; a check like `if (title.trim() === "") return;`; then `onAddQuest(title.trim(), priority)`; then `setTitle("")`. If you're still stuck after this, ask your AI session for the full solution rather than guessing further.
