# Exercise 02 — SSH Key-Based Login (Guided)

**Concepts this exercise uses (all taught in
[`lessons/02-ssh-and-key-based-auth.md`](../../lessons/02-ssh-and-key-based-auth.md)):**
generating an Ed25519 key pair, `authorized_keys`, file permission
requirements for `.ssh` and its contents, connecting with `ssh`, the
"authenticity of host" prompt, and disabling password authentication in
`sshd_config`.

**Where to work:** your WSL2 Ubuntu shell, connecting to itself (exactly
Lesson 02's own practice setup). No real VPS required.

This exercise is more guided than Exercise 01 — you'll follow a specific
sequence, but you're expected to diagnose and fix at least one
deliberately-introduced failure yourself along the way (Part C).

## Part A — Generate a key pair and connect to yourself

1. If you haven't already (from following along with Lesson 02),
   generate a fresh Ed25519 key pair. If you already have one from the
   lesson, that's fine to reuse here.
2. Install and start an SSH server inside WSL2, if not already running:
   `sudo apt install -y openssh-server && sudo service ssh start`.
3. Add your **public** key to your own `~/.ssh/authorized_keys`, with
   correct permissions on both the `.ssh` folder and the file itself.
4. Connect: `ssh yourusername@localhost`. Confirm you land in a shell
   with **no password prompt**.

## Part B — Prove it's really the key, not something else

1. Temporarily rename your private key file
   (`mv ~/.ssh/id_ed25519 ~/.ssh/id_ed25519.bak`) so SSH can't find it.
2. Try `ssh yourusername@localhost` again. What happens? Write down the
   exact behavior (does it fail outright, fall back to asking for a
   password, or something else?), and explain *why*, referencing what
   `PasswordAuthentication` is currently set to on this machine (it's
   still the default, `yes`, unless you already changed it).
3. Restore your key: `mv ~/.ssh/id_ed25519.bak ~/.ssh/id_ed25519`.
   Confirm `ssh yourusername@localhost` works again with no password.

## Part C — Diagnose a broken `authorized_keys` (deliberate failure)

1. Deliberately loosen your `.ssh` folder's permissions:
   `chmod 755 ~/.ssh`.
2. Try connecting again: `ssh yourusername@localhost`.
3. **This should now fail to use your key** (OpenSSH refuses to trust an
   `.ssh` folder with permissions that loose). Depending on your
   `PasswordAuthentication` setting from Part B, it will either fall
   back to a password prompt or fail outright.
4. Diagnose and fix it yourself, using Lesson 02's "Common mistakes &
   gotchas" section as your only reference (don't just copy the exact
   original `chmod` command from memory without understanding why it's
   `700` specifically) — restore the correct permission and confirm
   key-based login works again.

## Part D — Disable password authentication

1. Edit `/etc/ssh/sshd_config` and set `PasswordAuthentication no` and
   confirm `PubkeyAuthentication yes` is present and not commented out.
2. Restart the SSH service.
3. **Before closing your current session**, open a **second** terminal
   and confirm `ssh yourusername@localhost` still works with your key.
4. Now try to prove password auth is really off: temporarily rename your
   private key again (`mv ~/.ssh/id_ed25519{,.bak}`) and attempt
   `ssh yourusername@localhost` — it should now be refused outright with
   no password prompt offered at all, unlike Part B's behavior. Restore
   your key afterward.

## Acceptance criteria

- [ ] You can log in to `localhost` via SSH with zero password prompts.
- [ ] You can explain, in your own words, exactly what happened in Part
      B when the private key was temporarily missing, and why.
- [ ] You correctly diagnosed and fixed Part C's deliberately broken
      permissions **without being told the exact fix directly** — state
      what permission value you found broken and what you changed it to.
- [ ] After Part D, a missing private key results in an outright refusal
      with no password fallback — and you can explain why that's
      different from Part B's behavior.

## Hints

<details>
<summary>Hint 1 (Part C)</summary>

Re-read Lesson 02's gotcha about `Permission denied (publickey)` — it
names the exact three most common causes. One of the three matches this
exercise's deliberate setup precisely.

</details>

<details>
<summary>Hint 2 (Part C)</summary>

Run `ssh -v yourusername@localhost` (verbose mode) instead of a plain
`ssh` — it prints much more detail about *why* a key was rejected,
including a line explicitly mentioning permissions being too open.

</details>

<details>
<summary>Hint 3 (Part C)</summary>

The correct permission for the `.ssh` directory itself is `700`, not
`755` — re-check Lesson 02's Step 3 for exactly why `755` (group/other
read+execute) is considered "too loose" for SSH to trust.

</details>
