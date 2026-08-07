# Module 04 — Checklist

Complete this after finishing all five exercises and the capstone project,
and after your module-end review ("Check my module"). Don't start Module 05
until every box below is checked and any remedial exercises from your
review are done.

## Self-assessment

Answer these honestly, in your own words (writing them down is more
valuable than answering silently in your head):

- [ ] I can explain, using the Module 03 DOM-manipulation exercise as a
  concrete example, the specific bookkeeping burden that grows as a
  hand-written vanilla-JS app adds more interactive pieces — and what
  React does differently to remove it.
- [ ] I can explain what a component actually is (a function returning a
  description of UI), why props are read-only from the receiving
  component's side, and what JSX actually compiles to (it is not HTML).
- [ ] I can explain React's rendering model precisely: what a "render"
  actually is, at least two specific things that trigger one, what the
  Virtual DOM is, and what reconciliation does with it.
- [ ] I can state, from memory, all three forms of `useEffect`'s
  dependency array (no array, `[]`, `[a, b]`) and exactly when each runs.
- [ ] I can explain a stale closure concretely — what "stale" means here,
  and why a missing dependency causes it — using the word "closure"
  correctly (Module 01, Lesson 02's definition).
- [ ] I can explain the specific "new object/array literal every render"
  trap that causes `useEffect` infinite loops, and how to fix it.
- [ ] I can explain what a cleanup function actually does (the two
  specific moments React calls it) and why the `cancelled`-flag pattern
  prevents a stale async response from overwriting fresher state.
- [ ] I can write a custom hook, following the Rules of Hooks, and explain
  why those rules exist (how React tracks hook state by call order).
- [ ] I can explain what "controlled" means for a form input, and can
  build a multi-field controlled form from scratch.
- [ ] I can explain "lifting state up" with a concrete before/after
  example, and know when that pattern stops being practical.
- [ ] I can explain prop drilling concretely, and build the real
  `createContext<T | undefined>(undefined)` + custom-hook-wrapper pattern
  from memory — including *why* it's better than a fake default value.
- [ ] I can state one honest, concrete reason NOT to put a given piece of
  state into Context, even though it would technically work.
- [ ] I can build a `{ data, loading, error, refetch }`-shaped custom hook
  around a mocked async function, with correct cleanup, without copying
  an example directly.
- [ ] I can build a multi-page React Router app with nested routes, a
  dynamic segment read with `useParams()`, an index route, and a
  catch-all route — and explain why `<Link>` doesn't reload the page.
- [ ] I can explain, in my own words, the difference between SSR, SSG,
  CSR, and ISR, and correctly assign the right one to at least three
  different realistic example pages.
- [ ] I can explain why QuestLog is deliberately 100% CSR right now, and
  what would have to be true for that decision to change.
- [ ] I can translate at least five real Tailwind utility classes into
  the literal CSS properties/values they produce, without looking them up.
- [ ] All five exercises were reviewed and scored 7/10 or higher (or
  revised until they were).
- [ ] The capstone (QuestLog web) runs, correctly shows loading/error/
  success states, and was reviewed.

## Spaced-repetition review questions from earlier modules

These five questions are pulled from Modules 00–03's actual content —
answer them from memory before checking the relevant lesson if you get
stuck. If any of these feel shaky, that's a real signal to briefly revisit
the relevant lesson before moving on to Module 05, not just to review this
module's own material.

1. What's the difference between `git fetch` and `git pull`, and which
   one actually merges changes into your current branch?
   *(Module 00, Lesson 05)*
2. Why is `def add_quest(quests=[]):` a dangerous Python function
   signature, and what's the correct fix? *(Module 01, Lesson 02 — this
   exact "shared mutable default" family of bug is conceptually close to
   why this module's Lesson 02 insists on producing a *new* array/object
   rather than mutating an old one when updating React state.)*
3. What does "HTTP is stateless" mean, and name one real mechanism
   applications use to work around it. *(Module 02, Lesson 04)*
4. Why does `fetch`'s Promise fulfill even for a 404/500 response, and
   what specific check fixes the resulting bug? *(Module 03, Lesson 07 —
   you relied on this exact fact again in this module's data-fetching
   lesson, just inside a `useEffect` instead of a plain `async function`.)*
5. What's the difference between the CSS box model's `content-box` and
   `border-box`, and which one does this course's CSS reset use?
   *(Module 03, Lesson 02 — worth having solid before Module 04, Lesson 10
   asked you to translate Tailwind classes back into exactly this kind of
   real CSS property.)*

## Before you move on to Module 05

- [ ] You've said "check my module" and received a full module-end review.
- [ ] [PROGRESS.md](../PROGRESS.md) has been updated by the AI with your
  Module 04 report.
- [ ] Any remedial exercises the review generated (if any) are complete.
- [ ] You've read the Module 05 README to see what's coming next — a real
  FastAPI backend, replacing QuestLog's mocked `fetchQuests()` with a real
  HTTP API call.
