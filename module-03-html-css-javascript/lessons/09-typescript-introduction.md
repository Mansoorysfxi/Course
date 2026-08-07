# Lesson 09 — TypeScript: Why Types Matter, and the Basics

## What you'll learn

- What TypeScript actually is in relation to JavaScript, and why it exists.
- Why static types matter at scale — an argument you already believe from C++, applied to why the JavaScript world eventually wanted it back.
- Type annotations on variables, function parameters, and return values.
- `interface` — describing the shape of an object, and comparing it directly to a C++ `struct`/Python's type hints on a `dict`.
- Union types, optional properties, and the specific type-safety trap `any` represents.
- Typing a real `fetch` response, and catching a genuine bug at compile time that plain JavaScript would only reveal at runtime.

## Why this matters

You already know, from years of C++, that the compiler catching a type mismatch before the program ever runs is worth something real — a category of bug simply doesn't reach you at runtime, or reach a user in production, or reach a teammate reviewing your pull request. JavaScript has no such compiler at all — Lesson 05 showed you a JavaScript file just... runs, with the interpreter discovering type problems (if it discovers them at all) only at the exact moment a broken line actually executes. TypeScript exists specifically to give JavaScript back the thing C++ never let you live without — and once you've used it on even one small project, like this module's capstone, you'll understand exactly why huge, real-world JavaScript codebases overwhelmingly choose to write TypeScript instead.

## Prerequisites

Lesson 00 (Node.js/TypeScript installed, `tsc` compiling, `tsconfig.json` already set up). Lessons 05–08 (the JavaScript this lesson adds types on top of). Module 01, Lesson 09 (Python type hints) — this lesson compares directly against it.

## The concept, explained simply

**TypeScript is JavaScript, plus an optional type-annotation syntax, plus a compiler (`tsc`) that checks those annotations *before* your code runs and then strips them out, producing plain JavaScript.** Every valid piece of JavaScript is close to being valid TypeScript too (TypeScript was deliberately designed as a **superset** of JavaScript) — you're not learning a separate language from scratch, you're learning an additional layer of optional annotations on top of everything Lessons 05–08 already taught you.

Here's the comparison worth sitting with, since it maps onto two things you already know from different angles:

- **From C++:** you already know what a compiler catching `int x = "hello";` before the program runs feels like, and you already know the discipline of declaring a function's parameter and return types up front. TypeScript's type checking happens at a similar point in your workflow — before running — but with one real, structural difference worth naming precisely: **TypeScript's types are erased entirely at compile time and have zero effect on how the compiled JavaScript actually runs.** There is no runtime type checking left over, no performance cost, and no way for a type annotation to change your program's actual behavior — it purely catches mistakes *before* you run, then vanishes.
- **From Python (Module 01, Lesson 09):** you already know Python's type hints (`def foo(x: int) -> str:`) are *not enforced by the interpreter itself* — they're annotations a separate tool (a **type checker**, like Pylance/mypy) reads and checks, entirely optionally, with Python running your code exactly the same whether you add hints or not. **TypeScript works on the same principle** — `tsc` is that separate type-checking tool, exactly analogous to mypy — except TypeScript's checking is enforced as a mandatory step *before* your code can even be compiled into runnable JavaScript at all (recall Lesson 00's deliberate demonstration: `const greeting: string = 42;` made `tsc` outright refuse to compile), where Python happily runs code a type checker would have flagged, since Python's checker is entirely optional and separate from actually running the program.

## The details

### Type annotations on variables and functions

```bash
cd ~/js-practice   # from Lesson 00
cat > src/quests.ts << 'EOF'
let questName: string = "Slay the Dragon";
let rewardGold: number = 500;
let isUrgent: boolean = true;

function formatQuest(name: string, difficulty: string, rewardGold: number): string {
  return `${name} [${difficulty}] — ${rewardGold} gold`;
}

console.log(formatQuest(questName, "Hard", rewardGold));
EOF
npx tsc
node dist/quests.js
```
**Expected output:**
```
Slay the Dragon [Hard] — 500 gold
```

**Line by line:** `let questName: string = ...` is a **type annotation** — `: string` states, explicitly, that `questName` must always hold a string; assigning it a number later would be a compile error, exactly like Lesson 00's deliberate mistake. `function formatQuest(name: string, difficulty: string, rewardGold: number): string` annotates every parameter *and* the return type — the `: string` right after the closing `)` says "this function must return a string," and `tsc` checks the function body's actual `return` statement(s) against that promise.

**Try it yourself:** change `formatQuest`'s body to `return rewardGold;` (returning a number where a string was promised) and run `npx tsc` again. Predict the error before running. **Expected:** `error TS2322: Type 'number' is not assignable to type 'string'.` — the return-type annotation caught a genuine mismatch between what the function promised and what it actually did, before a single line of the compiled JavaScript ever ran.

**Type inference — you don't always need to write the annotation explicitly:**
```typescript
let maxLevel = 99;      // tsc infers `number` automatically — no `: number` needed
// maxLevel = "high";   // still an error! tsc remembers the inferred type just as strictly.
```
TypeScript is usually smart enough to figure out (**infer**) a variable's type from its initial value, without you writing it explicitly — and once inferred, that type is enforced exactly as strictly as if you'd written it by hand. This course writes explicit annotations on function parameters and return types (where inference can't see far enough ahead to help) and lets inference handle simple local variables — matching real-world TypeScript style.

### `interface` — describing the shape of an object

```typescript
interface Quest {
  name: string;
  difficulty: string;
  rewardGold: number;
  completed: boolean;
}

function formatQuest(quest: Quest): string {
  return `${quest.name} [${quest.difficulty}] — ${quest.rewardGold} gold`;
}

const dragonQuest: Quest = {
  name: "Slay the Dragon",
  difficulty: "Hard",
  rewardGold: 500,
  completed: false,
};

console.log(formatQuest(dragonQuest));
```
**Expected output:**
```
Slay the Dragon [Hard] — 500 gold
```

**Line by line:** `interface Quest { ... }` declares a **named shape** — exactly what any object claiming to be a `Quest` must contain: these four properties, with these four exact types. This is genuinely close to a C++ `struct` declaring its member variables and types up front, or to a Python `TypedDict`/dataclass with type hints (Module 01, Lesson 09) describing a dict's expected shape — all three are ways of saying "here is the guaranteed shape of this data," checked before use rather than discovered by accident at some `some_dict["typo_key"]` runtime `KeyError`.

**Try it yourself:** delete the `rewardGold: 500,` line from `dragonQuest` and run `npx tsc`. Predict the error. **Expected:** `error TS2741: Property 'rewardGold' is missing in type '{ ... }' but required in type 'Quest'.` — a genuinely missing field, caught immediately, at the exact point of creation, rather than discovered later as `undefined` the first time something tries to use `quest.rewardGold` at runtime.

### Optional properties, union types, and the trap of `any`

```typescript
interface Quest {
  name: string;
  difficulty: string;
  rewardGold: number;
  completed: boolean;
  notes?: string;              // optional — may be present or absent
  status: "open" | "closed";   // union type — must be exactly one of these two strings
}

const quest: Quest = {
  name: "Water the Plants",
  difficulty: "Trivial",
  rewardGold: 5,
  completed: false,
  status: "open",
};
```

**Line by line:** `notes?: string` — the `?` marks a property as **optional**; an object satisfying `Quest` may include `notes` or leave it out entirely, and TypeScript will correctly type `quest.notes` as `string | undefined` (note the `|` — that's a **union type**, meaning "one type or another") anywhere you access it, forcing you to actually consider the missing case (exactly what Lesson 08's `?.`/`??` operators exist to handle cleanly) rather than assuming it's always there. `status: "open" | "closed"` is a union type made of specific **string literal values**, not general types — this means `status` can genuinely only ever be exactly `"open"` or exactly `"closed"`; assigning `status: "in-progress"` (a real string, but not one of the two allowed values) is a compile error. This is a small but genuinely powerful TypeScript pattern for representing a fixed, known set of valid states — directly comparable to reaching for a Python `Enum`, but expressed as literal-string types instead.

**The trap of `any`, worth naming explicitly since you'll be tempted by it constantly at first:**
```typescript
let quest: any = { name: "Slay the Dragon" };
quest.thisPropertyDoesNotExist.someMethod();   // tsc allows this with ZERO complaint
```
`any` tells TypeScript "stop checking this value's type entirely" — it's an escape hatch, and using it anywhere quietly disables every benefit this lesson is teaching you, for that one value, with no warning that you've done so. It compiles fine and then crashes at runtime exactly like plain, un-typed JavaScript would have — you've paid for a type system and then opted out of it. **This course, and most real production TypeScript style guides, treat `any` as something to avoid deliberately**, reaching for it only as a genuinely last resort (interfacing with an untyped third-party library, for instance) rather than a quick way to make an error message go away. If you ever find yourself typing `: any` just to silence `tsc`, that's a strong signal to pause and figure out the *actual* correct type instead.

### Typing a real `fetch` response — catching a real bug at compile time

This is where TypeScript's payoff becomes concrete, using exactly Lesson 07's Open-Meteo example:

```typescript
interface CurrentWeather {
  temperature_2m: number;
  relative_humidity_2m: number;
}

interface WeatherResponse {
  latitude: number;
  longitude: number;
  current: CurrentWeather;
}

async function getCurrentTemperature(latitude: number, longitude: number): Promise<number> {
  const response = await fetch(
    `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,relative_humidity_2m`
  );

  if (!response.ok) {
    throw new Error(`Weather service returned status ${response.status}`);
  }

  const data = (await response.json()) as WeatherResponse;
  return data.current.temperature_2m;
}
```

**Line by line:** `interface WeatherResponse` describes exactly the JSON shape Lesson 07 actually observed from a real Open-Meteo response — this is the concrete, common real-world pattern: write an `interface` matching a real API's real documented (or observed) response shape, once, and every place you use that data afterward gets checked against it. `Promise<number>` is a **generic type** — `Promise` on its own doesn't say *what* it eventually resolves to; `<number>` fills in that detail, stating precisely "this async function's Promise, once it fulfills, holds a number" (you don't need to write your own generic types for this module — recognizing this one built-in pattern is enough). `(await response.json()) as WeatherResponse` uses a **type assertion** (`as SomeType`) — this is worth being honest about exactly what it does and doesn't do: `response.json()`'s actual return type is only ever `any` (TypeScript genuinely cannot know, on its own, what shape of JSON a network response will contain), so `as WeatherResponse` is you, the developer, *asserting* "trust me, I know this will actually have this shape" — TypeScript takes your word for it and checks everything *after* this line against `WeatherResponse`, but it performed **no actual runtime verification** that the real response truly matches. If Open-Meteo's real response were missing `relative_humidity_2m` entirely, this code would still compile fine and only fail later, at runtime, when something tries to use a value that's actually `undefined` — type assertions are a genuinely useful, common pattern, but they are a promise *you* make, not a guarantee TypeScript verifies for you.

**Try it yourself:** in `data.current.temperature_2m`, deliberately misspell it as `data.current.temprature_2m` (dropping the middle `e`) and run `npx tsc`. Predict the error. **Expected:** `error TS2551: Property 'temprature_2m' does not exist on type 'CurrentWeather'. Did you mean 'temperature_2m'?` — TypeScript even suggests the correct name. In plain JavaScript, this exact typo would have compiled and run with zero complaint, silently returning `undefined` everywhere `temprature_2m` was read — a bug you might not notice until a user reports a broken weather display. This one example is the entire case for TypeScript, demonstrated concretely rather than argued abstractly.

## Common mistakes & gotchas

- **Reaching for `any` the first time `tsc` complains**, rather than writing the correct type. This defeats the entire purpose for that value — treat `any` as a last resort, not a first response to a red squiggle.
- **Forgetting that type assertions (`as SomeType`) are not runtime checks.** `as` only affects what `tsc` *believes* about a value's shape for the rest of your code — it performs no actual validation of the real data. A genuinely malformed API response will still cause a runtime error later; `as` just changes when/how confidently your own code *assumes* it's safe until then.
- **Forgetting the `?` on a property that's genuinely sometimes absent**, and TypeScript correctly, strictly flagging every object literal that omits it — this is TypeScript doing its job, not a bug in the type system; the fix is either adding `?` if absence is legitimately allowed, or actually always providing the field if it's supposed to be required.
- **Confusing `interface` (a type-only description, entirely erased at compile time — it produces zero actual JavaScript) with a `class`** (a real, runtime construct that still exists in the compiled output, since JavaScript itself has classes — Lesson 05 mentioned this). This module sticks to `interface` for describing plain data shapes, which is by far the most common real-world use for API response/request data.
- **Not re-running `npx tsc` after an edit and wondering why an old error (or old bug) is still "there."** `tsc` only checks/compiles when you actually run it — unlike Python or plain JavaScript, where saving and re-running a file always uses your latest edit automatically. Get in the habit of `npx tsc` (or `npx tsc --watch`, which recompiles automatically on every save — worth using for this module's capstone) before assuming your latest change took effect.

## How this connects

You now have every individual skill this module set out to teach: HTML structure (Lesson 01), CSS layout (Lessons 02–04), JavaScript fundamentals and the event loop (Lesson 05), the DOM and events (Lesson 06), `fetch`/Promises/`async`-`await` (Lesson 07), modern JavaScript syntax (Lesson 08), and now TypeScript's type system on top of all of it. This module's capstone (`project/BRIEF.md`) combines every one of these into one real, working weather dashboard — semantic, accessible HTML; a responsive Flexbox/Grid layout; a TypeScript file, compiled with `tsc`, that fetches live weather data with correctly typed responses, handles loading/error states, and updates the DOM. Module 04 then rebuilds QuestLog on React, which you'll now recognize as a tool that automates large parts of exactly what Lesson 06 (the DOM) and this lesson (types) had you do by hand.

## Quick self-check

1. What specifically happens to TypeScript's type annotations when `tsc` compiles a file — do they exist anywhere in the output?
2. Compare TypeScript's `tsc` to Python's type checker (Module 01, Lesson 09) — name one genuine similarity and one genuine difference in how strictly each is enforced.
3. What does `status: "open" | "closed"` allow that a plain `status: string` would not catch?
4. Why is `as WeatherResponse` not the same thing as TypeScript actually verifying the real API response's shape at runtime?
5. Give one concrete reason to avoid reaching for `any` the moment `tsc` reports an error you don't immediately understand.
