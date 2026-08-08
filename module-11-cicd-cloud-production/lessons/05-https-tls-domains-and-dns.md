# Lesson 05 — HTTPS, TLS Certificates, Domains, and DNS, in Practice

**Verified against (August 2026):** Render's own custom-domain and TLS
documentation (`render.com/docs/tls`, `render.com/docs/custom-domains`) —
Render uses Let's Encrypt and Google Trust Services to automatically
issue and renew certificates for both its own `*.onrender.com`
subdomains and any custom domain added to a service, with automatic
HTTP→HTTPS redirection and no manual `certbot` step required at any
point. Namecheap's current `.com` pricing (roughly $9-10 first year,
$14-19/year renewal) reconfirmed via multiple current sources, August
2026.

## What you'll learn

- How a TLS certificate actually gets **issued and automatically renewed**
  for a real domain, with no human running `certbot` by hand — building
  directly on Module 02's own TLS-handshake mechanics.
- The DNS record types a real deployment actually uses in practice:
  `A`, `AAAA`, `CNAME`, and `TXT` — going beyond Module 02's own `A`-record-
  only `nslookup` example.
- Exactly how Render's own automatic domain verification and certificate
  issuance works, mechanically, and how to point a real domain at a
  Render deployment.
- Why this module's own capstone treats a real, purchased domain as
  fully optional, and what changes if you choose to add one.

## Why this matters

Module 09's manual VPS deploy was explicitly, honestly HTTP-only — no
TLS at all, and that module said so directly. This lesson closes that
gap for good, and explains exactly what "automatic HTTPS" — something
Module 09 could only gesture at as "Module 11's job" — actually consists
of, mechanically, rather than treating it as unexplained magic (this
course's Rule 2, applied to one of the most common pieces of unexplained
"magic" in web deployment).

## Prerequisites

- **Module 02, Lesson 02** — the TLS handshake itself (versions, cipher
  negotiation, what a certificate proves) is assumed, fully taught, and
  not re-explained here; this lesson picks up exactly where that one
  stopped: how a certificate gets onto a server in the first place, and
  kept valid over time.
- **Module 02, Lesson 01** — basic DNS/`nslookup` (an `A` record
  resolving a name to an IP) is assumed.
- **Module 09's networking lesson** — ports, and the general shape of
  "a request has to reach the right machine first" — this lesson doesn't
  re-teach that, only extends it to "how does the RIGHT machine get a
  valid certificate for the domain the request arrived on."

## The concept, explained simply

Recall Module 02's own certificate explanation: a TLS certificate is a
signed document proving "this domain name genuinely belongs to whoever
is presenting this certificate," issued by a **Certificate Authority**
(CA) both sides already trust. The genuinely new question this lesson
answers is: **how does a CA know it's safe to issue that certificate to
you specifically, for a domain you claim to own, without a human at the
CA manually verifying every single request?** The answer, for the
overwhelming majority of the modern web, is an automated protocol called
**ACME** (Automatic Certificate Management Environment), and the CA
almost everyone uses it against is **Let's Encrypt** — a free,
nonprofit CA created specifically to make this whole process free and
fully automatable. Think of ACME as a fully automated version of
"prove you have the keys to this house before we hand you a copy" — the
CA gives your server (or, in this module's case, Render, acting on your
behalf) a small, temporary challenge only the real owner of a domain
could satisfy, and issues a real certificate the moment that challenge is
satisfied — no human at Let's Encrypt ever looks at your request
individually.

## The details

### How an ACME domain-validation challenge actually works

There are two common ACME challenge types worth knowing by name:

- **HTTP-01 challenge** — the CA asks your server to serve a specific,
  random file at a specific, temporary URL
  (`http://yourdomain.com/.well-known/acme-challenge/<random-token>`).
  Only whoever actually controls the server that `yourdomain.com`'s DNS
  currently points at could make that URL return the right content — so
  successfully serving it back proves real control of the domain's live
  traffic.
- **DNS-01 challenge** — the CA asks you to create a specific `TXT` DNS
  record (see below) with a specific value. Only whoever controls the
  domain's actual DNS settings could add that record — so its presence
  proves domain ownership a different way, useful specifically for
  domains that aren't (or can't yet be) publicly reachable over HTTP at
  all.

Render's own current documentation states it checks your domain's DNS,
and, once that DNS is confirmed correctly pointed at Render, automatically
requests and receives a certificate from Let's Encrypt (or, in some
cases, Google Trust Services) — completing within minutes of successful
DNS verification, with **zero manual `certbot` command, zero manually
copied certificate file, and zero manual renewal ever required** — a
direct, concrete contrast to how a real `certbot`-based manual setup
(the kind Module 09's own deploy explicitly chose not to cover) would
work on a raw VPS.

### DNS record types, in practice

Module 02 introduced DNS with a single record type: **`A`** — the
simplest possible mapping, a domain name straight to an IPv4 address
(`AAAA` is the exact same idea for IPv6). Real deployments, including
this module's own, regularly need a few more:

- **`CNAME`** (Canonical Name) — points one domain name at ANOTHER
  domain name, not directly at an IP address. This is exactly what
  Render's own custom-domain instructions ask for: point
  `app.yourdomain.com` at `your-service-name.onrender.com` via a
  `CNAME` record, rather than at a raw IP address. This matters because
  Render's own underlying IP addresses can and do change over time (its
  infrastructure scales, machines get replaced) — a `CNAME` pointed at
  a *name* Render controls keeps working automatically through any such
  change; a hardcoded `A` record pointed at today's IP would silently
  break the moment that IP changed.
- **`TXT`** — stores arbitrary text, most commonly used for exactly this
  lesson's own domain-verification purpose (an ACME DNS-01 challenge, or
  a platform's own "prove you own this domain" check before letting you
  attach it to a service at all).
- **Why a domain's own root/"apex" (`yourdomain.com` with no subdomain,
  as opposed to `app.yourdomain.com`) is a genuinely special case:** DNS
  rules technically forbid a `CNAME` record at a domain's apex if any
  other record type also exists there (which is almost always true, for
  technical reasons this lesson won't fully unpack) — this is exactly
  why real platforms, including Render, generally recommend pointing a
  `www.yourdomain.com` subdomain at them via `CNAME`, and using a
  redirect (or a special, non-standard record some registrars call
  `ALIAS`/`ANAME`) for the bare apex domain specifically.

### Pointing a real domain at Render (only if you bought one)

If you completed Lesson 00-setup.md's optional Step 4:

1. In your Render service's dashboard, go to **Settings → Custom
   Domains**, add your domain (e.g. `questlog.yourdomain.com`).
2. Render shows you the exact DNS record to add (per the section above,
   almost always a `CNAME` pointed at your service's own
   `*.onrender.com` name) — add it at your domain registrar's own DNS
   management page.
3. Wait for DNS to propagate (usually minutes; can occasionally take
   longer — DNS changes are not instant worldwide) and for Render to
   confirm verification.
4. **Expected:** within a few minutes of verification, `https://` on your
   own domain works, with a real, valid, auto-renewing certificate — no
   further action ever required, including at renewal time, indefinitely.

### The free path (no domain purchase at all)

Every Render service already gets a real, working
`https://your-service-name.onrender.com` URL, with the exact same
automatic TLS as a custom domain — this is a completely legitimate way
to complete this module's entire capstone. The only difference a real,
purchased domain buys you is a shorter, more memorable, more
professional-looking URL — genuinely a cosmetic and branding
consideration for a personal learning project, not a functional one.

## Common mistakes & gotchas

- **Adding an `A` record pointed at an IP address you copied once,
  instead of the `CNAME` a platform actually asked for.** This
  technically often "works" the day you set it up, then silently breaks
  weeks or months later the moment the platform's underlying IP changes —
  exactly the failure mode a `CNAME` is designed to prevent. Always
  follow the exact record type a platform's own dashboard instructs, not
  whatever IP a manual `dig`/`nslookup` happens to show you today.
- **Expecting DNS changes to take effect instantly.** DNS records have a
  **TTL** (Time To Live) telling other DNS servers around the world how
  long they're allowed to cache an old answer before checking again —
  propagation can take anywhere from a couple of minutes to (rarely) a
  day or more, depending on TTL settings and caching along the way. If a
  domain "isn't working yet" immediately after adding a record, waiting
  is usually the correct first troubleshooting step, not assuming the
  record itself is wrong.
- **Trying to put a `CNAME` at a domain's bare apex** (`yourdomain.com`
  itself, not a subdomain) and hitting a real, standards-based DNS
  restriction — see this lesson's own explanation above; use `www.` (or
  whatever subdomain a platform recommends) instead, or your registrar's
  own `ALIAS`/`ANAME` record type if it offers one specifically for this
  case.
- **Confusing "my browser shows a padlock" with "this connection is
  definitely trustworthy."** A valid TLS certificate proves the domain
  genuinely belongs to whoever is presenting it — it says nothing at all
  about whether that domain's OWNER is trustworthy (a real, valid,
  auto-renewed certificate for a genuinely malicious phishing domain is
  completely possible, and common) — see Module 07's own security lesson
  for the broader context this fact sits inside.

## How this connects

Lesson 06 covers what happens *after* a real, HTTPS-secured deployment is
live — how you'd actually find out something went wrong. Lesson 08's
capstone applies this lesson's Render custom-domain steps for real,
alongside the free-path alternative. Exercise 05 has you use `dig` and
`curl -i` against several real, live domains to observe exactly the
record types and certificate details this lesson described, hands-on.

## Quick self-check

1. What specific problem does the ACME protocol solve, and why does
   using it mean a human at Let's Encrypt never manually reviews your
   certificate request?
2. What's the difference between an HTTP-01 and a DNS-01 ACME challenge —
   what does each one actually prove, and how?
3. Why does Render's own custom-domain setup ask for a `CNAME` record
   instead of an `A` record pointed at a specific IP address?
4. What is a DNS record's TTL, and why does it explain why a freshly
   added DNS record might not "work" for several minutes (or longer)?
5. What does a valid TLS certificate actually prove about a website, and
   what does it deliberately NOT prove?
