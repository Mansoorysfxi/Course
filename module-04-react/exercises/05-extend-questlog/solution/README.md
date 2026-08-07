# Exercise 05 solution — QuestLog + a Quest Lines overview page

This is the QuestLog capstone (`project/questlog/`) plus Exercise 05's
required feature: a `/quest-lines` page. See
[`../INSTRUCTIONS.md`](../INSTRUCTIONS.md) for the full requirements, and
[`../starter/`](../starter/) for the unmodified starting point.

```bash
npm install
npm run dev
```

## What was added, relative to the starter

- `src/pages/QuestLinesPage.tsx` (new) — aggregates `quests` from
  `useQuests()` into one entry per quest line (name, total count, done
  count), sorted alphabetically.
- `src/App.tsx` — one new nested route: `path="quest-lines"` ->
  `<QuestLinesPage />`.
- `src/components/Layout.tsx` — one new `<NavLink to="/quest-lines">` in
  the header.

No other file changed. In particular, `QuestsContext.tsx` did not need
any changes — this feature only *reads* `quests`, which the context
already exposed.
