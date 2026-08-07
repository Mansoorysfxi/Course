# Reference Solution — Your First Requests With curl

Don't read this until you've made a genuine attempt. Your exact IP
address, byte counts, and TLS session details may differ slightly from
what's shown here (servers can answer from different data centers, and
`Content-Length` will differ if PokeAPI's data changes) — that's expected
and fine. What matters is that you found the *same kind* of information in
the *same places* in your own output.

## Step 1 — `curl -v https://pokeapi.co/api/v2/pokemon/ditto -o /dev/null`

Resolved IP address (from the `Trying`/`Connected to` lines):

```
* Connected to pokeapi.co (104.26.14.6) port 443
```

Negotiated TLS version (from the TLS handshake lines):

```
* SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256
```

Request line sent (a `>` line):

```
> GET /api/v2/pokemon/ditto HTTP/2
```

Status line received (a `<` line):

```
< HTTP/2 200
```

## Step 2 — `curl -i ... -o response-body.json -D headers.txt`

`headers.txt` contents (abridged):

```
HTTP/2 200
content-type: application/json; charset=utf-8
content-length: 16482
cache-control: public, max-age=86400
date: Wed, 12 Aug 2026 10:03:11 GMT
server: cloudflare
```

## Step 3 — Comparing `Content-Length` to the actual file size

```bash
ls -la response-body.json
```

```
-rw-r--r-- 1 you you 16482 Aug 12 10:03 response-body.json
```

**16482** from `ls -la` matches **16482** from `content-length:` exactly.
This is expected: `Content-Length` is the server telling the client, in
advance, precisely how many bytes of body to expect — a `curl`-saved file
should match it byte for byte, since nothing is added or stripped on the
way to disk. (If yours is off by a small amount, the most likely cause is
that PokeAPI's underlying data for that Pokémon simply changed slightly
between when this reference was written and when you ran it — not a bug
in your command.)

## Step 4 — `curl -i -X HEAD ...`

```
HTTP/2 200
content-type: application/json; charset=utf-8
content-length: 16482
...
(nothing after the headers — no JSON body at all)
```

**Why no body appeared:** `HEAD` is explicitly defined (Lesson 03) to be
identical to `GET` in every way *except* that the server must not send a
body — you get the exact same headers (including `content-length`, which
still correctly reports what a matching `GET` *would* have returned), but
the body itself is deliberately withheld. This is useful for cheaply
checking "does this exist, and how big is it" without paying the cost of
downloading the full response.

## Step 5 — three more Pokémon

```bash
curl -s https://pokeapi.co/api/v2/pokemon/charizard | head -c 200
```
```
{"abilities":[{"ability":{"name":"blaze","url":"https://pokeapi.co/api/v2/ability/66/"}...
```

```bash
curl -s https://pokeapi.co/api/v2/pokemon/snorlax | head -c 200
```
```
{"abilities":[{"ability":{"name":"immunity","url":"https://pokeapi.co/api/v2/ability/17/"}...
```

```bash
curl -s https://pokeapi.co/api/v2/pokemon/gengar | head -c 200
```
```
{"abilities":[{"ability":{"name":"cursed-body","url":"https://pokeapi.co/api/v2/ability/130/"}...
```

All three returned real JSON starting with `{"abilities":...` and no
`404` — confirming all three names are valid, real resources on this API.

## Self-grading notes

- If your TLS line shows `TLSv1.2` instead of `TLSv1.3`, that's not
  automatically wrong — it can happen on an older `curl`/OpenSSL build
  that doesn't offer 1.3, and the server will negotiate down. Note it, but
  it doesn't fail this exercise; the exercise is about *finding* the line
  and reading it correctly, not about forcing a specific version.
- The exact `content-length` number will differ from this reference the
  moment PokeAPI's underlying data for a given Pokémon changes — don't
  worry if your number differs from this file's, only that your *own*
  `ls -la` number matched your *own* `headers.txt` number.
- If step 4 showed no `content-length` header at all (rare, some servers
  omit it on `HEAD`), that's worth flagging as a genuine observation in
  your own notes — real APIs vary here, and noticing the variation is
  exactly the kind of careful reading this exercise is grading for.
