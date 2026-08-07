# Lesson 07 — Frontend Testing with Vitest and React Testing Library

## What you'll learn

- What Vitest is, and how it mirrors everything Lessons 02–03 already
  taught about `pytest` — same core ideas, new syntax.
- What React Testing Library (RTL) is, and its central, opinionated
  philosophy: **test behavior, not implementation**.
- The three-step shape every RTL test follows: **render**, **interact**,
  **assert** — and the specific functions each step uses (`render`,
  `screen`, `userEvent`, `expect`).
- How `vi.mock` replaces an entire module for a test — JavaScript's
  direct equivalent of Lesson 03's `unittest.mock.patch`.
- How to read and understand this module's own four real frontend test
  files, and why each one is shaped the way it is.

## Why this matters

Every backend lesson so far tested Python code. QuestLog's frontend
(Module 04 onward) is a completely separate codebase, in a completely
different language, and needs its own, separate testing story — the
core *ideas* (Lesson 01's testing pyramid, fixtures-as-setup, mocking)
transfer directly, but the concrete tools do not. This lesson is where
you learn the frontend-specific vocabulary and tools, then apply them to
QuestLog's own real components.

## Prerequisites

Module 04 (React components, props, state, hooks) in full — this lesson
assumes you can already read `QuestForm.tsx`, `ProtectedRoute.tsx`, and
`QuestListPage.tsx` and understand what each one does. Lessons 01–03
(the testing pyramid, fixtures, mocking) — this lesson reuses every one
of those concepts, translated into JavaScript/TypeScript.

## The concept, explained simply

**Vitest is `pytest`'s direct counterpart for JavaScript/TypeScript** —
a test runner that discovers test files, runs test functions, and
reports pass/fail, built specifically to work well with Vite (the same
build tool QuestLog's frontend already uses, Module 04) and to feel
familiar to anyone who's used Jest (an older, extremely popular
JavaScript test runner Vitest deliberately mirrors the API of).

**React Testing Library answers a different, more specific question:**
given that you *have* a test runner, how should you actually test a React
component? Its answer, stated as directly as its own documentation
states it: **test your software the way your users use it** — meaning,
concretely: find things on screen the way a real user would (by the text
they can see, by a label, by a button's accessible name), interact with
them the way a real user would (click, type), and check what a real user
would actually observe (text on screen, whether a button is disabled) —
**never** by reaching into a component's internal state, calling its
internal functions directly, or checking implementation details a real
user could never see at all. This is a deliberate, opinionated
constraint, not an accident of the library's design — RTL's own utilities
are built to make the "wrong," implementation-reaching way of testing
awkward on purpose, and the "right," behavior-focused way the path of
least resistance.

## The details

### Your first Vitest + RTL test, from scratch

Anywhere inside `frontend/src/`, create a tiny, throwaway component to
test — `Greeting.tsx`:

```tsx
// Greeting.tsx
export function Greeting({ name }: { name: string }) {
  return <p>Hello, {name}!</p>;
}
```

And its test, `Greeting.test.tsx`, in the same folder:

```tsx
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Greeting } from "./Greeting";

describe("Greeting", () => {
  it("renders the given name", () => {
    render(<Greeting name="Hero" />);
    expect(screen.getByText("Hello, Hero!")).toBeInTheDocument();
  });
});
```

Run it (from `frontend/`):
```bash
npx vitest run src/Greeting.test.tsx
```

**Expected output:**
```
 RUN  v4.1.10 .../frontend

 Test Files  1 passed (1)
      Tests  1 passed (1)
```

**Line by line, the three-step shape every test in this lesson follows:**
- **Render:** `render(<Greeting name="Hero" />)` — mounts the component
  into jsdom's fake DOM (Lesson 00), exactly as if a real browser had just
  loaded a page containing it.
- **Interact:** (none in this first, simplest example — Step 2 below
  adds a real one.)
- **Assert:** `screen.getByText("Hello, Hero!")` — `screen` is RTL's
  entry point for *finding* things in whatever was just rendered, the
  same way `document.querySelector` would in a real browser, but
  restricted to queries that match how a real user actually perceives a
  page (by visible text, here) rather than by internal implementation
  detail (a CSS class name, an internal React prop). `.toBeInTheDocument()`
  is one of the extra matchers `@testing-library/jest-dom` adds (Lesson
  00's setup) — it asserts the element `getByText` found is genuinely
  present in the rendered output.

**`describe`/`it`, explicitly, since this course doesn't enable Vitest's
`globals: true` option (Lesson 00):** `describe("Greeting", () => {...})`
groups related tests under one readable label in the output; `it(...)`
(a direct synonym for `test(...)` — both exist, purely for readability;
this module's own files consistently use `it`) declares one actual test,
taking a description string and the function to run.

Delete `Greeting.tsx`/`Greeting.test.tsx` once you've run this — they
were scratch files, not part of QuestLog itself.

### `getBy`, `queryBy`, and `findBy` — three families of query, three purposes

RTL's `screen` object has three families of query method, each answering
a subtly different question:

- **`getByX`** (e.g. `getByText`, `getByLabelText`, `getByRole`) — "find
  this element; if it doesn't exist, **throw an error immediately**."
  Use this whenever you *expect* the element to be there — a failed
  `getBy` query gives you an immediately useful error, right where the
  problem is.
- **`queryByX`** — "find this element; if it doesn't exist, return
  `null` instead of throwing." Use this specifically when you're
  asserting something is **absent** — `expect(screen.queryByText("Error"))
  .not.toBeInTheDocument()` — because `getByText` would itself throw
  before that assertion even ran, for exactly the case you're trying to
  confirm.
- **`findByX`** — like `getByX`, but returns a `Promise` that retries for
  a short time before giving up — needed whenever whatever you're
  looking for might not exist *yet* (e.g. right after a button click that
  triggers an async state update) but should appear soon. This module's
  own capstone tests don't need `findBy` (every state they check is
  already settled by the time they assert, since mocking — see below —
  removes real async delays entirely) but it's worth knowing exists for
  when you write tests against real, unmocked async behavior later.

This module's real `QuestListPage.test.tsx` uses both `getByText` (for
things it expects present) and `queryByText` (for things it expects
absent) — open that file now and find one example of each.

### `userEvent`: interacting the way a real user does

```tsx
import userEvent from "@testing-library/user-event";

const user = userEvent.setup();
await user.type(screen.getByLabelText("Title"), "Slay the Dragon");
await user.click(screen.getByRole("button", { name: "Add Quest" }));
```

**Line by line:** `userEvent.setup()` creates one interaction session for
a test — call it once, near the top of a test that needs to interact
with anything. `user.type(...)` simulates real keystrokes, one at a
time, into the given element — genuinely more realistic than just
setting a value directly, because it also fires every intermediate event
a real keyboard would (React's own controlled-input `onChange` handling,
Module 04, depends on exactly these events firing). `user.click(...)`
simulates a real mouse click, including everything a real browser would
do as a consequence — for a `type="submit"` button inside a `<form>`,
that includes the browser's own native form-submission behavior, which
is exactly what makes this module's real
`QuestForm.test.tsx::does_not_call_onSubmit_when_a_required_field_is_left_empty`
test work at all (covered fully below). Every method on `user` (`type`,
`click`, `selectOptions`, and others) returns a `Promise` — always
`await` it.

### `getByRole`: RTL's most-recommended query, and why

`screen.getByRole("button", { name: "Add Quest" })` finds an element by
its **accessibility role** (a browser/assistive-technology concept:
every interactive element has an implicit role — a `<button>` is role
`"button"`, an `<input type="checkbox">` is role `"checkbox"`) and its
**accessible name** (usually its visible text, or an associated
`<label>`). RTL's own documentation actively recommends `getByRole` over
more implementation-specific queries wherever possible, for two real
reasons: it matches what a sighted user *and* a screen-reader user would
both perceive (this course hasn't covered accessibility in depth, but
this is a genuine, free byproduct of testing this way), and it's the
query least likely to break from a purely cosmetic change (renaming a CSS
class doesn't change an element's role or accessible name at all).

### `vi.mock`: replacing an entire module, JavaScript's version of `patch`

Lesson 03 taught `unittest.mock.patch` for replacing one specific
attribute. Vitest's `vi.mock` replaces an **entire module's exports**, for
every test in a file, from the moment the file is loaded:

```tsx
import { vi } from "vitest";
import { useAuth } from "../context/AuthContext";

vi.mock("../context/AuthContext", () => ({
  useAuth: vi.fn(),
}));
```

This module's real `ProtectedRoute.test.tsx` opens with exactly this.
**Line by line:** the string `"../context/AuthContext"` names the module
to replace — the *exact* import path this test file itself uses to reach
it, mirroring Lesson 03's "patch where it's used" rule precisely. The
second argument is a function returning what the *fake* module should
export instead — here, an object with one key, `useAuth`, whose value is
`vi.fn()` — Vitest's name for a mock function (directly analogous to
`unittest.mock.Mock`). Because `ProtectedRoute.tsx` itself imports
`useAuth` from that same path, every place it calls `useAuth()` inside
this test file is now calling the mock instead of the real hook — which
is real, genuine `AuthContext.tsx` code from Module 07/08 never running
at all during this test, on purpose: this test's whole job is checking
`ProtectedRoute.tsx`'s own rendering logic, not `AuthContext.tsx`'s
session-restoring logic (which has no test of its own in this module —
see Exercise 05 for a chance to write exactly that one yourself).

Each test then configures what that specific call should return, using
Vitest's own mock-configuration method:

```tsx
vi.mocked(useAuth).mockReturnValue({
  user: null,
  loading: true,
  error: null,
  login: vi.fn(),
  signup: vi.fn(),
  logout: vi.fn(),
});
```

`vi.mocked(useAuth)` is purely a TypeScript-typing helper — at runtime
it's the exact same mock function; the wrapper just tells TypeScript "I
know this is actually a mock, so let me call mock-only methods like
`.mockReturnValue` on it without a type error." `.mockReturnValue(...)`
is Lesson 03's "tell the mock what to return" rule, in Vitest's own
syntax.

### Reading this module's real test files, together

**`QuestForm.test.tsx`** — the simplest starting point (as its own
opening comment says). Read
`does_not_call_onSubmit_when_a_required_field_is_left_empty` closely —
notice it mocks *nothing at all*. `QuestForm.tsx` has no hand-written
validation logic; every `<input>` just has a plain HTML `required`
attribute (Module 03). jsdom implements the same browser-native form
**constraint validation** a real browser does — clicking a submit button
inside a form with an unfilled `required` field never fires that form's
`submit` event, so `QuestForm`'s own `handleSubmit`, and therefore this
test's `handleSubmit` mock prop, is never called. This test genuinely
proves the browser is rejecting the submission, before any of this app's
own JavaScript runs — a real, if slightly hidden, piece of "testing
behavior, not implementation": there is no *implementation* to check
here at all, only the observable behavior.

**`ProtectedRoute.test.tsx`** — read all three tests
(`loading`/`no user`/`logged in`) and notice each one only changes what
the mocked `useAuth()` returns, then asserts on what's visible afterward
(a spinner, the login page's own text, or the protected content) — never
on `ProtectedRoute.tsx`'s internal `if` statements directly. This is
"behavior, not implementation" again: the test doesn't know or care
*how* `ProtectedRoute.tsx` decides what to render, only *what actually
renders* for each input.

**`QuestListPage.test.tsx`** — mocks `useQuests` (from
`QuestsContext.tsx`) the same way, covering Module 04's own
loading/error/success states (its own `lessons/07-data-fetching-loading-and-error-states.md`)
now checked by code instead of by eye. Its last test,
`shows_the_empty-filters_message_once_a_filter_excludes_every_quest`, is
the one real, multi-step interaction in this file: it renders with one
"high"-priority quest, confirms that quest is visible, uses `userEvent`
to select "Low" in the priority filter (a real interaction with
`QuestListPage.tsx`'s own local filter state — nothing mocked about
*that* part), and confirms the quest disappears and the "no matches"
message appears. Notice this test never reaches into `priorityFilter`
(the component's actual `useState` variable) directly — it only ever
observes the *effect* of changing it, through the real `<select>`
element, exactly RTL's philosophy.

**`QuestCard.test.tsx`** — the smallest, "presentational"-component
example (Module 04's term, reused in that file's own comment) — worth
reading last, as confirmation that the same three-step shape (render,
interact, assert) applies just as well to the simplest components as it
does to a whole page.

## Common mistakes & gotchas

- **`Unable to find an element with the text: ...`.** The single most
  common RTL failure. Before guessing, call `screen.debug()` (Lesson 04)
  immediately before the failing query — it prints the *actual* rendered
  DOM to your terminal, showing you exactly what text/structure really
  exists, almost always revealing the real mismatch immediately (a typo,
  text split across two separate DOM nodes by a `{variable}` interpolation,
  or the component simply not rendering what you expected at all).
- **Querying by CSS class name or a `data-testid` you invented purely for
  testing, when a `getByRole`/`getByText`/`getByLabelText` query would
  have worked.** This isn't a hard error, but it drifts away from RTL's
  whole philosophy — a class name a real user never sees is an
  implementation detail, and a test built on it can pass even when the
  actual user-visible behavior is broken (e.g. the right class is present
  but the element is invisible due to unrelated CSS).
- **Forgetting `await` before a `userEvent` method.** `user.click(...)`
  returns a `Promise` — omitting `await` means your assertion can run
  *before* the click (and any state update it triggers) has actually
  happened, producing a flaky, timing-dependent test that sometimes
  passes and sometimes doesn't for no visible reason.
- **A component that needs a React Router or Context provider ancestor,
  tested without one, crashing with an unrelated-looking error.**
  `ProtectedRoute` needs `useAuth()` to exist somewhere above it (either
  a real `AuthProvider`, or — as this module's tests do — a `vi.mock`
  replacing the whole hook); `QuestCard` needs a `<MemoryRouter>` ancestor
  purely because it renders a react-router `<Link>` internally, even
  though this module's own tests never actually navigate anywhere. If a
  component test throws immediately on `render(...)`, check what
  ancestors/providers the *real* app tree (`App.tsx`, `main.tsx`) gives
  that component that your test hasn't supplied.
- **Not calling `cleanup()` between tests, and seeing elements from a
  *previous* test's render still present.** This module's own
  `frontend/src/test-setup.ts` already handles this globally (an
  `afterEach(() => cleanup())`, since this project deliberately doesn't
  enable Vitest's `globals: true` — Lesson 00) — but if you ever copy a
  test file into a project without that setup file wired in
  (`vite.config.ts`'s `test.setupFiles`), this exact symptom is the
  first thing to check.

## How this connects

This lesson completes the "how do I actually test this specific kind of
code" arc Lessons 05–06 started for the backend. Lesson 08 (linters and
formatters) and Lesson 09 (pre-commit hooks) shift from "does the code
work" to "is the code written in a clean, consistent way" — a genuinely
different, complementary kind of quality check, covered next.

## Quick self-check

1. What is React Testing Library's central philosophy, stated in one sentence, and what specific kinds of query does it discourage as a result?
2. What's the real difference between `getByText`, `queryByText`, and `findByText`, and when would you reach for each one?
3. Why does `QuestForm.test.tsx`'s "required field" test need no mocking at all, and what is actually preventing `onSubmit` from being called in that test?
4. Explain, in your own words, what `vi.mock("../context/AuthContext", () => ({ useAuth: vi.fn() }))` does, and why `ProtectedRoute.test.tsx` uses it instead of rendering a real `<AuthProvider>`.
5. Why does `QuestCard.test.tsx` need a `<MemoryRouter>` wrapper even though none of its tests ever navigate anywhere?
