# Lesson 00 — Setup: What This Module Needs (Short, On Purpose)

## What you'll learn

- Why this module needs almost no new installation.
- How to confirm `curl` — which you already have — is working.
- What a REST client is, why one is genuinely convenient (but optional), and
  how to install the one this course recommends.
- How to verify everything before moving on.

## Why this matters

Rule 8 of this course says every module must front-load whatever setup it
needs before teaching material that depends on it. Module 02 is unusual:
**it needs almost nothing new.** You already installed Git for Windows in
Module 00, and Git for Windows quietly gave you a fully working `curl`
alongside it. This lesson exists to (a) prove that to you with a real
command, and (b) offer one small, optional convenience tool. It is
deliberately short — padding it with unnecessary steps would waste your
time and contradict the same rule it's satisfying.

## Prerequisites

Module 00 complete: Git for Windows installed, Git Bash working. That's it.

## The concept, explained simply

Two tools matter in this module:

1. **`curl`** — a command-line program for making HTTP requests (the same
   kind of request your browser makes when you visit a website, but with no
   browser, no graphics, and full visibility into exactly what was sent and
   received). "curl" stands for "Client URL" — it's a **client** program (a
   concept Lesson 05 defines fully) whose only job is to speak HTTP to
   servers and show you the result. You will use it in every remaining
   lesson in this module.
2. **A REST client** (optional) — a tool that makes it more convenient to
   build, save, and re-run HTTP requests than typing long `curl` commands
   every time. Think of it as the difference between running a game from a
   raw command-line launch versus double-clicking a saved shortcut with
   your preferred launch options remembered — same underlying action, less
   retyping. Every lesson in this module works with `curl` alone; the REST
   client is a convenience you can adopt later if you like it.

## The details

### Step 1 — Confirm `curl` is already installed

Open Git Bash and run:

```bash
curl --version
```

**Expected output** (your exact version/date will differ, and that's
fine — the point is that real version text prints instead of an error):

```
curl 8.16.0 (x86_64-pc-win32) libcurl/8.16.0 Schannel zlib/1.3.1 ...
Release-Date: 2026-xx-xx
Protocols: dict file ftp ftps ...http https...
Features: alt-svc AsynchDNS ... SSL ...
```

Where did this come from? You never ran a "curl installer." Git for
Windows bundles `curl` as part of its own toolset (it's stored inside
`C:\Program Files\Git\mingw64\bin\`, a folder that Module 00's Git
installer already added to your `PATH` — recall from
[Module 00, Lesson 01](../../module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md)
that `PATH` is the list of folders your shell searches to find a program
matching a typed command). This is exactly why Module 00 told you not to
assume a tool "just appears" — it appears because something specific put it
on `PATH`, and now you've confirmed what that something was.

If you get `bash: curl: command not found`, see Troubleshooting below.

### Step 2 (optional) — Install a REST client: VS Code's "REST Client" extension

You do not need this to complete any lesson or exercise in this module —
every example uses plain `curl`. It's offered because, once you're firing
off more than two or three requests, being able to save a request in a
file, tweak one line, and re-run it with a keyboard shortcut is genuinely
nicer than retyping a long `curl` command or scrolling your shell history.

Verified for this lesson (August 2026): the recommended tool is the **REST
Client** extension for VS Code, published by Huachao Mao (extension ID
`humao.rest-client`). It was chosen over alternatives (Thunder Client,
Insomnia, Bruno, Postman) specifically because:

- It's completely free with no usage caps, no account, and no login —
  Thunder Client's free tier is capped (30 requests) since it moved to a
  paid model; Insomnia and Postman both push you toward an account.
- It works directly inside VS Code, which you already have installed and
  are already comfortable navigating from Module 00.
- Requests are just plain-text `.http` files you write and save — no
  proprietary format, no separate database of saved requests. A `.http`
  file can be committed to a Git repo right next to your code, which fits
  everything you already learned about version control in Module 00.

To install it:

1. Open VS Code.
2. Click the Extensions icon in the left sidebar (or press `Ctrl+Shift+X`).
3. Search for `REST Client`.
4. Install the one published by **Huachao Mao** (`humao.rest-client`) — it
   will typically be the top result and has by far the most installs.
5. No further configuration is needed.

To use it: create any file ending in `.http` (e.g. `scratch.http`), type a
request like `GET https://pokeapi.co/api/v2/pokemon/pikachu`, and a small
"Send Request" link appears above the line — click it (or use the keyboard
shortcut shown) and a response pane opens beside your file. This module's
lessons stick to `curl` in the main text (since it works identically for
every reader, with no extension version differences to account for), but
feel free to follow along in `.http` files instead if you install this.

## Verify your setup

Run this exact command:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://pokeapi.co/api/v2/pokemon/pikachu
```

**Expected output:**

```
200
```

**What this proves, and what each piece means (you'll learn all of this
properly starting in Lesson 02 — for now, just confirm the number
matches):** `-s` (silent — hide progress info), `-o /dev/null` (throw away
the actual response body, we don't care about it yet), `-w "%{http_code}\n"`
(after the request finishes, print the numeric status code it got back,
followed by a newline). `200` is the status code meaning "successful" —
Lesson 03 explains status codes in full. If you see `200`, three things are
simultaneously true and working: your internet connection, `curl` itself,
and a live server on the other end. That's everything this module's
lessons will lean on.

**Try it yourself:** run the same command against a different PokeAPI
path, `https://pokeapi.co/api/v2/pokemon/not-a-real-pokemon`. Predict,
before running it, whether you'll see `200` again. (You should see `404`
— a real, different status code, proving `-w "%{http_code}\n"` is
genuinely reporting whatever the server said, not a hardcoded success
value. Lesson 03 explains exactly what `404` means and why.)

If you installed the REST client, open a new `scratch.http` file, type:

```
GET https://pokeapi.co/api/v2/pokemon/pikachu
```

and click "Send Request." **Expected:** a response pane opens showing
`HTTP/1.1 200 OK` at the top and a large JSON body below it.

## Common mistakes & gotchas

- **`curl: command not found`.** This means either Git for Windows wasn't
  actually installed correctly (unlikely if Module 00's checks passed), or
  you're in a terminal that isn't Git Bash and doesn't have the same
  `PATH`. Fix: close every terminal window and reopen Git Bash specifically
  (not PowerShell/cmd — this course uses Git Bash throughout, per Module
  00). If it's still missing, rerun Module 00's setup verification steps
  first — something upstream of this module needs fixing, not this lesson.
- **`curl: (6) Could not resolve host`.** This is a real DNS failure (you'll
  understand exactly what that means after Lesson 01) — check your internet
  connection, or that you didn't typo the domain name.
- **`curl: (60) SSL certificate problem`.** Rare on a normal setup; usually
  caused by corporate network security software intercepting HTTPS traffic.
  If you hit this on a work/school machine, note it and move on — it's an
  environment issue, not a concept you're missing.
- **No "Send Request" link appears above a line in a `.http` file.** Confirm
  the file's extension is literally `.http` (not `.http.txt`) and that the
  extension installed correctly (check the Extensions sidebar — it should
  show as installed, not just downloading).

## How this connects

Every lesson from here on gives you an exact `curl` command and exact
expected output, the same way Lesson 00 in Module 00 and Module 01 did for
their respective tools. Lesson 01 starts one layer *before* `curl` even
sends anything — how your computer turns a domain name into an address it
can actually connect to.

## Quick self-check

1. Where does the `curl` on your machine actually live, and which earlier
   module's installer put it there?
2. Name one concrete reason the REST Client extension was chosen here over
   Thunder Client or Postman for this course.
3. In the verification command, what does `-o /dev/null` do, and why didn't
   we just let the body print to the screen?
