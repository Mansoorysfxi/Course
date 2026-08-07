# Lesson 01 — Networks, IP Addresses, and DNS

## What you'll learn

- What a "network" actually is, in concrete terms — not the buzzword.
- What the Internet literally is (a network of networks) and how that's
  different from "the Web."
- What an IP address is, what it's for, and the difference between a
  public and a private one.
- What a port is, and why an IP address alone isn't enough to reach a
  specific program.
- What DNS is and exactly what happens, step by step, when your computer
  turns a name like `pokeapi.co` into an address it can actually use.
- What `localhost` / `127.0.0.1` means, since you'll see it constantly
  starting in Module 05.

## Why this matters

Every single thing you'll build for the rest of this course — a React app
talking to a FastAPI backend, that backend talking to a database, an AI
agent calling a tool over the network — ultimately reduces to two programs
on possibly-different machines finding each other and exchanging bytes.
This lesson is the "finding each other" half. Skip it and every later
error message involving `ECONNREFUSED`, `localhost:8000`, or "why won't my
frontend reach my backend" becomes a guess instead of a diagnosis.

## Prerequisites

Module 00's shell lesson (you'll run a couple of simple commands in Git
Bash). No networking knowledge is assumed — this lesson starts from
literally nothing.

## The concept, explained simply

Think about LAN multiplayer in a game engine you already know well.
Before any gameplay data flows, two things have to happen: one machine has
to be running as the **host** (listening for connections), and every other
machine has to know **which physical machine, on the network, to connect
to** — its address — and there has to be **a way for machines to reach each
other at all** (the network connecting them, whether that's a home Wi-Fi
router or the public Internet). Only once "which machine" and "how do
packets get there" are solved does any gameplay data get exchanged.

Everything in this lesson is that same problem, generalized: how does any
one computer find and reach any other computer, anywhere, given nothing
but a name typed into a browser? We'll build this up in the exact order
the pieces actually get used.

## The details

### What a network is

A **network**, in the computing sense, is just two or more devices
connected in a way that lets them send data to each other. The absolute
simplest possible network is two computers connected by a single cable.
Your home Wi-Fi is a slightly bigger network: your laptop, phone, and
router are all connected (wirelessly), and the router is the one device
that also connects onward to your Internet Service Provider (ISP).

Data on a network travels in **packets** — small chunks of data, each
carrying a bit of the actual content plus addressing information (where
it's from, where it's going), the way a shipped parcel carries both goods
and a shipping label. A large file or web page gets broken into many
packets, sent separately (possibly over different physical paths), and
reassembled at the destination. You don't need to manipulate packets by
hand in this course, but knowing they exist explains why networks can
survive a single bad connection: if one packet gets lost or corrupted, only
that packet needs to be re-sent, not the entire page.

### The Internet is a network of networks

Your home network connects to your ISP's network. Your ISP's network
connects to other, bigger networks. Those connect to still others. **The
Internet is literally just this: an enormous, interconnected mesh of
individually-owned networks, all agreeing to use the same addressing and
routing rules so that data can hop from any one of them to any other.**
Nobody "owns" the Internet as a whole — it's a cooperative agreement
between the owners of all these individual networks to pass each other's
traffic along.

**"The Internet" and "the Web" are not the same thing** — a very common
beginner mix-up. The Internet is the underlying global network described
above. The **Web** (short for World Wide Web) is one particular *use* of
that network: HTML pages, linked to each other, fetched over the HTTP
protocol (Lessons 02–04 cover HTTP in depth). Email, online multiplayer
game traffic, and video calls all also run over the Internet, but none of
them are "the Web." Every web request in this course travels over the
Internet, but not everything travelling over the Internet is a web
request.

### IP addresses — how a machine gets found

For a packet to reach the right machine, every device on a network needs a
unique numeric address, the same way every house on a street needs a
unique street address for mail to arrive correctly. This is an **IP
address** (IP = Internet Protocol — the specific set of addressing/routing
rules the whole Internet agrees to use).

The most common form you'll see (called **IPv4**) looks like this:

```
104.26.14.6
```

Four numbers, each from 0–255, separated by dots — this is why it's called
a "dotted quad." (There's a newer format, **IPv6**, which looks like
`2606:4700:20::681a:e06`, created because IPv4 only has about 4.3 billion
possible addresses total, and the world ran out of new ones to hand out
years ago. You don't need to work with IPv6 directly in this course, but
you'll occasionally see it appear in tool output — recognize the colon-heavy
format and know it's "the newer kind of IP address," nothing more.)

**Public vs. private IP addresses.** Not every IP address is reachable from
the whole Internet. Certain address ranges (like anything starting
`192.168.`, `10.`, or `172.16.`–`172.31.`) are reserved as **private** —
they're only meaningful *inside* one local network, like your home Wi-Fi.
Your laptop's private IP address on your home network might be
`192.168.1.42`; your router then has one **public** IP address (assigned by
your ISP) that represents your entire home network to the outside
Internet, and it privately translates traffic between the two (a process
called NAT — Network Address Translation — which you don't need to
implement, just recognize by name if you see it mentioned). This is exactly
why, in an old-school LAN party, "connect to 192.168.1.42" worked fine
between machines in the same room, but that same address would mean
nothing if you tried to connect to it from a friend's house on a different
network — it's only valid *inside* that one local network.

**`localhost` and `127.0.0.1`.** Every computer also has a special address
that always means "myself," regardless of network: `127.0.0.1`, almost
always referred to by its friendly name, `localhost`. When you start a
backend server on your own machine in Module 05 and visit
`http://localhost:8000`, you're telling your own computer to talk to a
program running on itself — no network, router, or ISP involved at all.
You'll live at this address constantly for the rest of the course during
local development, so it's worth fixing firmly now: **`localhost` never
leaves your machine.**

Try this now, in Git Bash:

```bash
ping -n 4 pokeapi.co
```

**Expected output (roughly):**

```
Pinging pokeapi.co [104.26.14.6] with 32 bytes of data:
Reply from 104.26.14.6: bytes=32 time=14ms TTL=57
Reply from 104.26.14.6: bytes=32 time=13ms TTL=57
Reply from 104.26.14.6: bytes=32 time=14ms TTL=57
Reply from 104.26.14.6: bytes=32 time=13ms TTL=57

Ping statistics for 104.26.14.6:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
```

**Line by line:** `ping` sends a tiny packet to a target and measures how
long a reply takes to come back (`time=14ms`) — it's the simplest possible
"is anything out there, and how far away is it" tool, the network
equivalent of shouting into a canyon and timing the echo. `-n 4` tells
Windows' `ping` to send exactly 4 packets and stop (without a limit it
would ping forever until you press `Ctrl+C`). Notice the very first line:
you typed a *name* (`pokeapi.co`), but `ping` immediately shows you a
*number* in brackets — `[104.26.14.6]`. That number-from-a-name step is
DNS, and it's the next thing this lesson explains. `TTL=57` ("Time To
Live") is a packet-hop counter that decrements every network it passes
through, mainly there to guarantee lost packets eventually get discarded
instead of looping forever — you don't need to manage it yourself.

**Try it yourself:** run `ping -n 2 localhost` and compare the address it
shows in brackets to the one you just got for `pokeapi.co`. (You should see
`127.0.0.1` and a `time` of `<1ms` — because "the network" it's traveling
over is your own machine talking to itself, there's effectively no
distance to cover.)

### Ports — reaching a specific program, not just a machine

An IP address gets a packet to the right *machine*. But a single machine
can run many network programs at once — maybe a game server, a chat
client, and a web browser, all simultaneously. An IP address alone doesn't
say *which* of those programs should receive the data. That's what a
**port** is for: a number (0–65535) that identifies a specific "door" on a
machine that one particular program is listening at.

An address plus a port together (written `IP:PORT`, e.g. `104.26.14.6:443`)
fully specifies "this exact machine, and this exact program running on it."
Certain ports are reserved by convention for specific well-known purposes —
port `80` for plain HTTP, port `443` for HTTPS (HTTP secured with TLS,
covered fully in Lesson 02). This is why you've never had to type a port
number into a browser for ordinary websites: `https://pokeapi.co` silently
means "port 443," because that's HTTPS's universally agreed default. When
you start your own backend server in Module 05 at `localhost:8000`, `8000`
is that server's chosen port — nothing reserved about it, just a common
convention among developers for "a backend I'm running myself, not a real
public website."

If you've ever hosted a private multiplayer session and had to "port
forward" on your router to let friends outside your house connect in, this
is the exact same concept: you were telling your router "traffic arriving
on port such-and-such should be handed to this specific game server
program running on this specific machine inside my home network."

### DNS — turning names into addresses

Nobody wants to memorize `104.26.14.6` to visit a website, the same way you
don't memorize your friends' phone numbers by digit — you save a name and
let your phone look up the number. **DNS (Domain Name System)** is the
Internet's version of that contacts list: a distributed system whose whole
job is answering the question *"what IP address does this domain name
currently point to?"*

A **domain name** is the human-readable name itself — `pokeapi.co`,
`github.com`, `google.com`. It is not the same thing as a URL (Lesson 05
defines URLs fully) — the domain name is just one *part* of a URL.

Here is exactly what happens, step by step, the first time your computer
needs to resolve a domain name it hasn't looked up recently (this is the
very first stage of "what happens when you type a URL," which Lesson 02
assembles completely):

1. Your computer first checks its own **local cache** — did it already
   look this name up recently? If yes, it reuses that answer immediately
   and none of the following steps happen. (This is why the *second* time
   you `ping` or `curl` the same domain in a short session, it can feel
   instantaneous — DNS already answered once and the answer is cached for
   a while.)
2. If not cached, your computer asks a **DNS resolver** — typically run by
   your ISP, or a public one you've configured (like `1.1.1.1` or
   `8.8.8.8`) — "what's the address for `pokeapi.co`?"
3. If that resolver doesn't already know either, it asks a **root name
   server** (there are only a handful of these globally, and they're one
   of the oldest, most heavily-redundant parts of the entire Internet).
   The root server doesn't know the answer either, but it knows which
   server handles the domain's **TLD** (Top-Level Domain — the part after
   the last dot, like `.com`, `.co`, `.org`) and points the resolver there.
4. The **TLD name server** (for `.co` in this case) doesn't know the exact
   IP either, but it knows which server is *authoritative* for
   `pokeapi.co` specifically, and points the resolver there.
5. The **authoritative name server** for `pokeapi.co` is the one that
   actually holds the real answer — the current IP address(es) for that
   domain — and returns it.
6. The resolver hands that answer back to your computer, and **caches it**
   for a while (governed by a value called TTL, unrelated to the packet-hop
   TTL from `ping` above, but conceptually similar: "how long is this
   answer good for before you should ask again").
7. *Now*, and only now, your computer has an actual IP address, and can
   move on to Lesson 02's next step: opening an actual connection to it.

This multi-step lookup (steps 2–6) typically completes in well under a
second, and thanks to caching at every layer, it often doesn't happen at
all for domains you've recently visited.

Try this now:

```bash
nslookup pokeapi.co
```

**Expected output (roughly):**

```
Server:   your-router-or-isp-resolver
Address:  192.168.1.1

Non-authoritative answer:
Name:    pokeapi.co
Address:  104.26.14.6
```

**Line by line:** `nslookup` ("name server lookup") is a diagnostic tool
built into Windows (it works from Git Bash too, since Git Bash can call
regular Windows programs on your `PATH`) that performs *only* the DNS
lookup step, with nothing else — no actual connection is made to
`pokeapi.co` at all. The `Server`/`Address` at the top show *which
resolver you asked* (almost always your router or ISP, step 2 above) — not
the answer itself. The answer is below, under "Non-authoritative answer":
the domain name you asked about, and the IP address it currently maps to.
"Non-authoritative" here just means "this came from a resolver that cached
it, not from `pokeapi.co`'s own authoritative server directly" — which is
completely normal and expected.

**Try it yourself:** run `nslookup github.com` and `nslookup google.com`.
Notice you likely get back *multiple* IP addresses for one or both. Large
services intentionally answer DNS lookups with several different IPs
(often geographically distributed) so that traffic spreads across many
machines and a single server going down doesn't take the whole site with
it — a preview of load balancing, which Module 09 covers properly.

## Common mistakes & gotchas

- **Confusing "the Internet" with "the Web."** The Internet is the network;
  the Web is one thing that runs on top of it (HTTP + HTML). You'll build
  things that use the Internet without using "the Web" at all later in this
  course (e.g., raw API calls with no HTML in sight).
- **Assuming a domain's IP address never changes.** It absolutely can (and
  does, for large services, routinely) — this is exactly *why* DNS exists
  as an indirection layer instead of everyone just hardcoding IP addresses
  everywhere. If IPs never changed, DNS would be pointless.
- **Typing a private IP address (like `192.168.1.42`) expecting it to work
  from a different network.** It won't — private addresses are only
  meaningful inside the one local network they belong to, exactly like the
  LAN party example above.
- **Thinking `localhost` and your machine's real network IP address are
  interchangeable.** They usually behave similarly for local testing, but
  `localhost`/`127.0.0.1` never leaves your machine even in principle,
  while your machine's actual network IP could (with the right
  configuration) be reached by other devices on your network.
- **`nslookup` or `ping` hanging or failing entirely.** Usually a genuine
  connectivity issue (no internet, VPN misconfiguration, or a
  corporate/school network blocking these specific diagnostic tools
  outright, which some IT departments do deliberately) — try a different
  domain, then suspect your network before suspecting your command.

## How this connects

This lesson covered exactly the first, "find the machine" phase of "what
happens when you type a URL." Lesson 02 picks up **immediately** where this
one ends — you now have an IP address; next is actually opening a
connection to it (TCP), securing that connection (TLS), and sending the
first real HTTP request. Ports, introduced here almost in passing, become
directly relevant the moment you run your first backend server in Module
05 and need to explain why `localhost:8000` and `localhost:3000` are two
completely separate, non-conflicting programs running on the very same
machine.

## Quick self-check

1. In your own words, what's the difference between "the Internet" and
   "the Web"?
2. What problem does DNS solve, and what would you have to do every time
   you wanted to visit a website if DNS didn't exist?
3. Why doesn't a private IP address like `192.168.1.42` work if a friend on
   a different network tries to connect to it?
4. What's the difference between an IP address and a port, and why do you
   need both to reach a specific running program?
5. What does it mean that `nslookup`'s answer was "non-authoritative," and
   is that a problem?
