# Module 03 — HTML, CSS, and JavaScript Fundamentals

**Phase:** 1 — How the Web Actually Works + Frontend
**Estimated time:** 18–24 hours over two to three weeks (this is the widest module so far — three real languages, plus a new toolchain)
**Verified against (August 2026):** Node.js **24.19.0** ("Krypton" line — the current Active LTS release, confirmed on nodejs.org's own download page; the newer 26.7.0 line is "Current" but not yet LTS) — verified live at [nodejs.org/en/download](https://nodejs.org/en/download); TypeScript **7.0.2** (the first stable release of TypeScript's new Go-based compiler, published to npm on 2026-08-05, confirmed via the npm registry) — verified against [Microsoft's official TypeScript 7.0 announcement](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/); the weather API used throughout this module and its capstone, **[Open-Meteo](https://open-meteo.com/)**, confirmed live with a real HTTP request while writing this module (see `lessons/07-fetch-promises-and-async-await.md`), confirmed to require no API key, no signup, and no credit card for non-commercial use, with a free-tier limit of 10,000 calls/day, 300,000/month (checked against Open-Meteo's own pricing page); JavaScript feature status (optional chaining, nullish coalescing, ES modules, `async`/`await`) confirmed as long-standing, stable, "Baseline: widely available" language features with no experimental syntax used anywhere in this module. See each lesson for exactly what was checked and when.

## What this module is

Module 02 taught you *what* HTTP, APIs, and JSON are — but everything you did there used `curl`, a command-line tool. This module is where you learn to build the thing that's actually making those requests in the real world: a running page in a browser. You'll learn the three languages every website is built from — **HTML** (structure and meaning), **CSS** (appearance and layout), and **JavaScript** (behavior) — from genuine zero, assuming no prior exposure to any of the three. Then, because you're coming from C++'s static typing and will appreciate having it back, you'll learn **TypeScript**, a layer on top of JavaScript that adds real compile-time type checking.

Per [`RUNNING_PROJECT.md`](../RUNNING_PROJECT.md), this module's capstone is **deliberately not QuestLog**. QuestLog is an internal-data app with no real reason to call an external API yet; this module's whole point is calling a *real, live, external* API from code running in a browser, with no framework doing the work for you — so the capstone is a standalone **weather dashboard**. QuestLog itself starts fresh, with React, in Module 04 — nothing you build here carries forward as code, but everything you learn here (DOM manipulation, events, `fetch`, promises, `async`/`await`, TypeScript) is exactly what React sits on top of, and Module 04 builds directly on this module's mental model rather than replacing it.

## What you'll be able to do after this module

- Write semantically correct HTML: structure a real page with the right elements for the right jobs, build an accessible form, and explain why "a `<div>` for everything" is a real, specific problem rather than just a style preference.
- Explain the CSS box model precisely (content, padding, border, margin, and the two `box-sizing` modes), and lay out real pages with Flexbox (one-dimensional) and Grid (two-dimensional), including responsive layouts that adapt to different screen widths.
- Explain how JavaScript actually differs from Python and C++ (dynamic typing, prototypal objects, the event loop) and correctly use variables, functions, arrow functions, and control flow in JavaScript specifically.
- Explain the **event loop** — JavaScript's specific, browser-flavored version of the same "single thread, cooperative scheduling" idea Module 01 taught for Python's `asyncio`, adapted to a UI that must never freeze.
- Select, read, and modify real page elements with the DOM, and respond to real user interactions with event listeners.
- Fetch real data from a real API using `fetch`, and handle asynchronous results correctly with `.then()` chains and, preferably, `async`/`await` — including loading and error states, a pattern you'll reuse in every module from here to the end of the course.
- Use modern (and now simply *standard*) JavaScript features fluently: `const`/`let`, arrow functions, template literals, destructuring, the spread operator, and ES modules (`import`/`export`).
- Explain why static types matter at scale (a case you already believe from C++), write basic TypeScript with real type annotations, interfaces, and union types, and compile it to plain JavaScript with `tsc`.
- Build and ship a real, interactive, TypeScript-powered weather dashboard that calls a live public API and handles loading/error states correctly — your Module 03 capstone.

## Prerequisites

**Module 00, specifically:** shell comfort (Git Bash, navigating folders, `PATH`, reading error messages) is assumed with no re-teaching — this module's setup lesson installs a new tool (Node.js) using exactly the same "install → close and reopen the terminal → verify with `--version`" pattern Module 00 and Module 01 already taught you. **Module 02, specifically:** this module assumes you already know what HTTP, an API, a request/response cycle, and JSON are ([Module 02, Lessons 03 and 05](../module-02-internet-and-web-fundamentals/lessons/)) — those concepts are *linked back to*, not re-taught, when this module's `fetch` lesson has you make real HTTP requests from inside JavaScript instead of from `curl`. No prior HTML, CSS, or JavaScript knowledge is assumed at all.

## Module structure

```
module-03-html-css-javascript/
├── README.md                                          ← you are here
├── lessons/
│   ├── 00-setup.md                                   ← install Node.js, npm, TypeScript; verify VS Code
│   ├── 01-html-structure-forms-and-accessibility.md  ← semantic HTML, forms, accessibility basics
│   ├── 02-css-the-box-model.md                       ← box model, box-sizing, the cascade
│   ├── 03-css-flexbox.md                             ← one-dimensional layout
│   ├── 04-css-grid-and-responsive-design.md          ← two-dimensional layout, media queries
│   ├── 05-javascript-fundamentals-and-the-event-loop.md ← JS vs. Python/C++, the event loop
│   ├── 06-the-dom-and-events.md                      ← selecting/modifying elements, event listeners
│   ├── 07-fetch-promises-and-async-await.md          ← real HTTP from JS, promises, async/await
│   ├── 08-es6-plus-features-and-modules.md           ← destructuring, spread, template literals, ES modules
│   └── 09-typescript-introduction.md                 ← types, interfaces, compiling with tsc
├── exercises/
│   ├── 01-semantic-html-and-a-form/                  ← very easy
│   ├── 02-css-layout-with-flexbox-and-grid/          ← easy/guided
│   ├── 03-dom-manipulation-and-events/               ← guided
│   ├── 04-fetch-promises-and-async-await/            ← guided/independent
│   └── 05-typescript-conversion/                     ← independent
├── project/
│   └── BRIEF.md                                      ← Weather Dashboard capstone (vanilla JS/TS)
└── CHECKLIST.md
```

Read the lessons in numeric order — later lessons assume earlier ones without re-explaining. Do not skip `00-setup.md`, even if you think you already have Node.js — it ends with a "Verify your setup" section this module's exercises and capstone genuinely depend on (a working `tsc` compiler, specifically).

## How to work through this module

Follow the workflow in the [root README](../README.md): read a lesson fully, answer its self-check questions, do the matching exercise without peeking at the solution, then ask your AI session *"Review my solution for exercise 0N."* After all five exercises and the capstone are done, say *"Check my module"* for the full module-end review.

## A note on scope

This is the widest module so far: three languages (HTML, CSS, JavaScript) plus one type system (TypeScript) plus a new toolchain (Node.js/npm/tsc). It's split into ten lesson files specifically so no single lesson tries to do too much at once — HTML gets one lesson, CSS gets three (box model, flexbox, grid/responsive — each is genuinely a distinct skill), and JavaScript gets four (fundamentals/event loop, DOM/events, fetch/promises/async-await, ES6+ features), with TypeScript closing out the module. Expect this module to take noticeably longer than Module 02; that's intentional, not a sign you're moving too slowly.

## A note on the capstone

The Module 03 capstone (`project/BRIEF.md`) has you build a **Weather Dashboard** — a small, real, interactive vanilla JS/TS web app (no framework) that lets a user search for a city and see live current-weather data, fetched from a real, free, no-key public API ([Open-Meteo](https://open-meteo.com/), verified live and free while writing this module), with correctly handled loading and error states. Per [`RUNNING_PROJECT.md`](../RUNNING_PROJECT.md), this is deliberately **not** QuestLog — QuestLog is an internal-data app that doesn't need an external API, and this module's whole point is practicing exactly that external-API-from-the-browser skill without a framework hiding any of the mechanics from you. QuestLog itself begins, fresh, in Module 04 — built with React on top of the exact DOM/fetch/TypeScript mental model this module gives you.
