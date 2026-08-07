# Lesson 01 — HTML: Structure, Forms, and Accessibility

## What you'll learn

- What HTML actually is, what a browser does with it, and why it's not a programming language.
- Tags, elements, and attributes — the complete grammar of HTML, and how to read/write it correctly.
- The overall document skeleton every HTML page needs, line by line.
- **Semantic HTML**: why `<header>`, `<nav>`, `<main>`, `<article>`, and friends exist, instead of just using `<div>` for everything, and what specifically breaks when you don't use them.
- How to build a real, working HTML form: inputs, labels, buttons, and the built-in browser validation you get for free.
- Accessibility basics: what a screen reader is, why semantic HTML and labels matter to it, and the handful of habits that make a page usable by everyone.

## Why this matters

Every single thing you build for the rest of this course — QuestLog starting in Module 04, every React component, every page you'll ever ship — ultimately becomes HTML in a browser. React (Module 04) doesn't replace HTML; it's a more convenient way of *generating* HTML. Getting HTML's actual structure and vocabulary right now means every later lesson in this course builds on solid ground instead of you copy-pasting `<div>` tags without understanding what any of them mean. Accessibility, specifically, is not an optional nice-to-have you can bolt on later — screen-reader users, keyboard-only users, and even browsers' own automated tools (search engines, translation tools) all depend on the semantic choices you make in this lesson, in every page you ever ship professionally.

## Prerequisites

Module 02 in full — you already know what an HTTP response's body can be ([Module 02, Lesson 03](../../module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md)), and that a `Content-Type` of `text/html` (rather than `application/json`) means "this response body is a webpage" ([Module 02, Lesson 04](../../module-02-internet-and-web-fundamentals/lessons/04-headers-cookies-and-statelessness.md)). This lesson is about what's actually *inside* that body. No prior HTML knowledge is assumed.

## The concept, explained simply

**HTML (HyperText Markup Language)** is not a programming language — it has no variables, no loops, no functions, no logic. It's a **markup language**: plain text with extra symbols (**tags**) wrapped around pieces of content to describe *what each piece is*, not *how to make it look* (that's CSS's job, starting next lesson) and not *how it behaves* (that's JavaScript's job, starting Lesson 05). A useful analogy from a domain you already know: think of HTML like an Unreal level's **World Outliner** hierarchy — it's a structural, nested description of *what things exist and how they relate* (this Actor is a child of that one; this widget is inside that panel), not the rendering code that actually draws pixels, and not the Blueprint logic that responds to input. HTML says "this text is the main heading, this is a paragraph, this is a list of three items" — a browser's own rendering engine (the same kind of engine, incidentally, that Node.js's V8 is a sibling of — Lesson 00) then decides how to actually draw that structure on screen, using CSS's rules for exactly *how*.

## The details

### Tags, elements, and attributes

```html
<p>Hello, world.</p>
```

**Line by line:**
- `<p>` — an **opening tag**. `p` is the **tag name**, here standing for "paragraph."
- `Hello, world.` — the **content** the tag wraps around.
- `</p>` — a **closing tag** — identical to the opening tag but with a leading `/`.
- The opening tag, its content, and its closing tag together form one **element**. "Tag" and "element" get used loosely interchangeably in casual conversation, but precisely: a tag is one of the two bracketed pieces; an element is the whole unit.

Elements can carry extra information via **attributes**, written inside the opening tag as `name="value"` pairs:

```html
<a href="https://developer.mozilla.org">MDN</a>
```
`href` is an attribute (short for "hypertext reference") — it tells the browser *where this link goes*. `<a>` is the anchor/link element; without `href` it's just decorated text that goes nowhere.

Some elements never wrap any content and have no closing tag at all — these are **void elements**:
```html
<img src="cat.png" alt="A sleeping cat">
<br>
<input type="text">
```
`<img>` (image), `<br>` (line break), and `<input>` (a form field, covered later this lesson) are the void elements you'll meet most often. Trying to write `</img>` is simply wrong — there's nothing to close.

### The document skeleton

Every HTML page starts with the same handful of required pieces. Create a real file and open it in a browser to see this for yourself:

```bash
mkdir -p ~/html-practice
cd ~/html-practice
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My First Page</title>
</head>
<body>
  <h1>Hello, world.</h1>
  <p>This is a real paragraph of real text.</p>
</body>
</html>
EOF
```

Open `index.html` directly in your browser (in Git Bash: `start index.html`, or just double-click the file in File Explorer). **Expected result:** a plain page with a large heading "Hello, world." and a smaller line of text below it — no server, no `curl`, no Node.js needed; your browser reads `.html` files directly off disk.

**Line by line:**
- `<!DOCTYPE html>` — not a tag in the usual sense (no closing tag, no nesting) — a **declaration** telling the browser "interpret everything that follows using the current, standard HTML rules," as opposed to some ancient, quirks-riddled interpretation from the 1990s. Every HTML file you ever write starts with exactly this line, unchanged.
- `<html lang="en">` — the root element; every other element in the page nests inside this one. `lang="en"` declares the page's primary language — screen readers use this to choose correct pronunciation rules, and it's one of the smallest, cheapest accessibility wins available (more on this later in the lesson).
- `<head>` — a container for information *about* the page that isn't itself displayed content: the page's title, character encoding, and (starting next lesson) links to CSS files.
- `<meta charset="UTF-8">` — declares the page's text encoding. **UTF-8** is the modern universal standard capable of representing virtually every character in every human language — always include this exact line; omitting it risks a browser guessing wrong and garbling non-ASCII text (accented letters, emoji, non-Latin scripts).
- `<meta name="viewport" content="width=device-width, initial-scale=1.0">` — tells mobile browsers "render this page at the device's actual width, don't zoom out to fake-fit a desktop layout." Without this line, every page you build looks tiny and zoomed-out on a phone by default — you'll see this line's effect directly once Lesson 04 covers responsive design.
- `<title>` — the text shown in the browser tab and bookmarks. Not the same as `<h1>` (the visible on-page heading) — a page has exactly one `<title>` but can have several headings.
- `<body>` — a container for everything actually *displayed* on the page. Everything visible you'll ever add goes inside this one element.
- `<h1>` through `<h6>` — headings, in decreasing importance/size order. `<h1>` should appear exactly once per page, as the single main heading — this isn't just a style convention; screen reader users frequently navigate a page heading-by-heading (jumping "next heading, next heading"), and a page with no `<h1>` or with headings used out of order genuinely disorients that navigation, not just "looks odd."
- `<p>` — a paragraph of text.

### Semantic HTML: why not just `<div>` for everything?

A `<div>` is a **generic**, meaning-free container — it groups content visually/structurally but says *nothing* about what that content actually is. You could, technically, build an entire webpage out of nothing but nested `<div>`s with CSS classes for styling hooks, and it would render identically to a page built the "right" way. **Semantic HTML** means choosing tags that describe what a piece of content actually *is*, not just where it sits — and it has real, non-cosmetic consequences:

```html
<div class="header">
  <div class="nav">
    <div class="nav-link">Home</div>
    <div class="nav-link">Quests</div>
  </div>
</div>
<div class="main">
  <div class="article">
    <div class="heading">Slay the Dragon</div>
    <div class="text">A fearsome red dragon has been terrorizing the village...</div>
  </div>
</div>
<div class="footer">© 2026</div>
```

versus the semantic equivalent:

```html
<header>
  <nav>
    <a href="/">Home</a>
    <a href="/quests">Quests</a>
  </nav>
</header>
<main>
  <article>
    <h2>Slay the Dragon</h2>
    <p>A fearsome red dragon has been terrorizing the village...</p>
  </article>
</main>
<footer>&copy; 2026</footer>
```

Both render as visually identical text with zero CSS applied so far. Here's what the semantic version buys you that the `<div>`-soup version genuinely does not:

- **Screen readers understand structure, not just text.** A screen reader (software that reads a page aloud for a blind or low-vision user — this lesson's accessibility section covers it properly below) can announce "navigation, 2 links," "main content," "article," and "footer" — and let the user jump directly between these regions with a keystroke, *because* it recognizes these specific tags. It cannot infer any of that from `<div class="nav">` — `class` names are meaningless to a screen reader; they're just CSS/JavaScript hooks that happen to have a helpful-looking name for *you*, the developer reading the source.
- **Search engines weight semantic structure when ranking pages.** A search engine has an easier, more confident time identifying your page's actual main content (`<main>`, `<article>`) versus boilerplate (`<nav>`, `<footer>`) when you tell it directly, rather than it having to guess from CSS class names, which vary project to project with no standard meaning at all.
- **Built-in keyboard behavior "just works" on some semantic elements** (most notably forms, covered next) in ways a `<div>` dressed up to *look* like the same element never automatically gets, and would require you to hand-write in JavaScript to match.
- **Readability for the next developer** (very possibly future-you) — `<article>` announces its purpose at a glance; `<div class="article">` requires trusting that whoever wrote the class name was accurate and that it never silently drifted out of sync with the content's actual role.

The core semantic layout elements you'll use constantly:

| Element | Meaning |
|---|---|
| `<header>` | Introductory content for a page or a section — often a logo/title and navigation |
| `<nav>` | A block of navigation links |
| `<main>` | The page's single primary content region (use exactly once per page) |
| `<article>` | One self-contained, independently distributable piece of content (a blog post, a quest description) |
| `<section>` | A thematically grouped chunk of content, usually with its own heading, when no more specific element fits |
| `<aside>` | Content tangentially related to the main content (a sidebar, a pull quote) |
| `<footer>` | Closing content for a page or section — copyright, links, contact info |

**A practical rule of thumb:** reach for one of the elements above first; fall back to a plain `<div>` only when none of them actually describes the content's role (a purely visual wrapper needed just for CSS layout purposes, with no semantic meaning of its own, is a legitimate use of `<div>` — semantic HTML doesn't mean *never* use `<div>`, it means *don't use only `<div>`.*)

Common inline-content tags, for reference (these describe pieces *within* a block of text, not whole page regions): `<strong>` (real emphasis/importance — screen readers may audibly stress it, unlike `<b>`, which is purely visual bold with no meaning), `<em>` (emphasis, similarly meaningful vs. `<i>`'s purely visual italics), `<a>` (a link), `<span>` (the inline equivalent of `<div>` — a meaning-free wrapper for styling a piece of text).

### Lists

```html
<ul>
  <li>Slay the Dragon</li>
  <li>Find the Amulet</li>
  <li>Water the Plants</li>
</ul>
```

**Line by line:** `<ul>` (**u**nordered **l**ist) wraps a group of `<li>` (**l**ist **i**tem) elements — rendered by default with bullet points. Use `<ol>` (**o**rdered **l**ist) instead when the sequence/numbering itself matters (step-by-step instructions) — it renders numbered by default. Never use a list element for content that isn't actually a list — screen readers announce "list, 3 items" and let users navigate item-by-item, which is actively confusing if what's inside isn't conceptually a list at all.

### Building a real form

Forms are how a page collects input from a user and (eventually — this lesson doesn't send it anywhere yet; that's Lesson 07's `fetch`) submits it somewhere. Build one:

```html
<form>
  <div>
    <label for="quest-name">Quest name</label>
    <input type="text" id="quest-name" name="questName" required>
  </div>

  <div>
    <label for="quest-difficulty">Difficulty</label>
    <select id="quest-difficulty" name="difficulty">
      <option value="easy">Easy</option>
      <option value="medium">Medium</option>
      <option value="hard">Hard</option>
    </select>
  </div>

  <div>
    <label for="quest-notes">Notes</label>
    <textarea id="quest-notes" name="notes" rows="3"></textarea>
  </div>

  <div>
    <input type="checkbox" id="quest-urgent" name="urgent">
    <label for="quest-urgent">Urgent</label>
  </div>

  <button type="submit">Add Quest</button>
</form>
```

Add this inside your `index.html`'s `<body>` and reload the page in your browser to see it render as a real, interactive form.

**Line by line, and why each piece matters:**
- `<form>` — the container for the whole set of inputs. On its own (no `action`/`method` attributes set) it doesn't submit anywhere yet — Lesson 07 revisits forms once you know how to intercept a submission in JavaScript and send it with `fetch` instead of a full page reload.
- `<label for="quest-name">` paired with `<input id="quest-name">` — **this pairing is the single most important accessibility habit in this entire lesson.** The `for` attribute's value must exactly match the input's `id`. This does two concrete, testable things: (1) clicking the *label text itself* (not just the tiny input box) focuses/activates the input — try clicking directly on the word "Quest name" in your browser right now and watch the text field get focus; (2) a screen reader announces the label's text when the user tabs into that field, so a blind user hears "Quest name, edit text" instead of just "edit text" with no idea what it's for. An `<input>` with no associated `<label>` is a genuinely broken experience for a screen reader user, not just a minor style nitpick.
- `<input type="text" ... required>` — `type` changes both the input's behavior and, often, what keyboard/UI a mobile browser shows (`type="email"` shows an `@`-optimized keyboard on phones; `type="number"` shows a numeric pad). `required` is a **boolean attribute** — its mere presence (no `="true"` needed) tells the browser to block form submission and show a real, built-in validation message if the field is left empty, with **zero JavaScript written by you.** Try removing the text and clicking "Add Quest" — the browser itself refuses to submit and highlights the field.
- `name="questName"` — this is the key the form's data will eventually be submitted under (Lesson 07). Note it's separate from `id` — `id` is for `<label for>` and CSS/JavaScript to target this exact element; `name` is for the form submission itself. They're allowed to differ, though keeping them similar (as done here) avoids confusing yourself later.
- `<select>`/`<option>` — a dropdown; each `<option>`'s `value` attribute is what actually gets submitted, while the text between the tags is what the user sees (they can differ — useful when a database expects `"easy"` but you want to display "Easy").
- `<textarea>` — a multi-line text input; unlike `<input>`, it has genuine opening/closing tags around its default content (empty, here) rather than a `value` attribute.
- `<input type="checkbox">` — a checkbox; also paired with a `<label>` for the same clickability/screen-reader reasons as the text input above.
- `<button type="submit">` — clicking this attempts to submit the enclosing `<form>`. **Always set `type="submit"` explicitly** (or `type="button"` for a button that should *not* submit the form, e.g. a "Cancel" action) — a `<button>` with no `type` attribute defaults to `type="submit"` inside a form, which is a very common source of "why did my page reload when I just wanted to run some JavaScript" bugs once Lesson 06 has you attach click handlers to buttons.

**Try it yourself:** add a second `<input type="email" required>` field (with its own matching `<label for>`/`id` pair) for an "Assigned to" email address. Reload the page, leave it empty, and click "Add Quest" — predict what the browser's built-in validation message will say before you check. Then type something that isn't a valid email shape (like `notanemail`) and try again — the browser's `type="email"` validation catches that too, with no JavaScript.

## Common mistakes & gotchas

- **Forgetting a closing tag, or closing tags in the wrong order.** Elements must nest like properly matched parentheses — `<div><p></div></p>` is invalid. Modern browsers are forgiving and often render *something* anyway by silently "fixing" your mistake in ways you didn't intend, which is precisely what makes this bug sneaky: it can look fine until a later change exposes the malformed structure. Keep tags properly nested from the start.
- **Using `<div>`/`<span>` for everything, out of habit or because a tutorial did.** You now know specifically why this costs you: broken screen-reader navigation, weaker search-engine understanding, and no free built-in behavior. Default to a semantic element first.
- **An `<input>` with no matching `<label>`, or a `<label>` whose `for` doesn't exactly match the input's `id`** (a typo'd `id` is the classic version of this bug — everything *looks* fine visually, and the bug is invisible unless you actually click the label text or use a screen reader).
- **Multiple `<h1>` elements on one page**, or skipping heading levels (`<h1>` straight to `<h3>`, no `<h2>`) purely for visual size rather than genuine structure. Use CSS (starting next lesson) to control size; use heading *level* to reflect actual document structure.
- **Forgetting `type="button"` on a non-submit button inside a `<form>`.** The button silently defaults to `type="submit"` and triggers an unwanted page reload/validation the moment Lesson 06 wires up a click handler expecting it to do something else instead.
- **Omitting `alt` on `<img>`.** A screen reader announces an image's `alt` text in its place; omitting it entirely means the image is either skipped silently or announced uselessly as just "image" — always include `alt="..."` (a short, accurate description of what the image shows or means; `alt=""` — deliberately empty — is the *correct* choice specifically for purely decorative images that carry no real content, telling the screen reader to skip it entirely rather than announcing something unhelpful).

## How this connects

You now have real HTML structure to apply CSS to — Lesson 02 starts immediately with the box model, styling the exact `<form>` and semantic elements you just built. The `<form>` you built here gets revisited in Lesson 06 (adding real click/submit behavior with JavaScript) and Lesson 07 (actually sending its data somewhere with `fetch`) — nothing here is thrown away; this lesson's HTML is the literal starting point for later lessons and this module's capstone.

## Quick self-check

1. What is the concrete difference between a tag and an element?
2. Give two specific, non-cosmetic reasons to use `<nav>` and `<article>` instead of `<div class="nav">` and `<div class="article">`.
3. Why must a `<label>`'s `for` attribute exactly match its `<input>`'s `id`, and what two things break if it doesn't?
4. What does the `required` attribute on an `<input>` do, and how much JavaScript did you have to write to get that behavior?
5. Why is a `<button>` with no explicit `type` attribute, inside a `<form>`, a common source of bugs once you start attaching click handlers to it?
