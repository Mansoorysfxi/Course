// TODO (Exercise 01, Step 2): QuestCard
//
// See lessons/01-why-react-components-props-and-jsx.md for everything
// this file needs.
//
// Build a component named `QuestCard` that:
//   1. Accepts three props: `title` (string), `priority`
//      ("low" | "medium" | "high"), and `questLine` (string). Define a
//      TypeScript `interface` for these props (Module 03, Lesson 09
//      already taught you `interface` -- this is the exact same feature,
//      just describing a component's props instead of an API response).
//   2. Renders:
//      - a <div className="card">, containing:
//        - an <h3> with the quest's title
//        - a <PriorityBadge priority={priority} /> (import it from
//          "./PriorityBadge" -- you're composing the component you just
//          built into this one, exactly as the lesson describes)
//        - a <p className="muted"> with the quest's questLine
//
// This is "composition": QuestCard doesn't know or care how
// PriorityBadge renders its priority internally -- it just uses it,
// exactly like calling any other function.
//
// Delete everything below this line and write the real thing.

export function QuestCard() {
  return null;
}
