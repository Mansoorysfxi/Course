# Lesson 00 — Setup: Node.js, npm, and TypeScript

## What you'll learn

- What Node.js actually is, and why a module about *browser* code needs you to install something that runs *outside* the browser.
- How to install Node.js on Windows, and which exact version to get.
- What npm is, what `package.json` records, and the handful of commands you'll use constantly from here to the end of this course.
- How to install TypeScript as a per-project tool and compile your first `.ts` file to plain JavaScript with `tsc`.
- How VS Code's built-in JavaScript/TypeScript support works, and the one setting worth knowing about it.
- How to verify every piece of this setup, and how to fix the most common failures — including ones specific to Git Bash on Windows.

## Why this matters

Every lesson from here on has you write real HTML, CSS, JavaScript, and (starting with Lesson 09) TypeScript files and run them. The HTML/CSS/JavaScript you write for most of this module runs entirely *inside your browser* — you don't need Node.js to open an `.html` file and look at it. So why install Node.js at all?

Two reasons, and both matter for the rest of this course, not just this module:

1. **TypeScript code cannot run directly in a browser.** Browsers only understand JavaScript. TypeScript files (`.ts`) have to be **compiled** — translated — into plain `.js` files first, by a program called `tsc` (the **TypeScript compiler**). `tsc` itself is a program you install and run, and it needs somewhere to run *from* — that's Node.js. Node.js is a program that runs JavaScript (and, via `tsc`, TypeScript) **outside** a browser, directly on your machine, the same way the Python interpreter (Module 01) runs `.py` files directly on your machine.
2. **Node.js and its package manager, npm, are the standard way the entire JavaScript/TypeScript ecosystem installs and runs tools.** Starting in Module 04 (React), you'll use Node.js and npm constantly — to install React itself, to run a local development server, to build your app for production. This lesson's setup is not a one-off for this module; it's the foundation every remaining frontend module in this course sits on.

## Prerequisites

Module 00 in full — a working shell (Git Bash) and comfort with `PATH`, running installers, and reopening terminals after an install (Module 00, Lesson 01). No prior JavaScript or Node.js knowledge is assumed.

## The concept, explained simply

Here's the analogy that will make this click fastest, coming from Unreal: think of **JavaScript** as a *language*, the same way C++ is a language. A language on its own doesn't run anywhere — it needs an **engine** to actually execute it. In a browser, that engine is built in (Chrome and Edge both use an engine called V8; Firefox uses SpiderMonkey). **Node.js is that same V8 engine, pulled out of the browser and packaged as a standalone program**, so JavaScript can run directly on your machine, with no browser involved at all — closer to how you'd run a standalone compiled `.exe` than to how a webpage loads.

Once you can run JavaScript outside a browser, two things become possible that weren't before:

- **You can run developer tools written in JavaScript** — like `tsc`, the TypeScript compiler, and (starting Module 04) React's whole build toolchain.
- **You can install and share reusable packages of JavaScript code**, the same way Python's `pip` lets you install reusable packages (Module 01, Lesson 07). Node.js's package manager is called **npm** ("Node Package Manager"), and it ships bundled with Node.js — installing one installs both.

So: this lesson installs Node.js (which gives you the `node` command and, bundled with it, `npm`), then uses `npm` to install TypeScript as a small tool inside one practice project, and confirms `tsc` actually compiles a `.ts` file into a `.js` file you can run.

## The details

### Step 1 — Install Node.js from nodejs.org

1. Go to `https://nodejs.org/en/download` in your browser.
2. The page highlights two lines: an **LTS** version and a **Current** version. **Verified for this lesson (August 2026): the current Active LTS release is Node.js 24.19.0** ("Krypton" — LTS lines get project codenames), with **26.7.0** being the newer "Current" release (features land here first, but it hasn't yet been promoted to LTS support). **Install the LTS version.** "LTS" stands for **Long-Term Support** — it means this release line gets security and bug fixes for years, and it's the version the whole Node.js ecosystem (including every tool you'll use starting in Module 04) targets and tests against by default. "Current" gets newer features sooner but with a shorter support window and less ecosystem-wide testing — not the right trade-off for a learning environment where stability matters more than bleeding-edge features. By the time you install, you'll likely see a slightly newer patch version within the 24.x line (e.g. 24.20.0) — that's fine, this course doesn't depend on an exact patch version.
3. Download the **Windows Installer (.msi)**, 64-bit, and run it.
4. Click through the installer with the default options. On the "Tools for Native Modules" screen, you do **not** need to check the box to install Chocolatey/build tools — this course never compiles native Node add-ons, so skip that optional step.
5. Let it finish, then **close every open terminal window and open a fresh Git Bash window** — exactly the same PATH-reload rule from Module 00 and Module 01: an installer can update `PATH`, but only terminal windows opened *after* the update will see the change.

### Step 2 — Verify Node.js and npm

```bash
node --version
```
**Expected output:** `v24.19.0` (or a newer 24.x patch — the `v` prefix is normal and part of how Node reports its own version).

```bash
npm --version
```
**Expected output:** something like `11.x.x`. npm is installed automatically alongside Node.js — you never install it separately, exactly like `pip` shipping automatically with Python in Module 01.

If either command says `command not found`, see Troubleshooting below before continuing.

### Step 3 — Create a practice project and understand `package.json`

```bash
mkdir -p ~/js-practice
cd ~/js-practice
npm init -y
```

**Line by line:**
- `npm init` starts a small interactive wizard asking your project's name, version, description, etc.
- `-y` skips every question and accepts the defaults immediately — fine for practice; you'd normally answer the questions for a real project.

**Expected output:** a summary of the generated file, ending by writing it to disk. Look at what got created:

```bash
cat package.json
```
**Expected output (yours may vary slightly):**
```json
{
  "name": "js-practice",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "description": ""
}
```

**What `package.json` is, and why it matters:** this is npm's equivalent of Python's `requirements.txt` (Module 01, Lesson 00) *and* a project identity file combined. It records your project's name and version, and — critically, once you install something — every package your project depends on and which exact version, so the exact same project can be recreated on another machine (or by another developer, or by you in six months) with one command. You'll see this file in literally every JavaScript/TypeScript project for the rest of this course, including QuestLog starting in Module 04.

### Step 4 — Install TypeScript as a per-project tool

```bash
npm install --save-dev typescript
```

**Line by line:**
- `npm install <package>` downloads a package (here, `typescript`) and everything *it* depends on, into a new folder called `node_modules/` inside your current project — **not** installed globally on your whole machine. This mirrors exactly why Module 01 taught you virtual environments: keeping a project's dependencies local to that project, instead of shared globally, means Project A needing TypeScript 7.0 and some future Project B needing an older version never conflict.
- `--save-dev` records this package under a `"devDependencies"` section in `package.json` specifically, marking it as a tool you need *while developing* (compiling, testing, bundling) rather than something your finished app needs to actually run in a user's browser. TypeScript is the textbook example: `tsc` compiles your code, but the *compiled output* (plain JavaScript) is all a browser ever needs — the TypeScript compiler itself never ships to a user.

**Expected output:** a line ending in something like `added 1 package in 2s`, and `package.json` now has a new section:
```json
"devDependencies": {
  "typescript": "^7.0.2"
}
```

**Verified for this lesson (August 2026): the current stable TypeScript release is 7.0.2** — confirmed directly against the npm registry while writing this module. This is a significant release: TypeScript 7 is the first stable version built on an entirely new compiler, rewritten from the ground up in Go instead of TypeScript/JavaScript, reported by Microsoft to be roughly 8–12× faster on real projects. For everything you do in this lesson and this module, **the day-to-day commands are unchanged** — you still run `npx tsc`, write the same `.ts` syntax, and read the same kind of error messages. The one thing that *did* change is some of `tsc`'s **default settings** when you generate a fresh config file, covered in Step 6.

**A quick note on that `^` in `"^7.0.2"`:** this is npm's version-range syntax — `^7.0.2` means "this version, or any newer version that doesn't change the first number" (i.e., any `7.x.x`), so a later `npm install` can pick up small fixes automatically without silently jumping to a `TypeScript 8` that might work differently. You don't need to memorize npm's full versioning syntax now; just recognize `^` when you see it.

Look inside `node_modules/`:
```bash
ls node_modules/.bin/tsc
```
**Expected output:** the path prints with no error — confirming the actual `tsc` program was installed inside this project, not globally.

### Step 5 — Run `tsc` with `npx`

```bash
npx tsc --version
```
**Expected output:** `Version 7.0.2` (or newer 7.x).

**What `npx` does, and why you need it:** you just installed `tsc` *inside this one project's* `node_modules/` folder, not anywhere your shell's `PATH` (Module 00, Lesson 01) searches by default. `npx` is a small helper, bundled with npm, that means "look for this command inside the current project's `node_modules/.bin/` first, and run it from there." Without `npx`, typing plain `tsc` would give `command not found` (unless you'd separately installed TypeScript globally, which this course deliberately avoids, for the same reasons Module 01 avoided global `pip install`s).

### Step 6 — Generate a config file, and write/compile your first TypeScript file

```bash
npx tsc --init
```
**Expected output:** `Created a new tsconfig.json with:` followed by a short settings summary, and a new file, `tsconfig.json`, appears in your folder. This file tells `tsc` *how* to compile your project — Lesson 09 explains its options in depth; for now, open it and replace its contents with exactly this (a small, explicit beginner-friendly config):

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM"],
    "module": "ES2022",
    "moduleResolution": "bundler",
    "rootDir": "./src",
    "outDir": "./dist",
    "strict": true,
    "sourceMap": true
  }
}
```

**Why this exact config, and a note on TypeScript 7's new defaults:** a freshly-generated TypeScript 7 config now turns `strict` mode on by default and defaults `module` to `esnext` — both good, modern defaults that this course wants anyway (Lesson 09 explains exactly what `strict` catches). Two settings, though, need to be explicit rather than left to defaults for a project like this one: `rootDir`/`outDir` (TypeScript 7 requires `rootDir` to be stated explicitly rather than inferring it), and `lib` (you need `"DOM"` included so `tsc` knows about browser things like `document` and `fetch` — without it, plain browser code would show type errors for using perfectly normal browser APIs). This exact config is what every exercise and the capstone in this module use.

Now write an actual file:

```bash
mkdir src
cat > src/hello.ts << 'EOF'
const greeting: string = "Setup verified.";
console.log(greeting);
EOF
```

**Line by line:** `const greeting: string = ...` is real TypeScript syntax — `: string` is a **type annotation**, stating explicitly that `greeting` must always hold a string (Lesson 09 covers this properly; for now, just recognize the shape). Compile it:

```bash
npx tsc
```
**Expected output:** no output at all if compilation succeeds — `tsc` (like most compilers) stays silent on success and only prints when something is wrong. Confirm the result:

```bash
ls dist/
cat dist/hello.js
```
**Expected output for `ls dist/`:** `hello.js` and `hello.js.map` — the
`.map` file is a **source map**, generated because this course's
`tsconfig.json` sets `"sourceMap": true`; it lets browser/Node.js
debuggers show you your original `.ts` source and line numbers while
stepping through the compiled `.js`, instead of the harder-to-read
compiled output. You won't edit this file directly.

**Expected output for `dist/hello.js`:**
```javascript
"use strict";
const greeting = "Setup verified.";
console.log(greeting);
//# sourceMappingURL=hello.js.map
```
That last line is what actually connects the compiled file to its source
map — confirmed directly against a real `tsc 7.0.2` compile while writing
this lesson.

**What just happened:** `tsc` read `src/hello.ts`, checked its types, stripped away the TypeScript-only parts (the `: string` annotation — plain JavaScript has no such syntax), and wrote out a plain `.js` file a browser (or Node.js) can actually run. Run the compiled output directly with Node.js to prove it's genuine, ordinary JavaScript now:

```bash
node dist/hello.js
```
**Expected output:**
```
Setup verified.
```

**Try it yourself:** open `src/hello.ts`, change the line to `const greeting: string = 42;` (a number, not a string) and run `npx tsc` again. Predict what happens before you run it. **Expected:** `tsc` refuses to compile and prints an error like `error TS2322: Type 'number' is not assignable to type 'string'.` — this is the entire point of TypeScript, demonstrated in one line: a mistake that plain JavaScript would only reveal later, at runtime (or never, if that exact line happened not to run during testing), TypeScript catches immediately, before the code ever runs. Change it back to a string before moving on.

### Step 7 — Confirm VS Code's built-in TypeScript/JavaScript support

VS Code has genuinely built-in JavaScript and TypeScript support — unlike Python (Module 01), where you had to install the Python extension separately, **no extension install is required** for basic TypeScript/JavaScript editing, syntax highlighting, autocomplete, or inline error squiggles. This is worth confirming rather than assuming, though, because of one specific gotcha:

**Verified for this lesson (August 2026):** VS Code bundles its own internal copy of the TypeScript *language service* (the part that powers autocomplete and red squiggly underlines as you type) — separate from whatever TypeScript version you install per-project with npm. Most of the time this difference is invisible. Occasionally (especially right after a very new TypeScript release, like 7.0 at the time of writing) VS Code's bundled version lags behind, and you'll want VS Code to use *your project's* installed version instead, so the errors it shows you match exactly what `tsc` will actually enforce when you compile.

1. Open your `~/js-practice` folder in VS Code (`File → Open Folder…`).
2. Open `src/hello.ts`.
3. Click anywhere inside the file, then look at the bottom-right status bar — it shows a version number next to "TypeScript." Click it.
4. A menu appears with an option **"Select TypeScript Version…"** → choose **"Use Workspace Version"**. This tells VS Code to use the exact `typescript` package you installed into this project's `node_modules/` (Step 4), rather than its own bundled copy — the same principle as Module 01 confirming VS Code was pointed at your project's `.venv` Python interpreter rather than some other Python install.

## Verify your setup

Run each command in a **fresh** Git Bash window, inside `~/js-practice`:

```bash
node --version
```
**Expected:** `v24.19.0` (or newer 24.x).

```bash
npm --version
```
**Expected:** `11.x.x` or similar.

```bash
npx tsc --version
```
**Expected:** `Version 7.0.2` (or newer 7.x).

```bash
cat dist/hello.js && node dist/hello.js
```
**Expected:** the compiled JavaScript prints out, then running it prints exactly `Setup verified.`

Open `src/hello.ts` in VS Code and confirm: no red squiggly underline on the `greeting` line, and the status bar's TypeScript version (bottom right) matches `7.0.2` (or shows "Workspace Version" is selected, per Step 7).

If every one of the above matches, your setup is ready for the rest of this module.

## Common mistakes & gotchas

- **`node: command not found` right after installing.** Almost always a stale terminal — close *every* terminal window completely and open a brand-new Git Bash window (same PATH-reload rule as every previous module's setup lesson). If it's still missing, rerun the installer and confirm it completed without errors.
- **`npx tsc` says `command not found` or downloads a random package instead of running yours.** This usually means you ran it outside the project folder where you ran `npm install --save-dev typescript` — `npx` looks for `node_modules/.bin/tsc` relative to your **current directory**, not globally. `cd` back into `~/js-practice` (or wherever you installed it) first.
- **`tsc` compiles but the browser (later exercises) shows an old version of your code.** Browsers aggressively cache files. If a `dist/*.js` file's behavior doesn't match your latest edit, hard-refresh the page (`Ctrl+Shift+R` in most browsers) rather than assuming your code is wrong.
- **Windows Defender / antivirus flags `node_modules/` as slow to scan.** `node_modules/` folders can contain thousands of small files. This is a known, harmless (if occasionally annoying) characteristic of the npm ecosystem — not a sign anything is broken. Never commit `node_modules/` to Git; add a `.gitignore` (Module 00, Lesson 03) containing `node_modules/` before your first commit in any Node.js project — it's large, and, exactly like Python's `.venv`, entirely regenerable from `package.json` with `npm install`.
- **`npm install` seems to hang or is very slow.** Usually a slow/corporate network, not a real failure — let it finish. If it fails outright with a network error, retry; npm has its own retry logic but sometimes needs a nudge.
- **Git Bash path weirdness with `npx`.** Rare, but if a command that clearly exists in `node_modules/.bin/` still isn't found from Git Bash specifically, confirm you're not accidentally inside a Windows-style path with backslashes pasted from Explorer — Git Bash expects forward slashes (`~/js-practice`, not `~\js-practice`), consistent with everything Module 00 already taught about this shell.
- **VS Code shows a red squiggle that `tsc` doesn't actually error on, or vice versa.** This is exactly the "workspace vs. bundled TypeScript version" mismatch from Step 7 — re-check that VS Code is using your workspace's installed version.

## How this connects

Lessons 01–08 use plain JavaScript, running directly in a browser — no Node.js/`tsc` step needed for those, since browsers execute JavaScript natively (that's the whole reason JavaScript's engine lives *inside* every browser in the first place). Node.js and `tsc`, installed in this lesson, become essential starting with Lesson 09 (TypeScript) and stay essential for the rest of this course — Module 04 (React) uses this exact `node`/`npm`/`npx` toolchain to run a real development server and build process, on top of everything else npm manages.

## Quick self-check

1. Why does compiling TypeScript require a separate step (`tsc`) before a browser can run it, when plain JavaScript doesn't need that step at all?
2. What's the difference between installing a package with plain `npm install <package>` and with `npm install --save-dev <package>` — and which one did you use for `typescript`, and why?
3. What does `npx` actually do, and why did plain `tsc` (without `npx`) not work right after installing?
4. Name one concrete way `package.json` in this ecosystem plays the same role `requirements.txt` played in Module 01.
5. What did the deliberate type mistake (`const greeting: string = 42;`) prove about when TypeScript catches an error, compared to plain JavaScript?
