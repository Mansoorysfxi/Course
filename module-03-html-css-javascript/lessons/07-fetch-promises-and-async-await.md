# Lesson 07 — Fetch, Promises, and Async/Await

## What you'll learn

- What a **Promise** is: a real JavaScript object representing a value that isn't ready yet, and its three possible states.
- How to make a real HTTP request from inside JavaScript with `fetch`, and why its result is a Promise.
- `.then()`/`.catch()` chains — the original way to work with Promises.
- `async`/`await` in JavaScript — a cleaner syntax for the exact same underlying mechanism, and how it compares directly to Python's `async`/`await` from Module 01.
- How to correctly handle **loading** and **error** states for a real network request — not just the "happy path" where everything works.
- A live, tested request against **Open-Meteo**, the real weather API this module's capstone uses.

## Why this matters

This lesson is the single most important one in this module for the capstone: every interactive app you build for the rest of this course — this module's weather dashboard, QuestLog's API calls starting Module 05, any AI feature starting Module 13 — fetches data from somewhere and has to correctly handle "it's still loading," "it worked," and "it failed" as three genuinely distinct states. Getting comfortable with Promises and `async`/`await` here, on a small, real example, is what makes every later module's data-fetching code feel familiar instead of mysterious.

## Prerequisites

Module 02 in full — you already know what an HTTP request/response is, what a status code means, and what JSON looks like; this lesson makes those exact same requests from JavaScript instead of `curl`. Module 01, Lesson 11 (Python's `async`/`await`) — this lesson explicitly compares against it. Lesson 05 (JavaScript's event loop) — this lesson is where that event loop's practical payoff finally shows up directly. Lesson 06 (the DOM) — you'll display fetched data using exactly the DOM methods you already know.

## The concept, explained simply

Recall Module 01, Lesson 11's core idea: `async`/`await` lets a function pause at a slow operation and hand control back to the event loop, instead of freezing everything while it waits. JavaScript needs the *exact same* capability for the *exact same* reason — a network request can take anywhere from a few milliseconds to several seconds, and Lesson 05 already showed you that JavaScript runs on one single thread shared with the whole page's rendering — so a network call must never be allowed to block that thread, or the entire page would freeze for however long the request takes.

JavaScript's mechanism for representing "a value that will exist eventually, but doesn't yet" is a real, concrete built-in object type called a **Promise**. This is worth sitting with for a moment because it's a slightly different shape from Python's model: Python's `asyncio` doesn't hand you a distinct "Promise object" the way JavaScript does — an `async def` function, when called, hands you a coroutine object (Module 01, Lesson 11), and `await`-ing it is what actually runs it and gets the result. JavaScript's `fetch()` function, by contrast, returns an actual **Promise object immediately** — a real value you can inspect, store in a variable, and pass around — that starts in a `pending` state and eventually settles into either `fulfilled` (succeeded, with a value) or `rejected` (failed, with a reason). `async`/`await` in JavaScript (covered later this lesson) is a *second*, more convenient syntax for working with these same Promise objects — not a separate mechanism, just a nicer way to write code that deals with them.

## The details

### Promises: the three states

```javascript
const promise = fetch("https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m");
console.log(promise);
```
**Expected output (immediately, in the console):**
```
Promise { <pending> }
```

**Line by line:** calling `fetch(url)` starts a real HTTP request (recall Module 02's whole DNS → TCP → TLS → request/response journey — all of that genuinely happens here, just triggered from JavaScript instead of `curl`) and returns a Promise **immediately**, before the request has actually finished — that's exactly why logging it right away shows `<pending>`: the network round-trip hasn't completed yet at the exact moment `console.log` ran. This is the browser's event loop in action, precisely as Lesson 05 described it: `fetch` hands the slow work off and returns control to your code right away, instead of blocking.

A Promise settles into exactly one of two final states, never both, and never back to `pending` once settled:
- **Fulfilled** — the operation succeeded; the Promise now holds a resulting value.
- **Rejected** — the operation failed; the Promise now holds a reason (usually an `Error` object).

### `.then()` and `.catch()` — reacting to a settled Promise

```javascript
fetch("https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m")
  .then(function (response) {
    console.log("Status:", response.status);
    return response.json();
  })
  .then(function (data) {
    console.log("Current temperature:", data.current.temperature_2m);
  })
  .catch(function (error) {
    console.error("Something went wrong:", error);
  });
```
**Expected output** (real numbers will differ — this is a genuine live weather reading for Berlin, at whatever moment you run it):
```
Status: 200
Current temperature: 21.9
```

**Line by line, and this is worth reading slowly:**
- `.then(callback)` registers a function to run **once the Promise fulfills**, receiving the fulfilled value as its argument. This does *not* block anything — it just says "whenever this eventually succeeds, run this."
- The **first** `.then` receives a `Response` object (recall `response.status` from Module 02, Lesson 03 — the exact same status code concept, now inspected from JavaScript). Crucially: **`fetch`'s Promise fulfills as soon as the server sends back *any* HTTP response headers — even for a 404 or 500 error response.** `fetch` only *rejects* on a genuine network-level failure (DNS failure, no internet connection, CORS block) — a "successful request that got an error status code back" is still a *fulfilled* Promise, not a rejected one. This is a real, common surprise covered fully in this lesson's gotchas.
- `response.json()` **also returns a Promise** — parsing a response body takes a moment (however small) and is itself asynchronous, so it needs the same treatment. `return response.json();` from inside a `.then` callback is the specific pattern that lets you **chain** another `.then` onto the result — returning a Promise from inside a `.then` callback makes the *next* `.then` in the chain wait for that inner Promise too, rather than receiving the still-pending Promise object itself.
- The **second** `.then` finally receives the actual parsed JavaScript object (`data`) — the direct equivalent of Python's `response.json()` from `requests`, or `json.loads()` (Module 01, Lesson 08) turning JSON text into a real object you can access with `.` and `[...]`.
- `.catch(callback)` registers a function to run if **any** step in the chain above it rejects — one network failure, one `.catch`, regardless of which specific `.then` step failed.

### Async/await — the same thing, cleaner syntax

```javascript
async function getCurrentTemperature(latitude, longitude) {
  const response = await fetch(
    `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m`
  );
  const data = await response.json();
  return data.current.temperature_2m;
}

getCurrentTemperature(52.52, 13.41).then((temp) => console.log("Temperature:", temp));
```
**Expected output:**
```
Temperature: 21.9
```

**Line by line, mapped directly against Module 01's Python version:** `async function` marks this function as one that can use `await` inside it — the exact same rule as Python's `async def`. `await fetch(...)` pauses this function's execution right at that line, hands control back to the event loop (letting the rest of the page stay responsive), and resumes with the *fulfilled value* the moment the Promise settles — the exact same mechanical behavior as Python's `await some_coroutine`, applied to a JavaScript Promise instead of a Python coroutine. `await response.json()` does the same for the second async step. Notice how dramatically flatter and more readable this is than the `.then()` chain above, while doing *exactly* the same underlying work — this is precisely why `async`/`await` exists in both languages: it's syntax sugar over the same asynchronous mechanism, not a different mechanism.

**One genuine difference from Python, worth naming precisely:** an `async function` in JavaScript **always returns a Promise**, even if you write a plain `return` with a normal value inside it — that's why `getCurrentTemperature(...)` above still needed a `.then()` to actually use its result, rather than getting the number back directly. (You could instead `await` it from inside another `async function` — this lesson's error-handling example below does exactly that.) Python's `async def` functions work the same way in spirit (calling one gives you a coroutine object, not the result directly — Module 01, Lesson 11) — the parallel holds; only the vocabulary differs (JavaScript calls the returned object a Promise; Python calls it a coroutine).

### Error handling with `async`/`await`: `try`/`catch`

```javascript
async function getWeatherSafely(latitude, longitude) {
  try {
    const response = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m`
    );

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    return data.current.temperature_2m;
  } catch (error) {
    console.error("Could not fetch weather:", error.message);
    return null;
  }
}
```

**Line by line:** `try { ... } catch (error) { ... }` is JavaScript's direct equivalent of Python's `try`/`except` (Module 01, Lesson 06) — code that might throw/reject goes in `try`; the recovery/handling logic goes in `catch`. `response.ok` is a convenience boolean `fetch` provides — `true` for any 2xx status code, `false` otherwise — and this line demonstrates the fix for the exact surprise flagged above: **since `fetch` doesn't reject on HTTP error status codes, you must explicitly check `response.ok` (or inspect `response.status` yourself, per Module 02, Lesson 03's status categories) and `throw` your own error if it's not okay** — otherwise a 404 or 500 response would silently flow through as if it had succeeded, straight into code expecting valid weather data. `throw new Error("...")` creates and immediately throws a real `Error` object — the direct equivalent of Python's `raise SomeException("...")` — which any enclosing `try`/`catch` (or a rejected-Promise `.catch()`, if you're outside an `async` function) will catch.

### Correctly handling loading and error states in the DOM

This is the pattern this module's capstone is built around — combining Lesson 06's DOM skills with this lesson's `fetch`:

```html
<div id="weather-status">Ready.</div>
<div id="weather-result"></div>
```

```javascript
async function showWeather(latitude, longitude) {
  const statusEl = document.querySelector("#weather-status");
  const resultEl = document.querySelector("#weather-result");

  statusEl.textContent = "Loading...";
  resultEl.textContent = "";

  try {
    const response = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m`
    );

    if (!response.ok) {
      throw new Error(`Weather service returned status ${response.status}`);
    }

    const data = await response.json();
    statusEl.textContent = "";
    resultEl.textContent = `Current temperature: ${data.current.temperature_2m}°C`;
  } catch (error) {
    statusEl.textContent = `Error: ${error.message}`;
  }
}

showWeather(52.52, 13.41);
```

**Why this exact shape — set a loading state *before* the `await`, clear/replace it in both the success path and the `catch` — matters:** a real user needs to see *something* happen the instant they trigger a request (Lesson 05's event loop lesson explained why this can take a visible amount of time, not zero), and needs to see a clear, specific failure message rather than a silently blank or frozen-looking page if the request fails. This "loading → success or error, never left hanging" pattern is one you'll rebuild, in slightly different clothes, in React starting Module 04, in FastAPI-backed frontends starting Module 05, and in every AI-feature UI starting Module 13 — it's a genuinely universal shape for handling anything asynchronous in a user interface.

## Common mistakes & gotchas

- **Assuming `fetch` rejects on a 404/500 status code.** It doesn't — check `response.ok` (or `response.status`) explicitly and `throw` your own error if the request wasn't actually successful, exactly as this lesson's `getWeatherSafely` example does. Skipping this check is the single most common `fetch`-related bug.
- **Forgetting `await` before `response.json()`** — `response.json()` returns a Promise, not the parsed data directly; forgetting `await` (or a `.then()`) leaves you holding a Promise object instead of real data, the exact same "forgot to await" mistake Module 01, Lesson 11 flagged for Python coroutines.
- **Using `await` outside an `async function`.** `await` is only valid syntax directly inside a function marked `async` (with one narrow exception, top-level `await` in ES modules — Lesson 08 — not needed for this lesson's examples). Using it elsewhere is a syntax error, not a runtime one — you'll see it immediately when you try to run the file.
- **Not handling the error path at all**, writing only the success case and letting a network failure (no internet, DNS failure, a CORS block) crash silently or leave the UI stuck on "Loading..." forever. Always pair a `try`/`catch` (or `.then`/`.catch`) with a real, visible update to the UI on failure — never assume the happy path is the only path.
- **Confusing JavaScript's Promise-returning `fetch` with Python's `requests` library** (Module 01, Lesson 00's example package) — `requests.get(...)` in Python is **synchronous** by default (it blocks until the response arrives) unless you're specifically using an async HTTP library; `fetch` in JavaScript is asynchronous *by design*, with no synchronous alternative offered at all in a browser — this is a real, structural difference between the two ecosystems' defaults, not just a naming difference.

## How this connects

You can now make real, live requests to a real API from inside a browser, correctly handling loading and error states — this is, quite directly, most of this module's capstone. Lesson 08 covers a handful of remaining modern JavaScript syntax features (destructuring, spread, ES modules) you'll want for writing this cleanly, and Lesson 09 (TypeScript) shows you how to add real type safety on top of exactly this kind of fetch-and-handle-the-response code, so a typo'd property name (`data.current.temprature_2m`) gets caught before you ever run the code, rather than silently returning `undefined` at runtime.

## Quick self-check

1. What are the three states a Promise can be in, and can a settled Promise ever go back to `pending`?
2. Why does `fetch`'s Promise fulfill even for a 404 response, and what line of code fixes the resulting bug if you don't want that behavior?
3. Rewrite, in your own words, why `async`/`await` in JavaScript is "the same mechanism as `.then()`/`.catch()`, just different syntax" rather than a separate feature.
4. Name one genuine difference between how Python's `async def` and JavaScript's `async function` behave when called, and one genuine similarity.
5. In the loading/error DOM example, why is the loading-state line (`statusEl.textContent = "Loading..."`) placed *before* the `await`, not after it?
