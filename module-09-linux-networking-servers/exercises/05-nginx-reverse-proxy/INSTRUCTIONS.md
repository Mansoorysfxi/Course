# Exercise 05 — Nginx Reverse Proxy to a Local App (Independent)

**Concepts this exercise uses (all taught in
[`lessons/06-nginx-and-reverse-proxies.md`](../../lessons/06-nginx-and-reverse-proxies.md)):**
`location` blocks, `proxy_pass` (including the trailing-slash behavior
difference), `proxy_set_header`, `nginx -t`, `sites-available`/
`sites-enabled`, and `systemctl reload nginx`.

**Where to work:** your WSL2 Ubuntu shell (with Nginx installed —
`sudo apt install -y nginx`, per Lesson 06's Step 1, if you haven't
already). No real VPS required.

This is this module's most independent exercise before the capstone —
you're given a target behavior and the toy backend to test against, not
a config to fill in the blanks of.

## Setup

```bash
python3 exercises/05-nginx-reverse-proxy/starter/toy_backend.py
```
Leave it running. In another terminal, confirm it works directly:
```bash
curl http://127.0.0.1:5000/hello
```
**Expected:** `{"message": "toy_backend received this exact path:", "path_received": "/hello"}`.

## Your task

Write an Nginx site config, from scratch (referencing Lesson 06's
worked example as needed, but typing it yourself, not copy-pasting
directly) that satisfies **all** of the following:

1. Listens on port 80.
2. Any request to a path starting with `/service/` should be forwarded
   to `toy_backend` (port 5000) **with the `/service/` prefix stripped
   off** before it reaches the backend — meaning a request to
   `http://localhost/service/hello` should cause `toy_backend` to report
   `"path_received": "/hello"` (**not** `/service/hello`). This is the
   *opposite* of Lesson 06's own QuestLog example (which deliberately
   preserved the prefix) — you must deliberately choose the other form
   of `proxy_pass` this time, and be able to explain why it produces
   this result.
3. Any request **not** starting with `/service/` should return a plain
   `404` — you do not need to serve any real files for this exercise
   (no `root`/`try_files` needed here, unlike the capstone). Nginx's own
   inherited default behavior for an unmatched path depends on how your
   specific install's default `root` is configured, which makes it an
   unreliable way to guarantee a `404` on purpose — the more explicit,
   predictable approach is a catch-all `location` block that
   deliberately returns one.
4. Correctly forwards the real client IP to the backend using the
   headers Lesson 06 taught (you won't be able to see them in
   `toy_backend`'s current output, since it doesn't print headers — just
   include the correct `proxy_set_header` lines and be ready to explain
   what each does).

## Verify it yourself

```bash
sudo nginx -t
sudo systemctl reload nginx
curl http://localhost/service/hello
```
**Expected:** `"path_received": "/hello"` — proof the prefix was
stripped, on purpose, by your specific `proxy_pass` form.

```bash
curl -i http://localhost/service/quests/42
```
**Expected:** `"path_received": "/quests/42"`.

```bash
curl -i http://localhost/not-a-service-path
```
**Expected:** `404` from Nginx itself (no matching `location` block, and
no fallback — this is different from the capstone's SPA behavior on
purpose).

## Acceptance criteria

- [ ] `curl http://localhost/service/hello` shows `toy_backend` received
      exactly `/hello`, not `/service/hello`.
- [ ] `curl -i http://localhost/anything-else` returns a real `404`.
- [ ] You can explain, precisely, which single character (or its
      absence) in your `proxy_pass` line is responsible for the prefix
      being stripped — and what the *other* form would have produced
      for the exact same incoming request.
- [ ] `nginx -t` passes before you ever reload.
- [ ] You can name, and explain the purpose of, each `proxy_set_header`
      line you included.

## Hints

<details>
<summary>Hint 1</summary>

Lesson 06's Step 3 showed both forms of `proxy_pass` side by side —
form (A), with no path after the host:port, versus form (B), with a
trailing `/`. This exercise deliberately wants the *stripping* behavior,
which is the opposite of what QuestLog's own real config needed.

</details>

<details>
<summary>Hint 2</summary>

If `/service/hello` is reaching `toy_backend` as `/service/hello`
instead of `/hello`, you've used the form that preserves the full path.
Compare your `proxy_pass` line's exact characters against Lesson 06's
Step 3 example one more time.

</details>

<details>
<summary>Hint 3</summary>

For the `404` on unmatched paths, an explicit
`location / { return 404; }` block is the simplest, most predictable
way to guarantee this — Nginx's `return` directive immediately sends
the given status code with no further processing, no proxying, and no
dependence on any `root`/file-serving configuration at all.

</details>
