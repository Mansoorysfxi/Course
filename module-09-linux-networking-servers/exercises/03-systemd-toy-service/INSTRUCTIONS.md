# Exercise 03 — A Real systemd Service for a Flaky Program (Guided → Independent)

**Concepts this exercise uses (all taught in
[`lessons/03-systemd-and-services.md`](../../lessons/03-systemd-and-services.md)):**
unit file sections (`[Unit]`/`[Service]`/`[Install]`), `Type=simple`,
`ExecStart` with absolute paths, `Restart=`/`RestartSec=`,
`WantedBy=multi-user.target`, `daemon-reload`, `start`/`enable`/`status`,
and `journalctl -u`.

**Where to work:** your WSL2 Ubuntu shell (must have `systemd` enabled —
`lessons/00-setup.md`). No real VPS required.

## Setup

Copy `starter/flaky_server.py` to somewhere in your home directory, e.g.:
```bash
mkdir -p ~/exercise-03
cp starter/flaky_server.py ~/exercise-03/flaky_server.py
```
Read the script — note it deliberately crashes with a real, unhandled
exception after a random number of heartbeats. **Do not modify the
script to stop it crashing** — the crash is the exercise.

## Your task

1. Write a real `systemd` unit file, `flaky-server.service`, that runs
   this script and **automatically restarts it every time it crashes**,
   waiting 2 seconds between restart attempts.
2. Install it (the right directory, the right `daemon-reload` step),
   start it, and **enable** it so it would also survive a reboot.
3. Watch it crash and come back **on its own, with no manual `kill` or
   `restart` command from you** — since this script crashes by itself,
   unlike Lesson 03's toy example, which needed a manual `kill` to
   demonstrate the same thing. Prove this happened using `journalctl`,
   not just `systemctl status`'s current snapshot.
4. Using `journalctl -u flaky-server --no-pager`, find and record: how
   many times it restarted in a 2-minute observation window, and the
   exact log lines showing "Simulated crash!" and a subsequent fresh
   "flaky_server starting" line right after.
5. Stop and disable the service when you're done observing, and remove
   the unit file (cleanup, same as Lesson 03's own closing step).

## A design decision to make yourself (this is the "independent" part)

Lesson 03 used `Restart=on-failure`, and stated that `systemctl stop`
suppresses automatic restart regardless of which `Restart=` value you
chose. Before testing anything, write a short (2–4 sentence) prediction
of what happens in **two** separate scenarios:

1. You deliberately run `sudo systemctl stop flaky-server` while it's
   healthy and mid-heartbeat (not currently crashing).
2. `flaky_server.py` is changed so it exits **cleanly** (exit code `0`,
   e.g. via `sys.exit(0)`) after a fixed number of beats, instead of
   raising an exception.

Then actually test both, once with `Restart=on-failure` and once with
`Restart=always`, and record what you observed against your prediction.
Specifically: does `systemctl stop` ever get overridden by either
`Restart=` value? Does a *clean* exit (`0`) get restarted differently
than the script's normal crash (non-zero) depending on which `Restart=`
value is set?

## Acceptance criteria

- [ ] A unit file exists with correct `[Unit]`/`[Service]`/`[Install]`
      sections, an absolute-path `ExecStart`, `Restart=on-failure`, and
      a `RestartSec` of your choosing.
- [ ] `sudo systemctl status flaky-server` at some point shows
      `Active: active (running)` with a **different** `Main PID` than
      it had a few minutes earlier, with no manual intervention from you
      in between.
- [ ] `journalctl -u flaky-server` shows at least two full
      "starting → several heartbeats → Simulated crash! → starting
      again" cycles.
- [ ] You correctly predicted (or corrected your prediction after
      testing) that a deliberate `systemctl stop` is **not** overridden
      by either `Restart=` value.
- [ ] You correctly predicted (or corrected your prediction after
      testing) that `Restart=always` restarts the process even after a
      *clean* exit (code `0`), while `Restart=on-failure` does not.

## Hints

<details>
<summary>Hint 1</summary>

Find your Python interpreter's absolute path first:
`which python3` — you'll need it for `ExecStart`, since unit files
never expand `~` or rely on your shell's own `PATH`.

</details>

<details>
<summary>Hint 2</summary>

If `systemctl status` shows `Active: failed` immediately and it never
even prints one heartbeat, double check the path to `flaky_server.py`
itself in `ExecStart` — it must also be absolute, and it's a separate
mistake from getting the Python interpreter's path wrong.

</details>

<details>
<summary>Hint 3</summary>

Re-read Lesson 03's explanation of `Restart=on-failure` closely — it
already states, in passing, what `systemctl stop` does regardless of
which `Restart=` value is configured. The genuinely new thing to test
for yourself here is the *clean exit code `0`* scenario, which the
lesson's own toy example never actually exercised (its heartbeat script
never exits on its own at all).

</details>

See `solution/` only after you've genuinely attempted this yourself —
it contains one valid reference unit file and a short explanation, not
the only possible correct answer.
