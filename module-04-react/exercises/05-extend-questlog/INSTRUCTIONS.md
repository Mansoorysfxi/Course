# Exercise 05 — Extend QuestLog: a Quest Lines Overview Page

**Lessons:** every lesson in this module contributes something here, but the two doing the most direct work are:
- [`lessons/08-react-router.md`](../../lessons/08-react-router.md) — adding a new page/route to an existing nested route tree.
- [`lessons/06-context.md`](../../lessons/06-context.md) — reading shared data from `useQuests()` in a brand-new page, without changing the context itself.

You'll also be reading and working inside real code from Lessons 01, 02, 05, 07, and 10 (components/props, state, forms, data fetching, and Tailwind) without being told exactly where each applies — that's the point of this being the *independent* exercise.

**Difficulty:** Independent. This is the closest thing in this module to real work: extending an existing, unfamiliar-until-you-read-it codebase with a genuinely new feature, end to end.

## The task

`starter/` is an exact copy of the QuestLog capstone (`project/questlog/`). Add a new page: **`/quest-lines`**, a "Quest Lines" overview showing, for every distinct quest line that exists across all quests, how many quests it has in total and how many are done — e.g. "Main Story — 1 / 1 done" or "Village Errands — 0 / 2 done."

## Concepts this exercise uses (all already taught)

- Reading shared data via `useQuests()` (Lesson 06) — this feature only *reads* `quests`; you should not need to change `QuestsContext.tsx` at all.
- A new page component (Lesson 01) rendering the loading/error/success states correctly (Lesson 07) — this page fetches nothing new itself, but `quests` still starts out loading/possibly-erroring, exactly like every other page.
- Adding a new nested `<Route>` to an existing route tree, and a new `<NavLink>` in `Layout.tsx` to reach it (Lesson 08).
- Deriving new information (per-quest-line counts) from existing state, without needing any new state of its own — plain JavaScript/TypeScript (a `Map`, or a plain object, keyed by quest line name) computed directly in the component body on every render, no `useState`/`useEffect` needed for this part at all, since it's cheaply recomputed from `quests` and not something that needs to persist independently.
- Tailwind utility classes (Lesson 10), matching the existing app's visual style (look at `QuestListPage.tsx` for the styling patterns already in use — cards, spacing, text colors).

## Acceptance criteria

- [ ] Visiting `/quest-lines` (via a new nav link, not just by typing the URL) shows one entry per distinct quest line, with a correct total count and done count for each.
- [ ] The loading and error states (the same ones every other page already handles) are handled correctly on this page too — don't assume `quests` is always instantly available.
- [ ] Adding a new quest (via the existing "New Quest" page) with a brand-new quest line, then visiting `/quest-lines`, shows that new quest line with a count of 1.
- [ ] Toggling a quest's done status, then revisiting `/quest-lines`, shows an updated done count.
- [ ] The new page visually matches the rest of the app (Tailwind utility classes, not hand-written CSS, not inline styles copied from a different exercise).
- [ ] `QuestsContext.tsx` was **not modified** — if you found yourself needing to change it, that's a sign you're solving this differently than intended; re-read the "Concepts" section above.
- [ ] `npm run build` completes with zero TypeScript errors.

## What to submit

Point your AI session at your completed `starter/` folder (or wherever you copied it to work in) and say *"Review my solution for exercise 05."*

## Hints

**Level 1:** Start by reading `src/pages/QuestListPage.tsx` in full — it already shows you the loading/error/success early-return pattern, how to pull `quests` out of `useQuests()`, and what Tailwind classes the rest of the app already uses for cards and text. Your new page follows the same shape.

**Level 2:** Building the per-line counts is a small loop, not a big one:
```typescript
const statsByLine = new Map<string, { total: number; done: number }>();
for (const quest of quests) {
  const current = statsByLine.get(quest.questLine) ?? { total: 0, done: 0 };
  current.total += 1;
  if (quest.done) current.done += 1;
  statsByLine.set(quest.questLine, current);
}
```
Then render `Array.from(statsByLine.entries())`.

**Level 3 (near-answer):** The three files that need to change are `src/pages/QuestLinesPage.tsx` (new file), `src/App.tsx` (one new `<Route path="quest-lines" element={<QuestLinesPage />} />` inside the existing `<Route path="/" element={<Layout />}>` block), and `src/components/Layout.tsx` (one new `<NavLink to="/quest-lines">Quest Lines</NavLink>`). If you're still stuck after this, ask your AI session for the full solution rather than guessing further.
