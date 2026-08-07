# Exercise 05 — TypeScript Conversion: Typing a Quest Roster

**Difficulty:** Independent — this exercise gives you working, untyped
(`any`-riddled) TypeScript and asks you to add real types throughout,
using everything from
[`lessons/09-typescript-introduction.md`](../../lessons/09-typescript-introduction.md).
No new HTML/CSS/DOM work here — this is entirely about the type system,
deliberately isolated so you can focus on it without also juggling `fetch`
or the DOM at the same time.

**Concepts this exercise uses** (all taught in Lesson 09, building on
Lessons 05–08's plain JavaScript): `interface`, type annotations on
function parameters/return values, optional properties (`?`), union types
(including string-literal unions), the trap of `any`, and running `tsc`
to catch real mistakes before runtime.

## Setup

This exercise needs its own Node.js project (per
[`lessons/00-setup.md`](../../lessons/00-setup.md)):

```bash
cd starter
npm install
npx tsc --version
```
**Expected:** `Version 7.0.2` (or newer 7.x) — confirming `typescript` (listed
in `package.json`'s `devDependencies`) installed correctly.

## What to build

Open `starter/src/quests.ts`. Every function currently has its parameters
and return value typed as `any` (Lesson 09's explicitly-flagged escape
hatch) — your job is to replace every single `any` with the correct, real
type, adding one `interface` to describe a quest's shape. Specific TODOs:

1. **Define `interface Quest`** with: `name: string`, `difficulty:` a
   string-literal union of exactly `"Easy" | "Medium" | "Hard"` (not a plain
   `string` — Lesson 09's union-type section), `rewardGold: number`,
   `completed: boolean`, and an **optional** `notes?: string`.
2. **Type `formatQuest`** to accept one `Quest` and return a `string`.
3. **Type `filterByDifficulty`** to accept a `Quest[]` and a difficulty
   value of the *same* union type used in `Quest["difficulty"]` (not a plain
   `string` — this should reject a call passing `"Impossible"`, which isn't
   one of the three valid difficulties), returning a `Quest[]`.
4. **Type `totalRewards`** to accept a `Quest[]` and return a `number`.
5. **Type `findQuestByName`** to accept a `Quest[]` and a `string`, and
   return `Quest | undefined` (it may not find a match — Lesson 09's union
   types apply here too, and this exact return type is why the demo code at
   the bottom of the file needs `?.`/`??`, from Lesson 08, to use the result
   safely).
6. Fill in the **`sampleQuests`** array with at least four `Quest` objects
   (satisfying the interface exactly — `tsc` will catch any missing/
   mistyped field), including at least one with `notes` present and at
   least one without it.

## The compile-error checkpoint (do this deliberately, don't skip it)

Once everything above compiles cleanly with `npx tsc`, **deliberately break
one thing on purpose**: change one `sampleQuests` object's `difficulty` to
`"Impossible"` (not one of the three allowed values) and run `npx tsc`
again. Read the actual error message `tsc` gives you, then **fix it back**
before submitting. This step is checked as part of the review — the point
is proving to yourself the union type genuinely rejects an invalid value,
not just trusting that it theoretically would.

## Acceptance criteria

- [ ] `npx tsc` compiles with **zero errors** on your final, submitted code.
- [ ] No `any` remains anywhere in `src/quests.ts`.
- [ ] `Quest["difficulty"]` is a three-value string-literal union, not a
  plain `string` — confirm by trying (temporarily) to assign an invalid
  difficulty and seeing `tsc` reject it.
- [ ] `findQuestByName` is typed to return `Quest | undefined`, and the
  demo code at the bottom of the file safely handles the "not found" case
  using `?.`/`??` rather than assuming a match was always found.
- [ ] `sampleQuests` has at least four entries, with `notes` present on at
  least one and absent on at least one other.
- [ ] Running `node dist/quests.js` (after `npx tsc`) produces sensible,
  correct console output with no runtime errors.

## What to submit

Point your AI session at your completed `starter/src/quests.ts` and say
*"Review my solution for exercise 05."*

## Hints

- Stuck on the difficulty union type specifically? Re-read Lesson 09's
  `status: "open" | "closed"` example closely — `difficulty` here needs the
  exact same shape, just with three values instead of two, and reused in
  two different places (`Quest`'s own field, and `filterByDifficulty`'s
  second parameter) — consider whether repeating the literal union by hand
  in both places, or referencing `Quest["difficulty"]` from the interface
  directly in the function signature, is more maintainable if the list of
  difficulties ever changes.
- Stuck on why `findQuestByName`'s result needs `?.`/`??` at the call site?
  Recall Lesson 08's exact reasoning — a `Quest | undefined` return type
  means TypeScript will genuinely refuse to let you access `.name` (or
  anything else) directly on the result without first handling the
  `undefined` case, exactly the way it should.
- Stuck on what real object literal satisfies `Quest` exactly? Re-read
  Lesson 09's `dragonQuest` example and its deliberate "missing property"
  demonstration — the same `error TS2741` message will appear if you leave
  a required field out of one of your `sampleQuests` entries.
- If you've re-read Lesson 09's relevant section and are still stuck, ask
  your AI session for a hint — Level 1 first, per
  [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md).
