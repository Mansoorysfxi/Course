# Lesson 06 — The DOM and Events

## What you'll learn

- What the DOM actually is — the live, in-memory tree structure a browser builds from your HTML, and why it's a genuinely different thing from the HTML file itself.
- How to attach JavaScript to a page, and where that `<script>` tag should go and why.
- How to select existing elements, and how to create/modify/remove elements entirely from JavaScript.
- How to change an element's content, attributes, and CSS classes from code.
- **Events**: how to make a page respond to a real user action, using `addEventListener`, and the object every event handler receives.
- How to wire up the actual `<form>` you built in Lesson 01 so it responds to a real submission with JavaScript instead of a full page reload.

## Why this matters

Everything a webpage does *after* it initially loads — every button click, every typed character reacted to, every piece of data that appears without a full page reload — happens through the DOM and events. This is the mechanism JavaScript actually uses to make a static page interactive, and it's the exact mechanism React (Module 04) exists specifically to make *more convenient* — you cannot appreciate what React is doing for you, or debug it confidently when something goes wrong underneath its abstractions, without first understanding the DOM manipulation it's automating.

## Prerequisites

Lessons 01 (HTML — you'll manipulate the exact structure you already built), 02–04 (CSS — you'll toggle classes whose styles you already know how to define), and 05 (JavaScript fundamentals — variables, functions, and the event loop this lesson's event handlers actually run inside of).

## The concept, explained simply

When a browser loads an HTML file, it doesn't just display the text of that file — it **parses** it into a live, in-memory tree of objects, one object per element, called the **DOM (Document Object Model)**. This is a genuinely important distinction: the DOM is not "the HTML" — it's a *representation* of it that JavaScript can read and, crucially, **change** — and once JavaScript changes the DOM, the browser immediately re-renders the page to reflect the change, with the original `.html` file on disk completely untouched and unaware any of this happened.

**The direct analogy from your Unreal background:** think of the DOM as a live **scene graph** — the actual, in-memory hierarchy of Actors/Components that exists once a level is loaded and running, as opposed to the level's saved `.umap` file on disk. Editing the saved file doesn't affect a level that's already running; you have to reach into the live scene and change actual Actor properties/spawn new Actors/destroy existing ones at runtime — precisely what DOM manipulation does to a loaded page. And exactly like a running level responds to spawning/destroying Actors by visibly updating on screen without you manually redrawing anything, the browser automatically re-renders whenever the DOM changes — you never manually "repaint pixels" yourself; you just change the tree, and rendering happens as a consequence.

## The details

### Attaching JavaScript to a page

```bash
cd ~/html-practice
cat >> index.html << 'EOF'
EOF
```

Edit `index.html` and add, as the very last line before `</body>`:
```html
<script src="script.js"></script>
```

```bash
cat > script.js << 'EOF'
console.log("script.js is connected.");
EOF
```

Reload `index.html`, open DevTools (`F12`), and click the **Console** tab. **Expected output:** `script.js is connected.` printed in the console — proof your JavaScript file is actually running.

**Why `<script>` goes right before `</body>`, not in `<head>`:** the browser reads and runs HTML/JavaScript **top to bottom, in order**. If a `<script>` tag appears in `<head>` (before the `<body>`'s actual elements exist yet), any JavaScript trying to select those elements would find nothing — they haven't been parsed into the DOM yet. Placing `<script>` at the very end of `<body>` guarantees every element above it already exists in the DOM by the time your script runs. (An alternative, the `defer` attribute on a `<head>`-placed `<script>`, achieves the same ordering guarantee differently — worth knowing exists, not needed for this course, which places scripts at the end of `<body>` consistently.)

### Selecting elements

Add a real target to select. In `index.html`'s `<body>`, add:
```html
<h1 id="page-title">Hello, world.</h1>
<button id="rename-btn">Rename</button>
```

```javascript
const heading = document.getElementById("page-title");
console.log(heading);

const button = document.querySelector("#rename-btn");
console.log(button);

const allParagraphs = document.querySelectorAll("p");
console.log(allParagraphs.length);
```

**Line by line:** `document` is a special, globally available object every browser provides — it *is* the DOM's entry point, representing the whole loaded page. `document.getElementById("page-title")` finds the one element with that exact `id` (recall from Lesson 02: IDs must be unique on a page) and returns it as a live object you can act on — or `null` if nothing matches, a real, common source of bugs covered in this lesson's gotchas. `document.querySelector("#rename-btn")` does the same job but accepts **any CSS selector** (Lesson 02's selectors, reused directly here) — `#rename-btn` is a CSS ID selector, but you could equally pass `.quest-card` or `nav a`, exactly the same selector syntax you already know. `querySelectorAll` returns *every* match (as a static list-like object, `NodeList`), not just the first — useful for "do something to every element matching this selector." **This course prefers `querySelector`/`querySelectorAll` over `getElementById` for everything**, specifically because one function handles every kind of selector, rather than needing a different DOM method per selector type.

### Modifying content, attributes, and classes

```javascript
const heading = document.querySelector("#page-title");

heading.textContent = "Quest Log";
console.log(heading.textContent);

const button = document.querySelector("#rename-btn");
button.setAttribute("disabled", "");
console.log(button.outerHTML);

heading.classList.add("highlighted");
console.log(heading.classList.contains("highlighted"));
```

**Line by line:**
- `heading.textContent = "Quest Log";` — reassigning `textContent` replaces the element's text content entirely; the browser immediately re-renders the heading with new text — no separate "refresh" step, exactly the scene-graph analogy above.
- `button.setAttribute("disabled", "")` — sets an HTML attribute directly, here disabling the button (matching the boolean-attribute behavior `required` had in Lesson 01 — its mere presence is what matters). `removeAttribute("disabled")` reverses it.
- `heading.classList.add("highlighted")` — **`classList` is the correct, modern way to add/remove/toggle CSS classes from JavaScript** (rather than manually rewriting the whole `className` string and risking typos or accidentally wiping out other classes already present). `classList.remove("highlighted")` removes it; `classList.toggle("highlighted")` flips it on/off each call — you'll use `toggle` constantly for "show/hide" or "active/inactive" UI states.

Add a small style rule to actually see the class's effect:
```css
.highlighted { background-color: yellow; }
```

**A note on `textContent` vs. `innerHTML`, worth knowing precisely:** `innerHTML` also exists, and lets you set an element's content as a raw HTML string (`el.innerHTML = "<strong>bold</strong>"` actually creates a real `<strong>` element). This course avoids `innerHTML` for anything containing user-supplied or API-supplied text (this module's own capstone included), because it will genuinely execute any HTML/script-like content it's given — inserting untrusted text this way is a real, well-known security vulnerability (cross-site scripting, covered properly in Module 07). `textContent` always treats its value as plain, literal text, with no such risk — use it by default; reach for `innerHTML` only when you deliberately need to insert real markup you trust completely (e.g., a fixed string you wrote yourself, never anything from user input or `fetch`).

### Creating and removing elements

```javascript
const list = document.querySelector("#quest-list");

const newItem = document.createElement("li");
newItem.textContent = "Defeat the Bandit King";
list.appendChild(newItem);

const firstItem = list.querySelector("li");
firstItem.remove();
```
(Add a `<ul id="quest-list"></ul>` to your `index.html` to actually see this run.)

**Line by line:** `document.createElement("li")` builds a brand-new `<li>` element **in memory only** — it exists as a real DOM object, but is not yet part of the visible page at all, exactly like calling Unreal's `SpawnActor` before it's actually placed into the level. `list.appendChild(newItem)` is the "place it into the level" step — it inserts the new element as the last child of `list`, and *only now* does the browser actually render it. `firstItem.remove()` deletes an element from the DOM entirely — the browser equivalent of `DestroyActor`.

### Events: making the page respond to a user

```javascript
const button = document.querySelector("#rename-btn");

button.addEventListener("click", function (event) {
  console.log("Button was clicked!");
  console.log(event.type);
  heading.textContent = "Renamed Quest Log";
});
```

**Line by line:** `addEventListener(eventType, handlerFunction)` is how you tell the browser "run this function whenever this specific thing happens to this element" — `"click"` is one of dozens of built-in event types (others you'll use in this module's exercises: `"submit"`, `"input"`, `"change"`, `"keydown"`). This is the actual mechanism behind "interactive" — nothing in this lesson so far runs *automatically* on its own timeline; it all runs **in response to** something, exactly the reactive, "wait for a trigger" shape of an Unreal input binding or an `OnClicked` delegate.

The **`event` object** your handler function receives is filled in automatically by the browser with real, useful details about what just happened: `event.type` (the event name, `"click"` here), `event.target` (the exact element the event happened on — useful when one handler is attached to a parent and needs to know which specific child was actually interacted with), and, for form-related events, `event.preventDefault()` — covered next, since it's essential for handling forms correctly.

### Wiring up the Lesson 01 form correctly

Recall from Lesson 01: clicking a `<button type="submit">` inside a `<form>` triggers the browser's **default behavior** — submitting the form, which (with no `action` attribute set) reloads the current page. That default reload wipes out any JavaScript state and is not what you want once you're handling submission yourself:

```javascript
const form = document.querySelector("form");

form.addEventListener("submit", function (event) {
  event.preventDefault();   // stop the default page-reload behavior

  const questNameInput = document.querySelector("#quest-name");
  console.log(`Quest submitted: ${questNameInput.value}`);
});
```

**Line by line:** `event.preventDefault()` is the single most important line in this example — it tells the browser "do not perform this event's normal default action," specifically here, "do not actually submit/reload." Without it, your `console.log` would run, immediately followed by a full page reload wiping out everything, including the console output you just produced — a genuinely common beginner confusion ("why does my code seem to run but then nothing happens" — it did run, then the page reloaded a fraction of a second later). `questNameInput.value` reads the **current typed content** of a text input — note this is a different property from `textContent` (used for an element's own inner text, like a heading) — `value` is specifically how you read/write what's inside a form field.

**Try it yourself:** add an `"input"` event listener (fires on every keystroke, unlike `"submit"`, which only fires on actual submission) to the quest-name field that live-updates some other element's `textContent` with "Live preview: <whatever's typed so far>". Type into the field and watch the preview update on every keystroke, with zero page reloads — this exact pattern (react instantly to typing) is the direct precursor to what React's controlled form inputs do automatically, starting Module 04.

## Common mistakes & gotchas

- **Placing `<script src="script.js">` in `<head>`**, then getting `null` from every `querySelector` call because the elements below it in `<body>` don't exist in the DOM yet when the script runs. Keep scripts right before `</body>`, or use `defer` (mentioned above) if you have a specific reason to place one in `<head>`.
- **Forgetting that `querySelector` returns `null` when nothing matches**, then calling a method on that `null` and getting `TypeError: Cannot read properties of null (reading '...')`. This is one of the single most common real-world JavaScript runtime errors — when you see it, the fix is almost always "double-check the selector actually matches something that exists at the point this code runs," not something more exotic.
- **Forgetting `event.preventDefault()` on a form's `"submit"` handler**, and being confused why the page reloads and any in-progress JavaScript state disappears.
- **Using `innerHTML` with any text that came from a user or an API**, opening a real security hole (cross-site scripting, Module 07). Default to `textContent`.
- **Confusing `textContent` (an element's own text) with `value` (a form field's current typed content).** Setting `textContent` on an `<input>` does nothing useful — inputs don't render their "value" as inner text; use `.value` for form fields specifically.
- **Attaching the same event listener repeatedly** (e.g., inside a function that runs more than once) without realizing each call to `addEventListener` adds an *additional* listener rather than replacing the previous one — leading to a handler firing multiple times per single click. Attach listeners once, typically right after selecting the element, not inside code that might re-run.

## How this connects

You can now build a page that genuinely responds to a user, using nothing but what Lessons 01–06 taught: real semantic HTML, real CSS layout, and real JavaScript reading input and updating the DOM. Lesson 07 takes this exact skill set and connects it to a live external server — instead of `console.log`-ing what a user typed, you'll `fetch` real data from a real API and use DOM manipulation (exactly what this lesson taught) to display the result, with correct loading and error states. This module's capstone weather dashboard is, structurally, this lesson's form-handling pattern plus Lesson 07's `fetch`, combined.

## Quick self-check

1. What is the precise difference between "the HTML file on disk" and "the DOM," and why does changing one not automatically change the other?
2. Why does this course place `<script>` tags right before `</body>` rather than in `<head>`?
3. What does `querySelector` return when no element matches, and what specific error does using that result incorrectly tend to produce?
4. Why does this lesson prefer `textContent` over `innerHTML` for displaying any text that came from user input or an API?
5. What does `event.preventDefault()` do on a form's `"submit"` event, and what visibly happens if you forget it?
