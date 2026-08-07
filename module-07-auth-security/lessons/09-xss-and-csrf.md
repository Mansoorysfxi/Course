# Lesson 09 — XSS and CSRF: Two Attacks, Two Different Trust Boundaries

## What you'll learn

- What **XSS** (Cross-Site Scripting) is, the three common varieties, and why it's dangerous specifically *because* of what JavaScript is allowed to do on a page it's running on.
- Why React already defends against the most common form of XSS by default, and the one specific API that turns that protection off on purpose.
- What **CSRF** (Cross-Site Request Forgery) is, and why it's fundamentally a *cookie* problem — a browser automatically attaching credentials to a request the user never actually intended to make.
- Why QuestLog's specific design (a JWT in a manually-set header, not a cookie) sidesteps CSRF's usual mechanism entirely — and why that isn't a free win, since Lesson 03 already named the cost of that same design choice.
- The standard, named defenses for both: output escaping/CSP for XSS, the `SameSite` cookie attribute and anti-CSRF tokens for CSRF.

## Why this matters

XSS and CSRF are two of the most common, longest-standing web
vulnerability categories — both are perennial entries on the OWASP Top
10 — and both exploit a similar underlying idea from two different
angles: a browser's own default trust behaviors, turned against the site
that trusted them. Understanding both is essential for any full-stack
engineer, and understanding *why* QuestLog's specific architecture avoids
one of them for free (while still needing a real defense against the
other) is a genuinely useful, concrete example of how an architectural
decision made for one reason (Lesson 03's session-vs-JWT trade-off) has
security consequences you might not have anticipated when you made it.

## Prerequisites

Module 02 (cookies, and specifically that browsers resend a cookie
**automatically** on every request to a matching domain, with no
JavaScript involved at all), Module 03 (the DOM, and how JavaScript can
read/modify anything on the page it's running on), Lesson 03 (why
QuestLog stores its JWT in `localStorage` and attaches it manually, not
via a cookie).

## The concept, explained simply

Both attacks abuse a browser's own default behaviors — but from two
opposite directions:

- **XSS** tricks the browser into running an attacker's JavaScript *as
  if it were the real site's own code* — like a forged ID badge that
  fools the security guard into believing an intruder is genuinely
  authorized staff, granted the same building access as anyone else with
  a real badge.
- **CSRF** tricks the browser into sending a *genuine, valid* credential
  (a cookie) to the real site, on the attacker's behalf, without the real
  user ever intending that specific request — like someone secretly
  slipping a form under your office door, already pre-addressed and
  stamped with your own real signature, that gets mailed the moment you
  don't notice and throw it out with your regular outgoing mail.

## The details

### XSS: getting your JavaScript to run as the site's own code

If an attacker can get *any* JavaScript of their choosing to execute in
the context of your site (i.e., running as if the site itself served it),
they can do essentially anything your own site's JavaScript could do:
read anything in the DOM, make requests using the user's own cookies or
tokens, redirect the page, or — directly relevant to Lesson 03's
trade-off — **read `localStorage` directly**, including QuestLog's own
stored JWT, and send it straight to a server the attacker controls.

Three common varieties, by *where* the malicious script comes from:

- **Stored XSS** — an attacker's script gets saved on the server (e.g. as
  a quest's `title` or `description`, if this app rendered them
  unsafely) and served back to *every* future viewer of that data,
  including completely unrelated users.
- **Reflected XSS** — the malicious script rides along in a URL or form
  submission and is echoed straight back into that same response's HTML,
  affecting only whoever clicks a crafted link.
- **DOM-based XSS** — the vulnerability lives entirely in client-side
  JavaScript itself, which takes some untrusted input (a URL fragment, for
  instance) and unsafely inserts it into the page, with no server
  involvement in the vulnerable step at all.

### Why React already protects you, by default

If you tried to make QuestLog vulnerable to stored XSS by typing
`<script>alert('gotcha')</script>` as a quest's title, it wouldn't work —
and it's worth understanding exactly why. `QuestCard.tsx` renders a
quest's title with plain JSX:

```tsx
<h3>{quest.title}</h3>
```

React treats `{quest.title}` as **text content**, never as HTML to be
parsed — even if the string literally contains `<script>` characters,
React escapes them before inserting them into the real DOM, so the
browser displays the literal text `<script>alert('gotcha')</script>` on
screen, rather than ever creating a real, executable `<script>` element
from it. This is a structural property of how JSX/React rendering works,
not a security feature someone had to remember to turn on — every
ordinary `{expression}` interpolation in this entire codebase already
gets this protection automatically, for free.

**The one way to turn this protection off, on purpose:** React's
`dangerouslySetInnerHTML` prop does exactly what its own (deliberately
alarming) name says — it inserts a string as **raw HTML**, bypassing
React's automatic escaping entirely:

```tsx
{/* Deliberately unsafe if `content` is ever user-supplied — shown only as an example, not present anywhere in QuestLog */}
<div dangerouslySetInnerHTML={{ __html: content }} />
```

QuestLog uses this **nowhere at all** — every piece of user-supplied text
in this app (a quest's title, description, quest line name, a user's
email) is rendered through plain `{expression}` JSX interpolation, which
is precisely why this app has no stored-XSS surface today. If a future
feature ever needed to render actual rich text/HTML a user supplied (a
formatted quest description, say), that would be the moment to reach for
a dedicated **sanitization library** that strips dangerous tags/attributes
first — never raw, unsanitized `dangerouslySetInnerHTML`.

### CSRF: a forged request, riding on real credentials

CSRF specifically targets **cookie**-based authentication (session
cookies, Lesson 03) — here's the classic shape of the attack: you're
logged into `real-bank.com`, which authenticates you via a cookie. You
then visit a completely unrelated, malicious page,
`evil-site.com`, which contains a hidden auto-submitting form:

```html
<form action="https://real-bank.com/transfer" method="POST">
  <input type="hidden" name="to_account" value="attacker-account" />
  <input type="hidden" name="amount" value="1000" />
</form>
<script>document.forms[0].submit();</script>
```

Your browser, following its own normal, unremarkable cookie rule
("always attach this domain's cookies to any request to that domain,
regardless of which page initiated it"), automatically attaches your
*real*, valid `real-bank.com` session cookie to this forged request — the
attacker never sees your cookie, never needs to steal it, and never needs
to run any of *their* JavaScript in `real-bank.com`'s own context at all
(unlike XSS). They only need you to have an active session and to visit
their page while it's still valid.

### Why QuestLog's design sidesteps CSRF's usual mechanism — and what that costs

CSRF fundamentally exploits **automatic** credential attachment. QuestLog's
JWT is never attached automatically by the browser at all — Lesson 03
already described this: the frontend reads the token from `localStorage`
itself, in its own JavaScript, and sets the `Authorization` header
**by hand**, on every request (`src/api/http.ts`'s `request()`). A
malicious page on a completely different origin has no way to make *your
browser* set that header on a forged request to QuestLog's API — it has
no access to QuestLog's `localStorage` at all (browsers isolate
`localStorage` per origin, exactly as Module 02's own-origin rules apply
generally), so it cannot know what value to even put in that header.
**This means QuestLog's specific token design is not vulnerable to
classic CSRF, by construction** — not because anyone added a CSRF
defense, but because the attack's own precondition (automatic credential
attachment) simply doesn't apply here.

This is *not*, however, a free win — Lesson 03 already named the actual
cost of this same design choice: because the token lives in
`localStorage`, readable by JavaScript, it *is* exposed to XSS in a way an
`HttpOnly` cookie explicitly would not be. **This is the honest trade-off
in full:** QuestLog's approach is naturally CSRF-resistant, and XSS
protection is what actually matters most for this app's specific design,
which is why this lesson leads with React's default escaping behavior
above as the thing genuinely doing the protective work here.

### The standard defenses, named, for a cookie-based app (not QuestLog's own situation, but essential vocabulary)

If a system *does* use cookies for authentication, two real, standard
defenses exist:

- **The `SameSite` cookie attribute** — a flag a server sets on a cookie
  (`Set-Cookie: session=...; SameSite=Strict` or `SameSite=Lax`) telling
  the browser "don't send this cookie along with requests that originated
  from a different site." Modern browsers default new cookies to
  `SameSite=Lax` if unspecified, which already blocks the most naive
  version of the attack above, but `Strict` is stronger still for
  sensitive actions.
- **Anti-CSRF tokens** — a random, unpredictable value the server embeds
  in a legitimate page (e.g. a hidden form field) that must be resubmitted
  along with the real request; a forged request from `evil-site.com` has
  no way to know or supply the correct value, since it never actually
  loaded the real page containing it.

## Common mistakes & gotchas

- **Believing "we use JSON, not HTML forms, so we're immune to CSRF."**
  Not automatically true — the real deciding factor is whether credentials
  are attached *automatically* by the browser (cookies) or *manually* by
  your own JavaScript (a header, as in QuestLog). A cookie-authenticated
  JSON API can still be CSRF-vulnerable via other request shapes
  (though modern browsers' default `SameSite=Lax` behavior has closed off
  many of the older, simplest versions of this).
- **Reaching for `dangerouslySetInnerHTML` "just this once" for
  convenience, without sanitizing the input first.** This is the single
  most direct way to reintroduce stored XSS into an otherwise-safe React
  app — treat this prop as a loud, deliberate exception requiring its own
  sanitization step, never a casual shortcut.
- **Assuming XSS only matters for cookie-based apps.** It's the opposite,
  in fact — an app storing a token in `localStorage` (like this one) is
  specifically exposed to token theft via XSS in a way a *cookie-based*
  app using `HttpOnly` isn't (JavaScript can't read an `HttpOnly` cookie
  at all). Never assume "we don't use cookies for auth" means "XSS doesn't
  matter here."

## How this connects

Lesson 08 covered SQL injection, a backend-side "don't let untrusted data
control structure" problem; this lesson covers the browser-side version
of a similar family of issues. Lesson 03's session-vs-JWT architecture
decision turns out to have real consequences for exactly these two
attacks, which is why this lesson circled back to that decision directly
rather than treating XSS/CSRF as generic, context-free vocabulary.
Lesson 10 covers CORS, a *third*, related-but-distinct browser security
mechanism that's frequently confused with both of these — that lesson
explicitly untangles the difference.

## Quick self-check

1. What is the essential difference between how XSS and CSRF each abuse a browser's trust?
2. Why does ordinary JSX interpolation (`{quest.title}`) already protect against stored XSS, and what specific API turns that protection off?
3. Why is CSRF fundamentally a cookie-specific problem, and why doesn't it apply to QuestLog's specific token design?
4. What real cost does QuestLog's CSRF-resistant design choice have, and which earlier lesson already named it?
5. Name the two standard defenses against CSRF for a cookie-based app, and briefly explain how each one works.
