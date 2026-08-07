"""A deliberately unreliable toy "server" for Exercise 03.

Prints a heartbeat every 2 seconds, like Lesson 03's heartbeat.py -- but
this one deliberately crashes (a real, unhandled exception, producing a
non-zero exit code) after a random number of beats, to simulate a real
application bug that only shows up after the process has been running
for a while. Your job (see INSTRUCTIONS.md) is to write a systemd unit
file that keeps this process running despite its own flakiness, and to
prove -- with real evidence from journalctl -- that it worked.

Do not "fix" this script so it stops crashing. The crash is the point:
a systemd unit file that correctly uses Restart=on-failure doesn't care
*why* a process died, only that it's supposed to be running and isn't.
"""

import random
import sys
import time

count = 0
crash_after = random.randint(5, 10)

print(f"flaky_server starting (will crash after {crash_after} beats)", flush=True)

while True:
    count += 1
    print(f"heartbeat #{count}", flush=True)
    if count >= crash_after:
        print("Simulated crash!", file=sys.stderr, flush=True)
        raise RuntimeError("flaky_server hit its scripted failure point")
    time.sleep(2)
