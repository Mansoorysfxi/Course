# Lesson 03 — CSS: Flexbox (One-Dimensional Layout)

## What you'll learn

- The specific layout problem Flexbox solves, and why plain block/inline flow (the browser's default) can't do it cleanly.
- How to turn any container into a flex container, and what changes immediately when you do.
- The main axis vs. the cross axis, and every property that controls alignment along each one.
- How individual flex items can grow, shrink, or take a fixed size, and what actually controls that.
- A direct, explicit comparison to UMG's anchors and slots, since you already have a working mental model for "arranging widgets" from Unreal.

## Why this matters

Almost every row of buttons, every navbar, every card layout, every "space these things evenly" requirement you'll ever build uses Flexbox. It's the default tool for one-dimensional layout (a single row or a single column) — Grid (next lesson) is for two-dimensional layout (rows *and* columns together) — and knowing which one fits a given layout problem, rather than fighting the wrong tool, is a real, practical skill you'll use in literally every module from here through the rest of this course, including every React component you'll ever style.

## Prerequisites

Lesson 02 (the box model) — Flexbox arranges the exact same content/padding/border/margin boxes Lesson 02 taught; it doesn't change what a box *is*, only how a group of boxes are positioned relative to each other.

## The concept, explained simply

By default, HTML elements lay out in **normal flow**: block-level elements (like `<div>`, `<p>`, `<form>`) stack vertically, one after another, each taking the full available width; inline elements (like `<a>`, `<span>`) flow horizontally within a line, wrapping like text. This default is fine for a document of paragraphs, but it has no real answer for "put these three boxes in a row, evenly spaced" or "center this one thing both horizontally and vertically" — normal flow simply wasn't designed for that, and pre-Flexbox CSS required genuinely awkward workarounds (`float`, manual `margin` math) to fake it.

**Flexbox** (short for "Flexible Box Layout") is a layout *mode* you turn on for a container, which then arranges its direct children along a single line — either a row or a column, you choose — handling spacing, alignment, and (its namesake feature) letting items grow or shrink to fill available space, all through named properties instead of margin-math guesswork.

**Direct comparison to UMG, since you already have this exact mental model:** a **Horizontal Box** or **Vertical Box** panel in UMG arranges its child widgets along one axis, and each child slot has its own `Size` (Fill vs. Auto) and alignment/padding settings independent of the others — that is *precisely* what a flex container and its flex items do. `display: flex; flex-direction: row;` is CSS's Horizontal Box. `display: flex; flex-direction: column;` is CSS's Vertical Box. A flex item's `flex-grow` is UMG's "Fill" sizing (take a proportional share of remaining space); a flex item with no `flex-grow` at its natural size is UMG's "Auto" sizing (take only the space its content needs). If you've ever nested a Horizontal Box inside a Vertical Box to build a real UMG layout, you've already done, conceptually, exactly what nesting flex containers does in CSS.

## The details

### Turning a container into a flex container

```bash
cat > flex-practice.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Flexbox Practice</title>
  <style>
    * { box-sizing: border-box; }
    .toolbar {
      display: flex;
      background-color: #222;
      padding: 8px;
    }
    .toolbar button {
      margin-right: 8px;
      padding: 8px 16px;
    }
  </style>
</head>
<body>
  <div class="toolbar">
    <button>New Quest</button>
    <button>Filter</button>
    <button>Sort</button>
  </div>
</body>
</html>
EOF
```

Open `flex-practice.html` in your browser. **Expected result:** three buttons sitting in a row, evenly spaced by their own margins — before Flexbox, three `<button>` elements (which are inline-level by default) would still have ended up roughly in a row anyway, so this first example undersells Flexbox slightly on purpose — you're about to see what it does that plain inline flow genuinely cannot.

**Line by line:** `display: flex` is the one declaration that turns `.toolbar` into a **flex container** — the moment you add it, every *direct child* of `.toolbar` (the three `<button>`s) automatically becomes a **flex item**, arranged in a row by default, with no other changes needed. This single property is doing all the structural work here.

### The main axis and the cross axis

Flexbox thinks in exactly two axes, and almost every Flexbox property is "alignment along the main axis" or "alignment along the cross axis" — get comfortable with this pair of terms, since the property names build directly on them:

- **Main axis** — the direction items are laid out in, controlled by `flex-direction`. `row` (the default) makes the main axis horizontal, left to right. `column` makes it vertical, top to bottom.
- **Cross axis** — always perpendicular to the main axis. If the main axis is horizontal (`row`), the cross axis is vertical, and vice versa.

```css
.toolbar {
  display: flex;
  justify-content: space-between;  /* main-axis alignment */
  align-items: center;             /* cross-axis alignment */
}
```

Add these two lines to `.toolbar` and, to actually see the cross-axis effect, give the toolbar some height and one differently-sized item:

```css
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 80px;
  background-color: #222;
  padding: 8px;
}
```

Reload. **Expected result:** the three buttons now spread out with maximum space *between* them (not around the edges) — that's `justify-content: space-between` acting along the main (horizontal) axis — and every button is vertically centered within the 80px-tall toolbar, regardless of its own height — that's `align-items: center` acting along the cross (vertical) axis.

**Every common value for each property, since you'll reach for these constantly:**

`justify-content` (main-axis alignment/distribution of items):
- `flex-start` (default) — items packed at the start of the main axis.
- `flex-end` — items packed at the end.
- `center` — items packed together in the center.
- `space-between` — max space *between* items, none at the outer edges.
- `space-around` — equal space around *each* item (so edges get half as much visual gap as between-item gaps).
- `space-evenly` — genuinely equal space everywhere, including the outer edges.

`align-items` (cross-axis alignment, applied to all items at once):
- `stretch` (default) — items stretch to fill the container's cross-axis size.
- `flex-start` / `flex-end` / `center` — same meaning as above, applied to the cross axis instead.

**Try it yourself:** change `flex-direction: row` (add this explicitly) to `flex-direction: column` on `.toolbar`, keeping everything else the same. Predict, before reloading, which properties will visibly swap roles. **Expected:** `justify-content` now controls *vertical* spacing (since the main axis flipped to vertical) and `align-items` now controls *horizontal* alignment — this swap-on-direction-change is exactly why Flexbox uses axis-relative names ("main"/"cross") instead of absolute ones ("horizontal"/"vertical") in the first place.

### Individual flex-item sizing: grow, shrink, and `flex`

This is the property that gives Flexbox its name, and its closest direct analogy to UMG's Fill/Auto slot sizing:

```html
<div class="layout" style="display: flex; height: 300px; border: 2px solid #333;">
  <div style="background: lightcoral;">Sidebar (fixed)</div>
  <div style="background: lightblue; flex-grow: 1;">Main content (fills remaining space)</div>
</div>
```

**Line by line:** the sidebar `<div>` has no `flex-grow` set, so it defaults to `0` — it takes only the width its own content needs (an "Auto" slot, in UMG terms) and never grows to fill leftover space. The main-content `<div>` has `flex-grow: 1` — a positive growth factor tells it to consume *all remaining space* in the container after every other item has taken its natural size (a "Fill" slot, in UMG terms). Reload to see the sidebar stay content-sized while the main content visibly stretches to fill everything else.

`flex-grow`'s number is a **ratio**, not a fixed size, and this matters once more than one item wants to grow:

```html
<div style="display: flex;">
  <div style="flex-grow: 1; background: khaki;">1 share</div>
  <div style="flex-grow: 2; background: lightgreen;">2 shares</div>
</div>
```
The second box ends up exactly twice as wide as the first, because the *combined* remaining space is divided proportionally by each item's growth factor (1 + 2 = 3 total shares; item one gets 1/3, item two gets 2/3) — not because `2` means "twice a fixed width."

There's also `flex-shrink` (the mirror image — whether/how much an item is allowed to shrink below its natural size when the container is too small to fit everyone at natural size; defaults to `1`, meaning items *do* shrink by default) and a shorthand, `flex`, combining `flex-grow`, `flex-shrink`, and a base size in one declaration (`flex: 1 1 0;` is an extremely common real-world shorthand meaning "grow and shrink freely, starting from a base size of 0" — you'll see this exact shorthand throughout React/Tailwind work starting Module 04).

### `gap` — spacing between flex items, without margin math

```css
.toolbar {
  display: flex;
  gap: 8px;
}
```
`gap` puts consistent space *between* flex items (not around the outer edge, and with no margin-collapse quirks from Lesson 02) — this is the modern, preferred way to space out flex items, replacing the older pattern of putting `margin-right` on every item except the last one.

## Common mistakes & gotchas

- **Forgetting `display: flex` on the parent, then wondering why `justify-content`/`align-items` do nothing.** These properties only have any effect on an element that is itself a flex *container* — setting them on a random `<div>` with no `display: flex` is simply ignored.
- **Confusing `justify-content` and `align-items`.** A reliable memory aid: `justify-content` is always about the **main** axis (whichever direction `flex-direction` points); `align-items` is always about the **cross** axis. If you flip `flex-direction`, their visual effects swap too — this is expected, not a bug.
- **Applying flex properties to a *grandchild* instead of a direct child.** `display: flex` on `.toolbar` only turns `.toolbar`'s *direct* children into flex items — an element nested two levels deep is unaffected unless *its own* immediate parent is also a flex container.
- **Expecting `flex-grow: 2` to mean "twice as wide" in absolute terms.** It's a ratio applied to *leftover* space after natural sizes are accounted for, relative to other growing siblings' own factors — not a fixed multiplier of the container's total width.
- **Using Flexbox to force a full two-dimensional grid** (rows *and* columns that need to align with each other) by nesting flex containers and fighting widths to line things up. This is exactly the wrong tool for that job — Lesson 04 (Grid) is built specifically for genuine two-dimensional layouts, and reaching for it instead of nested Flexbox hacks will save you real pain.

## How this connects

You now have real one-dimensional layout skills — every row of buttons, every navbar, every "these three cards side by side" requirement in the rest of this course uses exactly what you just learned. Lesson 04 introduces Grid for the two-dimensional layouts Flexbox structurally can't do well (aligning items across *both* rows and columns simultaneously), and this module's capstone (the weather dashboard) uses both Flexbox and Grid together, each for the specific job it fits.

## Quick self-check

1. In your own words, map `display: flex; flex-direction: column;` onto its closest UMG equivalent.
2. What's the difference between the main axis and the cross axis, and which CSS property controls which one?
3. Given two flex items with `flex-grow: 1` and `flex-grow: 3` inside a container with leftover space, what fraction of that leftover space does each one get?
4. What does `flex-grow: 0` (the default) mean for an item's width, compared to `flex-grow: 1`?
5. Name one real layout problem where Flexbox is structurally the wrong tool, and say which lesson's tool fits it instead.
