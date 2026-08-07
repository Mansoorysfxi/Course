# Reference Solution — Full Request/Response Cycle Walkthrough

**Endpoint chosen:** `https://pokeapi.co/api/v2/type/electric` — a `type`
resource (a Pokémon elemental type), genuinely different from every
endpoint used in Exercises 01 (`/pokemon/{name}`) and 02 (httpbingo.org).

Don't read this until you've made a genuine attempt with your own,
different endpoint. This shows *a* correct approach and depth, not a
template to copy the specific content of.

## 1. The endpoint

`https://pokeapi.co/api/v2/type/electric` — represents the "Electric"
Pokémon type: which other types it's strong/weak against, and which
Pokémon and moves belong to it.

## 2. DNS

```bash
nslookup pokeapi.co
```
```
Non-authoritative answer:
Name:    pokeapi.co
Address:  104.26.14.6
```

My computer had no cached answer for `pokeapi.co`, so it asked my
configured resolver, which (per Lesson 01) walked the root → `.co` TLD →
`pokeapi.co`'s authoritative server chain until it got a real answer:
`104.26.14.6`. That answer is now cached locally for a while, which is why
running this same command again immediately would very likely be
instant.

## 3. TCP + TLS

```bash
curl -v https://pokeapi.co/api/v2/type/electric -o /dev/null
```

TCP established:
```
*   Trying 104.26.14.6:443...
* Connected to pokeapi.co (104.26.14.6) port 443
```

TLS negotiated:
```
* SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256
```

The connection completed a three-way handshake (SYN, SYN-ACK, ACK) to
`104.26.14.6` on port `443` (the default HTTPS port), then immediately
negotiated a TLS 1.3 session before any HTTP data was sent — exactly the
order Lesson 02 walked through.

## 4. The request

```
> GET /api/v2/type/electric HTTP/2
> Host: pokeapi.co
> User-Agent: curl/8.16.0
> Accept: */*
```

**Method:** `GET`. **Safe:** yes — this request only reads data about the
Electric type; it doesn't create, modify, or delete anything on the
server, satisfying Lesson 03's definition of a safe method exactly.
**Idempotent:** yes — running this exact request a hundred times in a row
returns the same Electric-type data each time (barring PokeAPI's own data
changing between calls, which is an external fact, not an effect of my
requests), so repetition doesn't accumulate or change anything.

## 5. The response

```
< HTTP/2 200
< content-type: application/json; charset=utf-8
< cache-control: public, max-age=86400
< date: Wed, 12 Aug 2026 10:41:07 GMT
< server: cloudflare
```

**Status:** `200`, category **2xx (Success)** — the request was received,
understood, and fulfilled with no error. **`Content-Type`:**
`application/json; charset=utf-8` — this tells the client (in this case,
`curl`) to interpret the body strictly as JSON text encoded in UTF-8,
rather than guessing the format from the bytes themselves.

## 6. The body

```json
{"damage_relations":{"double_damage_from":[{"name":"ground","url":"https://pokeapi.co/api/v2/type/5/"}],"double_damage_to":[{"name":"flying","url":"https://pokeapi.co/api/v2/type/3/"},{"name":"electric","url":"https://pokeapi.co/api/v2/type/13/"}],...},"id":13,"name":"electric","pokemon":[{"pokemon":{"name":"pikachu","url":"https://pokeapi.co/api/v2/pokemon/25/"},"slot":1},...]}
```

- **Object:** the entire response is one outer object (`{ ... }`); also
  `"damage_relations": { ... }` is itself a nested object.
- **Array:** `"double_damage_from": [{"name":"ground", ...}]` — a list of
  type-relation entries.
- **String:** `"name": "electric"` — the value `"electric"` is a JSON
  string.
- **Number:** `"id": 13` — the value `13` is a JSON number, unquoted.
- **Boolean/null:** not present at the top level of this particular
  resource — Electric-type data happens to only need objects, arrays,
  strings, and numbers to represent itself fully, which is itself worth
  noting: not every JSON document needs to use every JSON type.

## 7. REST check (for this specific request/response)

- **Client–server separation:** Confirmed — my `curl` process knows
  nothing about how PokeAPI internally stores type-relation data (a
  database table? a static file? irrelevant), only the URL, method, and
  the JSON shape it got back.
- **Statelessness:** Confirmed — running the exact same `curl` command
  again, in a fresh terminal with no prior requests, produces an
  identical response. Nothing about this request depended on any earlier
  interaction; there is no session, login, or cookie involved anywhere in
  this exchange (contrast with Exercise 02's cookie round-trip, which was
  a deliberately *added* mechanism precisely because plain HTTP doesn't
  provide this by default).
- **Cacheability:** Confirmed, with direct evidence — the response
  explicitly includes `cache-control: public, max-age=86400`, telling any
  client (or an intermediate cache) that this exact response is safe to
  reuse for up to 86,400 seconds (24 hours) without asking again, rather
  than leaving caching behavior undefined or ambiguous.

## Self-grading notes

- If your chosen endpoint happens to include a `null` or `true`/`false`
  value naturally, that's a slightly stronger answer for section 6 than
  this reference (which honestly notes their absence) — but absence,
  correctly explained, is also a completely acceptable answer.
- The core thing being graded in section 7 is *specific evidence*, not
  just correctly naming the constraint — "it's stateless because HTTP is
  stateless" restates the definition without evidence; "running the same
  request twice produced identical results with no session involved" is
  evidence.
