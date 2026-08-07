# Exercise 01 — Components, Props, and JSX

**Lesson:** [`lessons/01-why-react-components-props-and-jsx.md`](../../lessons/01-why-react-components-props-and-jsx.md). Read the whole lesson before starting — every concept below is taught there, in full, with a runnable example nearly identical to this one.

**Difficulty:** Very easy — this is Module 04's first exercise. If you've read the lesson, this should be close to a direct copy of its own example, with different names.

## Concepts this exercise uses

- A component as a plain function that returns JSX.
- Typed props via a TypeScript `interface`, destructured in the function's parameter list.
- Composing one component inside another (`QuestCard` renders `PriorityBadge`).
- Rendering a list of components from an array with `.map()` (already done for you in `App.tsx` — you don't need to write this part, just understand it).

## What's already done for you

`src/App.tsx` is complete and will not need any changes. It defines a hardcoded array of quest-like objects and maps over it, rendering one `<QuestCard>` per item. **It will not compile yet** — open a terminal in this `starter/` folder and try:

```bash
npm install
npm run dev
```

You'll see a TypeScript error naming `QuestCard` and a missing `title` property. That's expected — `QuestCard` doesn't exist as a real component yet.

## What to build

### Step 1 — `src/components/PriorityBadge.tsx`

Open this file — it has a stub with detailed TODO comments. Replace the stub with a real component that:
- Accepts one prop, `priority`, typed as `"low" | "medium" | "high"`.
- Returns a `<span className="badge">` containing the priority text.

### Step 2 — `src/components/QuestCard.tsx`

Open this file — same deal, a stub with TODO comments. Replace it with a real component that:
- Accepts three props: `title` (`string`), `priority` (`"low" | "medium" | "high"`), `questLine` (`string`).
- Returns a `<div className="card">` containing an `<h3>` with the title, a `<PriorityBadge priority={priority} />`, and a `<p className="muted">` with the quest line.

## Acceptance criteria

- [ ] `npm run dev` starts with **zero** TypeScript errors.
- [ ] The page shows three cards, one per hardcoded quest, each with a title, a priority badge, and a quest line.
- [ ] `PriorityBadge` is its own component, actually used *inside* `QuestCard` (not copy-pasted into `QuestCard` directly).
- [ ] Both components have an explicit, named TypeScript type/interface for their props — no `any`.
- [ ] `npm run build` completes with zero errors.

## What to submit

Point your AI session at your completed `starter/` folder (or wherever you copied it to work in) and say *"Review my solution for exercise 01."*

## Hints

**Level 1:** Re-read the lesson's own worked example end to end — this exercise asks for almost the exact same shape, with different prop names and different JSX inside the returned `<div>`.

**Level 2:** A component with typed props looks like this shape (fill in your own names/types):
```tsx
interface SomeComponentProps {
  someProp: string;
}

export function SomeComponent({ someProp }: SomeComponentProps) {
  return <div>{someProp}</div>;
}
```
`PriorityBadge` and `QuestCard` both follow this exact shape — they just have different prop names/types and different JSX inside the `return`.

**Level 3 (near-answer):** `QuestCard`'s JSX needs three things inside its `<div className="card">`: an `<h3>{title}</h3>`, a `<PriorityBadge priority={priority} />` (remember to `import { PriorityBadge } from "./PriorityBadge";` at the top of the file), and a `<p className="muted">{questLine}</p>`. If you're still stuck after this, ask your AI session for the full solution rather than guessing further.
