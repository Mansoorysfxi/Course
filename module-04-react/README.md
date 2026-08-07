# Module 04 — React (Modern Frontend)

**Phase:** 1 — How the Web Actually Works + Frontend
**Estimated time:** 20–28 hours over two to three weeks (this module is wide: ten teaching lessons plus a setup lesson, five exercises, and the widest capstone so far)
**Verified against (August 2026):** Vite **8.2.0** (scaffolded with `npm create vite@latest`, confirmed live via `npm view vite version` and an actual `npm install`/`npm run build` while writing this module) — verified at [vite.dev](https://vite.dev/guide/); React **19.2.8** (`react`/`react-dom`, confirmed via `npm view react version`); TypeScript **7.0.2** (the same Go-based-compiler release Module 03 verified, confirmed unchanged); Tailwind CSS **4.3.3** with the official `@tailwindcss/vite` plugin (CSS-first configuration, no `tailwind.config.js`) — verified at [tailwindcss.com](https://tailwindcss.com/docs/installation/using-vite); React Router **8.3.0** — verified at [reactrouter.com](https://reactrouter.com/), and note this is a genuine, current, active change worth calling out explicitly: **`react-router-dom` no longer exists** as of React Router v8 — everything imports from the single, unified `react-router` package now; Next.js **16.3** (App Router, referenced conceptually only — see Lesson 09). See each lesson's own header for exactly what was checked and when.

## What this module is

Modules 00–03 built your foundation: tooling, Python, how the web works, and HTML/CSS/JavaScript/TypeScript by hand, with the DOM manipulated directly. This module is where you learn **React** — the UI library that automates the exact bookkeeping you did manually in Module 03's DOM exercise — and, alongside it, the rest of a genuinely current professional frontend stack: **Vite** (the build tool), **Tailwind CSS** (utility-first styling, layered on top of the real CSS you already know), and **React Router** (multi-page navigation in a single-page app).

This is also where **QuestLog**, the course's running project, begins as real code for the first time. Per [`RUNNING_PROJECT.md`](../RUNNING_PROJECT.md), Module 01's QuestLog CLI and Module 03's weather dashboard were both deliberately separate, standalone codebases — this module's capstone is the actual starting point of the QuestLog application that every module from here through the final capstone extends. Module 05's agent is told to copy the finished codebase at [`project/questlog/`](./project/questlog/) forward and wire it up to a real FastAPI backend.

## What you'll be able to do after this module

- Explain precisely why a framework like React exists — the specific bookkeeping burden of keeping a hand-built DOM in sync with changing data, and what React does differently.
- Build components with typed props, understand JSX as sugar for plain function calls (not HTML), and explain React's rendering model — what a render actually is, what triggers one, and what the Virtual DOM/reconciliation are doing and why.
- Use `useState` and `useEffect` correctly and confidently, including the dependency array's three forms, the stale-closure trap, the infinite-loop trap, and cleanup functions — the single most commonly misused part of React, covered in this module's most detailed lesson.
- Use `useRef` and write your own custom hooks.
- Build controlled forms, know when to lift state up to a common parent, and know when that stops being practical.
- Use React's Context API correctly (the real, idiomatic `createContext` + custom-hook pattern), and explain honestly when it's the right tool and when it isn't.
- Fetch data the React way: a custom hook or Context managing loading/error/success state correctly, including the exact cleanup pattern that prevents a stale async response from overwriting fresher state.
- Build a real multi-page single-page app with React Router's declarative mode: nested routes, `<Outlet />`, dynamic segments, index and catch-all routes, and programmatic navigation.
- Explain SSR, SSG, CSR, ISR, and what Next.js actually is, well enough to make an informed choice on a future project — without having installed or built anything with it here.
- Style real UI with Tailwind's utility classes, understanding them as a productivity layer over the real CSS you already know, not a replacement for it.
- Have built, from scratch, **QuestLog (web)** — a real, working, multi-page React + TypeScript + Tailwind + React Router application.

## Prerequisites

**Module 03, in full.** This module explicitly does not re-teach JavaScript, TypeScript, the DOM, `fetch`/Promises/`async`/`await`, or ES6+ syntax — it links back to exactly where each of those was taught and builds directly on top of them. If `interface`, union types, destructuring, arrow functions, or the loading/error `fetch` pattern from Module 03 feel shaky, revisit that module's lessons before starting this one; this module's own lessons will tell you exactly which one, each time they lean on it. **Module 00** (shell/Git basics) is assumed throughout, with no re-teaching, exactly as every module since has assumed it.

## Module structure

```
module-04-react/
├── README.md                                          ← you are here
├── lessons/
│   ├── 00-setup.md                                   ← Vite + React + TS scaffold, Tailwind, React Router install
│   ├── 01-why-react-components-props-and-jsx.md      ← why frameworks exist, components, props, JSX
│   ├── 02-state-and-the-rendering-model.md           ← useState, re-rendering, Virtual DOM, reconciliation
│   ├── 03-useeffect-the-dependency-array-in-depth.md ← useEffect, dependency arrays, stale closures, cleanup
│   ├── 04-useref-and-custom-hooks.md                 ← useRef, writing your own hooks
│   ├── 05-forms-controlled-components-and-lifting-state.md
│   ├── 06-context.md                                 ← createContext, Provider, useContext, prop drilling
│   ├── 07-data-fetching-loading-and-error-states.md  ← the real useQuests()-shaped pattern
│   ├── 08-react-router.md                            ← BrowserRouter, nested routes, dynamic segments
│   ├── 09-nextjs-ssr-ssg-csr-concepts.md             ← SSR/SSG/CSR/ISR concepts (no install, QuestLog stays Vite)
│   └── 10-tailwind-and-utility-first-css.md          ← utility-first CSS on top of Module 03's real CSS
├── exercises/
│   ├── 01-components-props-and-jsx/                  ← very easy
│   ├── 02-state-and-a-controlled-form/                ← guided
│   ├── 03-a-custom-hook-for-mock-data/                ← guided/independent
│   ├── 04-routing-and-data-fetching/                  ← independent
│   └── 05-extend-questlog/                            ← independent, extends the real capstone codebase
├── project/
│   ├── BRIEF.md                                       ← the QuestLog (web) capstone brief
│   └── questlog/                                      ← the finished, real, working reference codebase
└── CHECKLIST.md
```

Read the lessons in numeric order. Do not skip `00-setup.md` — it ends with a "Verify your setup" section covering a real, reproducible issue this module's own author hit while writing it (a missing native build dependency on an outdated Node.js version), and every later lesson assumes Vite, React, TypeScript, Tailwind, and React Router are all confirmed working.

## How to work through this module

Follow the workflow in the [root README](../README.md): read a lesson fully, answer its self-check questions, do the matching exercise without peeking at the solution, then ask your AI session *"Review my solution for exercise 0N."* After all five exercises and the capstone are done, say *"Check my module"* for the full module-end review.

## A note on the capstone

The Module 04 capstone (`project/BRIEF.md`) has you build **QuestLog (web)**: a React + TypeScript single-page app, built with Vite, styled with Tailwind, routed with React Router, with quest data held in React state and fetched through a mocked async `fetchQuests()` (a real Promise, a real delay, a real chance of failure) since there's no backend yet. This is not a throwaway exercise — per [`RUNNING_PROJECT.md`](../RUNNING_PROJECT.md), the reference solution at [`project/questlog/`](./project/questlog/) is exactly what Module 05 copies forward and connects to a real FastAPI backend, Module 06 adds a real database to, and so on through the final capstone. It was actually built, installed, and built for production (`npm install && npm run build`) while writing this module — not just hand-verified — with zero TypeScript errors. Building it carefully here, with a clean separation between the mock API, the shared Context, and the pages that consume it, is what makes every later module's "extend QuestLog" instructions land on solid ground.
