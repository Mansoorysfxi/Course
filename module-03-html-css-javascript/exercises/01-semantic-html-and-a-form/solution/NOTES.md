# Notes on grading this yourself before asking for review

Open `index.html` directly in your browser (double-click it, or `start
index.html` from Git Bash) and check each item below against what you built
in `starter/index.html`.

- **Semantic structure** — confirm you have exactly one `<h1>` (inside
  `<header>`), and that `<nav>`, `<main>`, and `<footer>` each appear exactly
  once. This solution also uses two `<section>` elements inside `<main>` for
  the quest list and the form — `<section>` is the right choice here because
  each one is a thematically distinct, headed group of content that isn't
  itself an independently-distributable "article."
- **The label/input pairing is the single most important thing to check.**
  Click directly on the *text* "Quest name" (not the input box itself) in
  your browser — the text field should visibly get focus/a cursor. If it
  doesn't, your `for`/`id` pair has a typo somewhere. Do this for every
  field: the text input, the select, the textarea, and the checkbox.
- **Required-field validation** — leave "Quest name" empty and click "Add
  Quest." Your browser should refuse to submit and show its own built-in
  validation bubble pointing at the empty field, with zero JavaScript
  involved. If clicking the button does nothing visible at all, check that
  `required` is spelled correctly and that the button really is
  `type="submit"` inside the `<form>`.
- **The list is a real list.** Inspect the "Active Quests" section — it must
  be `<ul>`/`<li>` elements, not one `<p>` with commas. A screen reader
  announces "list, 3 items" only for the real thing.
- **`<button type="submit">`, not a bare `<button>`.** A bare `<button>`
  inside a `<form>` defaults to `type="submit"` anyway, so behaviorally this
  solution's explicit version and an omitted one currently look identical —
  the real reason this is checked is to build the habit *now*, before Lesson
  06 has you add a second, non-submitting button (like a "Cancel" or
  "Clear") to a form and the missing explicit `type` becomes an actual bug.
