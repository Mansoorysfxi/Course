# Lesson 00 — Setup: Scaffolding QuestLog's New Home

**Verified against (August 2026):** Vite **8.2.0** (scaffolded via `npm create vite@latest`, confirmed via `npm view vite version` against the live npm registry while writing this lesson) — Vite's own docs state it requires Node.js **20.19+ or 22.12+**; React **19.2.8** (`react`/`react-dom`, confirmed via `npm view react version`); TypeScript **7.0.2** (the same Go-based-compiler release verified in [Module 03's setup lesson](../../module-03-html-css-javascript/lessons/00-setup.md), confirmed unchanged via `npm view typescript version`); Tailwind CSS **4.3.3** with its official `@tailwindcss/vite` plugin (confirmed via `npm view tailwindcss version` and Tailwind's own installation docs); React Router **8.3.0** (confirmed via `npm view react-router version` and React Router's own docs — note this course had to actively unlearn an assumption here: **`react-router-dom` no longer exists as of React Router v8** — everything, including `<BrowserRouter>` itself, now imports from the single unified `react-router` package). Every command in this lesson was actually run against these exact versions while writing this module, including a real `npm install` and `npm run build` against the finished capstone codebase at [`project/questlog/`](../project/questlog/) — see this lesson's troubleshooting section for a real, reproducible failure this process hit and how it was fixed.

## What you'll learn

- What each new tool this module needs actually is, and why you need it, before installing anything.
- How to scaffold a new React + TypeScript project with **Vite**.
- How to add **Tailwind CSS** to that project using its current, official Vite plugin.
- How to add **React Router** for multi-page navigation.
- How to confirm all of it actually works, together, before writing a single line of QuestLog code.
- What to do when any of these steps goes wrong — including a real bug this exact lesson's author hit while verifying it.

## Why this matters

Every one of this module's lessons and exercises, and the entire QuestLog capstone, run on top of four tools: Vite, React, Tailwind, and React Router. Per the master plan's Rule 8, none of the teaching content that *uses* these tools is allowed to come before the lesson that gets them installed and verified — so, exactly as Module 00 got you a terminal and Git working before Module 01 needed them, and Module 03's Lesson 00 got you Node.js and TypeScript working before that module's HTML/CSS/JS content needed them, this lesson gets today's four new tools working, confirmed, before Lesson 01 asks you to write your first component.

## Prerequisites

**Module 03, Lesson 00 in full** — this lesson assumes Node.js, npm, and TypeScript's `tsc` compiler are already installed and working (`node --version`, `npm --version`, `npx tsc --version` all succeed). If any of those three commands fail, stop and redo Module 03's setup lesson first; this lesson does not re-explain what Node.js or npm *are* — only Module 03 does that. **Module 03 in full**, conceptually — you're about to meet a tool (React) that automates large parts of exactly what you did by hand in Module 03's DOM/fetch/TypeScript lessons; the less comfortable you are with that module, the more this one will feel like unexplained magic instead of automation of something you understand.

## The concept, explained simply

Today you're installing four things, and it's worth knowing what each one's actual job is before you type a single command — the difference between "a build tool," "a UI library," "a styling system," and "a navigation library" is easy to blur together if you install all four back-to-back without pausing:

- **Vite** (pronounced "veet," French for "fast") is a **build tool and dev server**. It's the thing that takes your `.tsx` files (React + TypeScript files — more on the extension in Lesson 01), compiles and bundles them into plain JavaScript a browser can run, and serves them to your browser instantly while you work, refreshing the page automatically the moment you save a file. Recall Module 03, Lesson 00: `tsc` alone only *compiles* TypeScript to JavaScript — it has no concept of a running dev server, live-reloading, or bundling many files into an optimized few. Vite is a much bigger tool that includes TypeScript compilation as one part of a much larger job.
- **React** is a **UI library** — a set of JavaScript/TypeScript functions and patterns for describing what a webpage should look like and how it should change over time, which Lesson 01 explains from first principles. React itself has no opinion about how your project gets built or served — that's Vite's job, not React's.
- **Tailwind CSS** is a **styling system** — a giant, pre-built collection of small CSS utility classes (like `text-lg`, `flex`, `bg-indigo-600`) you apply directly in your markup, instead of writing your own custom `.css` class names and rules by hand the way Module 03 taught. Lesson 10 explains this trade-off in full; for now, just know it's a styling tool, layered *on top of* the real CSS knowledge Module 03 already gave you, not a replacement for understanding it.
- **React Router** is a **navigation library** — it's what lets a single-page React app (which, without it, is really just one single HTML page) behave like a multi-page site with real, bookmarkable URLs (`/quests/new`, `/quests/17`), without a full page reload on every click. Lesson 08 covers it in full.

All four are separate, independently-maintained tools, developed by different teams, that happen to be commonly used together — nothing about React *requires* Vite, Tailwind, or React Router specifically. This course picks this exact combination (per [`RUNNING_PROJECT.md`](../../RUNNING_PROJECT.md)) because it's a genuinely standard, current, professional combination, not the only valid one.

## The details

### Step 1 — Scaffold a new Vite + React + TypeScript project

Navigate to wherever you keep your own practice projects (not inside the course repository itself — this lesson's examples are throwaway practice; the real, graded work lives in this module's `exercises/` and `project/` folders, which already contain their own project files for you) and run:

```bash
npm create vite@latest react-practice -- --template react-ts
```

**Expected output** (a short interactive-looking log, though this exact form of the command runs non-interactively since the template is already specified):

```
Scaffolding project in /path/to/react-practice...

Done. Now run:

  cd react-practice
  npm install
  npm run dev
```

**Line by line:** `npm create vite@latest` is npm's standard convention for "download and run a project-scaffolding tool," here Vite's own `create-vite` package — recall Module 03, Lesson 00's `npx`, which runs a tool without installing it globally first; `npm create` is a closely related shorthand specifically for scaffolding tools. `react-practice` is the folder name to create. Everything after the bare `--` is passed straight through to `create-vite` itself, not consumed by `npm create`; `--template react-ts` tells it which of its many starter templates to use — `react-ts` specifically means "React, with TypeScript already wired up," as opposed to plain `react` (JavaScript only) or entirely different frameworks' templates it also offers.

Now actually create the project and install its dependencies:

```bash
cd react-practice
npm install
npm run dev
```

**Expected output** (from `npm run dev`):

```
  VITE v8.2.0  ready in 400 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

Open the printed `http://localhost:5173/` URL in a browser. **Expected result:** a starter page with a spinning/counting demo (exact content varies by template version) and a live-reloading dev server — leave it running, open `src/App.tsx` in your editor, change some visible text, save, and watch the browser update automatically without you refreshing it. This automatic-refresh behavior is called **Hot Module Replacement (HMR)** — Vite watches your files and pushes just the changed piece into the already-running page, rather than reloading the whole thing from scratch.

**Try it yourself:** stop the dev server (`Ctrl+C` in the terminal) and run `npm run build` instead. **Expected:** a `dist/` folder appears, containing plain, optimized HTML/CSS/JS files — no React, Vite, or TypeScript involved at all anymore at this point, just what a browser needs. This is the exact same "compile-time tool vanishes, plain output remains" idea Module 03, Lesson 09 taught you about `tsc` — Vite's build step is `tsc`'s idea, scaled up to an entire multi-file app.

### Step 2 — Add Tailwind CSS (current official method: the Vite plugin)

Tailwind CSS's setup method has changed significantly across its major versions — the v3-era method (a `tailwind.config.js` file, a separate `postcss.config.js`, and a `content: [...]` array you had to remember to keep updated) is **not** what current Tailwind (v4+) uses with Vite. The current, official method, confirmed against Tailwind's own docs while writing this lesson, is a dedicated Vite plugin with no separate config file required at all:

```bash
npm install tailwindcss @tailwindcss/vite
```

Edit `vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

**Line by line:** `defineConfig({ plugins: [...] })` is Vite's own configuration format — a **plugin** is a piece of code that hooks into Vite's build process to add a capability Vite doesn't have on its own. `react()` (already present from the scaffold) is what teaches Vite to understand `.tsx` files' special JSX syntax (Lesson 01 explains JSX itself). `tailwindcss()` is the new piece — it teaches Vite to scan every file in your project for Tailwind class names as it builds, and generate exactly the CSS those classes need, automatically, with no separate watch step and no config file listing which folders to scan.

Replace the entire contents of `src/index.css` with just:

```css
@import "tailwindcss";
```

**Line by line:** this single line pulls in Tailwind's base styles, every utility class, and its default design values (spacing scale, color palette, font sizes) all at once — Tailwind v4 moved its configuration into CSS itself (via `@import` and, for anyone customizing the defaults, `@theme` blocks) specifically to eliminate the separate JavaScript config file earlier versions required.

**Verify it's working:** in `src/App.tsx`, replace the returned JSX with something using an actual Tailwind class, e.g. `<h1 className="text-4xl font-bold text-indigo-600">Hello, Tailwind</h1>`, save, and look at the running dev server in your browser. **Expected:** large, bold, indigo-colored text — if the text renders in the browser's default black serif/sans styling instead, Tailwind isn't wired up correctly; see this lesson's troubleshooting section.

**Try it yourself:** change `text-indigo-600` to `text-emerald-600` and predict the color before checking. Then try a class that doesn't exist, like `text-mega-huge`, and confirm nothing breaks — Tailwind simply doesn't generate CSS for a class name it doesn't recognize, and your browser silently ignores an unknown class, exactly like it would for a typo'd class name in Module 03's hand-written CSS.

### Step 3 — Add React Router

```bash
npm install react-router
```

That's the entire installation step — one package, no separate `-dom` package. (If you ever see a tutorial, blog post, or your own memory suggesting `react-router-dom` as a separate install, that instruction is for React Router v6 or earlier; as of v8, verified while writing this lesson, that package no longer exists at all — `react-router` alone now covers everything, including the DOM-specific pieces like `<BrowserRouter>`.) Lesson 08 covers actually using it; this step is purely "get it installed and confirm the import works":

```bash
cat > src/RouterCheck.tsx << 'EOF'
import { BrowserRouter } from "react-router";

export function RouterCheck() {
  return <BrowserRouter>{null}</BrowserRouter>;
}
EOF
npx tsc -b --noEmit
```

**Expected output:** nothing at all — a silent, successful exit means `tsc` found the import valid and the types check out. If instead you see an error naming `react-router-dom`, you (or an outdated example you copied from) tried to install/import the wrong package name for this version. Delete `src/RouterCheck.tsx` once you've confirmed this (`rm src/RouterCheck.tsx`) — it was only a wiring check, not part of your actual app.

## Verify your setup

Run every command below, in order, inside `react-practice/` (your throwaway scaffold from Step 1) — this is the exact checklist this module's lessons and exercises assume works before asking anything more of you.

```bash
node --version
npm --version
npx tsc --version
npm run build
```

**Expected output (approximately — your Node.js patch version may differ slightly from this lesson's, that's fine as long as the major version is 20 or higher):**

```
v24.19.0
10.9.x
Version 7.0.2

> react-practice@0.0.0 build
> tsc -b && vite build

vite v8.2.0 building client environment for production...
✓ NN modules transformed.
dist/index.html   ...
dist/assets/...
✓ built in ...ms
```

A `dist/` folder appears with no errors printed above it. If you completed Steps 2 and 3 above in this same scaffold, `dist/assets/*.css` should be noticeably larger than an empty stylesheet (a sign Tailwind actually generated real utility CSS, not just an empty pass-through).

**Also confirm the dev server:**

```bash
npm run dev
```

**Expected:** the `VITE vX.X.X ready in NNN ms` banner, a `Local: http://localhost:5173/` URL that shows your app with working Tailwind styling when opened, and Hot Module Replacement working when you edit and save `src/App.tsx`.

## Common mistakes & gotchas

- **An old Node.js version.** Vite 8 requires Node.js 20.19+ or 22.12+ — if your Node.js is older than that (Module 03's setup lesson should have already given you a current LTS release, but versions drift over months), `npm install`/`npm run dev`/`npm run build` will print a loud `EBADENGINE`/"Vite requires Node.js version..." warning. Sometimes things still limp along despite the warning; sometimes, per the next bullet, they don't. The fix is the same one Module 03 already taught: reinstall Node.js from [nodejs.org](https://nodejs.org), get the current LTS, close and reopen your terminal, and re-check with `node --version`.
- **A genuine bug this lesson's author actually hit, verifying this exact process:** on an older Node.js version, `npm install` can silently fail to install the correct native binary for Vite 8's Rust-based bundler (Rolldown) for your specific operating system — the symptom is `npm run dev` or `npm run build` crashing with an error like `Cannot find module './rolldown-binding.<platform>.node'` or naming a missing `@rolldown/binding-...` package, even though `npm install` itself reported success moments earlier. **This is not a typo in your code** — it's npm's own optional-dependency resolution getting confused when a package's declared minimum Node.js version isn't met. The fix: upgrade Node.js to a current LTS release (per the bullet above), then delete `node_modules` and `package-lock.json` and run `npm install` again from scratch. Do **not** try to hand-install the missing platform-specific package yourself as a permanent fix — on a correctly up-to-date Node.js install, this issue doesn't occur at all, and hand-patching it just hides the real, underlying version problem instead of fixing it.
- **Tailwind classes silently not applying.** The single most common cause, confirmed against Tailwind's own troubleshooting guidance: `tailwindcss()` missing from `vite.config.ts`'s `plugins` array, or `@import "tailwindcss";` missing (or misspelled) from the CSS file your `main.tsx`/`index.tsx` actually imports. Unlike Tailwind v3, current Tailwind has no `content: [...]` array to forget to update — if the plugin and the CSS import are both correctly in place, Tailwind scans your whole project automatically. Double-check those two things first, in that order, before assuming anything more exotic is wrong.
- **Port 5173 already in use.** If a previous `npm run dev` is still running in another terminal tab (or crashed without releasing the port), Vite will print a message and automatically try the next port (`5174`, etc.) — read the actual URL Vite prints rather than assuming it's always `5173`. To free the original port instead, find and stop the earlier process (on Windows, Task Manager's "Details" tab, or `Ctrl+C` in whichever terminal is still running it).
- **TypeScript errors on the very first run, before you've changed anything.** This usually means an editor extension (e.g. VS Code's TypeScript language service) is using a different, older TypeScript version than the one this project just installed. Run `npx tsc --version` directly in the project folder to see the version actually being used to build — if VS Code's inline red squiggles disagree with what a real `npx tsc -b` run reports, trust the terminal, and if needed, use VS Code's "Select TypeScript Version" command (Ctrl+Shift+P) to point the editor at the project's own `node_modules/typescript`.
- **Git Bash on Windows specifically:** `npm create vite@latest ...` and everything else in this lesson runs fine in Git Bash (recall Module 00) — no WSL2 or PowerShell needed for this module's tools. The one genuine Windows-specific gotcha: if a path you're working in contains spaces (e.g. somewhere under `C:\Users\Your Name\`), always quote it (`cd "C:\Users\Your Name\projects"`), exactly as Module 00's shell lesson taught, or `cd`/npm commands referencing that path can fail with a confusing "not found" error that has nothing to do with Vite, React, or Node.js at all.

## How this connects

You now have every tool this module needs, confirmed working together in one throwaway scaffold — the exact same four-tool combination [`project/questlog/`](../project/questlog/) (this module's capstone reference solution) actually uses, verified with a real `npm install` and `npm run build` while this module was written. Lesson 01 starts writing actual React code inside a fresh project exactly like the one you just scaffolded. Every exercise's `starter/` folder in this module already has this same setup done for you — this lesson exists so you understand *what* was set up and why, not just so you can copy-paste a working `package.json`.

## Quick self-check

1. Name the four tools this lesson installed, and state each one's actual job in one sentence, without saying "it's for React" for all four.
2. What specific thing does `npm run build` produce, and what happens to Vite, React, Tailwind, and TypeScript's own tooling in that output — are they still present?
3. Why does current (v4+) Tailwind not need a `tailwind.config.js` or a `content: [...]` array the way older tutorials describe?
4. What package name does React Router use as of the version this lesson verified, and what package name should you specifically *not* expect to need anymore?
5. If `npm run dev` fails immediately after a fresh `npm install` with an error mentioning a missing native binding/module, what is the first thing this lesson tells you to check, before assuming your own code is broken?
