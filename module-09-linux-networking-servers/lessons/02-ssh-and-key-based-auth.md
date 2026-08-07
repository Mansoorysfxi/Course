# Lesson 02 — SSH and Key-Based Authentication

**Verified against (August 2026), via live web search:** current
consensus (checked against multiple current security-focused sources,
including guidance reflecting OpenSSH's own defaults) is that **Ed25519**
is the recommended key algorithm for new SSH keys — OpenSSH's own
`ssh-keygen` has defaulted to generating Ed25519 keys (instead of RSA)
since OpenSSH version 9.5, released October 2023. RSA (specifically
4096-bit) remains an acceptable fallback **only** for the shrinking set
of legacy servers/hardware that don't yet support Ed25519 — not a
recommendation for new keys in the general case. This is a change worth
stating explicitly: older tutorials (and older AI training data) often
still show `ssh-keygen -t rsa` as the default example; that is dated
guidance as of this writing, not current best practice.

## What you'll learn

- What SSH actually is, and what problem it solves.
- What a **public/private key pair** is, in enough mechanical detail to
  explain *why* it's more secure than a password — not just "it is."
  This builds directly on Module 07's asymmetric-algorithm material
  (JWTs signed with `RS256`), applied to a different problem (logging
  into a machine, instead of signing a token).
- How to generate a real Ed25519 key pair with `ssh-keygen`.
- How an SSH server decides whether to accept a connection: the
  `authorized_keys` file, exactly.
- How to connect to a remote machine with `ssh`, and why disabling
  password login entirely is standard practice on any real server.

## Why this matters

Every single interaction with a real VPS in this module — copying files
onto it, running commands on it, restarting a crashed service on it —
happens over SSH. If you rent a real VPS for the capstone, SSH (with a
key, never a password) is the *only* way you'll ever touch it. Getting
this genuinely right, and understanding *why* it works the way it does,
is non-negotiable before Lessons 07–08.

## Prerequisites

- `lessons/00-setup.md` — a confirmed working `ssh -V` in PowerShell.
- `lessons/01-linux-processes-and-permissions.md` — this lesson's
  troubleshooting section leans directly on `chmod` and file ownership.
- Module 07's asymmetric-algorithm material
  (`module-07-auth-security/lessons/04-jwt-structure-in-depth.md`) is
  useful background but not required — this lesson re-explains the
  public/private key idea from scratch in a new context.

## The concept, explained simply

A password proves identity by being a **shared secret**: both you and
the server know the same string, and the server accepts you because you
recited it correctly. The problem: that exact string travels over the
network (even if encrypted in transit) and is stored, in some form, on
the server too — anyone who ever intercepts it or steals the server's
password database can now pretend to be you, forever, until you change
it everywhere it was used.

SSH's key-based login uses a completely different trick, based on
**asymmetric cryptography** — the same underlying idea Module 07 used
for `RS256`-signed JWTs, just aimed at a different job. You generate a
mathematically linked **pair** of keys: a **private key** you keep
secret, forever, on your own machine, and a **public key** that is safe
to hand out to anyone or anything — you can post it publicly and lose
nothing, because knowing the public key does not let you derive the
private one. You give the *public* key to the server (via a file called
`authorized_keys`); you keep the *private* key on your own laptop, and
guard it exactly like a password. To log in, your SSH client uses the
private key to prove, mathematically, that it possesses the matching
private half of a public key the server already trusts — **without ever
transmitting the private key itself over the network, at all, ever.**
Even if someone captured every byte of every SSH login you ever made,
they still could not derive your private key from it, and without it
they cannot log in as you. This is the single biggest practical
advantage over a password: **the secret that actually matters never
leaves your machine.**

Think of it like an Unreal Engine online subsystem's ticket/token
handshake versus just typing a shared password into a lobby: a shared
password sent over the wire (even encrypted) is one leak away from being
replayable by whoever captured it; a proper handshake proves "I hold the
matching credential" without ever actually transmitting that credential.

## The details

### Step 1 — Generate a real Ed25519 key pair

In your WSL2 Ubuntu shell (or PowerShell — Windows' built-in `ssh-keygen`
works identically; this lesson uses WSL2 for consistency with the rest
of the module):

```bash
ssh-keygen -t ed25519 -C "youremail@example.com"
```

**Line by line:** `-t ed25519` picks the key **type/algorithm** — the
current recommended default, per this lesson's header. `-C "..."` adds a
**comment** (typically an email or a label) embedded in the public key
file purely for your own future reference — it has zero effect on how
the key functions, it's just a readable label so that, a year from now,
looking at a list of public keys you've handed out to various servers,
you can tell which one is which.

**Expected interactive prompts:**
```
Generating public/private ed25519 key pair.
Enter file in which to save the key (/home/yourname/.ssh/id_ed25519):
```
Press **Enter** to accept the default location (`~/.ssh/id_ed25519`) —
there's no reason to change it unless you're deliberately managing
multiple distinct key pairs (a scenario this lesson doesn't need).

```
Enter passphrase (empty for no passphrase):
```
This is a **second** layer of protection, separate from the key pair
itself: if set, your *private* key file is encrypted at rest, and using
it requires typing this passphrase too — so even if someone stole the
private key *file* itself off your disk, it would be useless to them
without also knowing this passphrase. For following along with this
module, pressing Enter twice (no passphrase) is acceptable and keeps
later commands simpler; for a key you'll actually keep and use beyond
this course, setting a real passphrase is the safer, recommended choice.

**Expected final output:**
```
Your identification has been saved in /home/yourname/.ssh/id_ed25519
Your public key has been saved in /home/yourname/.ssh/id_ed25519.pub
The key fingerprint is:
SHA256:AbCdEf... youremail@example.com
The key's randomart image is:
+--[ED25519 256]--+
| ...             |
+----[SHA256]-----+
```

You now have **two files**: `~/.ssh/id_ed25519` (private — never share
this, ever) and `~/.ssh/id_ed25519.pub` (public — safe to share). Confirm
both exist and check the private key's permissions:

```bash
ls -l ~/.ssh/id_ed25519 ~/.ssh/id_ed25519.pub
```

**Expected:**
```
-rw------- 1 yourname yourname 411 Aug  7 10:15 /home/yourname/.ssh/id_ed25519
-rw-r--r-- 1 yourname yourname  98 Aug  7 10:15 /home/yourname/.ssh/id_ed25519.pub
```

Notice the private key is `600` (`rw-------`, Lesson 01's numeric
notation — owner read/write, nobody else anything) — `ssh-keygen` sets
this automatically, and it matters: OpenSSH's client will flatly refuse
to use a private key file that's readable by anyone but its owner,
specifically *because* a private key with loose permissions defeats the
entire point of keeping it private.

### Step 2 — Look at both files (this is genuinely safe to do)

```bash
cat ~/.ssh/id_ed25519.pub
```
**Expected:** one line, e.g.
`ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBc3...restofkey... youremail@example.com`
— this is exactly what you paste into a VPS provider's "SSH key" field
during signup, or append to a server's `authorized_keys` file (next
step). Posting this exact line publicly (a GitHub profile, a forum post)
is completely safe — it's the *public* half, deliberately meant to be
shareable.

**Do not** `cat` the private key and paste it anywhere. There's no
legitimate reason to ever need to; this lesson mentions it only so you
understand exactly what "never share the private key" refers to as a
concrete file, not an abstract warning.

### Step 3 — How a server decides to trust your public key: `authorized_keys`

Every user account on a Linux machine that accepts SSH logins has (or
can have) a file at `~/.ssh/authorized_keys` — a plain text file, **one
public key per line**. When you attempt to connect, the SSH server reads
that specific user's `authorized_keys` file and checks whether any line
in it matches the public key your client is presenting proof of holding
the private half of. If yes, and the cryptographic proof checks out, you're
in — no password ever asked. If a VPS provider's signup flow let you
paste a public key when creating the server, this exact file (in the
server's `root` or default user's home directory) is where that provider
put it, automatically, on your behalf, at first boot.

**Try it yourself (no real remote server needed):** WSL2 Ubuntu ships an
SSH client but not a running SSH *server* by default — install one to
practice against a completely safe, local target (your own WSL2
instance):

```bash
sudo apt update
sudo apt install -y openssh-server
sudo service ssh start
```

**Expected:** `* Starting OpenBSD Secure Shell server sshd` with an
`[ OK ]` (or similar) — the `ssh` daemon (a **daemon** is a process that
runs continuously in the background, waiting to handle requests, rather
than doing one thing and exiting — Lesson 03 formalizes this term) is now
listening for connections. Now add your own freshly generated public key
to your own `authorized_keys` (yes, connecting to yourself — this
proves the exact mechanism without any real server involved):

```bash
mkdir -p ~/.ssh
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

**Line by line:** `mkdir -p ~/.ssh` creates the folder if it doesn't
already exist (`-p`: don't error if it's already there). `>>` (Module
00's append-redirect) adds your public key as a new line onto
`authorized_keys` without erasing anything already in it. The two
`chmod` lines matter exactly as much as the private key's own
permissions did: OpenSSH's server also refuses to trust an
`authorized_keys` file (or its containing `.ssh` folder) that's writable
by anyone but its owner — because if anyone else could edit that file,
they could simply add *their own* public key and log in as you.

Now connect to yourself over real SSH:

```bash
ssh yourname@localhost
```

**Expected:** a `The authenticity of host 'localhost' can't be
established...` warning the **first time only** (explained below), then,
after typing `yes`, you land at a normal shell prompt — logged in with
**no password prompt at all**, because your key was accepted.

### Step 4 — That "authenticity of host" warning, explained

The first time you connect to any given server, SSH shows something
like:
```
The authenticity of host 'localhost (127.0.0.1)' can't be established.
ED25519 key fingerprint is SHA256:xyz...
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```
This is SSH protecting you from a **different** problem than the one key
pairs solve: it's asking "are you sure this is really the server you
meant to connect to, and not an impostor pretending to be it?" (a
**man-in-the-middle** scenario). Answering `yes` records that server's
own public key fingerprint into `~/.ssh/known_hosts` on your machine —
from then on, if you ever connect to that same address and get back a
*different* fingerprint, SSH refuses to connect at all and warns loudly,
because that's exactly what it would look like if someone were
intercepting the connection. This is why, in the real capstone, if you
ever destroy a VPS and create a fresh one reusing the same IP address,
your very next connection attempt will show a scary
`WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!` error — that's SSH
correctly noticing the fingerprint changed, not a real attack; the fix
(only when you're certain it's your own fresh server) is removing the
old line from `known_hosts` as the error message itself tells you how.

### Step 5 — Disabling password login (why real servers do this)

On a real VPS, once you've confirmed key-based login works, the standard
practice is to **disable password authentication entirely** in the SSH
server's own config, `/etc/ssh/sshd_config`:

```bash
sudo nano /etc/ssh/sshd_config
```

Find (or add) these two lines, making sure neither is commented out with
a leading `#`:

```
PasswordAuthentication no
PubkeyAuthentication yes
```

Save, then restart the SSH daemon to apply the change:

```bash
sudo systemctl restart ssh
```

(This is your first real `systemctl` command — Lesson 03 explains
exactly what it's doing; for now, it's simply "make the SSH server
re-read its config file.") **Why this matters on a real internet-facing
server, specifically:** the moment a VPS is created, its public IP is
immediately reachable by literally anyone on the internet, and automated
bots constantly scan the entire internet's IP space trying default
usernames and common passwords against port 22 (SSH's default port —
Lesson 04) within minutes of a new server appearing. `PasswordAuthentication no`
makes every single one of those attempts fail instantly and
automatically, regardless of how weak or strong any password would have
been, because there's no password to guess in the first place — only a
private key that never left your own laptop could ever succeed.

**Do this on WSL2 now to practice, but be careful on a real VPS:**
confirm key-based login *works* (Step 3) **before** disabling passwords
— if you disable password auth and your key login is somehow broken,
you can lock yourself out entirely. On WSL2 this is low-stakes (you can
always re-enable it, or just re-run Step 3's setup); on a real VPS,
most providers offer a "web console" fallback specifically for this
scenario. The capstone (Lesson 07) walks through this exact sequence
again, in order, on a real server.

## Common mistakes & gotchas

- **`Permission denied (publickey)`.** The single most common SSH error.
  Almost always one of: (a) the public key was never actually added to
  the target's `authorized_keys`, (b) `authorized_keys` or `.ssh` has
  permissions looser than `600`/`700` and the server is silently
  refusing to trust it (check with `ls -l ~/.ssh` on the *server* side),
  or (c) you're pointing `ssh` at the wrong username or the wrong private
  key file.
- **"It worked yesterday, now it says the host key changed and refuses
  to connect."** Covered above — you (or your provider) rebuilt the
  server at the same IP address. Remove the stale line from
  `~/.ssh/known_hosts` (the error message tells you the exact line
  number) only once you're sure it's genuinely your own server, not an
  actual attack.
- **Setting `PasswordAuthentication no` and then immediately closing your
  only working SSH session, only to discover the key login was
  misconfigured all along.** Always keep your current, working SSH
  session **open** while testing a fresh connection in a second window
  after any `sshd_config` change — if the new connection fails, you can
  fix it from the still-open original session instead of being locked
  out.
- **Pasting the *private* key (`id_ed25519`, no `.pub`) into a provider's
  "public key" field.** This doesn't work usefully and, worse, exposes
  your private key by uploading it somewhere. Always double-check you're
  copying the file ending in `.pub`.
- **Generating a brand new key pair for every single server** and losing
  track of which key goes where. It's completely normal, and often
  cleaner, to reuse the *same* key pair across multiple servers you
  personally control — the public key is safe to place in as many
  `authorized_keys` files as you like; only the still-single private key
  needs guarding.

## How this connects

Lesson 03's `systemd` services will be managed over exactly this kind of
SSH session, on a real server. Lesson 07 (the capstone) starts with
exactly this lesson's Steps 1, 3, and 5, performed for real against a
freshly created VPS instead of practiced against `localhost` — nothing
about the mechanism changes, only the target.

## Quick self-check

1. What specifically travels over the network when you log in with a password, versus when you log in with an SSH key pair — and why does that difference matter if someone is eavesdropping on the connection?
2. Which file, and on which side (yours or the server's), controls whether a given public key is trusted?
3. Why does OpenSSH refuse to use a private key file, or an `authorized_keys` file, if its permissions are too loose?
4. What is the "authenticity of host... can't be established" warning actually protecting against, and is it related to the public/private key pair mechanism or a separate concern?
5. Why is disabling password authentication considered standard practice on an internet-facing server, specifically (not just "more secure" in the abstract)?
