# Reference Solution — Status Codes, Redirects, and Cookies

Don't read this until you've made a genuine attempt. There's more than one
valid way to phrase the explanations — this shows *a* correct solution,
not *the only* correct wording.

## Task 1 — Real-world 404

```bash
curl -i https://pokeapi.co/api/v2/pokemon/not-a-real-pokemon-abc123
```
```
HTTP/2 404
content-type: application/json; charset=utf-8
...
{"detail":"Not found."}
```

A genuinely nonexistent name correctly returns `404 Not Found` — the
server understood the request perfectly; there's simply nothing at that
path, per Lesson 03's definition of the 4xx category ("you asked for
something that isn't there").

## Task 2 — Deliberate 500

```bash
curl -i https://httpbingo.org/status/500
```
```
HTTP/1.1 500 Internal Server Error
```

## Task 3 — Redirect, with and without `-L`

**Without `-L`:**

```bash
curl -i https://httpbingo.org/redirect/2
```
```
HTTP/1.1 302 Found
location: /relative-redirect/1
...
(no further body — curl stopped here, it did not follow the redirect itself)
```

Status code: `302` (temporary redirect, per Lesson 03). The `location`
header is exactly what tells a client (or a browser) where to go next —
`curl`, without `-L`, shows you this instruction but deliberately does not
act on it.

**With `-L`:**

```bash
curl -i -L https://httpbingo.org/redirect/2
```
```
HTTP/1.1 302 Found
location: /relative-redirect/1

HTTP/1.1 302 Found
location: /relative-redirect/0

HTTP/1.1 200 OK
content-type: application/json; charset=utf-8

{"args":{},"headers":{...},...}
```

With `-L`, `curl` follows each `Location` header itself, automatically
re-requesting each new URL, until it reaches a final non-redirect
response (`200 OK` here) — you can see all three "hops" if you scroll the
`-i` output, ending at the same `/get`-style JSON echo endpoint used
elsewhere in this module.

## Task 4 — Custom cookie round-trip

```bash
curl -i -c jar.txt "https://httpbingo.org/cookies/set?character-class=rogue"
```
```
HTTP/1.1 302 Found
set-cookie: character-class=rogue; Path=/
location: /cookies
```

(Note: httpbingo.org's `/cookies/set` sets the cookie *and* redirects to
`/cookies` to show it back to you in one step — following that redirect
with `-L` shows the confirmation directly, or you can check the jar file
in a second request as shown next.)

```bash
curl -i -b jar.txt https://httpbingo.org/cookies
```
```
HTTP/1.1 200 OK
content-type: application/json; charset=utf-8

{"cookies":{"character-class":["rogue"]}}
```

The second, completely separate request correctly received back
`character-class: rogue` — proving the cookie set in the first request
was successfully stored (in `jar.txt`, standing in for what a browser
would store in its own cookie storage) and resent automatically.

## Task 5 — Proving statelessness

```bash
curl -s https://httpbingo.org/cookies
```
```
{"cookies":{}}
```

No `-b` flag was used, so no `Cookie` header was sent at all this time —
and the server's answer is an empty `{"cookies":{}}`, not "welcome back"
or any memory of the cookie set in Task 4.

**Why this proves statelessness, not just "no cookie was asked for":** the
server didn't forget who I was — it never *knew* who I was in the first
place, and structurally *cannot* know, because nothing about a bare HTTP
request carries any identity or history unless the client explicitly
attaches it (Lesson 04). The cookie from Task 4 still technically "exists"
from the *server's* perspective (httpbingo.org isn't storing anything
server-side about me at all here — it's simply echoing back whatever
`Cookie` header it's handed on each individual request). Removing the
`-b` flag removed the only thing carrying any continuity between my two
requests, which is exactly Lesson 04's point: the *protocol* has no memory
of its own; any continuity a client experiences is because the client
itself chose to resend something, not because the server remembered
anything.

## Self-grading notes

- Task 3's exact number of redirect hops and their intermediate paths
  (`/relative-redirect/1`, `/relative-redirect/0`) may render slightly
  differently depending on httpbingo.org's current implementation — what
  matters is that you correctly identified a 3xx status, a `location`
  header, and the behavioral difference `-L` made, not the exact
  intermediate path names.
- If your Task 4 `Set-Cookie` line looks different (e.g., no automatic
  redirect), that's fine — some `curl`/environment combinations behave
  slightly differently around httpbingo.org's redirect-on-set design; as
  long as your second, separate request correctly showed the cookie
  coming back, the concept is demonstrated.
