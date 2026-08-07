# Module 03 — Checklist

Complete this after finishing all five exercises and the capstone project,
and after your module-end review ("Check my module"). Don't start Module 04
until every box below is checked and any remedial exercises from your
review are done.

## Self-assessment

Answer these honestly, in your own words (writing them down is more
valuable than answering silently in your head):

- [ ] I can explain why using `<div>` for everything, instead of semantic
  elements like `<nav>`/`<main>`/`<article>`, is a real, concrete problem —
  not just a style preference — and give at least two specific consequences.
- [ ] I can correctly pair a `<label>` with its `<input>` using `for`/`id`,
  and explain the two concrete things that break if the pairing is wrong or
  missing.
- [ ] I can explain the box model's four layers from memory, and correctly
  state why `box-sizing: border-box` changes what `width` measures.
- [ ] I can explain, without looking it up, the difference between the main
  axis and the cross axis in Flexbox, and which property controls which one.
- [ ] I can state a concrete rule for choosing CSS Grid over Flexbox (or
  vice versa) for a given layout problem.
- [ ] I can explain what "mobile-first" responsive design means and why
  this course's media queries use `min-width` rather than `max-width`.
- [ ] I can name at least two genuine differences between JavaScript and
  Python, beyond "different syntax for the same ideas" (e.g. JavaScript's
  single numeric type, its different falsy-value rules, `null` vs.
  `undefined`).
- [ ] I can explain JavaScript's event loop using the game-loop analogy, and
  say precisely how it's similar to and different from Python's `asyncio`
  event loop from Module 01.
- [ ] I can select, create, modify, and remove real DOM elements from
  JavaScript without looking up the exact method names, and I know why
  `textContent` is preferred over `innerHTML` for anything not 100% trusted.
- [ ] I can explain why `fetch`'s Promise fulfills even for a 404/500
  response, and what specific check (`response.ok`) fixes the resulting bug.
- [ ] I can write a small `async function` using `try`/`catch` that
  correctly updates a "loading," "success," and "error" UI state, without
  copying a lesson example directly.
- [ ] I can explain why `??` is sometimes necessary instead of `||` for a
  default value, with a concrete example where the two produce different
  results.
- [ ] I can write a TypeScript `interface` for a real piece of data, use a
  string-literal union type correctly, and explain what a type assertion
  (`as SomeType`) does and doesn't actually guarantee.
- [ ] I can explain, concretely, why reaching for `any` the moment `tsc`
  complains defeats the purpose of using TypeScript at all.
- [ ] All five exercises were reviewed and scored 7/10 or higher (or
  revised until they were).
- [ ] The capstone (Weather Dashboard) runs, correctly handles a "city not
  found" search, and was reviewed.

## Spaced-repetition review questions from earlier modules

These five questions are pulled from Modules 00, 01, and 02's actual
content — answer them from memory before checking the relevant lesson if
you get stuck. If any of these feel shaky, that's a real signal to briefly
revisit the relevant lesson before moving on to Module 04, not just to
review this module's own material.

1. What does `PATH` actually do, and what's the first thing you should try
   when a freshly-installed command gives `command not found`?
   *(Module 00, Lesson 01 — you hit this exact troubleshooting step again
   in this module's own `lessons/00-setup.md`, installing Node.js.)*
2. Why is `def f(items=[]):` dangerous in Python, and what's the correct
   fix? *(Module 01, Lesson 02)*
3. Using the game-loop analogy, why doesn't Python's `async`/`await` make
   CPU-bound code run faster, only I/O-bound waiting more efficient — and
   is that same statement true for JavaScript's event loop too?
   *(Module 01, Lesson 11, and Module 03, Lesson 05)*
4. What does "HTTP is stateless" mean, and how do cookies work around it?
   *(Module 02, Lesson 04)*
5. Name all five parts of a URL, in order, and state which one never
   actually gets sent to the server. *(Module 02, Lesson 05 — you used
   query parameters directly in this module's own `fetch` calls against
   Open-Meteo.)*

## Before you move on to Module 04

- [ ] You've said "check my module" and received a full module-end review.
- [ ] [PROGRESS.md](../PROGRESS.md) has been updated by the AI with your
  Module 03 report.
- [ ] Any remedial exercises the review generated (if any) are complete.
- [ ] You've read the Module 04 README to see what's coming next — React,
  and QuestLog's own web incarnation beginning for real.
