# Lesson 02 — CSS: Selectors, the Cascade, and the Box Model

## What you'll learn

- What CSS actually is, how it attaches to HTML, and the three ways to write it (and why this course uses only one of them).
- Selectors: how to target exactly the elements you mean to style.
- The **cascade** and **specificity** — what happens when multiple rules could apply to the same element, and which one wins.
- The **box model**: every element on a page is a rectangular box made of content, padding, border, and margin — and precisely how each one affects layout.
- `box-sizing`, and why its default value causes a genuinely common, confusing bug.

## Why this matters

Every visual decision you'll ever make in a browser — spacing, sizing, borders, colors, alignment — is CSS. Flexbox and Grid (Lessons 03–04) are *built on top of* the box model this lesson teaches; skipping straight to "make a nice layout" without understanding what padding, border, and margin actually do to an element's true size is exactly how beginners end up with layouts that mysteriously overflow their containers by a few pixels and have no idea why.

## Prerequisites

Lesson 01 (HTML) — this lesson styles the exact HTML you already built.

## The concept, explained simply

**CSS (Cascading Style Sheets)** is a separate language from HTML, with a completely different job: HTML says *what* something is; CSS says *how it should look*. A **rule** in CSS has two parts: a **selector** (which element(s) this rule applies to) and a **declaration block** (what to actually change about them):

```css
p {
  color: navy;
  font-size: 18px;
}
```

`p` is the selector (target every `<p>`); `color` and `font-size` are **properties**, each given a **value**. Read this as: "for every paragraph, set its text color to navy and its font size to 18 pixels."

Here's the analogy that maps directly onto Unreal territory: think of an HTML element roughly like an Unreal **Widget** in UMG, and CSS roughly like the **Style** properties you'd set on that widget (padding, brush color, size) — separate from the widget's actual structural hierarchy (its parent/child slots, which is HTML's job) and separate from what happens when you click it (which is JavaScript's job, starting Lesson 05). You'll meet a much more direct UMG comparison specifically for *layout* in Lessons 03–04 (Flexbox/Grid vs. UMG's anchors and slots) — this lesson's box model is the foundation those build on.

## The details

### The three ways to write CSS (and which one this course uses)

1. **Inline**, directly on an element via a `style` attribute: `<p style="color: navy;">`. Avoid this — it mixes structure and style back together (exactly the separation CSS exists to provide), and it's painful to reuse or override.
2. **Internal**, inside a `<style>` block in the HTML `<head>`. Fine for tiny, throwaway examples; still mixes concerns for anything real.
3. **External**, in a separate `.css` file, linked from HTML. **This is what real projects use, and what this course uses from here on.**

Set this up now:

```bash
cd ~/html-practice
cat > styles.css << 'EOF'
body {
  font-family: sans-serif;
  margin: 0;
}
EOF
```

Edit `index.html`'s `<head>` to add one line, right after `<title>`:
```html
<link rel="stylesheet" href="styles.css">
```

**Line by line:** `<link>` is a void element (Lesson 01 — no closing tag) that connects an external resource to this page; `rel="stylesheet"` says *what kind* of resource; `href` says *where to find it* — the exact same attribute name you already met on `<a>` in Lesson 01, doing the analogous job of "where does this point to." Reload `index.html` in your browser — the font should visibly change to a plain sans-serif face, proving the external file is actually connected.

### Selectors

```css
/* Element selector — targets every <p> */
p { color: navy; }

/* Class selector — targets every element with class="quest-card" */
.quest-card { border: 1px solid gray; }

/* ID selector — targets the one element with id="quest-name" */
#quest-name { font-weight: bold; }

/* Descendant selector — targets <a> elements specifically inside <nav> */
nav a { text-decoration: none; }
```

**Line by line:** a **class** (`class="quest-card"` in HTML, targeted with a leading `.` in CSS) is a reusable label — many elements can share the same class, and one element can have several classes separated by spaces (`class="quest-card urgent"`). An **ID** (`id="quest-name"`, targeted with a leading `#`) must be unique on the page — you already used `id` in Lesson 01 to pair `<label for>` with an `<input>`; here you're seeing its *other* common use, as a styling/targeting hook, though in practice classes are used for styling far more often than IDs (reserve IDs for one-of-a-kind elements, like Lesson 01's form fields, or as JavaScript targets in Lesson 06). A **descendant selector** (`nav a`, with a space between two selectors) targets elements matching the second selector *nested anywhere inside* an element matching the first — not necessarily a direct child.

Add classes to your form from Lesson 01 and try each selector type — open `index.html`, add `class="quest-card"` to the outer `<form>`, then in `styles.css`:
```css
.quest-card {
  border: 2px solid steelblue;
  padding: 16px;
  max-width: 400px;
}
```
Reload and confirm a visible bordered, padded box now wraps your form.

### The cascade and specificity — what wins when rules conflict

**"Cascading"** in the name refers to what happens when more than one rule could apply to the same element: CSS doesn't error out or pick arbitrarily — it follows deterministic rules to decide which declaration wins.

```css
p { color: navy; }
.highlight { color: crimson; }
```
```html
<p class="highlight">Which color wins?</p>
```
**Answer: crimson.** A class selector has higher **specificity** than a plain element selector — CSS ranks selector types by how *specific* they are (roughly, from lowest to highest: element selectors, class selectors, ID selectors, inline `style` attributes), and the more specific selector wins regardless of which rule appears earlier or later in the file. If two rules have *equal* specificity, then **source order** is the tiebreaker — whichever rule appears later in the CSS wins. This is the actual mechanical reason "just move my rule to the bottom of the file" sometimes visibly "fixes" a styling bug — the real fix, though, is understanding *why* an equal-or-lower-specificity rule was losing in the first place, not developing a habit of blindly reordering CSS until something happens to work.

**Try it yourself:** add a third rule, `#quest-name { color: green; }`, and give one specific `<input>` (from Lesson 01's form) `id="quest-name"`. Predict which color wins against a `.highlight` class also applied to the same element, before checking — an ID beats a class, so green should win regardless of source order.

### The box model

**Every single element on a page is, structurally, a rectangular box** — even ones that don't look boxy, like text or a circular avatar image (a "circle" is just a square box with rounded corners, a CSS technique you'll meet later). Every one of these boxes is built from four concentric layers, from the inside out:

```
┌─────────────────── margin ───────────────────┐
│ ┌─────────────── border ──────────────────┐  │
│ │ ┌───────────── padding ───────────────┐ │  │
│ │ │                                     │ │  │
│ │ │            content                 │ │  │
│ │ │                                     │ │  │
│ │ └─────────────────────────────────────┘ │  │
│ └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

- **Content** — the actual text/image/whatever the element holds, sized by `width`/`height` (or its natural size, if you set neither).
- **Padding** — space *inside* the border, between the border and the content. Padding is "inside the box" — it shares the element's own background color.
- **Border** — a visible (or invisible, `border: none`) line drawn exactly at the edge between padding and margin.
- **Margin** — space *outside* the border, pushing neighboring elements away. Margin is always transparent — it's not part of the element's own visual box at all, just breathing room around it.

See this directly:

```css
.quest-card {
  border: 2px solid steelblue;
  padding: 16px;
  margin: 24px;
  background-color: aliceblue;
  max-width: 400px;
}
```

Reload the page. **What you should observe:** the blue border sits right at the edge of the light-blue background — that background fills the *content + padding* area exactly, proving padding is "inside" (same background) while margin (the 24px gap before anything else on the page) shows the page's own white background instead, proving margin is genuinely outside the box.

**Shorthand syntax**, since you'll see this constantly: `padding: 16px;` sets all four sides equally. `padding: 8px 16px;` sets top/bottom to `8px` and left/right to `16px` (two values: vertical, then horizontal). `padding: 8px 16px 24px 32px;` sets top, right, bottom, left, in that clockwise order (four values). The exact same shorthand pattern applies to `margin` and `border-width`.

### `box-sizing` — the setting that resolves a genuinely common bug

Here's a bug nearly every beginner hits at least once. Given:

```css
.quest-card {
  width: 300px;
  padding: 20px;
  border: 5px solid steelblue;
}
```

**Question: how wide is this box actually rendered, on screen?** The instinctive answer is 300px, since that's what `width` says. **The actual, default answer is 350px** — `300 (width) + 20 + 20 (left/right padding) + 5 + 5 (left/right border) = 350`. By default, CSS's `width` property sets the size of the **content box only** — padding and border get added *on top of* that, making the element's true rendered size larger than the `width` you wrote. This is exactly the mechanism behind "why does my fixed-width box overflow its container by a few pixels" bugs.

The fix, applied near-universally in real-world CSS, is one declaration:

```css
* {
  box-sizing: border-box;
}
```

**Line by line:** `*` is the **universal selector** — it matches every element on the page, with no exceptions, making this the single most common "first rule in the file" in real-world CSS. `box-sizing: border-box` changes what `width` *measures* — instead of "content only," it now means "content + padding + border, all included in that one number," and the content area shrinks automatically to make room for them. With `border-box` active, the same `.quest-card` above renders at genuinely, exactly 300px wide, full stop — padding and border now eat into the content area instead of adding on top of it.

Add `* { box-sizing: border-box; }` as the very first rule in `styles.css` now, and keep it there for every remaining lesson and exercise in this module — this course, like the overwhelming majority of real-world CSS, treats this as a non-negotiable baseline reset rather than an optional style choice.

**Try it yourself:** with `box-sizing: border-box` active, change `.quest-card`'s `width` to exactly `300px`, and its `padding` to `40px`. Open your browser's DevTools (right-click the element → "Inspect"), hover over the `.quest-card` element in the Elements panel, and check the little box-model diagram tooltip that appears — confirm the total rendered width is 300px, with the diagram showing your 40px padding eating into the content area rather than adding to the outside.

## Common mistakes & gotchas

- **Forgetting `box-sizing: border-box`, then being confused why a `width: 100%` element overflows its parent** the moment any padding or border is added. Set the universal `border-box` reset first, in every project, as a habit.
- **Confusing padding and margin.** A quick mnemonic: padding is like the stuffing *inside* a padded jacket (same jacket, more of it); margin is the empty space *around* the jacket on a hanger. If you want space between two sibling elements, that's margin; if you want breathing room between an element's border and its own content, that's padding.
- **Margin collapse** (a genuinely confusing default behavior): when two block elements stack vertically and both have margin between them, the *larger* of the two margins wins — they don't simply add together. This is a real CSS behavior (not a bug in your code), and it's one of several reasons Flexbox/Grid (next two lessons) are generally preferred over relying on plain margins for consistent spacing between multiple elements — they don't have this collapsing quirk.
- **Assuming higher specificity always means "more CSS written."** A single ID selector beats ten combined class selectors — specificity is about selector *type*, not the total number of characters or rules.
- **Editing `styles.css` and seeing no change on reload.** Almost always a caching issue (same note as Lesson 00) — hard-refresh (`Ctrl+Shift+R`), or double check the `<link>` tag's `href` path is actually correct relative to where `index.html` lives.

## How this connects

You now understand what every element's box actually contains and how its true rendered size is determined — this is the literal foundation Flexbox (Lesson 03) and Grid (Lesson 04) arrange *boxes of exactly this kind* into rows, columns, and full-page layouts. Nothing about the box model goes away once you learn Flexbox/Grid — those are additional layout systems that position and size these same content/padding/border/margin boxes; they don't replace this lesson's concepts, they build directly on top of them.

## Quick self-check

1. What are the four layers of the box model, from innermost to outermost, and which one is always visually transparent?
2. Given `width: 200px; padding: 10px; border: 2px solid black;` with the *default* `box-sizing`, what is the element's true rendered width? What would it be with `box-sizing: border-box` instead?
3. Given two CSS rules of equal specificity targeting the same element with conflicting values, which one wins, and why?
4. Between an element selector, a class selector, and an ID selector, rank them from lowest to highest specificity.
5. Why does this course apply `* { box-sizing: border-box; }` as the very first rule in every project, rather than leaving the browser's default behavior in place?
