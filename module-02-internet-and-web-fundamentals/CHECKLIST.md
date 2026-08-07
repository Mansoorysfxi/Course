# Module 02 — Checklist

Complete this after finishing all three exercises and the capstone
project, and after your module-end review ("Check my module"). Don't
start Module 03 until every box below is checked and any remedial
exercises from your review are done.

## Self-assessment

Answer these honestly, in your own words (writing them down — e.g. in
your Module 00 `course-companion` repo's notes — is more valuable than
answering silently in your head):

- [ ] I can explain, step by step and in the correct order, everything
  that happens between typing a URL and pressing Enter and seeing a
  response — DNS, TCP, TLS, the HTTP request, the HTTP response.
- [ ] I can explain the difference between "the Internet" and "the Web"
  without hesitating.
- [ ] I can explain the difference between a public and a private IP
  address, and why a private one only works inside its own local network.
- [ ] I can name at least five HTTP methods and correctly state, for each,
  whether it's safe and/or idempotent — and explain why those two
  properties matter in practice, not just recite the definitions.
- [ ] I can correctly categorize a status code by its first digit alone
  (1xx–5xx) and explain what each category means, including the
  structural difference between "the client's fault" (4xx) and "the
  server's fault" (5xx).
- [ ] I can explain what a header is, name at least five real headers
  I've personally seen in `curl` output, and say what each one does.
- [ ] I can explain, precisely, what "HTTP is stateless" means, why it was
  designed that way, and how cookies work around it — including which two
  headers are involved and which direction each one travels.
- [ ] I can explain the difference between a client and a server as
  *roles*, and give an example (from this course or otherwise) of a
  program that plays both roles in different interactions.
- [ ] I can write a syntactically correct JSON object from memory,
  including at least one nested array, with no single quotes and no
  trailing commas.
- [ ] I can name all five required REST constraints (plus the one
  optional one) and, for a real API I've actually explored (PokeAPI),
  state specifically which ones it satisfies and which it only partially
  satisfies.
- [ ] All three exercises were reviewed and scored 7/10 or higher (or
  revised until they were).
- [ ] The capstone (API Exploration Report) is complete and was reviewed.

## Spaced-repetition review questions from earlier modules

These five questions are pulled from Modules 00 and 01's actual content —
answer them from memory before checking the relevant lesson if you get
stuck. If any of these feel shaky, that's a real signal to briefly
revisit the relevant lesson before moving on to Module 03, not just to
review this module's own material.

1. What's the difference between Git and GitHub, in your own words?
   *(Module 00, Lesson 00)*
2. What does `PATH` actually do, and what's the first thing you should
   try when a freshly-installed command gives `command not found`?
   *(Module 00, Lesson 01)*
3. Why is `def f(items=[]):` dangerous in Python, and what's the correct
   fix? *(Module 01, Lesson 02)*
4. When would you reach for a Python `set` instead of a `list`, and what
   time-complexity reasoning justifies that choice? *(Module 01, Lesson 03)*
5. Using the game-loop analogy, why doesn't `async`/`await` make
   CPU-bound code run faster, only I/O-bound waiting more efficient?
   *(Module 01, Lesson 11)*

## Before you move on to Module 03

- [ ] You've said "check my module" and received a full module-end review.
- [ ] [PROGRESS.md](../PROGRESS.md) has been updated by the AI with your
  Module 02 report.
- [ ] Any remedial exercises the review generated (if any) are complete.
- [ ] You've read the Module 03 README to see what's coming next.
