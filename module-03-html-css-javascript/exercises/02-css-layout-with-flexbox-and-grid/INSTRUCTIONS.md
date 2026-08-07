# Exercise 02 — CSS Layout with the Box Model, Flexbox, and Grid

**Difficulty:** Easy/guided — the HTML structure is already given and
correct; your job is entirely CSS, in `starter/styles.css`, guided by
`/* TODO */` comments matching specific sections of
[`lessons/02-css-the-box-model.md`](../../lessons/02-css-the-box-model.md),
[`lessons/03-css-flexbox.md`](../../lessons/03-css-flexbox.md), and
[`lessons/04-css-grid-and-responsive-design.md`](../../lessons/04-css-grid-and-responsive-design.md).

**Concepts this exercise uses:** the universal `box-sizing: border-box`
reset (Lesson 02), the box model (padding/border/margin, Lesson 02), Flexbox
for one-dimensional rows (`display: flex`, `justify-content`, `align-items`,
`gap`, Lesson 03), CSS Grid for the overall two-dimensional page layout
(`display: grid`, `grid-template-columns`/`rows`, `fr`, `grid-column`,
Lesson 04), and a mobile-first `@media (min-width: ...)` responsive
breakpoint (Lesson 04).

## What to build

Open [`starter/index.html`](starter/index.html) — a complete, unstyled
"Quest Dashboard" page (a `<header>`, a `<nav>` toolbar, a sidebar `<aside>`
list of filters, a `<main>` grid of quest cards, and a `<footer>`). Do not
edit the HTML. Open [`starter/styles.css`](starter/styles.css) — it has
`/* TODO */` comments marking exactly what to add — fill in each one.

1. **Box model reset:** add the universal `box-sizing: border-box` rule as
   the very first rule in the file.
2. **The `.toolbar` (inside `<nav>`):** make it a flex container, its links
   laid out in a row, evenly spaced with `justify-content: space-between`,
   vertically centered with `align-items: center`.
3. **The `.quest-card` elements (inside `<main>`):** give each one padding,
   a border, and a background color of your choice, using the box model
   correctly (confirm with DevTools that your chosen `width` renders as the
   *true* width, thanks to `border-box`).
4. **The overall `.dashboard` page layout:** make it a **Grid** container
   with a header row, a row containing the sidebar and main content
   side-by-side, and a footer row — matching the structure taught in Lesson
   04's dashboard example. On narrow screens (below `768px`), the sidebar
   and main content should **stack** vertically instead (mobile-first: this
   stacked, single-column layout should be your *default*, unconditional
   CSS, with the side-by-side version added inside a `@media (min-width:
   768px)` block).
5. **The `.quest-list` (inside `<main>`):** lay the quest cards out with
   Grid, using `repeat(auto-fit, minmax(220px, 1fr))` for the columns, with
   a sensible `gap`.

## Acceptance criteria

- [ ] `* { box-sizing: border-box; }` is the first rule in the file.
- [ ] The toolbar's links are visibly in a row, evenly spaced, vertically
  centered — inspect `.toolbar` in DevTools and confirm `display: flex` is
  applied.
- [ ] Each `.quest-card` has visible padding and a border; inspecting one in
  DevTools' box-model tooltip shows its rendered width matches whatever
  `width` you set in CSS, exactly (proving `border-box` is working).
- [ ] `.dashboard` is a Grid container; resizing the browser (or using
  DevTools' device toolbar) below 768px visibly stacks the sidebar above/below
  the main content instead of beside it, and above 768px they sit side by
  side.
- [ ] `.quest-list` uses `repeat(auto-fit, minmax(220px, 1fr))` (or an
  equivalent that produces the same self-adjusting behavior) — resizing the
  window should change how many cards fit per row with no media query
  needed for this specific piece.
- [ ] No inline `style="..."` attributes were added to `index.html` — all
  styling lives in `styles.css`.

## What to submit

Point your AI session at your completed `starter/styles.css` and say
*"Review my solution for exercise 02."*

## Hints

- If `justify-content`/`align-items` seem to do nothing on `.toolbar`,
  re-read Lesson 03's first gotcha — confirm `display: flex` is actually
  set on `.toolbar` itself, not on `<nav>` or some other ancestor.
- If your grid columns don't seem to respect `1fr`, double check you didn't
  accidentally write `1f` or forget the `repeat(...)` parentheses — small
  typos in Grid track syntax fail silently (the browser just ignores the
  malformed value and falls back to a default) rather than throwing a
  visible error.
- If the mobile/desktop stacking doesn't switch at exactly 768px, confirm
  you have the viewport `<meta>` tag in `index.html`'s `<head>` (it's already
  there in the starter — just confirm you didn't remove it) and that you're
  testing with DevTools' device toolbar, not just narrowing your desktop
  browser window slightly (which still works, but is easy to misjudge by eye).
- Stuck after re-reading the relevant lesson section? Ask your AI session for
  a hint — Level 1 first, per [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md).
