# Exercise 03 — Full Request/Response Cycle Walkthrough (Independent)

**Difficulty:** Independent — this is a dry run for the module capstone,
scoped to a single endpoint. You get a required outline of sections, not
step-by-step commands. You should be pulling together everything from
every lesson in this module on your own.

**Concepts this exercise uses** (all taught across this module's lessons):
DNS resolution
([Lesson 01](../../lessons/01-networks-ip-addresses-and-dns.md)), the TCP
three-way handshake and TLS handshake
([Lesson 02](../../lessons/02-tcp-tls-and-the-request-response-journey.md)),
the request line, method, and status line/code
([Lesson 03](../../lessons/03-http-methods-and-status-codes.md)), request
and response headers plus statelessness
([Lesson 04](../../lessons/04-headers-cookies-and-statelessness.md)),
client/server roles, URL anatomy, and JSON structure
([Lesson 05](../../lessons/05-clients-servers-apis-and-json.md)), and
REST's constraints
([Lesson 06](../../lessons/06-rest-from-first-principles.md)).

## What to build

Choose **one** endpoint from PokeAPI that you have not already used in
Exercises 01–02 (pick any resource type — `/type/{name}`,
`/generation/{name}`, `/move/{name}`, `/berry/{name}`, etc. — see
`https://pokeapi.co/docs/v2` for the full list, or just try a plausible
URL and confirm it returns `200`). Write a complete, first-principles
walkthrough document of everything that happens when that one request is
made — from typing the URL to the response being fully received. This is
not a summary or a copy of the lessons — it must be about *your specific
chosen endpoint*, with real output from real commands you actually ran.

Your document, `solution/WALKTHROUGH.md`, must contain these sections, in
this order:

1. **The endpoint** — the exact URL, and one sentence on what resource it
   represents.
2. **DNS** — run the appropriate lookup command; state the resolved IP
   address; briefly explain, in your own words, what your computer just
   did to get that answer (you don't need to re-derive every root/TLD/
   authoritative-server step — a correct, compressed explanation is fine,
   as long as it's accurate).
3. **TCP + TLS** — run `curl -v` against your endpoint; quote the specific
   lines proving the TCP connection was established and which TLS version
   was negotiated.
4. **The request** — quote the exact request line and every request
   header `curl` sent; state which HTTP method was used and whether it's
   safe/idempotent, and why.
5. **The response** — quote the exact status line and every response
   header received; state the status code's category and specific
   meaning; state the `Content-Type` and explain what it tells the
   client to do with the body.
6. **The body** — show a real (possibly truncated, if very long) excerpt
   of the actual JSON body; identify at least one object, one array, one
   string, one number, and (if present) one boolean or null value inside
   it, quoting the actual JSON fragment for each.
7. **REST check** — go through client-server separation, statelessness,
   and cacheability specifically for *this* request/response (not a
   generic restatement of the lesson), citing the specific evidence (a
   specific header, a specific observed behavior) for each.

## Acceptance criteria

- [ ] The chosen endpoint is genuinely different from anything used in
  Exercises 01–02.
- [ ] Every section above is present, in order, and grounded in real,
  actually-run command output — not paraphrased or invented.
- [ ] Section 4 correctly states whether the method used is safe and/or
  idempotent, with a correct reason (not just a restated definition).
- [ ] Section 6 correctly identifies all five required JSON element types
  (object, array, string, number, boolean-or-null) with the actual
  fragment for each, not a generic description.
- [ ] Section 7 cites specific, real evidence (an actual header value, an
  actual repeated-request result) for each of the three constraints
  checked — generic restatement of the lesson without evidence does not
  meet this bar.

## What to submit

`solution/WALKTHROUGH.md`, complete, inside this exercise's own folder.
Point your AI session at it for review.

## Hints

This exercise is intentionally less scaffolded than Exercises 01–02. If
you're stuck for more than 30 minutes on any one section:

- Re-read the specific lesson listed next to that section above — every
  section maps to exactly one lesson's content.
- If you can't decide which endpoint to pick, that's fine — any valid,
  real PokeAPI resource endpoint works equally well for this exercise;
  the choice itself isn't graded, only the completeness of your
  walkthrough of whichever one you pick.
- If you've re-read the mapped lesson and are still stuck, ask your AI
  session for a hint per
  [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md) — but try to get
  further on your own here than in Exercises 01–02 before asking; that's
  the point of this exercise being independent.
