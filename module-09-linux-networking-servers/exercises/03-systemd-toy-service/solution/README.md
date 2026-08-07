# Exercise 03 — Reference Solution

One valid unit file is in `flaky-server.service` (replace
`/home/yourname/exercise-03/flaky_server.py` with your own real path —
`whoami` and `pwd` to confirm yours). This is **one** correct answer,
not the only one — for example, a different, still-correct solution
could use a longer `RestartSec` or add `StandardOutput=journal`
explicitly (already the default, so redundant but not wrong).

## Installing it

```bash
sudo cp flaky-server.service /etc/systemd/system/flaky-server.service
sudo systemctl daemon-reload
sudo systemctl enable --now flaky-server
```

## Expected behavior

```bash
journalctl -u flaky-server --no-pager
```
should show a repeating pattern like:
```
... flaky_server starting (will crash after 7 beats)
... heartbeat #1
... heartbeat #2
...
... heartbeat #7
... Simulated crash!
... flaky-server.service: Main process exited, code=exited, status=1/FAILURE
... flaky-server.service: Scheduled restart job, restart counter is at 1.
... flaky_server starting (will crash after 5 beats)
...
```

`sudo systemctl status flaky-server` at any point shows
`Active: active (running)`, and its `Main PID` changes each time you
check shortly after a crash — direct proof `Restart=on-failure` is doing
its job with zero manual intervention.

## The design-decision part, answered

- **A deliberate `sudo systemctl stop flaky-server`:** does **not**
  trigger a restart, regardless of whether `Restart=` is `on-failure` or
  `always`. `systemd` tracks a `stop` request as an intentional,
  requested shutdown, distinct from the process dying unexpectedly —
  `Restart=` only ever governs the *unexpected* case. This is exactly
  what Lesson 03 states in its explanation of `Restart=on-failure`.
- **A clean exit (`sys.exit(0)`)** is where `on-failure` and `always`
  genuinely diverge: `Restart=on-failure` only restarts on a *non-zero*
  exit code or a signal — a clean, successful (`0`) exit is treated as
  "this program finished its job on purpose," and is left alone.
  `Restart=always` restarts the process **regardless of exit code**,
  including a clean `0` exit — meaning a service configured with
  `Restart=always` would immediately relaunch even a script that exited
  perfectly successfully on its own. This is why `on-failure` is
  generally the better default for a genuinely long-running server
  process (like QuestLog's Uvicorn) that should only ever exit
  unexpectedly, never on purpose while the machine is still up.
