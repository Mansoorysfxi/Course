# Module 05 — Checklist

Complete this after finishing all five exercises and the capstone project,
and after your module-end review ("Check my module"). Don't start Module 06
until every box below is checked and any remedial exercises from your
review are done.

## Self-assessment

Answer these honestly, in your own words (writing them down is more
valuable than answering silently in your head):

- [ ] I can explain what job a web framework (FastAPI) does versus what job
  an ASGI server (Uvicorn) does, and why an app needs both.
- [ ] I can explain, using Module 01's own decorator mechanism, exactly what
  `@app.get("/")` does to the function directly below it — no unexplained
  magic.
- [ ] I can state the precise rule FastAPI uses to decide whether a
  function parameter is a path parameter, a query parameter, or a request
  body.
- [ ] I can read a `422` validation error response fluently — explaining
  what `type`, `loc`, `msg`, and `input` each mean, from memory.
- [ ] I can explain, precisely, what "validation" means in this module's
  sense, and what happens, step by step, when a request fails it (including
  the fact that the route function's body never runs).
- [ ] I can explain `Literal[...]` and when to use it instead of a plain
  `str`, and I can write a `@field_validator` from scratch, including why
  it needs `@classmethod` and a `return`.
- [ ] I can explain dependency injection as a general idea (no FastAPI
  syntax), then explain exactly what `Depends()` does mechanically, step by
  step, for a request that fails a dependency's own check.
- [ ] I can explain FastAPI's sub-dependency resolution and its per-request
  caching behavior, including when I'd deliberately disable that caching.
- [ ] I can explain, using the tick-chain analogy, the precise difference
  between middleware and a dependency — which is unconditional, and which
  is opted into.
- [ ] I can write custom middleware using `call_next`, and explain what
  breaks if `return response` is omitted.
- [ ] I can choose correctly between `HTTPException` and a custom exception
  + `@app.exception_handler(...)`, and explain the tradeoff.
- [ ] I can explain what `response_model` actually does to a route's return
  value, including hiding an internal-only field.
- [ ] I can explain OpenAPI as a specification (not a page), name two
  separate tools that render it differently, and explain where FastAPI's
  generated documentation actually comes from.
- [ ] I can map CRUD's four operations onto the correct HTTP method for
  each, and explain specifically why this module's update endpoint uses
  `PATCH` rather than `PUT`.
- [ ] I can explain, honestly, this capstone's "database" and its real
  limitation, and name the module that removes it.
- [ ] All five exercises were reviewed and scored 7/10 or higher (or
  revised until they were).
- [ ] The capstone (the QuestLog API, plus the updated frontend) runs, and
  was reviewed.

## Spaced-repetition review questions from earlier modules

These five questions are pulled from Modules 00–04's actual content —
answer them from memory before checking the relevant lesson if you get
stuck. If any of these feel shaky, that's a real signal to briefly revisit
the relevant lesson before moving on to Module 06, not just to review this
module's own material.

1. What's the difference between a merge conflict and a fast-forward
   merge, and which one actually requires you to manually edit a file
   containing conflict markers? *(Module 00, Lessons 03–04)*
2. What two facts about Python make decorators possible at all, and what
   is `@my_decorator` above a function definition literally shorthand for?
   *(Module 01, Lesson 10 — this module's Lesson 01 leaned on this exact
   answer directly for `@app.get(...)`.)*
3. What's the difference between a "safe" HTTP method and an "idempotent"
   one, and name one method that's idempotent but not safe. *(Module 02,
   Lesson 03 — this module's Lesson 06 assumed you still had this solid.)*
4. Why does a JavaScript `fetch()` call's Promise fulfill even for a
   404/500 response, and what specific check catches this? *(Module 03,
   Lesson 07 — this module's `project/questlog/frontend/src/api/questsApi.ts`
   relies on exactly this fact, via `response.ok`.)*
5. What specific problem does React's Context API solve, and what's the
   real reason `createContext<T | undefined>(undefined)` plus a
   custom-hook wrapper is better than a fake default value? *(Module 04,
   Lesson 06 — `QuestsContext.tsx`, unchanged in this module except for its
   mutation functions becoming `async`, still uses exactly this pattern.)*

## Before you move on to Module 06

- [ ] You've said "check my module" and received a full module-end review.
- [ ] [PROGRESS.md](../PROGRESS.md) has been updated by the AI with your
  Module 05 report.
- [ ] Any remedial exercises the review generated (if any) are complete.
- [ ] You've read the Module 06 README to see what's coming next — trading
  this module's in-memory `dict` for a real PostgreSQL database.
