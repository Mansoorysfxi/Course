# Lesson 09 — Using AI in Your Own Dev Workflow

**Verified August 9, 2026, via live web research, cross-checking several
2026 sources on AI-assisted development practice:** by early 2026,
surveys reported roughly 95% of professional software engineers using AI
coding tools weekly, with about 75% applying them to at least half their
work, and one widely-cited estimate put AI-generated code at roughly 46%
of all code written. Current guidance converges on a specific, non-obvious
point: **AI-generated code should be reviewed exactly like code from a
competent but unfamiliar new team member** — plausible-looking, often
correct, but needing the same real scrutiny you'd give any code you
didn't write yourself, not less scrutiny just because it arrived fast and
fluent. Reported effective habits for tools like Claude Code specifically
include a lean, accurate project-context file (Claude Code's own
`CLAUDE.md`), planning before editing on non-trivial changes, and a real
verification loop (tests, not just a glance) before accepting output.

## What you'll learn

- Why prompting an AI coding assistant well is a real, distinct skill —
  not the same thing as writing a good comment or a good commit message.
- A concrete, practiced way to review AI-generated code critically,
  instead of either rubber-stamping it or distrusting it reflexively.
- What "skill atrophy" actually means in this context, and a genuine,
  practical way to guard against it — not just "don't use AI too much."

## Why this matters

This entire course was itself produced with heavy AI assistance — Claude
Code generated the lessons, exercises, and QuestLog's own capstone code
you've been reading and running throughout. That's not incidental to this
lesson; it's the reason this lesson exists at all. You are about to enter
a professional environment where using an AI coding assistant well is
already a baseline expectation, not a novelty — and "well" is a specific,
learnable skill, not something that happens automatically just because
you have access to the tool.

## Prerequisites

- **Every prior module's own capstone work** — you've been reading,
  running, and being asked to explain real, substantial AI-assisted code
  since Module 04. This lesson names, explicitly, the judgment you've
  already been implicitly practicing every time this course's own
  workflow (Rule 3, in `GRADING_PROTOCOL.md`) asked you to explain *why*
  a piece of code was correct, not just confirm that it ran.

## The concept, explained simply

Think about the difference between a junior programmer fresh out of
school and a senior one with five years of production experience, both
handed the exact same task. The junior one might produce code that
*compiles*, *runs*, and even *looks* professional — good naming, clean
formatting — while still containing a subtly wrong assumption about
concurrency, or an edge case nobody tested. The senior one's real edge
isn't typing faster; it's knowing *where a plausible-looking solution is
most likely to be wrong*, and checking exactly those places before
trusting it. Working with an AI coding assistant well means bringing that
same senior-level scrutiny to *every* piece of AI-generated code — not
because the AI is bad at coding (it's often very good), but because
"looks right" and "is right" are different properties, and an AI's own
fluency makes the gap between them easy to miss if you don't deliberately
check for it.

## The details

### Prompting well: give it the spec, not just the request

The single highest-leverage habit, confirmed across current guidance, is
**writing the specification before asking for the code** — the same
discipline as writing a clear GitHub issue before starting work yourself.
Compare:

```
Weak:  "Add a login feature."

Strong: "Add email/password login. Requirements: bcrypt for password
         hashing, JWT for the session token, 8-character minimum
         password length (no complexity rules -- see Module 07's own
         NIST-based reasoning), a 401 with no distinction between 'wrong
         password' and 'no such user', and a test covering both the
         happy path and the wrong-password path."
```

The second version isn't longer for its own sake — every extra sentence
removes one decision the assistant would otherwise have to guess at, and
every guess is a place the output can silently diverge from what you
actually needed. This is the exact same "context, not just a task" habit
this course's own Rule 2 has practiced on you since Module 00: an
assistant (human or AI) does better work the less it has to guess.

### Reviewing critically: a real checklist, not a vibe

"Review it critically" is easy advice to nod along to and hard to
actually practice without a concrete method. Use this course's own
`GRADING_PROTOCOL.md` (Rule 3) as a template — it's not a coincidence
that it fits AI-generated code just as well as a learner's own:

1. **What's actually correct, and why** — not "looks fine," but naming
   the specific decisions that are right and the reasons they're right.
2. **What's wrong, with an exact location** — a file, a line, a function
   — and *why* it's wrong: a bug, a security gap, a bad practice, not
   just "this feels off."
3. **What could be improved even if technically correct** — naming,
   structure, edge cases, performance.
4. **Comprehension questions you could answer yourself** — could you
   explain, to someone else, why this code works, not just that it does?
   If the honest answer is no, that's a real signal to slow down and
   actually read it before it goes into your codebase.

**The places most worth checking specifically**, per current guidance and
this course's own accumulated experience across fourteen modules of
AI-assisted feature work: **assumptions about state and side effects**
(does this code assume something is already true that a caller might not
guarantee?), **edge cases the happy path doesn't exercise** (empty input,
concurrent access, the "not found" branch), and **security-sensitive
boundaries** (auth checks, input validation, anything touching money or
destructive actions) — precisely the categories this course's own
Modules 07 and 08 already trained you to scrutinize by hand, now applied
to code an assistant produced instead of code you typed yourself.

### Avoiding skill atrophy: a genuine, practiced answer

"Don't let AI make you worse at your job" is true but useless without a
concrete practice. Two real, specific habits that actually work, not just
platitudes:

1. **Periodically write something yourself, all the way through, with no
   assistance, on a problem you already understand the shape of.** Not
   as a purity test — as a genuine diagnostic. If you *can't* still do it
   without help, that's real information about a skill quietly eroding,
   caught early enough to do something about it. If you can, you've
   confirmed the AI is accelerating work you're still capable of, not
   replacing understanding you no longer have.
2. **Never accept code you can't explain.** This is the single practice
   this entire course has modeled from Module 00 onward — every exercise
   review in this course's own workflow asks *why*, not just *does it
   work*. Carrying that same standard into a real job, applied to AI
   output specifically, is the actual, durable defense against atrophy:
   understanding doesn't erode from *using* a tool, it erodes from
   accepting outputs you stopped bothering to understand.

### A concrete workflow habit worth adopting: plan before you edit

For anything beyond a small, obviously-scoped change, ask an AI coding
assistant to describe its intended approach *before* it starts editing
files — Claude Code's own "plan mode" is one concrete example of this
built directly into a tool, but the underlying habit transfers to any
assistant: reviewing a two-paragraph plan takes far less time than
reviewing a full diff after the fact, and catching a wrong assumption at
the plan stage is dramatically cheaper than catching it after several
files have already changed.

## Common mistakes & gotchas

- **Accepting a large diff without reading all of it, because the parts
  you did read looked fine.** A subtly wrong assumption is just as likely
  to hide in the part you skimmed as the part you read carefully — there
  is no substitute for actually reading the whole thing on anything that
  matters.
- **Treating a vague prompt's bad output as the AI's failure, not the
  prompt's.** If the spec was ambiguous, the output reflecting that
  ambiguity is expected, not a sign the tool is unreliable — tighten the
  spec (per this lesson's own "prompting well" section) before concluding
  the tool can't do the job.
- **Never writing anything unassisted, ever, "because it's slower."**
  This is exactly the atrophy risk this lesson names — the short-term
  speed cost of occasionally working unassisted is precisely what buys
  you the long-term signal that you still can.
- **Assuming code that passes tests is automatically correct.** Tests
  only check what they were written to check — an AI assistant (or a
  human) can write code and tests together that both pass while sharing
  the same wrong assumption. This is exactly why Module 08's own testing
  lessons emphasized testing the *right* things, not just having
  *some* tests pass.

## How this connects

This lesson is the odd one out in this module — the only one about AI
you use rather than AI you build — and it's here specifically because
this course's final capstone (Lessons 10–11) is real, substantial
production code, and you're about to be evaluated (Rule 3, this course's
own grading protocol) on your ability to explain and defend it, the exact
skill this lesson just named directly. Every review this course has ever
given you, going back to Module 00, has been practicing exactly the
critical-review habit this lesson makes explicit.

## Quick self-check

1. Why does this lesson claim "review AI-generated code like it came from
   a competent but unfamiliar new team member," rather than either
   trusting it fully or distrusting it by default?
2. Give a concrete example (not from this lesson) of a weak prompt and a
   strong version of the same request, and explain what specifically the
   strong version removes that the weak one left ambiguous.
3. Name the four review steps this lesson borrows from this course's own
   `GRADING_PROTOCOL.md`, and explain why "could you explain this to
   someone else" is a real test, not a rhetorical one.
4. What are the two concrete, practiced habits this lesson gives for
   avoiding skill atrophy — not vague advice, the two specific things you
   could actually start doing this week?
5. Why is "it passed the tests" not sufficient evidence that AI-generated
   code is correct?
