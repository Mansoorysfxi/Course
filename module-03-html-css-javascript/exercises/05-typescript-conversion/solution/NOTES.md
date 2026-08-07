# Notes on grading this yourself before asking for review

```bash
cd solution
npm install
npx tsc
node dist/quests.js
```

**Expected output:**
```
Slay the Dragon [Hard] — 500 gold
Hard quests: 2
Total rewards: 1155
Found quest name: Slay the Dragon
Not-found lookup: No quest found
```

- **Zero `any` remaining** — search your file for the literal text `any`;
  it should not appear anywhere except possibly inside a comment you wrote
  yourself explaining why you avoided it.
- **The union-type checkpoint.** Temporarily change `sampleQuests[0]`'s
  `difficulty` to `"Impossible"` and run `npx tsc` again. Confirmed against
  a real compile with TypeScript 7.0.2: `tsc` reports
  `error TS2322: Type '"Impossible"' is not assignable to type '"Easy" |
  "Hard" | "Medium"'.` — note `tsc` alphabetizes the union's members in its
  own error message, so don't worry if that order doesn't match the order
  you wrote them in `interface Quest`; what matters is that a real error
  appears at all. If you don't see an error here, `difficulty` is still
  typed as a plain `string` somewhere (most likely in `Quest` itself, or in
  `filterByDifficulty`'s second parameter) — go back and check both. Revert
  the change once you've confirmed this.
- **`findQuestByName`'s return type.** Hover over `found` in VS Code (or
  temporarily try `found.name` without the `?.`) — it should show/require
  handling `Quest | undefined`, not just `Quest`. If VS Code shows plain
  `Quest` with no `| undefined`, the function's return type annotation is
  missing or wrong.
- **`sampleQuests` shape.** Confirm at least one entry has `notes` and at
  least one doesn't, and that leaving `notes` out doesn't cause a compile
  error (since it's optional) while leaving out `rewardGold` or any other
  required field *would* (try it briefly, then undo, to confirm).
- **A note on `filterByDifficulty`'s parameter type,** since there's a
  legitimate design choice here worth understanding either way: this
  solution writes `difficulty: Quest["difficulty"]` — indexing into the
  `Quest` interface's own type to reuse its exact union — rather than
  retyping `"Easy" | "Medium" | "Hard"` a second time by hand. Both are
  correct and `tsc` accepts either; `Quest["difficulty"]` has the practical
  advantage that if you ever add a fourth difficulty to `Quest` later, this
  function's parameter type updates automatically instead of silently
  drifting out of sync with a hand-copied list.
