# Exercise 05 — DNS and HTTPS Investigation (Independent)

**Concepts this exercise uses (all taught in
[`lessons/05-https-tls-domains-and-dns.md`](../../lessons/05-https-tls-domains-and-dns.md),
building on Module 02's own TLS-handshake and `nslookup` material):**
`dig`, `A`/`AAAA`/`CNAME`/`TXT` records, TTL, ACME/Let's Encrypt,
certificate issuers, `curl -I`/`curl -v`.

**Where to work:** no starter code — this is a real-world investigation
exercise against live, public domains. No account, no signup, no
spending required; everything here runs against infrastructure that
already exists on the public internet.

## Setup — installing `dig`

If you're on WSL2 Ubuntu (Module 09/10's own environment), `dig` is part
of the `dnsutils` package:
```bash
sudo apt update && sudo apt install -y dnsutils
dig -v
```
**Expected:** a version string, no error.

## Your task

Answer every question below with the REAL command you ran and its REAL
output — not a guess, and not what you expect the answer "should" be.
Write your answers into a new file, `investigation-report.md`, in this
same folder (create it yourself; no fixed template).

### Part 1 — DNS record types, for real domains

```bash
dig github.com A
dig github.com CNAME
dig www.github.com CNAME
```
1. Does `github.com` (the bare apex domain) have an `A` record, a
   `CNAME` record, both, or neither? Does `www.github.com`?
2. Explain, using Lesson 05's own "apex domain" section, why the pattern
   you observed makes sense.

```bash
dig questlog-backend.onrender.com CNAME
```
(Substitute a real Render-hosted domain if you've deployed one yourself
by this point — otherwise, any real `*.onrender.com` name works for this
question, even one that doesn't resolve to anything you own.)
3. What TTL value does the answer show? Using Lesson 05's own
   explanation, what does that number actually mean in practice?

### Part 2 — TLS certificates, for real

```bash
curl -v https://github.com 2>&1 | grep -A 3 "Server certificate"
```
4. Which Certificate Authority issued this certificate, per the output?
5. Run the exact same command against `https://example.com`. Is the
   issuer the same organization? Different real sites can, and often do,
   use completely different Certificate Authorities — this is expected
   and fine, not an inconsistency to worry about.

```bash
curl -I http://github.com
```
6. What status code and header do you see that indicates GitHub redirects
   plain HTTP traffic to HTTPS automatically? (Module 02's own
   status-code lesson already taught you how to read this.)

### Part 3 — Your own deployment (only if you've completed Lesson 08 / Exercise 06)

If you have a real, live Render deployment by this point:
```bash
dig questlog-backend-XXXX.onrender.com CNAME
curl -v https://questlog-backend-XXXX.onrender.com/health 2>&1 | grep -A 3 "Server certificate"
```
7. Who issued YOUR deployment's own certificate? Is it the same CA
   GitHub uses?

If you haven't deployed anything real yet, answer this instead: based on
Lesson 05's own explanation of Render's automatic TLS, name the exact CA
(or CAs) Render's own documentation says it uses.

## Acceptance criteria

- [ ] `investigation-report.md` exists, with real command output pasted
      in for every question (not paraphrased from memory).
- [ ] Every answer correctly distinguishes what you directly OBSERVED
      from what Lesson 05 told you to EXPECT — where they match, say so;
      if anything ever doesn't match what you expected, say that too and
      take your best honest guess why.
- [ ] You can explain, unprompted, the real difference between an `A`
      record and a `CNAME` record, using your own `dig` output as
      evidence, not just the lesson's own description.

## Hints

<details>
<summary>Hint 1</summary>

If `dig` isn't available and you don't want to install anything,
`nslookup` (Module 02's own tool) can answer the A-record question, and
most DNS lookup websites (search "dig CNAME lookup") can answer the
CNAME questions without installing anything at all — note in your report
which tool you actually used.

</details>

<details>
<summary>Hint 2</summary>

`curl -v` (verbose) shows the entire TLS handshake, including the
certificate details — you're looking for a line that starts with
something like `* Server certificate:` followed by `issuer:` — this is
the exact same output shape Module 02's own TLS lesson already walked
through.

</details>

There is no `solution/` folder for this exercise — every real domain
you investigate will show slightly different, entirely correct real-
world data. Ask for a review of your `investigation-report.md` directly.
