# Exercise 02 — Status Codes, Redirects, and Cookies (Guided)

**Difficulty:** Guided — more independent than Exercise 01. You're given
*what* to trigger and *what to record*, but not the exact command for
every single step; you'll need to combine flags yourself from what
Lessons 03–04 taught.

**Concepts this exercise uses** (all taught in the lessons named):
status code categories and specific codes 200/301/302/404/500
([Lesson 03](../../lessons/03-http-methods-and-status-codes.md)),
redirects
([Lesson 03](../../lessons/03-http-methods-and-status-codes.md)),
the `Location` header, `Set-Cookie`/`Cookie`, statelessness
([Lesson 04](../../lessons/04-headers-cookies-and-statelessness.md)), and
`curl`'s `-c`/`-b` cookie-jar flags plus `-L` (follow redirects, taught in
[Lesson 03](../../lessons/03-http-methods-and-status-codes.md)'s redirect
example).

## What to build

You'll use **httpbingo.org** — a small, free, public HTTP-testing service
this module has used throughout (see
[Lesson 03](../../lessons/03-http-methods-and-status-codes.md)) built
specifically for deliberately triggering exact status codes, redirects,
and cookie behavior — plus PokeAPI for one real-world 404.

Create a folder for this exercise's work:

```bash
mkdir -p ~/web-fundamentals-practice/exercise-02
cd ~/web-fundamentals-practice/exercise-02
```

Complete each task. For each one, you must show the **exact command you
ran** and the **relevant part of its output**.

1. **Trigger a `404` from a real-world API**, not the demo one: request a
   Pokémon name that does not exist from PokeAPI, and confirm you get
   `404 Not Found`.
2. **Trigger a `500`** using httpbingo.org's status-code endpoint (check
   Lesson 03 for the exact path pattern). Confirm the status line.
3. **Trigger a redirect** using httpbingo.org's redirect endpoint, but do
   it **twice**: once *without* `-L`, and once *with* `-L`. For the
   version without `-L`, identify the status code you got back (should be
   in the 3xx range) and find the `Location` header telling `curl` where
   it *would* go next. For the version with `-L`, confirm `curl` followed
   the redirect(s) all the way through and tell you the final status code.
4. **Set and then read back a cookie**, exactly like Lesson 04 demonstrated,
   but use a *different* cookie name/value than the lesson's example (pick
   your own quest-themed key/value). Show both the `Set-Cookie` header
   from setting it, and the `Cookie` header (or the echoed value in the
   response body) proving it came back on your second request.
5. **Prove statelessness directly**: make a plain `GET` request to
   `https://httpbingo.org/cookies` **without** using your cookie jar file
   at all (no `-b`). Confirm the response shows no cookies were received —
   in your own words, explain *why* this confirms HTTP's statelessness
   rather than just being "empty because you didn't ask for any."

## Acceptance criteria

- [ ] `solution/OBSERVATIONS.md` shows the exact command and output for
  all five tasks.
- [ ] Task 1's status is genuinely `404`, from a genuinely nonexistent
  Pokémon name (not a typo of a real one that happened to fail for a
  different reason).
- [ ] Task 3 clearly shows two different results for the same underlying
  URL depending only on whether `-L` was used — and correctly names the
  header that told `curl` where to go.
- [ ] Task 4's cookie round-trip uses a name/value you chose yourself, not
  copy-pasted from Lesson 04.
- [ ] Task 5's explanation correctly connects the empty result back to
  Lesson 04's definition of statelessness — not just "because I didn't
  send `-b`," but *why* that absence is the point.

## What to submit

Create `solution/OBSERVATIONS.md` inside this exercise's own folder with
all five tasks' commands, output, and explanations. Point your AI session
at it when asking for review.

## Hints

- **Level 1 (start here):** Re-read Lesson 03's status code table for the
  exact endpoint pattern httpbingo.org uses for arbitrary status codes,
  and its redirect endpoint's path pattern.
- **Level 2:** For task 3, `curl -i` alone (no `-L`) shows you the
  redirect response itself, headers included — that's where `Location`
  lives. Adding `-L` changes `curl`'s *behavior*, not what a bare request
  would have returned.
- **Level 3:** For task 5, think back to the vending-machine analogy in
  Lesson 04 — a vending machine doesn't fail to recognize you because it's
  "broken," it was *never designed* to remember individuals between
  transactions in the first place. What's the HTTP equivalent statement?
- If you've worked through all three hint levels and are still stuck, ask
  your AI session directly — per
  [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md).
