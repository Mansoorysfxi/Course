# Exercise 01 — Linux Processes and Permissions (Easy)

**Concepts this exercise uses (all taught in
[`lessons/01-linux-processes-and-permissions.md`](../../lessons/01-linux-processes-and-permissions.md)):**
processes and PIDs, `ps`/`top`, reading a permissions string, `chmod`
(both letter and numeric form), `chown`, `sudo`, and `apt`. If you can
answer this module's Lesson 01 self-check questions, you already have
everything you need — this exercise should be very hard to get wrong if
you read the lesson.

**Where to work:** your WSL2 Ubuntu shell (`lessons/00-setup.md`). No
real VPS needed for this exercise.

## Part A — Processes

1. Start a long-running "fake server" process in one terminal:
   ```bash
   sleep 300 &
   ```
   (the trailing `&` backgrounds it so your terminal stays free —
   Lesson 01's "Try it yourself" used this exact trick).
2. In the same or a different terminal, find this process's PID using
   `ps aux` piped to `grep`.
3. Write down the exact `ps aux` line for this process and, in your own
   words, explain every column in it (user, PID, state, command).
4. Stop it using `kill` and your PID from step 2 — **not** `Ctrl+C`,
   and **not** `kill -9`. Confirm it's gone with `ps aux | grep sleep`
   (it's fine if you still see the `grep` command itself matching its
   own search string — that's not the process you killed).

## Part B — Permissions

1. Create a new file called `secret-notes.txt` in your home directory
   with some placeholder text in it.
2. Using `ls -l`, write down its exact default permissions string and
   explain what each of the 10 characters means, for this specific file.
3. Change its permissions so that **only you** can read or write it —
   nobody else on the system, not even your own group — using the
   **numeric** (octal) form of `chmod`. Confirm with `ls -l`.
4. Create a second file, `shared-notes.txt`, and set its permissions so
   that you can read and write it, your group can read it, and everyone
   else has no access at all — again using numeric `chmod`. Write down
   the exact number you used and why.
5. Run `whoami` and then use `chown` to (redundantly, since you already
   own it) explicitly set `shared-notes.txt`'s owner and group to your
   own username. Confirm the command ran with no errors.

## Part C — Package manager

1. Check whether `tree` (a small utility that prints a directory as a
   visual tree) is already installed: `tree --version`.
2. If it's not installed, use `apt` to install it — remembering the two
   separate steps Lesson 01 taught (updating the package list, then
   installing).
3. Run `tree ~/systemd-practice` (or any directory of your choice) and
   confirm real output appears.

## Acceptance criteria

- [ ] You can state the PID of a process you started, and it changes
      between separate runs of the same command.
- [ ] `secret-notes.txt` shows `-rw-------` in `ls -l`.
- [ ] `shared-notes.txt` shows `-rw-r-----` in `ls -l`, and you can state
      the numeric `chmod` value you used (`640`) and why each digit is
      what it is.
- [ ] `chown` ran without a `Permission denied` or "no such user" error.
- [ ] `tree` runs successfully and you can explain, briefly, what `apt
      update` did versus what `apt install` did.

## Hints (use only if stuck 30+ minutes, per the root README's workflow)

<details>
<summary>Hint 1</summary>

For Part A step 4, `kill <PID>` with no flags sends `SIGTERM` — the
"polite" request Lesson 01 described. If the process is genuinely
ignoring it (it shouldn't for `sleep`), that itself is worth noticing
and asking about — it means `sleep` would have to be in an unusual,
uninterruptible state.

</details>

<details>
<summary>Hint 2</summary>

For the numeric `chmod` values: remember `r=4`, `w=2`, `x=1`, added per
digit, one digit per owner/group/others. `600` = owner gets `4+2=6`
(`rw-`), group and others get `0` (`---`) each.

</details>

<details>
<summary>Hint 3</summary>

If `apt install tree` fails with a message about not finding the
package, you likely skipped `sudo apt update` first, or it's been a
while since your WSL2 instance last ran it.

</details>
