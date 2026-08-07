# Exercise 01 — Your First Requests With curl

**Difficulty:** Very easy — this should be nearly impossible to fail if
you've read
[`lessons/00-setup.md`](../../lessons/00-setup.md),
[`lessons/02-tcp-tls-and-the-request-response-journey.md`](../../lessons/02-tcp-tls-and-the-request-response-journey.md),
[`lessons/03-http-methods-and-status-codes.md`](../../lessons/03-http-methods-and-status-codes.md),
and
[`lessons/04-headers-cookies-and-statelessness.md`](../../lessons/04-headers-cookies-and-statelessness.md)
carefully.

**Concepts this exercise uses** (all taught in the lessons above):
`curl` basics (`-v`, `-i`, `-s`, `-o`, `-D`), the request line, the status
line, IP address + DNS resolution appearing in `-v` output, the TCP and
TLS handshake phases appearing in `-v` output, the `GET` and `HEAD`
methods, status code `200`, and reading response headers (`Content-Type`,
`Content-Length`) — `-D` specifically is taught in Lesson 04's "Common
request headers" section, which dumps response headers to a location you
choose.

## What to build

You're going to make several real requests to the public
[PokeAPI](https://pokeapi.co/) with `curl`, and write down exactly what you
observe — no code to write, but real, careful observation, the same skill
you'll use to debug real network issues for the rest of this course.

Create a scratch folder to work in:

```bash
mkdir -p ~/web-fundamentals-practice/exercise-01
cd ~/web-fundamentals-practice/exercise-01
```

Then do each of the following, in order:

1. Run `curl -v https://pokeapi.co/api/v2/pokemon/ditto -o /dev/null` and
   read the entire output. Identify, and copy the exact line(s) that show:
   - the IP address the domain resolved to
   - which TLS version was negotiated
   - the full request line that was sent
   - the full status line that came back
2. Run `curl -i https://pokeapi.co/api/v2/pokemon/ditto -o response-body.json -D headers.txt`.
   This should produce two files in your current folder. Open both.
3. In `headers.txt`, identify the `Content-Type` and `Content-Length`
   values. Open `response-body.json` in VS Code and confirm its actual
   size (right-click the file → check size, or use `ls -la
   response-body.json`) roughly matches the `Content-Length` you saw.
4. Run `curl -i -X HEAD https://pokeapi.co/api/v2/pokemon/ditto`. Confirm,
   by looking at the output, that no JSON body was returned even though
   this is otherwise the "same" request as step 2.
5. Pick any **three** other Pokémon names of your choice (any real ones —
   check spelling against `https://pokeapi.co/api/v2/pokemon/` if unsure)
   and run a plain `curl -s ... | head -c 200` for each, just to see three
   different real responses.

## Acceptance criteria

- [ ] `solution/OBSERVATIONS.md` (see "What to submit") contains, quoted
  directly from your own terminal output: the resolved IP address, the
  negotiated TLS version, the exact request line, and the exact status
  line from step 1.
- [ ] `headers.txt` and `response-body.json` both exist in your working
  folder from step 2, and you correctly report both the `Content-Type`
  and `Content-Length` values you saw.
- [ ] You explicitly state whether the file size you checked matched
  `Content-Length` (it should, closely — note if it didn't and why you
  think so).
- [ ] You explain, in your own words, why step 4's `HEAD` request produced
  no body while otherwise looking like the same request as step 2.
- [ ] All three Pokémon names from step 5 returned real data (not a 404) —
  paste each command and its first line of output.

## What to submit

Create `solution/OBSERVATIONS.md` inside *this exercise's own folder*
(not your scratch practice folder) containing your answers to every
numbered step above, with real copy-pasted terminal output as evidence,
not paraphrased descriptions. When you ask for a review, point the AI at
this file.

## Hints

- If you're not sure which line in `-v` output is the TLS version, re-read
  Lesson 02's "Seeing every phase yourself" section — it annotates a real
  example output line by line.
- If `headers.txt` looks empty or wrong, double check you used a capital
  `-D` with a filename argument, not lowercase `-d` (which sets request
  *body* data, and is a completely different flag — covered in Lesson 03).
- If a Pokémon name in step 5 gives you a `404`, check your spelling first
  — that's expected/correct `curl` and API behavior, not a bug; just pick a
  name that actually exists.
- If you've re-read the relevant section and are still stuck, ask your AI
  session for a hint — Level 1 first, per
  [GRADING_PROTOCOL.md](../../../GRADING_PROTOCOL.md).
