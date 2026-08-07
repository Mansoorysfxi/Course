# Exercise 04 — Configuring ufw for a Realistic Scenario (Independent)

**Concepts this exercise uses (all taught in
[`lessons/05-firewalls-with-ufw.md`](../../lessons/05-firewalls-with-ufw.md)
and
[`lessons/04-networking-ports-and-ips.md`](../../lessons/04-networking-ports-and-ips.md)):**
default-deny posture, app profiles, `ufw allow`/`deny`, numbered rules
and deletion, and the refused-vs-timeout distinction.

**Where to work:** your WSL2 Ubuntu shell. No real VPS required — `ufw`
inside WSL2 genuinely enforces its rules against WSL2's own network
stack, which is enough to observe every behavior this exercise asks
about, even though WSL2 itself isn't reachable from the public internet
(Lesson 00).

This exercise is intentionally less step-by-step than Exercises 01–03 —
you're given a scenario and a set of requirements, and you decide the
exact commands.

## Scenario

Imagine a (fictional) small internal tool running on a server that:

- Must be reachable over SSH, from anyone with a valid key (standard).
- Runs a web dashboard on port `8080` (not `80`) that should be reachable
  from the public internet.
- Runs an internal metrics endpoint on port `9090` that should **only**
  be reachable from one trusted internal monitoring box at IP address
  `10.0.5.20` — nowhere else, not even other machines on the same
  private network.
- Runs PostgreSQL on the standard port, which should **not** be
  reachable from outside this machine at all, under any circumstance.

## Your task

1. Starting from `ufw`'s default state (reset if you've been
   experimenting: `sudo ufw reset`, confirm with `y`), configure rules
   satisfying every bullet above. Restricting a rule to one specific
   source IP (needed for the port-`9090` requirement) was only shown in
   passing, in Lesson 05's "Common mistakes & gotchas" section — go back
   and find that exact command shape before writing your own, rather
   than guessing.
2. Enable `ufw` and confirm with `sudo ufw status numbered` that:
   - SSH is allowed from anywhere.
   - Port `8080` is allowed from anywhere.
   - Port `9090` is allowed **only** from `10.0.5.20`.
   - Port `5432` (Postgres) has **no** allow rule at all.
3. Explain, in your own words, why item 4 above needs **no rule at all**
   rather than an explicit `deny` rule — referencing `ufw`'s default
   policy.
4. Simulate the "internal-only" requirement locally: start a fake
   listener on port `9090` (`python3 -m http.server 9090` works fine for
   this — ignore that it's not really "metrics," it's just something to
   test connectivity against) and, from your own machine, try to reach
   it (`curl http://localhost:9090/` from WSL2 itself, and, if you can
   arrange it, from a genuinely different source than `10.0.5.20` — even
   testing that a *non-matching* source is blocked while a request from
   `localhost`/`127.0.0.1` itself is a reasonable, honest approximation
   here, since WSL2 can't literally simulate a second real IP).
5. Clean up: `sudo ufw reset` when finished (confirm with `y`).

## Acceptance criteria

- [ ] `ufw status numbered` output (paste it, or describe it exactly)
      shows exactly the four rule outcomes listed above — no more, no
      fewer.
- [ ] You can state the exact `ufw` command you used to restrict port
      `9090` to one source IP, and explain each part of it.
- [ ] You correctly explain why no `ufw deny` rule was needed for
      PostgreSQL's port.
- [ ] You can distinguish, from direct testing or from Lesson 05's
      explanation, what a client would see (refused vs. timed out) for a
      port blocked by `ufw` versus a port with no listener at all.

## Hints

<details>
<summary>Hint 1</summary>

Re-read Lesson 05's "Common mistakes & gotchas" section, specifically
the bullet about one service on a private network needing to reach
another — it shows the exact command shape you need here, just applied
to a different port and IP.

</details>

<details>
<summary>Hint 2</summary>

If you're not sure whether your port-8080 rule is actually reachable
from "anywhere" versus accidentally restricted, re-read the exact rule
you added with `sudo ufw status numbered` and check whether it says
`Anywhere` in the "From" column, versus a specific IP.

</details>

<details>
<summary>Hint 3</summary>

For step 3, this is directly restating Lesson 05's own explanation of
why QuestLog's real Postgres and backend ports needed no `ufw` rule at
all — the same reasoning applies here, just to a different scenario.

</details>
