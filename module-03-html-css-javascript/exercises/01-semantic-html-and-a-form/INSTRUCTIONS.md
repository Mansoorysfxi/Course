# Exercise 01 — Semantic HTML and a Quest Form

**Difficulty:** Very easy — this should be nearly impossible to fail if you've
read [`lessons/01-html-structure-forms-and-accessibility.md`](../../lessons/01-html-structure-forms-and-accessibility.md)
carefully. There is no CSS and no JavaScript in this exercise — it's entirely
about HTML structure, forms, and accessibility, exactly as taught in that one
lesson.

**Concepts this exercise uses** (all taught in Lesson 01): the document
skeleton (`<!DOCTYPE html>`, `<html lang>`, `<head>`, `<meta charset>`,
`<meta viewport>`, `<title>`), semantic layout elements (`<header>`, `<nav>`,
`<main>`, `<article>`, `<footer>`), heading levels, lists (`<ul>`/`<li>`), and
a real, accessible form (`<label for>`/`id` pairing, `<input>` types
including `required`, `<select>`/`<option>`, `<textarea>`, a checkbox, and a
`<button type="submit">`).

## What to build

Open [`starter/index.html`](starter/index.html) — it has the document
skeleton already filled in and a series of `<!-- TODO: ... -->` HTML comments
marking exactly what to add. Do not delete the TODO comments until you've
addressed what they ask for; leave the rest of the file structure as given.

Build a one-page "Quest Board" for QuestLog's in-universe world (this is
**not** the QuestLog web app itself — Module 04 builds that with React; this
is a standalone practice page) with:

1. A `<header>` containing an `<h1>` reading exactly `Quest Board`, and a
   `<nav>` containing at least two `<a>` links (they don't need to go
   anywhere real yet — `href="#"` is fine for this exercise).
2. A `<main>` containing:
   - At least **two** `<article>` elements, each representing one quest, each
     with its own heading (`<h2>`) and at least one `<p>` describing it.
   - A `<ul>` listing at least three "Active Quests" by name, using real
     `<li>` items (not comma-separated text in one `<p>`).
   - A real, accessible **form** for submitting a new quest, with:
     - A text `<input>` for the quest name, `required`, correctly paired
       with a `<label>` via matching `for`/`id`.
     - A `<select>` for difficulty, with at least three `<option>`s.
     - A `<textarea>` for optional notes, correctly labeled.
     - A checkbox for "Urgent," correctly labeled.
     - A `<button type="submit">` (not a bare `<button>` with no `type`).
3. A `<footer>` containing some real text (a copyright line is fine).

## Acceptance criteria

- [ ] The file opens in a browser with no visibly broken/garbled layout, and
  passes basic validity (every tag you opened is properly closed, in the
  correct nested order — Lesson 01's "Common mistakes" section).
- [ ] Exactly one `<h1>` exists on the page, inside `<header>`.
- [ ] `<nav>`, `<main>`, and `<footer>` are each used exactly once; at least
  two `<article>` elements exist inside `<main>`.
- [ ] Every `<input>`, `<select>`, `<textarea>`, and checkbox in the form has
  a `<label>` whose `for` exactly matches that field's `id` — clicking each
  label's text in the browser should focus/activate its field.
- [ ] The quest-name `<input>` has `required` — leaving it empty and clicking
  the submit button shows the browser's real, built-in validation message.
- [ ] The submit button has `type="submit"` explicitly written.
- [ ] The "Active Quests" list uses `<ul>`/`<li>`, not comma-separated text.
- [ ] `<meta charset="UTF-8">` and the viewport `<meta>` tag from Lesson 01
  are both present in `<head>`.

## What to submit

When you're ready for review, point your AI session at your completed
`starter/index.html` (or copy it elsewhere if you'd rather keep the starter
folder pristine) and say *"Review my solution for exercise 01."*

## Hints

- If you're unsure whether a tag is closed correctly, open the file in VS
  Code — its built-in HTML support will underline obviously mismatched tags.
- Stuck on why clicking a label doesn't focus its field? Double-check the
  exact spelling of `for="..."` against the field's `id="..."` — a common
  typo (e.g. `quest-name` vs. `questName`) is the usual cause, and it fails
  silently with no error message at all.
- Stuck on what "at least two different kinds of content" inside `<main>`
  should look like? Re-read Lesson 01's semantic table — `<article>` is for
  one self-contained quest description; the `<ul>` is a different, simpler
  kind of content (a plain list), and the form is a third, distinct kind
  (user input) — all three legitimately coexist inside one `<main>`.
- If you've re-read Lesson 01's relevant section and are still stuck, ask
  your AI session for a hint — Level 1 first, per
  [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md).
