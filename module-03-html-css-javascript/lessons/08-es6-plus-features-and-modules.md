# Lesson 08 — Modern JavaScript: Destructuring, Spread, Template Literals, and Modules

## What you'll learn

- Template literals, properly — multi-line strings and nesting expressions, beyond the basics Lesson 05 introduced.
- **Destructuring** — pulling values out of objects and arrays into named variables in one step.
- The **spread operator** (`...`) — expanding an array/object's contents into another array/object, or into function arguments.
- Optional chaining (`?.`) and nullish coalescing (`??`) — two small operators that eliminate a huge amount of defensive "is this actually there" checking.
- **ES modules** (`import`/`export`) — how to split JavaScript across multiple files properly, and how this compares to Python's `import` system.
- A note on what "ES6+" and "modern JavaScript" actually mean as terms, and confirmation of which features are genuinely standard, stable, and safe to rely on in 2026.

## Why this matters

Every one of these features shows up constantly in real-world JavaScript and TypeScript code — and, not coincidentally, in essentially every React example you'll see starting Module 04 (destructuring props, spreading arrays/objects for state updates, optional chaining on data that might not have loaded yet). Learning them now, on small standalone examples, means Module 04's React syntax reads as "the same JavaScript I already know, in a new context" rather than a wall of unfamiliar punctuation.

## Prerequisites

Lesson 05 (variables, functions, basic template literals) and Lesson 07 (you'll destructure the exact kind of API response object `fetch` gave you there).

## The concept, explained simply

**"ES6"** refers to **ECMAScript 2015** — ECMAScript is the official, standardized specification JavaScript implements (the language's formal name; "JavaScript" is really the common/trademarked name for one implementation of it), and 2015's edition (its sixth, hence "ES6") introduced an unusually large batch of changes at once: `let`/`const`, arrow functions, template literals, destructuring, the spread operator, classes, and modules, among others. Every one of these has been standard, universally supported, "just JavaScript" for roughly a decade at this point — there is nothing experimental or cutting-edge about any feature in this lesson; "ES6+ features" is really just a historical label for "the modern JavaScript syntax everyone uses," not a warning that any of it might not work somewhere. **Verified for this lesson (August 2026):** every feature covered here — destructuring, spread, optional chaining, nullish coalescing, and ES modules — is formally "Baseline: Widely available" per current browser-compatibility references, meaning it has worked, unchanged, in every major browser for years.

## The details

### Template literals, beyond the basics

```javascript
const questName = "Slay the Dragon";
const rewardGold = 500;

// Multi-line, with no \n needed
const summary = `Quest: ${questName}
Reward: ${rewardGold} gold`;
console.log(summary);

// Expressions, not just variables, are allowed inside ${ }
console.log(`Half the reward is ${rewardGold / 2} gold.`);
```
**Expected output:**
```
Quest: Slay the Dragon
Reward: 500 gold
Half the reward is 250 gold.
```

Backtick-quoted strings genuinely span multiple lines with no escape sequence needed (try this with a regular `"..."` string and confirm it's a syntax error), and `${ }` accepts any valid JavaScript expression, not just a bare variable name — exactly like Python's f-strings (Module 01, Lesson 01) accepting arbitrary expressions inside `{ }`.

### Destructuring objects and arrays

```javascript
const quest = { name: "Slay the Dragon", difficulty: "Hard", rewardGold: 500 };

// Without destructuring:
const name1 = quest.name;
const difficulty1 = quest.difficulty;

// With destructuring — same result, one line:
const { name, difficulty } = quest;
console.log(name, difficulty);
```
**Expected output:**
```
Slay the Dragon Hard
```

**Line by line:** `const { name, difficulty } = quest;` pulls the `name` and `difficulty` properties out of `quest` directly into two new variables of the same names, in one statement — the direct JavaScript equivalent of Python's tuple/dict unpacking. Rename while destructuring with `:`:
```javascript
const { name: questTitle } = quest;
console.log(questTitle);   // "Slay the Dragon" — bound to a differently-named variable
```

Array destructuring works positionally, not by name:
```javascript
const coordinates = [52.52, 13.41];
const [latitude, longitude] = coordinates;
console.log(latitude, longitude);
```
**Expected output:**
```
52.52 13.41
```

**Where you'll use this constantly, starting immediately:** destructuring function parameters directly, extremely common in real code (and everywhere in React props starting Module 04):
```javascript
function formatQuest({ name, difficulty, rewardGold }) {
  return `${name} [${difficulty}] — ${rewardGold} gold`;
}
console.log(formatQuest(quest));
```
This function never needs a separate `quest.name`/`quest.difficulty` line at all — the parameter list itself destructures the incoming object.

### The spread operator (`...`)

```javascript
const baseQuest = { name: "Slay the Dragon", difficulty: "Hard" };

// Create a NEW object with all of baseQuest's properties, plus one more
const questWithReward = { ...baseQuest, rewardGold: 500 };
console.log(questWithReward);

// Overriding a property while spreading — later properties win
const easierQuest = { ...baseQuest, difficulty: "Easy" };
console.log(easierQuest);
```
**Expected output:**
```
{ name: 'Slay the Dragon', difficulty: 'Hard', rewardGold: 500 }
{ name: 'Slay the Dragon', difficulty: 'Easy' }
```

**Line by line:** `{ ...baseQuest, rewardGold: 500 }` builds a genuinely **new** object, copying every property from `baseQuest` into it, then adding (or, if the same key repeats, overwriting) `rewardGold`. **The critical detail: `baseQuest` itself is completely unmodified** — `questWithReward` and `easierQuest` are new, independent objects. This "make a changed copy instead of mutating the original" pattern is exactly the "don't silently mutate what a caller handed you" principle Module 01, Lesson 03 taught for Python lists/dicts — and it's *the* standard way React (Module 04) updates state, since React specifically needs to detect "this is a genuinely new object" to know a re-render is needed.

The exact same `...` syntax works on arrays:
```javascript
const easyQuests = ["Water the Plants", "Sweep the Floor"];
const allQuests = [...easyQuests, "Slay the Dragon"];
console.log(allQuests);
```
**Expected output:**
```
[ 'Water the Plants', 'Sweep the Floor', 'Slay the Dragon' ]
```

And spread also works to expand an array directly into individual function arguments:
```javascript
function totalGold(a, b, c) {
  return a + b + c;
}
const rewards = [100, 250, 50];
console.log(totalGold(...rewards));
```
**Expected output:** `400` — directly analogous to Python's `*args` unpacking a list/tuple into separate positional arguments (Module 01, Lesson 02), though note the direction is reversed from Python's `*rewards` *parameter* syntax: here, `...rewards` is spreading an *existing* array out at the call site, not collecting incoming arguments into one.

### Optional chaining (`?.`) and nullish coalescing (`??`)

```javascript
const quest = { name: "Slay the Dragon", giver: { name: "Elder Mira" } };
const questWithNoGiver = { name: "Water the Plants" };

console.log(quest.giver?.name);              // "Elder Mira"
console.log(questWithNoGiver.giver?.name);   // undefined — no crash

// Without ?. , this next line would throw:
// console.log(questWithNoGiver.giver.name); // TypeError: Cannot read properties of undefined
```

**Line by line:** `quest.giver?.name` means "if `quest.giver` is `null` or `undefined`, stop right there and evaluate to `undefined` — otherwise, continue and read `.name` normally." This directly solves the exact `TypeError: Cannot read properties of null/undefined` crash Lesson 06 flagged as one of the most common real JavaScript runtime errors — anywhere you're not 100% certain a nested property chain exists (extremely common with data that came from an API, like Lesson 07's `fetch` responses, where a field might legitimately be missing), `?.` lets you check safely in one operator instead of a multi-line manual `if` chain.

`??` (**nullish coalescing**) supplies a default value, specifically only when the left side is `null` or `undefined` — not for other falsy values like `0` or `""`, which is precisely the distinction that makes it more precise than JavaScript's older `||` ("or") trick for defaults:
```javascript
const rewardGold = quest.rewardGold ?? 0;

const zeroReward = { rewardGold: 0 };
console.log(zeroReward.rewardGold ?? 100);   // 0 — correctly kept, since 0 is a REAL value, not missing
console.log(zeroReward.rewardGold || 100);   // 100 — WRONG here: || treats falsy 0 as "missing" too
```
**This is the exact bug `??` was introduced specifically to fix:** `||` can't distinguish "this value is genuinely `0`" from "this value doesn't exist at all" — both are falsy (recall Lesson 05's JavaScript falsy list), so `||` incorrectly overrides a real, intentional `0` with the fallback. `??` only triggers its fallback for the two actually-missing values, `null`/`undefined`, leaving a real `0` (or `""`, or `false`) alone. Combine both operators for the single most common real-world pattern you'll write constantly: `quest.giver?.name ?? "Unknown"`.

### ES modules — splitting code across files properly

```bash
cd ~/js-fundamentals
cat > formatting.js << 'EOF'
export function formatQuest(quest) {
  return `${quest.name} [${quest.difficulty}]`;
}

export const DEFAULT_DIFFICULTY = "Easy";
EOF

cat > main.js << 'EOF'
import { formatQuest, DEFAULT_DIFFICULTY } from "./formatting.js";

console.log(formatQuest({ name: "Slay the Dragon", difficulty: "Hard" }));
console.log(DEFAULT_DIFFICULTY);
EOF
```

To run ES modules with Node.js directly, either name files `.mjs`, or (simpler, and what this course uses) add one line to `package.json`: `"type": "module"`. In your `~/js-fundamentals` project (Lesson 00 already ran `npm init -y` there):
```bash
node -e "const fs=require('fs'); const pkg=JSON.parse(fs.readFileSync('package.json')); pkg.type='module'; fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2));"
node main.js
```
**Expected output:**
```
Slay the Dragon [Hard]
Easy
```

**Line by line:** `export function formatQuest(...)` and `export const DEFAULT_DIFFICULTY` mark these two names as available for *other files* to import — anything not marked `export` stays private to `formatting.js`, the direct equivalent of Module 01, Lesson 07's point that everything in a Python module is technically importable, but only exported names are the *intended* public surface (JavaScript actually enforces this one — a non-exported name genuinely cannot be imported at all, a stricter guarantee than Python's convention-based privacy). `import { formatQuest, DEFAULT_DIFFICULTY } from "./formatting.js";` is JavaScript's `from ... import ...` — the `./` prefix marks this as a **relative import** (recall the exact term from Module 01, Lesson 07, now applied to JavaScript's own, separately-designed module system) — pointing at a specific file path rather than a globally-installed package name (which would have no `./` prefix, e.g. `import { z } from "zod";` for an npm-installed package like the ones Lesson 00's `npm install` mechanism fetches).

**In a browser**, rather than Node.js, this same `import`/`export` syntax works directly in a `<script>` tag, with one required change:
```html
<script type="module" src="main.js"></script>
```
`type="module"` tells the browser to treat this script (and anything it `import`s) as an ES module rather than a classic script — this is the exact tag you'll use in this module's capstone to load a compiled TypeScript file (Lesson 09) as a proper module in the browser.

## Common mistakes & gotchas

- **Trying to use `import`/`export` in a plain `<script>` tag without `type="module"`.** Classic (non-module) scripts don't understand `import`/`export` syntax at all and will throw a syntax error — always add `type="module"` when using ES modules in a browser.
- **Forgetting the `.js` file extension in a relative import** (`from "./formatting"` instead of `from "./formatting.js"`). Node.js's ES module loader and browsers both require the extension explicitly for relative imports — unlike some bundler-based setups you may see in tutorials (including some React tooling, later in this course) that allow omitting it. This course's plain Node.js/browser examples need the extension.
- **Assuming spread (`...`) does a "deep" copy.** It only copies one level deep — `{ ...quest, giver: quest.giver }` still shares the *same* nested `giver` object by reference; mutating `questCopy.giver.name` would still affect the original `quest.giver` too. Deep-copying is a more advanced topic outside this lesson's scope; for this module's needs, one level of spread is enough as long as you're aware of the limit.
- **Using `||` for a default value on a field that might legitimately be `0` or `""`.** Use `??` instead whenever "the real value is falsy but not missing" is a genuine possibility (a reward of `0` gold, an empty-but-valid string) — this is precisely the bug `??` exists to prevent.
- **Chaining `?.` past a genuine function call incorrectly.** `obj.method?.()` (note the `?.` *before* the parentheses) calls `method` only if it exists — `obj.method?.` alone, with no following `()`, doesn't call anything at all; a common typo when adapting existing code.

## How this connects

You now have the modern JavaScript vocabulary that shows up in essentially every real-world example, tutorial, and React codebase you'll read from Module 04 onward — destructuring props, spreading state updates, optional-chaining API data are not React-specific tricks, they're this lesson's plain JavaScript, simply used heavily *by* React. Lesson 09 closes out this module by adding TypeScript's type system on top of everything you've learned in Lessons 05–08, so the same destructuring/spread/optional-chaining patterns you just practiced get real compile-time type checking, too.

## Quick self-check

1. What does `const { name, difficulty } = quest;` do, and what's its closest Python equivalent?
2. Why does `{ ...baseQuest, rewardGold: 500 }` not modify `baseQuest` at all, and why does that matter for how React (Module 04) detects changes?
3. Give a concrete example where `??` and `||` produce genuinely different results, and explain why.
4. What does `type="module"` on a `<script>` tag actually change, and what would happen if you used `import`/`export` without it?
5. Is any feature in this lesson experimental or at risk of not being supported in a current browser? How do you know?
