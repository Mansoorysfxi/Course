# Lesson 04 — Networking for Developers: Ports, IPs, and Where a Program Actually Listens

**Verified against (August 2026):** IANA's own port registry conventions
(well-known ports 0–1023, registered 1024–49151, ephemeral/dynamic
49152–65535) and RFC 1918's private IP address ranges are long-standing
internet standards, unchanged for decades — this lesson's factual content
is stable, not fast-moving; the specific thing worth flagging is that
this course's Module 02 already taught IP addresses, DNS, `localhost`,
and private IP addresses in the context of *how the web works* — this
lesson revisits those exact terms from a different angle: not "what
happens when a browser requests a page" but "what does it mean for a
program running on a server to actually be reachable at all."

## What you'll learn

- What a **port** actually identifies, precisely, and why an IP address
  alone isn't enough to reach a specific program.
- The real, practical difference between binding to `127.0.0.1` and
  binding to `0.0.0.0` — the single setting that determines whether a
  running server is reachable from anywhere but itself.
- Private vs. public IP addresses, revisited specifically in the context
  of "which machines can even attempt to reach mine."
- What **NAT** is, in enough detail to explain why your own home
  computer doesn't need a firewall against the entire internet the same
  way a VPS does.
- How to actually check what's listening on a given port on a real
  machine.

## Why this matters

Every deployment mistake in this module that *isn't* a permissions or
`systemd` problem is a networking problem, and almost always the exact
same one: a program is running correctly, `systemctl status` shows it
healthy, but nothing outside the machine can reach it. Understanding
*why* — usually because it's bound to the wrong address, or nothing is
listening on the port a request is arriving on — is the single most
useful diagnostic skill this module teaches, and it's needed before
Lesson 06 (Nginx) and the capstone make any sense.

## Prerequisites

- Module 02's `lessons/01-networks-ip-addresses-and-dns.md` — this
  lesson assumes you already know what an IP address and a port are in
  the abstract (both defined there, and in `GLOSSARY.md`); this lesson
  applies those definitions to a new, more operational question.
- Lesson 03 (`systemd`) — QuestLog's backend, as a running service, is
  this lesson's running example of "a program that needs to be reachable
  on a specific port."

## The concept, explained simply

An IP address gets a request to the right **machine** — like a street
address gets a delivery truck to the right building. A **port** is what
gets it to the right **program running on that machine** — like an
apartment number, or in Unreal terms, like the specific listen socket a
dedicated server binds when it starts up so that game clients (not the
OS, not some other running program) can find and connect to it
specifically, even though many programs might be running on that same
machine's single IP address at once. A machine has exactly one (or a
handful of) IP addresses, but up to 65,536 possible ports, and normally
dozens of programs simultaneously listening on different ones —
PostgreSQL on `5432`, SSH on `22`, Nginx on `80`, QuestLog's Uvicorn
process on `8000` — the same physical network connection, sorted by
port number to the correct waiting program.

## The details

### Ports: what "listening" actually means

A running program doesn't receive network traffic passively — it has to
actively ask the operating system "please give me any traffic that
arrives on port N," a request called **binding** to that port. Prove
this on QuestLog's own backend. In one WSL2 terminal, inside this
module's copy of the backend:

```bash
cd module-09-linux-networking-servers/project/questlog/backend
# (venv setup / .env / migrations already covered in Module 08's own
#  setup lesson if you haven't done them yet in this exact folder)
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Expected:** the familiar `Application startup complete.` line. In a
**second** WSL2 terminal, check what's actually listening:

```bash
sudo ss -tlnp | grep 8000
```

**Expected output (abbreviated):**
```
LISTEN 0      2048       127.0.0.1:8000       0.0.0.0:*      users:(("python",pid=12345,fd=7))
```

**Line by line:** `ss` ("socket statistics," the modern replacement for
the older `netstat` command, still worth recognizing if you see it in
older material) lists active network connections and listening sockets.
`-t` = TCP only, `-l` = show only *listening* sockets (not active
connections), `-n` = show raw port numbers instead of trying to resolve
service names, `-p` = show which **process** (Lesson 01's term, again)
owns each socket. The output line above says: something is listening on
`127.0.0.1:8000` — and that "`127.0.0.1:8000`" pairing is the whole
concept of this lesson made completely concrete: not just "port 8000,"
but *specifically* on the `127.0.0.1` address, which (Module 02) means
**this same machine only.**

### `127.0.0.1` vs `0.0.0.0`: the single most common real deployment bug

Stop that Uvicorn process (`Ctrl+C`) and restart it with one difference:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Check again:
```bash
sudo ss -tlnp | grep 8000
```
**Expected:**
```
LISTEN 0      2048       0.0.0.0:8000         0.0.0.0:*      users:(("python",pid=12399,fd=7))
```

The address changed from `127.0.0.1` to `0.0.0.0`. **This is not a
placeholder or a typo — `0.0.0.0` as a *bind* address has a specific,
different meaning than `0.0.0.0` would mean anywhere else:** it means
"accept connections arriving on **any** of this machine's network
interfaces" — `127.0.0.1` (loopback, meaning "myself"), a private LAN
address if it has one, and its real public IP if it has one, all at
once — instead of accepting connections only on the one specific address
you'd otherwise have to name. On your own laptop, both behave similarly
enough for local development that this distinction rarely bites you. On
a **real VPS**, it is the difference between "only I, logged into this
exact machine, can reach this program" (`127.0.0.1`) and "anyone who can
route a packet to this machine's public IP can reach this program"
(`0.0.0.0`). Get this backwards in either direction on a real deploy and
you get one of two classic failures: bind to `127.0.0.1` when you needed
`0.0.0.0`, and Nginx (a separate process on the same machine, Lesson 06)
or an external client can't reach your app at all, even though it's
demonstrably running; bind to `0.0.0.0` for something that should stay
private (a database — see below) and you've potentially exposed it to
the entire internet.

**Try it yourself:** with Uvicorn bound to `0.0.0.0:8000` (still running
from above), find your WSL2 instance's own IP address:
```bash
hostname -I
```
This prints one or more addresses — WSL2 typically shows a private,
internal address (something like `172.x.x.x`) representing WSL2's own
small virtual network *inside* your Windows machine, not your home
network's address and definitely not a public internet address. From a
**separate** terminal (WSL2 or PowerShell) try:
```bash
curl http://<that IP>:8000/
```
This should reach QuestLog's backend, proving `0.0.0.0` really did open
it up beyond just `127.0.0.1`'s "myself only." Now stop Uvicorn
(`Ctrl+C`) — nothing this module needs stays running indefinitely on
`0.0.0.0` inside WSL2 itself; the capstone applies this on the real VPS
where it actually matters.

### Why PostgreSQL should almost never bind to `0.0.0.0`

This is the direct, practical payoff of the distinction above, and it's
exactly why the capstone's Postgres install (Lesson 07) leaves Postgres
listening only on `127.0.0.1` (or, more precisely, only accepts local
Unix-socket connections) — QuestLog's FastAPI backend and PostgreSQL run
**on the same machine**, so the backend never needs to reach Postgres
over the *public* internet at all; it only ever needs `127.0.0.1`, the
"myself" address. Binding Postgres to `0.0.0.0` on a real VPS would mean
your database becomes reachable by anyone on the entire internet who
happens to try port `5432` against your server's public IP — combined
with `ufw` (Lesson 05) as a second layer of defense, but the *first* and
most important layer is simply: **never bind a service to a wider
address than the specific things that need to reach it actually
require.**

### Private vs. public IP addresses, revisited operationally

Module 02 already defined both terms (see `GLOSSARY.md`'s "Private IP
address" and "IP address" entries). The operationally important addition
here: **your own WSL2 instance, and even your entire home network, sits
behind a private IP address** — nothing on the open internet can
initiate a connection *to* it directly, which is exactly why Lesson 00
pointed out WSL2 can't be the target of a real capstone deploy. A real
VPS is specifically valuable *because* it's assigned a real **public**
IP address, permanently reachable from anywhere, which is the entire
service a VPS provider is selling you.

### NAT, briefly: why your home network doesn't need `ufw` the same way

**NAT (Network Address Translation)** is the mechanism your home
router uses to let every device in your house (your laptop, your phone,
a smart TV) share your single ISP-assigned public IP address, by
silently rewriting each outgoing packet's private address to the
router's shared public one, and routing each *reply* back to whichever
internal device actually asked for it, using a translation table the
router keeps in memory. The practical consequence: a device behind NAT
(your WSL2 instance, your laptop, your phone) is not directly reachable
by an unsolicited *inbound* connection from the internet at all by
default — someone out there cannot simply connect to your laptop the way
they could connect to a real VPS, because your router never forwards an
unrequested inbound packet to any specific internal device without being
explicitly told to (a manual "port forwarding" rule, a topic outside this
module's scope). This is *not* the same thing as a firewall (Lesson 05)
— NAT exists to solve IP address scarcity, and only incidentally provides
a rough, no-configuration-needed layer of protection as a side effect. A
real VPS has **no NAT** standing between it and the internet — its
public IP address really is directly reachable — which is exactly why
Lesson 05's `ufw` firewall is not optional there the way it might feel
unnecessary on your home laptop.

### Well-known ports vs. ephemeral ports

Port numbers 0–1023 are **well-known ports**, reserved by long-standing
convention for specific, common services — `22` (SSH), `80` (HTTP), `443`
(HTTPS), `5432` (PostgreSQL). This is convention, not a hard technical
requirement (nothing stops you from running a web server on port `8080`
instead), but it's why a browser typing `http://example.com` with no
port number defaults to trying `80`, and `https://example.com` defaults
to `443` — the browser fills in the well-known default for you.
**Ephemeral ports** (roughly 49152–65535, per IANA's registered range)
are temporary ports your **own** operating system picks automatically,
for a short time, whenever *your* machine initiates an outgoing
connection (e.g., your browser connecting out to a web server) — you'll
occasionally see these appear as the *source* port in `ss` or browser
dev-tools network output and can now recognize them for what they are,
rather than a confusing extra number.

## Common mistakes & gotchas

- **"My service is definitely running (`systemctl status` shows
  active), but I can't reach it from outside the server at all."**
  Overwhelmingly, either (a) it's bound to `127.0.0.1` instead of
  `0.0.0.0` (or, once Nginx enters the picture in Lesson 06, this is
  actually *correct*, and the real issue is elsewhere — see that
  lesson), or (b) `ufw` (Lesson 05) is blocking the port. Check both,
  with `ss -tlnp` for the bind address and `sudo ufw status` for the
  firewall, before assuming the application itself is broken.
- **Assuming `0.0.0.0` is "a real address that means nowhere" or "an
  error placeholder."** It is a completely real, meaningful *bind*
  instruction — "listen on every interface" — not a broken or null
  value. It is meaningless as a *destination* to connect *to* (you'd
  never `curl http://0.0.0.0:8000` from a different machine and expect
  it to mean anything sensible), which is exactly why it's confusing:
  its meaning depends entirely on whether it's used as a bind address or
  a destination address.
- **Confusing WSL2's own internal IP (from `hostname -I`) with your real
  home network's IP, or with a public internet address.** WSL2 runs
  inside a lightweight virtual machine with its own small private
  network, itself sitting behind your Windows host, itself typically
  sitting behind your home router's NAT — three layers of "private"
  address between your WSL2 shell and the actual public internet.
- **Exposing a database directly to `0.0.0.0` "to make it easier to
  connect from my own laptop while testing."** This is a real, common
  mistake with real consequences on an actual VPS — automated scanners
  constantly probe well-known database ports across the entire public
  IP space. The correct fix for "I want to reach my VPS's Postgres from
  my own laptop" is an SSH tunnel (a real technique, outside this
  module's scope but worth knowing exists) — never simply widening the
  bind address.

## How this connects

Lesson 05's `ufw` firewall is the second, independent layer of defense
on top of everything this lesson just covered — even a service correctly
bound to `127.0.0.1` only needs no firewall rule for it at all (nothing
outside the machine could reach it regardless), while anything correctly
bound to `0.0.0.0` for a real reason (Nginx itself, listening for public
traffic) is exactly what `ufw` needs to deliberately, explicitly allow.
Lesson 06 introduces Nginx specifically as the *one* process on a real
server that should bind `0.0.0.0` on the public-facing ports, while
everything else (QuestLog's own Uvicorn process, Postgres) stays on
`127.0.0.1`, reachable only from Nginx itself, on the same machine.

## Quick self-check

1. Why isn't a machine's IP address alone enough to say which specific program on it should receive a request?
2. What's the practical difference between a program bound to `127.0.0.1:8000` and one bound to `0.0.0.0:8000`, in terms of who can reach it?
3. Why should PostgreSQL, on a server where the only thing that needs to talk to it is a backend running on that same machine, never bind to `0.0.0.0`?
4. What does NAT actually solve, and why is it not the same thing as a firewall, even though it has a side effect that resembles one?
5. If a `systemd` service shows `Active: running` but nothing outside the server can reach it, what are the first two things (from this lesson and the next) you should check?
