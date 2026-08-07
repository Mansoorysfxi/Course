# Lesson 05 — JavaScript Fundamentals, and the Event Loop (Browser Edition)

## What you'll learn

- What JavaScript actually is, and how it's genuinely different from both Python and C++ — not just different syntax for the same ideas.
- Variables: `let`, `const`, and why `var` is a legacy feature this course never uses.
- JavaScript's basic data types, and how "everything is an object" (mostly) plays out in practice.
- Functions: function declarations, function expressions, and your first look at arrow functions.
- Truthy/falsy values in JavaScript — genuinely different rules from Python's, despite the similar-sounding concept.
- The **event loop** — JavaScript's own, browser-flavored version of the single-threaded scheduling idea Module 01 taught for Python's `asyncio`, and precisely how it differs.

## Why this matters

Everything from here to the end of this course that runs in a browser (and, starting Module 04, everything in React) is JavaScript or TypeScript (a layer on top of JavaScript, Lesson 09). Getting the fundamentals genuinely right now — not just "it looks kind of like Python" — prevents a long tail of subtle bugs later, especially around JavaScript's specific type-coercion rules and its single-threaded, non-blocking execution model, which behaves differently from anything in a typical Unreal C++ codebase and only *rhymes* with, rather than exactly matches, Python's `asyncio`.

## Prerequisites

Module 01, Lesson 11 (Python's event loop) — this lesson explicitly compares and contrasts against it, rather than re-teaching the underlying concept from zero. Lessons 01–04 (HTML/CSS) — you'll attach the JavaScript from this lesson onward to real pages you already know how to build and style.

## The concept, explained simply

**JavaScript** is the one and only programming language every major web browser can run natively, with no separate installation (Lesson 00 explained *why* that's also true outside a browser, via Node.js). It was created in 1995, originally in about ten days, specifically to make static HTML pages capable of small interactive behaviors — and despite that rushed, unglamorous origin, it has become one of the most widely used programming languages in the world, purely because it's the only language browsers run.

Here's the core mental shift coming from your existing languages:

- **From C++:** JavaScript is **not compiled ahead of time** into a binary — a browser (or Node.js) reads and executes your `.js` file directly, the same "no separate build step" workflow Module 01 already showed you for Python. JavaScript is also **dynamically typed** (like Python, unlike C++) — a variable's type is whatever value it currently holds, checked at runtime, not fixed at compile time. And unlike C++'s class-based object model, JavaScript's object system is fundamentally **prototype-based** — objects can inherit behavior directly from other specific objects, not only from classes — though modern JavaScript's `class` syntax (which you'll use, starting this lesson) is friendly, class-shaped syntax built *on top of* that underlying prototype system, so day-to-day usage feels far more like the classes you already know than the "prototype" detail might suggest.
- **From Python:** JavaScript is also dynamically typed, so a lot of *that* instinct transfers directly — but JavaScript is more aggressively **loosely typed** in one specific way Python is not: JavaScript will often silently *convert* between types during an operation rather than raising an error (this lesson's "truthy/falsy" and equality sections make this concrete). JavaScript also has **no built-in indentation-based blocks** — it uses curly braces `{ }` everywhere Python uses a colon and indentation, and (crucially) indentation itself is cosmetic in JavaScript, with **zero effect on how code actually runs** — a real, common trip-up for anyone arriving with strong Python habits.

## The details

### `let`, `const`, and why not `var`

```bash
mkdir -p ~/js-fundamentals
cd ~/js-fundamentals
cat > lesson05.js << 'EOF'
let questsCompleted = 3;
questsCompleted = 4;         // fine — let allows reassignment
console.log(questsCompleted);

const maxLevel = 99;
// maxLevel = 100;           // would throw: Assignment to constant variable.
console.log(maxLevel);
EOF
node lesson05.js
```
**Expected output:**
```
4
99
```

**Line by line:** `let` declares a variable that **can** be reassigned later — roughly, "a normal Python variable." `const` declares a variable that **cannot** be reassigned after its initial value — attempting to (the commented-out line) throws a real error, `TypeError: Assignment to constant variable.` **This course, and the overwhelming majority of real-world JavaScript/TypeScript written in 2026, defaults to `const` for everything, switching to `let` only for variables you genuinely know will be reassigned** (a loop counter, an accumulator). This isn't a stylistic preference so much as a real bug-prevention habit: a variable declared `const` simply *cannot* be accidentally reassigned somewhere later in a long function, which is one entire category of bug eliminated for free.

You may encounter a third keyword, `var`, in older code or tutorials — **this course never uses it.** `var` predates `let`/`const` (both introduced in 2015) and has genuinely confusing scoping rules (it ignores block scope — a `var` declared inside an `if` block "leaks" out of that block, unlike `let`/`const`, which correctly stay scoped to the block they're declared in, matching the block-scoping behavior you already know from C++). `var` is not deprecated or broken — old code using it still runs fine — but there is no reason to write new `var` in 2026, and every real style guide agrees.

### Data types

JavaScript has a small set of **primitive** types — values that are not objects and have no methods/properties of their own (JavaScript actually lets you call methods on them anyway, like `"hello".toUpperCase()`, by silently, temporarily wrapping the primitive in an object behind the scenes — a detail worth knowing exists, not worth dwelling on):

```javascript
let questName = "Slay the Dragon";  // string
let rewardGold = 500;                // number — JS has ONE numeric type, not int vs. float
let isUrgent = true;                 // boolean
let assignedTo = null;               // null — deliberate "no value"
let notes;                           // undefined — declared but never assigned
```

**The one genuinely surprising item here, coming from Python or C++: JavaScript has exactly one numeric type, `number`**, covering everything Python splits into `int` and `float`, and everything C++ splits into `int`, `float`, `double`, etc. `500` and `500.5` are both just `number` — there's no separate integer type to worry about for ordinary arithmetic (a separate `bigint` type exists for integers too large for `number` to represent precisely, but you won't need it in this course).

**`null` vs. `undefined`** is a real distinction worth understanding precisely, since Python only has one such concept (`None`): `undefined` means "this variable exists but was never given a value" — JavaScript assigns it automatically, you rarely write it yourself. `null` means "this variable was deliberately set to represent *no value*" — you write this one explicitly, as a real choice, much closer to Python's `None`.

Objects and arrays (JavaScript's equivalents of Python's `dict` and `list`) are covered fully in Lesson 08 alongside destructuring and the spread operator — for now, recognize their basic shape, since you'll see them immediately in this lesson's own examples:
```javascript
let quest = { name: "Slay the Dragon", difficulty: "Hard", rewardGold: 500 };
let questNames = ["Slay the Dragon", "Find the Amulet", "Water the Plants"];
```

### Functions: three ways to write one

```javascript
// 1. Function declaration
function formatQuest(name, difficulty) {
  return `${name} [${difficulty}]`;
}

// 2. Function expression — a function stored in a variable
const formatQuest2 = function(name, difficulty) {
  return `${name} [${difficulty}]`;
};

// 3. Arrow function — a shorter syntax for a function expression
const formatQuest3 = (name, difficulty) => {
  return `${name} [${difficulty}]`;
};

console.log(formatQuest("Slay the Dragon", "Hard"));
console.log(formatQuest2("Slay the Dragon", "Hard"));
console.log(formatQuest3("Slay the Dragon", "Hard"));
```
**Expected output** (all three identical):
```
Slay the Dragon [Hard]
Slay the Dragon [Hard]
Slay the Dragon [Hard]
```

**Line by line, and why three ways exist:** a **function declaration** (`function name(...) { ... }`) is the most direct form, closest to a Python `def`. A **function expression** stores an unnamed (or separately named) function *as a value* inside a variable — functions in JavaScript are genuinely values, the same way a lambda or a plain function reference can be assigned to a variable in Python. An **arrow function** (`(...) => { ... }`) is newer (2015) syntax for writing a function expression more concisely — the `=>` visually separates parameters from body, no `function` keyword needed. `` `${name} [${difficulty}]` `` is a **template literal** — a string wrapped in backticks (`` ` ``) instead of quotes, letting you embed real expressions directly inside `${ }` — JavaScript's direct equivalent of Python's f-strings (Module 01, Lesson 01); Lesson 08 covers template literals in more depth.

**One further arrow-function shorthand you'll see constantly, and use starting this lesson's exercises:** if an arrow function's entire body is just one `return` expression, you can drop both the curly braces *and* the `return` keyword:
```javascript
const formatQuest4 = (name, difficulty) => `${name} [${difficulty}]`;
```
This is exactly equivalent to `formatQuest3` above — genuinely the same function, written more concisely. This "implicit return" shorthand is idiomatic, extremely common real-world JavaScript (and you'll see it everywhere in React starting Module 04) — but only use it when the whole function really is one expression; anything needing more than one statement needs the full `{ return ...; }` form.

**A meaningful behavioral difference to know exists, without needing to master it yet:** arrow functions handle the keyword `this` differently from `function` declarations/expressions (they don't get their own `this` at all — they use whatever `this` means in the surrounding code). `this` itself isn't needed for anything in this module, so this note is here only so the term doesn't blindside you later — Module 04 (React) is where `this`-related subtleties would actually start to matter, and modern React code (hooks-based, which this course teaches) mostly avoids `this` entirely regardless.

### Truthy and falsy — genuinely different rules from Python

Module 01, Lesson 01 taught you Python's truthiness rules (`0`, `""`, `None`, empty collections are falsy). JavaScript has its **own**, separate set of falsy values — similar in spirit, different in the specifics, and this is a real, common source of bugs for anyone assuming the two languages match exactly:

```javascript
// JavaScript's falsy values — memorize this exact list, it's short:
// false, 0, "" (empty string), null, undefined, NaN

if (0) {
  console.log("truthy");
} else {
  console.log("falsy");   // this runs
}

if ("0") {
  console.log("truthy");  // this runs! Non-empty string, even "0", is truthy
} else {
  console.log("falsy");
}

if ([]) {
  console.log("truthy");  // this runs! An empty array is truthy in JS
} else {
  console.log("falsy");
}
```
**Expected output:**
```
falsy
truthy
truthy
```

**This is the specific trap:** Python's empty list `[]` is falsy; **JavaScript's empty array `[]` is truthy** — arrays and objects are truthy in JavaScript *regardless of whether they're empty*, because they're real objects (technically, non-null references), and every object is truthy — only the six specific values listed above are falsy. Coming from Python, testing `if (someArray)` expecting it to mean "is this array non-empty" is a genuine, common bug — the correct JavaScript idiom is `if (someArray.length > 0)` or, equally common, `if (someArray.length)` (since `0` itself is falsy, this reads naturally as "if there's at least one item").

### The event loop — JavaScript's version, compared directly to Python's

Module 01, Lesson 11 taught you Python's `asyncio` event loop with a game-loop analogy: a single-threaded loop that runs one coroutine at a time, resuming each one when whatever it was waiting on becomes ready, giving the *illusion* of many things happening at once without genuine parallel execution. **JavaScript's event loop is built on exactly the same core idea — single thread, cooperative scheduling, an illusion of simultaneity from rapid switching — applied to a different, browser-shaped problem: keeping a webpage responsive to the user while things load and finish in the background.**

Run this to see it directly:
```javascript
console.log("1: start");

setTimeout(() => {
  console.log("2: inside setTimeout callback");
}, 0);

console.log("3: end");
```
**Expected output:**
```
1: start
3: end
2: inside setTimeout callback
```

**This ordering is the entire lesson, demonstrated in five lines — and it surprises almost everyone the first time.** Even with a delay of `0` milliseconds, the `setTimeout` callback runs **last**, after both `console.log` calls that appear *after* it in the source. Here's precisely why, and this is where "the event loop" as a concrete mechanism becomes real rather than an abstract phrase:

- JavaScript runs on **one single thread**, executing one thing at a time, top to bottom, via something called the **call stack** — the exact record of "which function is currently running, and which function called it," the same concept behind the stack traces Module 00, Lesson 02 taught you to read.
- `console.log("1: start")` runs immediately, synchronously, on the call stack.
- `setTimeout(callback, 0)` does **not** run `callback` immediately, no matter how small the delay. It hands `callback` off to the browser (or Node.js) itself, which starts a timer, and then `setTimeout` *itself* returns right away, letting the rest of your code keep running. This is the exact "I'm about to wait on something — go let someone else run" idea from Python's `await`, except here it's `setTimeout` doing the handing-off, not an `async`/`await` keyword pair (this lesson's JavaScript doesn't need `async`/`await` yet — Lesson 07 introduces it for `fetch` specifically).
- `console.log("3: end")` runs next, immediately, since the call stack is now free and nothing is blocking it.
- **Only once the call stack is completely empty** — every synchronous line of your script has already finished running — does the event loop check whether any pending callback (like your timer's callback, once its delay has elapsed) is ready to run, and finally runs it. This is why `"2: ..."` prints dead last, even with a `0`ms delay: the delay isn't really "0 milliseconds from now," it's "as soon as possible, but strictly *after* every currently-running synchronous line has already finished."

**The precise parallel to draw against Module 01:** Python's `await` explicitly, visibly marks the exact point where a coroutine says "I might pause here." JavaScript's browser event loop reaches the equivalent pause *implicitly*, automatically, the instant any currently-running synchronous code finishes and the call stack empties out — there's no keyword marking it in this `setTimeout` example specifically, though Lesson 07's `async`/`await` reintroduces an explicit, Python-shaped way to write this same underlying pause-and-resume behavior for a specific case (`fetch`) where writing raw callbacks would get unreadable fast.

**Why any of this matters practically, right now, before you've even met `fetch`:** JavaScript in a browser runs on the **same** single thread that also handles rendering the page and responding to clicks/scrolls. If your JavaScript ever runs a long, synchronous, CPU-heavy loop with no pauses, the *entire page freezes* for that whole duration — no clicks register, nothing redraws — exactly the "blocking the event loop" danger Module 01, Lesson 11 warned about for Python's `asyncio`, except here the visible cost is a frozen, unresponsive *webpage* a real user is looking at, not just a slow background task. This is precisely *why* slow operations in a browser — loading data from a server (Lesson 07's `fetch`), waiting on a timer — are built to be asynchronous/non-blocking by default, handed off to the browser itself rather than run directly, blocking, on your one and only thread.

## Common mistakes & gotchas

- **Using `var` out of habit from an old tutorial.** Use `const` by default, `let` when reassignment is genuinely needed, never `var`, for the scoping reasons explained above.
- **Assuming JavaScript's falsy values match Python's exactly.** They don't — memorize JavaScript's actual short list (`false, 0, "", null, undefined, NaN`) and specifically remember that `[]` and `{}` (empty array/object) are **truthy** in JavaScript, unlike Python's falsy empty collections.
- **Relying on indentation to mean anything.** JavaScript ignores whitespace/indentation entirely for execution — only curly braces `{ }`, parentheses, and semicolons (mostly optional but used consistently in this course for clarity) define actual structure. Badly-indented JavaScript can still run perfectly correctly, which is exactly why it's worth indenting consistently *for humans*, not because the language requires it.
- **Expecting `setTimeout(fn, 0)` to run `fn` immediately, synchronously.** It never does — it always waits for the current call stack to fully empty first, however briefly that takes, exactly as this lesson's ordering example demonstrated.
- **Confusing JavaScript's event loop with genuine multithreading.** Exactly like Python's `asyncio` (Module 01, Lesson 11): one thread, no true parallel execution, ever, in ordinary JavaScript — only the *illusion* of overlap, from not wasting time on things that are merely waiting.

## How this connects

You now have real JavaScript syntax fundamentals and, critically, the actual mechanism (call stack, single thread, event loop, non-blocking handoff for slow operations) behind everything that follows. Lesson 06 puts this syntax to work manipulating an actual page (the DOM) and responding to real user events — using exactly the functions, variables, and truthy/falsy rules from this lesson, now applied to something visible and interactive rather than `console.log` output. Lesson 07 revisits the event loop directly, showing how `fetch` and `async`/`await` build a cleaner, Python-`await`-shaped syntax directly on top of the exact non-blocking mechanism this lesson just demonstrated with `setTimeout`.

## Quick self-check

1. Give two concrete reasons JavaScript is not simply "Python with different punctuation," even though both are dynamically typed.
2. Why does this course default to `const` and treat `let` as the exception, never `var`?
3. List all six of JavaScript's falsy values from memory, and name one JavaScript value that is truthy despite being falsy in Python.
4. Walk through, line by line, exactly why `"2: inside setTimeout callback"` printed last in this lesson's ordering example, even with a 0ms delay.
5. In the game-loop analogy from Module 01, what does JavaScript's call stack correspond to, and what actually happens the moment it becomes empty?
