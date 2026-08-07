# Module 03 Capstone — Weather Dashboard

## What this is

Per [`RUNNING_PROJECT.md`](../../RUNNING_PROJECT.md), this capstone is
**deliberately not QuestLog** — QuestLog is an internal-data app with no
real reason to call an external API yet, and this module's whole point is
practicing exactly that skill (a real, live, external API, called from
browser code, with no framework doing the work for you) before Module 04
hands you React. QuestLog itself begins fresh, with React, in Module 04.

You will build a small, real, interactive **Weather Dashboard**: a page
where a user types a city name, your code looks up that city's coordinates,
fetches its current weather from a live public API, and displays it —
correctly handling the moments before the data arrives (loading) and the
moments when something goes wrong (error), not just the happy path.

## The API, verified

**Verified live while writing this module (August 2026):
[Open-Meteo](https://open-meteo.com/).**

- **No API key, no signup, no credit card required** for non-commercial
  use — confirmed directly against Open-Meteo's own documentation.
- **Free-tier limits:** 10,000 calls/day, 300,000 calls/month, 600 calls/
  minute — confirmed against Open-Meteo's own pricing page. This capstone's
  usage (a handful of manual searches while you build and test it) is
  nowhere close to these limits.
- **Confirmed with a real, live request** while writing this module — a
  request to the forecast endpoint below returned a genuine current
  weather reading for Berlin, with a real, current timestamp.
- Two endpoints, both plain HTTP GET requests returning JSON, no
  authentication headers of any kind:
  - **Geocoding** — turn a city name into coordinates:
    `https://geocoding-api.open-meteo.com/v1/search?name=<city>&count=5&language=en&format=json`
    Returns a `results` array of matches, each with `name`, `latitude`,
    `longitude`, `country`, and `admin1` (region/state), among other fields.
    If no city matches, `results` is absent entirely from the response —
    your error handling must account for this.
  - **Forecast** — get current weather for known coordinates:
    `https://api.open-meteo.com/v1/forecast?latitude=<lat>&longitude=<lon>&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&timezone=auto`
    Returns (among other fields) a `current` object with
    `temperature_2m` (°C), `relative_humidity_2m` (%), `wind_speed_10m`
    (km/h), and `weather_code` (a WMO numeric code — see below).

**Interpreting `weather_code`:** Open-Meteo returns a numeric WMO weather
code, not a text description. Use this table (from Open-Meteo's own
documentation) to convert it to something readable:

| Code(s) | Meaning |
|---|---|
| 0 | Clear sky |
| 1, 2, 3 | Mainly clear, partly cloudy, and overcast |
| 45, 48 | Fog and depositing rime fog |
| 51, 53, 55 | Drizzle: light, moderate, and dense intensity |
| 56, 57 | Freezing drizzle: light and dense intensity |
| 61, 63, 65 | Rain: slight, moderate, and heavy intensity |
| 66, 67 | Freezing rain: light and heavy intensity |
| 71, 73, 75 | Snow fall: slight, moderate, and heavy intensity |
| 77 | Snow grains |
| 80, 81, 82 | Rain showers: slight, moderate, and violent |
| 85, 86 | Snow showers: slight and heavy |
| 95 | Thunderstorm: slight or moderate |
| 96, 99 | Thunderstorm with slight and heavy hail |

You don't need every single code handled individually — a reasonable
approach is a lookup covering the ranges above, with a sensible fallback
label (e.g. `"Unknown"`) for anything not listed.

## Concepts this project uses

Every concept below has a dedicated lesson section — this project should
not require anything this module didn't already teach:

| Concept | Taught in |
|---|---|
| Semantic HTML structure, a real accessible form | [Lesson 01](../lessons/01-html-structure-forms-and-accessibility.md) |
| The box model, `box-sizing: border-box` | [Lesson 02](../lessons/02-css-the-box-model.md) |
| Flexbox (toolbar/card internals) | [Lesson 03](../lessons/03-css-flexbox.md) |
| CSS Grid (overall page layout) and mobile-first media queries | [Lesson 04](../lessons/04-css-grid-and-responsive-design.md) |
| `const`/`let`, functions, arrow functions, JS truthy/falsy | [Lesson 05](../lessons/05-javascript-fundamentals-and-the-event-loop.md) |
| DOM selection/modification, `classList`, events, `preventDefault` | [Lesson 06](../lessons/06-the-dom-and-events.md) |
| `fetch`, Promises, `async`/`await`, `try`/`catch`, loading/error DOM pattern | [Lesson 07](../lessons/07-fetch-promises-and-async-await.md) |
| Destructuring, optional chaining (`?.`), nullish coalescing (`??`), ES modules | [Lesson 08](../lessons/08-es6-plus-features-and-modules.md) |
| `interface`, type annotations, union types, typing a real `fetch` response | [Lesson 09](../lessons/09-typescript-introduction.md) |
| HTTP status codes, what a query parameter is, JSON structure | [Module 02, Lessons 03 and 05](../../module-02-internet-and-web-fundamentals/lessons/) |

## What to build

Set this up as its own small project (per [`lessons/00-setup.md`](../lessons/00-setup.md)):

```bash
mkdir -p weather-dashboard/src
cd weather-dashboard
npm init -y
npm install --save-dev typescript
npx tsc --init
```
Replace the generated `tsconfig.json` with the exact config from Lesson 00
(`target`/`lib`/`module`: ES2022/`["ES2022","DOM"]`/ES2022,
`moduleResolution: "bundler"`, `rootDir: "./src"`, `outDir: "./dist"`,
`strict: true`, `sourceMap: true`).

Build these files:

### `index.html`
- Correct document skeleton (`<!DOCTYPE html>`, `lang`, `charset`, viewport
  `<meta>`, `<title>`) — Lesson 01.
- A `<header>` with an `<h1>`.
- A `<main>` containing:
  - A real, accessible search **form**: a labeled text `<input>` for the
    city name (with `required`), and a `<button type="submit">`.
  - A status region (e.g. `<div id="weather-status">`) for "Ready" /
    "Loading..." / error messages.
  - A results region (e.g. `<div id="weather-result">`) for the actual
    weather display once data arrives — showing at minimum: the resolved
    city/region name, temperature, humidity, wind speed, and a text
    description of the weather code.
- A `<footer>` with attribution text (Open-Meteo's data is CC BY 4.0 —
  include a short line crediting Open-Meteo, per their license terms).
- `<script type="module" src="dist/app.js"></script>` right before
  `</body>` — loading your **compiled** TypeScript output, not the `.ts`
  file directly (recall Lesson 00: browsers cannot run `.ts` files).

### `styles.css`
- The universal `box-sizing: border-box` reset, first.
- A Flexbox-based header/toolbar or search bar.
- A Grid-based (or Flexbox-based, whichever genuinely fits better per
  Lesson 04's decision rule) overall page layout.
- At least one `@media (min-width: ...)` breakpoint, mobile-first, that
  visibly changes the layout between a narrow and a wide viewport — test
  with DevTools' device toolbar.
- Distinct, visible styling for the loading state and the error state (a
  different color/style for an error message than for normal results, at
  minimum).

### `src/app.ts`
- **At least one `interface`** describing the geocoding response shape you
  actually use, and **at least one more** describing the forecast response
  shape you actually use (Lesson 09) — no `any` anywhere in this file.
- An `async function` that geocodes a city name (calls the geocoding
  endpoint, handles the "no results" case explicitly — this is a real,
  common case with this API, not a hypothetical edge case).
- An `async function` that fetches the forecast for known coordinates,
  checks `response.ok`, and throws a real `Error` on failure (Lesson 07).
- A function that converts a numeric `weather_code` into a readable text
  description (the table above).
- A `"submit"` handler on your form that: calls `event.preventDefault()`,
  sets the status region to `"Loading..."`, calls your geocode-then-forecast
  functions in sequence (`await` one, then the other — you do not need
  `Promise.all` or anything not taught in this module), and on success
  updates the results region using `textContent` (never `innerHTML` on
  API-supplied text — Lesson 06's security note), clearing the status
  region; on failure, writes a clear, specific error message into the
  status region instead.
- Compile with `npx tsc` and confirm `dist/app.js` is what `index.html`
  actually loads.

## Acceptance criteria

- [ ] `npx tsc` compiles `src/app.ts` with zero errors, and no `any` appears
  anywhere in the file.
- [ ] Searching a real city (try "Tokyo," "Berlin," and your own city) shows
  "Loading..." immediately, then real, correct-looking current weather
  within a couple of seconds.
- [ ] Searching a city name that doesn't exist (try `"Nonexistentville"`)
  shows a clear, specific "not found"-style message — not a silent
  failure, not a page stuck on "Loading...", not a raw, unhandled console
  error with the page itself unchanged.
- [ ] The weather code is shown as a readable description (e.g. "Partly
  cloudy"), not the raw number.
- [ ] The layout is visibly, meaningfully different between a narrow
  (phone-width) and wide (desktop-width) viewport, confirmed with DevTools'
  device toolbar.
- [ ] Submitting the form never reloads the page.
- [ ] No `innerHTML` is used anywhere for API-supplied text.
- [ ] The Open-Meteo attribution line is present somewhere on the page.
- [ ] Re-searching a second, different city correctly replaces the first
  city's results rather than appending to them.

## What to submit

Point your AI session at your `weather-dashboard/` folder (`index.html`,
`styles.css`, `src/app.ts`, and the compiled `dist/app.js`) and say *"check
my module"* — this capstone is graded per
[GRADING_PROTOCOL.md](../../GRADING_PROTOCOL.md) alongside a re-check of
Exercises 01–05 as part of the full Module 03 module-end review.

## Why this project, specifically

This capstone deliberately combines every single lesson in this module into
one small, coherent, genuinely useful thing, mirroring the depth of
Module 01's QuestLog CLI capstone and Module 02's API Exploration Report —
except this time the deliverable is real, running, interactive code rather
than a written document. It's also a direct rehearsal for the shape of work
you'll do for the rest of this course: a UI, a real external API, correctly
handled asynchronous loading/error states, and real compile-time type
safety — exactly the skeleton QuestLog itself will follow starting Module
04, just without a framework doing the DOM/state work automatically yet.
Building it by hand once, here, is what makes React's automation in Module
04 legible as "a more convenient way to do what I already understand,"
rather than an unexplained black box.
