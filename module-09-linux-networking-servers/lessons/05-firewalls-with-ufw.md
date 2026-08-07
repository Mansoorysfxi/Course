# Lesson 05 — Firewalls with ufw

**Verified against (August 2026), via live web search:** `ufw`'s default
policy on current Ubuntu (24.04 and 26.04 alike) remains **deny all
incoming, allow all outgoing** by default; core command syntax
(`ufw allow`, `ufw deny`, `ufw enable`, `ufw status verbose`, app
profiles like `'Nginx Full'`/`OpenSSH`) is confirmed current and
unchanged against current Ubuntu documentation and community references
checked while writing this lesson.

## What you'll learn

- What a firewall actually does, at the level of individual network
  packets.
- Why "default deny incoming, allow outgoing" is the correct starting
  posture for any server exposed to the public internet.
- How to install, enable, and configure `ufw` (Uncomplicated Firewall) —
  Ubuntu's standard, beginner-friendly front end for the kernel's own
  firewall.
- The exact, minimal set of `ufw` rules a server running SSH + Nginx (in
  front of QuestLog) needs — and why "minimal" is itself the correct
  design goal, not a corner being cut.

## Why this matters

Lesson 04 established that a real VPS has no NAT quietly shielding it —
its public IP is directly reachable by anyone, and automated scanners
constantly probe the internet for exactly this. A firewall is the
deliberate, explicit control over exactly which ports may receive
incoming traffic at all, regardless of whether some program happens to
be listening there. Without one, *every* port any program on the
machine binds to `0.0.0.0` is immediately exposed to the whole internet
the moment it starts listening — `ufw` is what lets you say, explicitly,
"only these specific ports, for these specific purposes, and nothing
else," which is exactly the posture the capstone's real server needs.

## Prerequisites

- `lessons/04-networking-ports-and-ips.md` — ports, and the
  `127.0.0.1`/`0.0.0.0` bind-address distinction, both used directly
  below.
- `lessons/01-linux-processes-and-permissions.md` — `sudo`, and this
  lesson's `apt install` reuse.

## The concept, explained simply

A firewall is a checkpoint every network packet has to pass before it's
allowed to reach any program on the machine — think of it as a bouncer
standing at every single door (port) of a building, checking a list
before letting anyone in, rather than trusting whoever happens to be
standing at the door (the application) to turn away people who
shouldn't be there. The critical design decision is **default-deny**:
rather than trying to enumerate every bad actor and block them one by
one (an impossible, endless task), a correctly configured firewall
starts from "nobody gets in, for anything, unless I specifically said
so" and adds narrow, explicit exceptions — the same logic as an Unreal
project's packaging settings defaulting to "exclude everything not
explicitly marked for cook" rather than trying to remember to exclude
every file you don't want shipped.

## The details

### Step 0 — Install and check ufw's current state

`ufw` ships pre-installed on most Ubuntu images, including WSL2's, but
confirm:

```bash
sudo apt update
sudo apt install -y ufw
sudo ufw status verbose
```

**Expected output, on a completely fresh install:**
```
Status: inactive
```
`inactive` here means the underlying firewall rules aren't being
enforced *at all* yet — every port any program listens on is currently
reachable, filtered by nothing. This is `ufw`'s safe starting state
specifically so that installing it doesn't immediately lock you out of
a machine you're remotely `ssh`'d into before you've had a chance to
allow SSH itself through.

### Step 1 — The single most important rule, before enabling anything

**On a real remote server, this step must happen before `ufw enable`,
not after — getting this order wrong is how people lock themselves out
of a VPS entirely, sometimes permanently (short of a rescue console).**
Explicitly allow SSH first:

```bash
sudo ufw allow OpenSSH
```

**Expected output:**
```
Rules updated
Rules updated (v6)
```

**Line by line:** `OpenSSH` here isn't a magic keyword — it's an **app
profile**, a small, named bundle of port rules that packages register
with `ufw` when installed (the OpenSSH server package registers one for
port `22/tcp`, exactly the well-known port from Lesson 04). List every
profile currently registered on your system:

```bash
sudo ufw app list
```
**Expected (abbreviated, exact list depends what's installed):**
```
Available applications:
  Nginx Full
  Nginx HTTP
  Nginx HTTPS
  OpenSSH
```
(`Nginx Full`/`HTTP`/`HTTPS` only appear once Nginx itself is installed —
Lesson 06.) Using `allow OpenSSH` instead of the equivalent
`allow 22/tcp` is preferred purely for readability — both produce
identical underlying rules; check with:
```bash
sudo ufw show added
```

### Step 2 — Enable ufw

Only now, with SSH explicitly allowed:

```bash
sudo ufw enable
```
**Expected output:**
```
Command may disrupt existing ssh connections. Proceed with operation (y|n)? y
Firewall is active and enabled on system startup
```
`ufw` itself warns you about exactly the risk described above — type `y`
because you already allowed SSH in Step 1. Confirm the new state:

```bash
sudo ufw status verbose
```
**Expected:**
```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         --------    ----
OpenSSH                    ALLOW IN    Anywhere
OpenSSH (v6)                ALLOW IN    Anywhere
```
**Line by line, the `Default:` line — the single most important
sentence `ufw status verbose` ever prints:** `deny (incoming)` — every
inbound connection is refused unless a rule below explicitly allows it;
`allow (outgoing)` — anything *this* machine initiates outward (like
`apt update` reaching Ubuntu's package servers, or the backend reaching
an external API) is unaffected, since outbound traffic isn't the attack
surface this lesson is defending. `Anywhere` in the rule list means "any
source IP address" — SSH is reachable from anyone who has your key, which
is the intended, correct behavior (restricting SSH to specific source
IPs is possible but outside this module's scope, and unnecessary once
Lesson 02's key-based-only login is in place).

### Step 3 — The exact rules a QuestLog-hosting server needs

Once Nginx is installed (Lesson 06), the complete rule set this
capstone's server needs is exactly three allowances — nothing more:

```bash
sudo ufw allow OpenSSH       # already added above — port 22
sudo ufw allow 'Nginx HTTP'   # port 80 — plain HTTP, this module's scope
# (Module 11 later adds HTTPS/443 once a real domain + TLS cert exist)
```

**Try it yourself, right now (before Nginx is installed, so this fails
in an instructive way):** confirm port 80 currently has no listener at
all —
```bash
sudo ss -tlnp | grep :80
```
should print nothing. Then check:
```bash
sudo ufw status
```
Notice `ufw` would already be ready to *allow* port 80 traffic in, even
though nothing is listening on it yet — a firewall rule and "something
is actually running there" are two completely independent facts, and
confusing them is a common debugging trap (a request to an allowed-but-
unlistened port still fails, just for a different reason: **connection
refused**, versus a blocked port's silent **timeout** — a distinction
worth recognizing when troubleshooting a real deploy).

**Deliberately absent from this rule set:** port `8000` (QuestLog's own
Uvicorn process) and port `5432` (PostgreSQL). Neither needs a `ufw`
rule allowing outside access, because — tying directly back to Lesson
04 — both are bound only to `127.0.0.1` on the real server, reachable
only from Nginx and the backend respectively, both running on that same
machine; `ufw`'s rules only govern traffic arriving from **outside** the
machine in the first place. This is the concrete payoff of getting the
bind-address lesson right: the firewall configuration for a well-
architected deploy ends up *simpler*, not more complex, because most of
the attack surface was already closed by correct binding, before
`ufw` ever entered the picture.

### Removing a rule, and checking numbered rules

```bash
sudo ufw status numbered
```
**Expected:** the same rule list, each prefixed with `[1]`, `[2]`, etc.
Delete one by number:
```bash
sudo ufw delete 2
```
(`ufw` asks for confirmation before deleting — type `y`.) This
numbered-deletion approach is generally easier to get right than trying
to retype a rule's exact original spec to remove it.

## Common mistakes & gotchas

- **Running `ufw enable` on a remote server before allowing SSH.** This
  is the single most damaging mistake possible in this entire lesson —
  it can genuinely lock you out of a real VPS with no way back in except
  a provider's separate rescue/web console (if they offer one) or
  rebuilding the server from scratch. Always: allow SSH, *then* enable.
- **Confusing "connection refused" with "connection timed out."** A
  *refused* connection means a packet reached the machine and something
  (the OS, because nothing's listening; or the app itself) actively said
  "no" — this happens when `ufw` allows the port but nothing's listening.
  A connection that **times out** with no response at all is the
  signature of `ufw` (or an upstream network firewall) silently dropping
  the packet before it ever reaches the machine's own listening logic —
  this happens when a port isn't allowed. Learning to tell these two
  apart from a `curl` or browser error message alone is a genuinely
  useful, transferable debugging skill.
- **Forgetting `ufw`'s rules are evaluated top-to-bottom, first match
  wins**, when adding a `deny` rule *after* a broader `allow` that
  already covers the same traffic — the earlier `allow` wins and the
  later `deny` never gets a chance. `ufw status numbered`'s ordering
  reflects the real evaluation order.
- **Assuming `ufw`'s "deny incoming" default protects an application
  from a *different* server on the same private network reaching it.**
  If two services on the same local/private network segment need to talk
  (rare in this module's single-VPS setup, but real in a multi-server
  deployment), a rule allowing a specific source IP or subnet, rather
  than a blanket `Anywhere` rule, is exactly what's needed —
  `sudo ufw allow from 10.0.0.5 to any port 5432` as one example shape,
  outside this lesson's minimal-rule-set scope but worth knowing exists.
- **Thinking `ufw`'s job is anything like an application-level concern
  (authentication, input validation).** `ufw` operates entirely below
  the application — it has no idea what QuestLog's `/api/quests` route
  does or whether a request carries a valid JWT; it only ever decides
  "does this specific IP-address-and-port combination's traffic even
  reach any program at all." Module 07's auth/JWT material and this
  lesson solve two entirely different, complementary problems.

## How this connects

Lesson 06 installs Nginx, which is exactly what registers the
`Nginx HTTP`/`Nginx Full` profiles used above, and is the one process on
the real server whose whole job requires being reachable from the
public internet at all — everything this lesson set up exists to let
Nginx's own traffic through while keeping everything behind it
(QuestLog's backend, PostgreSQL) unreachable except from Nginx itself,
on the same machine.

## Quick self-check

1. Why must SSH be explicitly allowed *before* running `ufw enable` on a real remote server, not after?
2. What does `ufw`'s "Default: deny (incoming), allow (outgoing)" actually mean, in terms of which direction of traffic each half governs?
3. Why does this module's capstone server need no `ufw` rule at all for port 8000 (QuestLog's backend) or port 5432 (PostgreSQL)?
4. What's the practical difference, from a client's point of view, between a connection that's refused and one that times out — and which one does a `ufw`-blocked port typically produce?
5. Is `ufw` a substitute for the JWT-based authentication QuestLog's own API already enforces? Why or why not?
