# Exercise 03 — DOM Manipulation and Events: A Working Quest Tracker

**Difficulty:** Guided — the HTML and CSS are already complete;
`starter/script.js` has function signatures and `// TODO` comments for
every piece of behavior. This exercise turns the static Lesson 01 form
concept into a genuinely interactive page, using only what
[`lessons/06-the-dom-and-events.md`](../../lessons/06-the-dom-and-events.md)
taught — no `fetch`, no TypeScript yet.

**Concepts this exercise uses** (all taught in Lesson 06, building on
Lesson 05's fundamentals): `document.querySelector`, `textContent` vs.
`value`, `document.createElement`/`appendChild`/`.remove()`, `classList.add`/
`toggle`, `addEventListener` for `"submit"` and `"click"`, `event.preventDefault()`,
and reading a form field's current value.

## What to build

Open [`starter/index.html`](starter/index.html) and
[`starter/styles.css`](starter/styles.css) — both complete, no changes
needed. Open [`starter/script.js`](starter/script.js) and implement each
`// TODO`-marked function so that:

1. **Submitting the form adds a new quest to the list**, without reloading
   the page (`event.preventDefault()`), reading the quest name and
   difficulty from the form fields, and **clears the form fields** after
   adding.
2. **Each quest list item shows its name and difficulty**, and has two
   buttons: "Complete" and "Delete."
3. **Clicking "Complete" toggles a `completed` CSS class** on that quest's
   list item (already styled in `styles.css` — strikethrough text) — click
   it again and it un-completes, using `classList.toggle`.
4. **Clicking "Delete" removes that quest's list item from the page
   entirely** — using `.remove()`, not just hiding it with CSS.
5. **Submitting the form with an empty quest name does nothing** (no blank
   quest gets added) — you may rely on the `required` attribute already on
   the input for this, but confirm it's still there and working.

## Acceptance criteria

- [ ] Adding a quest via the form does **not** reload the page.
- [ ] A newly added quest appears in the list immediately, showing the exact
  name and difficulty you typed/selected.
- [ ] The form's fields are empty again immediately after a successful add.
- [ ] Clicking "Complete" on a quest visually strikes it through; clicking it
  again removes the strikethrough (toggle, not one-way).
- [ ] Clicking "Delete" on a quest removes it from the page; the item is
  genuinely gone from the DOM (confirm in DevTools' Elements panel, not just
  visually hidden).
- [ ] Adding several quests in a row and then deleting one from the middle
  correctly leaves the others intact and in the same order.
- [ ] No use of `innerHTML` anywhere in your script (Lesson 06's security
  note) — build new elements with `createElement`/`textContent` only.

## What to submit

Point your AI session at your completed `starter/script.js` and say *"Review
my solution for exercise 03."*

## Hints

- Stuck on how one "Complete"/"Delete" button click handler knows *which*
  quest's `<li>` it belongs to? Attach the listener to the button at the
  moment you create that specific quest's `<li>` (inside the same function
  that builds the whole item) — the button and its own `<li>` are both
  available as local variables right there, before you ever add them to the
  page. Re-read Lesson 06's "creating and removing elements" section.
- Stuck on why your new quest's fields don't clear after adding? You likely
  read `.value` correctly but never *set* `.value = ""` afterward on each
  field — reading and clearing are two separate steps.
- Stuck on why nothing happens when you click "Complete"? Confirm you
  actually called `addEventListener("click", ...)` on the *button itself*,
  not on the `<li>` or the whole list — and confirm the class name you're
  toggling (`"completed"`) exactly matches the one styled in `styles.css`
  (case-sensitive).
- If you've re-read Lesson 06's relevant section and are still stuck, ask
  your AI session for a hint — Level 1 first, per
  [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md).
