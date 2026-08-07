# Lesson 04 — CSS: Grid and Responsive Design

## What you'll learn

- What CSS Grid is, when it's the right tool over Flexbox, and how to build a real two-dimensional layout with it.
- `grid-template-columns`/`grid-template-rows`, the `fr` unit, and `repeat()`.
- Placing items into specific grid cells, and letting items span multiple rows/columns.
- What **responsive design** actually means, and how to build it with **media queries** — including the specific, mobile-first way this course teaches them.
- A direct comparison of CSS's responsive layout systems to UMG's `Anchor Panel`/`Size Box`/`Scale Box`, since "does this layout adapt to different screen sizes" is a problem you've already solved in a different context.

## Why this matters

Real pages are two-dimensional: a page header, a sidebar, a main content area, and a footer, all needing to align with each other both horizontally *and* vertically — exactly what Lesson 03 flagged Flexbox as structurally the wrong tool for. And every page you build in this course, starting with this module's capstone, has to work believably on a phone screen and a desktop monitor — "responsive design" isn't a nice-to-have feature, it's the baseline expectation for any real website in 2026, since the majority of web traffic worldwide is mobile.

## Prerequisites

Lessons 02–03 (box model, Flexbox). Grid arranges the same kind of boxes Flexbox does, and several concepts carry over directly (`gap`, `justify-content`/`align-items` mean almost the same thing, applied to two axes instead of one).

## The concept, explained simply

**CSS Grid** lets you define an explicit grid — a fixed number of rows and columns, with specific sizes — on a container, and then place child elements into specific cells (or let them auto-place in order), with full control over how many rows/columns an item spans. Where Flexbox is "arrange items along one line, letting them grow/shrink to fill it," Grid is "define a genuine two-dimensional grid of cells first, then place things into it" — a fundamentally different mental model, not just "Flexbox with an extra dimension bolted on."

**Direct comparison to UMG:** Grid's closest UMG relative is the **Grid Panel** widget — you define explicit rows and columns with their own sizes, then assign each child widget to a specific row/column (and optionally have it span several), exactly like CSS Grid's `grid-template-columns`/`grid-template-rows` plus placing items into named cells. If you've ever built a UMG inventory grid or a stat-block layout with a Grid Panel, you already have direct hands-on intuition for what CSS Grid is doing.

**Responsive design**, separately, is the practice of a layout *adapting* to the size of the screen/window it's displayed in — a sidebar that sits beside the main content on a wide desktop screen might need to stack *above* it on a narrow phone screen instead. UMG's closest tool for "adapt to different screen sizes" is the combination of **Anchors** (pinning a widget's edges to proportional positions within its parent, rather than fixed pixel coordinates) and **Scale Box**/**Size Box** (constraining or scaling content to fit available space) — the *goal* (one layout definition that behaves sensibly across different container sizes) is the same goal CSS responsive design solves, even though the specific mechanism (media queries, covered below) works differently.

## The details

### A basic grid

```bash
cat > grid-practice.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Grid Practice</title>
  <style>
    * { box-sizing: border-box; }
    .dashboard {
      display: grid;
      grid-template-columns: 200px 1fr;
      grid-template-rows: 60px 1fr 40px;
      gap: 8px;
      height: 100vh;
    }
    .header  { background: steelblue;   grid-column: 1 / 3; }
    .sidebar { background: lightcoral; }
    .main    { background: lightyellow; }
    .footer  { background: #333; color: white; grid-column: 1 / 3; }
  </style>
</head>
<body>
  <div class="dashboard">
    <div class="header">Header (spans both columns)</div>
    <div class="sidebar">Sidebar</div>
    <div class="main">Main content</div>
    <div class="footer">Footer (spans both columns)</div>
  </div>
</body>
</html>
EOF
```

Open `grid-practice.html`. **Expected result:** a full classic dashboard layout — a header bar spanning the full width, a sidebar and main content side by side below it, and a footer spanning the full width at the bottom — built with zero manual pixel math.

**Line by line:**
- `display: grid` — turns `.dashboard` into a **grid container**, the direct equivalent of `display: flex` from Lesson 03, but activating the two-dimensional grid layout mode instead of the one-dimensional flex mode.
- `grid-template-columns: 200px 1fr;` — defines exactly two columns: the first is a fixed `200px`, the second is `1fr`. **The `fr` unit ("fraction") means "one share of whatever space is left over"** after fixed-size tracks (like the `200px` sidebar column) are accounted for — directly analogous to Lesson 03's `flex-grow` ratio, just applied to defining grid tracks instead of sizing flex items. `1fr` here means "the second column takes 100% of whatever space remains after the 200px column is subtracted."
- `grid-template-rows: 60px 1fr 40px;` — same idea, for rows: a fixed 60px header row, a flexible middle row taking all remaining vertical space, and a fixed 40px footer row.
- `gap: 8px;` — spacing between grid cells, in both directions — the exact same property name as Flexbox's `gap` from Lesson 03, doing the analogous job.
- `grid-column: 1 / 3;` on `.header` and `.footer` — this is **placement syntax**, telling an item to span from grid line 1 to grid line 3. Grid lines are numbered starting at `1`, *between* tracks — with two columns, there are three vertical grid lines (before column 1, between the columns, after column 2), so `1 / 3` means "start at the very first line, end at the very last line" — i.e., span both columns entirely. This is precisely the UMG Grid Panel "span multiple columns" behavior.
- `height: 100vh;` — `vh` is a **viewport unit**: `1vh` equals 1% of the browser window's visible height, so `100vh` fills the entire visible viewport height regardless of the actual screen size — you'll use `vh`/`vw` (viewport width) constantly for "fill the whole screen" layouts, since a fixed pixel height obviously wouldn't adapt across different monitors/phones.

`repeat()` is a shorthand worth knowing immediately, since you'll use it constantly for evenly-sized columns:
```css
grid-template-columns: repeat(3, 1fr);
```
is exactly equivalent to writing `1fr 1fr 1fr` by hand — three equal-width columns. `repeat(auto-fit, minmax(200px, 1fr))` is an especially useful, very common real-world pattern: "as many columns as fit, each at least 200px wide, sharing remaining space equally" — a self-adjusting card grid with zero media queries needed, which you'll use directly in this module's exercises.

### Media queries: the mechanism behind responsive design

A **media query** is a CSS block that only applies its rules when a stated condition about the browser/device is true — most commonly, the viewport's width:

```css
.dashboard {
  display: grid;
  grid-template-columns: 1fr;   /* mobile default: single column, stacked */
  grid-template-rows: 60px auto auto 40px;
}

@media (min-width: 768px) {
  .dashboard {
    grid-template-columns: 200px 1fr;   /* wider screens: sidebar + main, side by side */
    grid-template-rows: 60px 1fr 40px;
  }
}
```

**Line by line:** `@media (min-width: 768px) { ... }` means "only apply the CSS rules inside these braces when the browser's viewport is at least 768 pixels wide." Everything *outside* a media query applies unconditionally, as a baseline; rules *inside* one only take effect once that condition is met.

**This example demonstrates "mobile-first" responsive design specifically, which is the approach this course teaches deliberately:** the base (unconditional) rules describe the **narrowest** layout — a single stacked column, sensible on a phone — and `min-width` media queries *add* more elaborate layouts as the screen gets wider. This is the opposite of writing a desktop layout first and then trying to "undo" it for mobile with `max-width` queries. Mobile-first is the current, dominant real-world convention because (a) starting simple and adding complexity as space allows is generally easier to reason about than starting complex and stripping things away, and (b) it naturally guarantees every page has at least a working, legible baseline layout on the narrowest, most constrained screens, since that's what you designed first rather than as an afterthought.

Since the `<meta name="viewport" ...>` tag from Lesson 01 tells mobile browsers to render at their true device width (rather than a zoomed-out fake desktop width), media queries can now reliably detect and respond to a phone's actual narrow viewport — this is exactly why that `<meta>` tag matters, and why omitting it breaks responsive design even if your media queries are otherwise correct.

**Try it yourself:** build the full mobile-first example above in a new file, `responsive-practice.html`. Open it in your browser, then open DevTools (`F12`) and toggle **Device Toolbar** (the small phone/tablet icon, or `Ctrl+Shift+M`) to simulate different screen widths. Drag the width slider slowly across 768px and watch the layout genuinely restructure — sidebar and main content should snap from stacked (narrow) to side-by-side (wide) right at your breakpoint.

**Common, sensible breakpoint values** (not a rigid law — pick values that fit your actual content, but these show up constantly in real projects and are a fine default to start from): `480px` (small phones vs. larger phones), `768px` (phone vs. tablet), `1024px` (tablet vs. desktop).

### Grid vs. Flexbox — a direct decision rule

Given how much these two tools overlap in casual conversation, here's a concrete rule you can apply immediately: **if you're arranging items along a single row or column, and don't need items in one row to line up with items in a different, unrelated row, use Flexbox. If you need a genuine two-dimensional structure — rows and columns that need to align with each other as a coherent grid — use Grid.** A card layout of unknown, varying-height cards that should still line up into neat rows and columns is Grid's job; a toolbar, a navbar, or "these three buttons in a row" is Flexbox's job. Nesting one inside the other is completely normal and extremely common in real code — a Grid-based page layout with a Flexbox-based toolbar inside one of its cells, for instance.

## Common mistakes & gotchas

- **Using `max-width` media queries and writing the desktop layout first**, then trying to override it back down for mobile. Works, but fights the mobile-first convention this course (and the overwhelming majority of real production CSS) uses — expect confusion translating between your own code and any real-world example you read online if you build the habit backwards.
- **Forgetting the viewport `<meta>` tag from Lesson 01.** Without it, mobile browsers render at a fake zoomed-out width, and your `min-width` breakpoints will trigger at the wrong moments (or never, or always) relative to what the phone's user actually sees.
- **Confusing grid line numbers with the number of tracks.** With 3 columns, there are **4** grid lines (1, 2, 3, 4), not 3 — `grid-column: 1 / 4` spans all three columns; `1 / 3` spans only the first two.
- **Using Grid for a simple single-row toolbar**, or fighting nested Flexbox containers to fake a real aligned grid. Apply the decision rule above rather than defaulting to whichever tool you happen to remember better.
- **Testing responsiveness only by resizing the actual desktop browser window**, rather than using DevTools' device toolbar or an actual phone. Desktop window resizing tests real breakpoints fine, but it can hide real mobile-only issues (touch target sizing, actual device viewport quirks) — get in the habit of checking the device toolbar, at minimum, before considering a layout "responsive."

## How this connects

You now have both of CSS's major layout tools (Flexbox, Grid) and the mechanism (media queries) for making any layout adapt across screen sizes. This module's capstone weather dashboard uses Grid for its overall page structure and Flexbox for smaller internal groupings (exactly the "nest one inside the other" pattern described above), with a mobile-first media query making it usable on a phone-width screen — everything Lessons 02–04 taught, combined in one real project. Lesson 05 shifts entirely from layout/appearance to *behavior* — JavaScript — which is what makes a page actually respond to a user doing something, rather than just sitting there looking right.

## Quick self-check

1. What does the `fr` unit mean in `grid-template-columns`, and what's its closest Flexbox equivalent concept?
2. Given a 3-column grid, how many vertical grid lines exist, and what `grid-column` value spans all three columns?
3. State, in one sentence, the decision rule for choosing Grid over Flexbox for a given layout.
4. What does "mobile-first" responsive design mean specifically, and which kind of media query (`min-width` or `max-width`) does it rely on as its primary building block?
5. Why does omitting the viewport `<meta>` tag from Lesson 01 break responsive design, even with otherwise-correct media queries?
