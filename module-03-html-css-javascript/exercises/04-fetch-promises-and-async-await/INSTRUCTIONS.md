# Exercise 04 — Fetch, Promises, and Async/Await Against a Real API

**Difficulty:** Guided/independent — the HTML and CSS are given; you write
the actual `fetch`/`async`/`await` logic in `starter/script.js`, following
the exact pattern taught in
[`lessons/07-fetch-promises-and-async-await.md`](../../lessons/07-fetch-promises-and-async-await.md).
This is the closest thing in this module to a "mini capstone rehearsal" —
get comfortable with this pattern here, since the real capstone
(`project/BRIEF.md`) builds directly on it, in TypeScript, with a live city
search instead of a fixed dropdown.

**Concepts this exercise uses** (all taught in Lesson 07, building on
Lesson 06's DOM skills): `fetch`, the three Promise states, `response.ok`/
`response.status`, `async function`, `await`, `try`/`catch`, `throw new
Error(...)`, and the loading/success/error DOM-update pattern.

**The API:** this exercise calls the real, live
**[Open-Meteo](https://open-meteo.com/)** forecast API — verified free, live,
and requiring no API key while this module was written (see Lesson 07 and
`project/BRIEF.md` for full verification details). You need a working
internet connection to complete this exercise.

## What to build

Open [`starter/index.html`](starter/index.html) — a page with a `<select>`
of four hardcoded cities (each `<option>`'s `value` attribute is a
`"latitude,longitude"` pair — already provided, no geocoding needed for this
exercise), a "Get Weather" button, and a "Trigger a Deliberate Error" button,
plus `<div id="weather-status">` and `<div id="weather-result">` elements
for you to update. Open `starter/script.js` and implement each `// TODO`:

1. **`getCurrentTemperature(latitude, longitude)`** — an `async` function
   that fetches `https://api.open-meteo.com/v1/forecast?latitude=...&longitude=...&current=temperature_2m,relative_humidity_2m`,
   checks `response.ok`, throws a real `Error` if the request failed, parses
   the JSON body, and returns an object `{ temperature, humidity }` pulled
   from the response.
2. **A click handler on "Get Weather"** that reads the selected city's
   `value`, splits it into latitude/longitude, sets `#weather-status` to
   `"Loading..."`, calls `getCurrentTemperature`, and on success writes a
   sentence like `"18.4°C, 62% humidity"` into `#weather-result` (clearing
   `#weather-status`); on failure, writes a clear error message into
   `#weather-status` instead.
3. **A click handler on "Trigger a Deliberate Error"** that calls `fetch`
   against a deliberately broken URL (the starter file already has one
   ready-made: an Open-Meteo request missing the required `latitude`
   parameter, which the API rejects with a real 400-range error) through
   the *same* loading/error-handling code path as #2 — proving your error
   handling genuinely works, not just that it's never triggered.

## Acceptance criteria

- [ ] Selecting a city and clicking "Get Weather" shows `"Loading..."`
  immediately, then replaces it with a real temperature/humidity reading
  within a second or two.
- [ ] `getCurrentTemperature` throws a real `Error` (not just returning
  `undefined` or `null`) when `response.ok` is `false`.
- [ ] Clicking "Trigger a Deliberate Error" shows a real, specific error
  message in `#weather-status` (not a silent failure, not an unhandled
  exception printed only to the console, and not a page that just hangs on
  "Loading...").
- [ ] No `await` is used outside an `async function` anywhere in your file.
- [ ] Running the successful path twice in a row (e.g. two different
  cities back to back) correctly clears the previous result each time
  rather than appending to it.

## What to submit

Point your AI session at your completed `starter/script.js` and say *"Review
my solution for exercise 04."*

## Hints

- Stuck on the exact response shape? Re-read Lesson 07's own worked example
  closely — `data.current.temperature_2m` and
  `data.current.relative_humidity_2m` are exactly the fields you need; this
  exercise's request URL asks for both by name in its `current=` query
  parameter, mirroring Lesson 07's own example almost exactly.
- Stuck on why your error case never seems to run? Open DevTools' Network
  tab, click "Trigger a Deliberate Error," and inspect the actual response —
  confirm you're checking `response.ok` (or `response.status`) rather than
  assuming `fetch`'s Promise will reject on its own — recall Lesson 07's
  explicit warning that it does not, for HTTP-level errors.
- Stuck on "Loading..." never disappearing on success? Confirm you're
  clearing/replacing `#weather-status`'s text in the success path, not just
  in the error path.
- If you've re-read Lesson 07's relevant section and are still stuck, ask
  your AI session for a hint — Level 1 first, per
  [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md).
