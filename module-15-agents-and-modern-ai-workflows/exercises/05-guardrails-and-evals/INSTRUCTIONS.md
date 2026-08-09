# Exercise 05 — Guardrails and Evals

**Difficulty:** Independent. This exercise gives you far less scaffolding
than the earlier ones — you're combining everything from Lessons 02, 06,
and 08 into one agent, the same way QuestLog's own capstone combines all
of it for real.

## What you'll build

A standalone Python script, `bank_agent.py`, modeling a tiny banking
assistant with one safe tool (`check_balance`) and one genuinely risky
one (`transfer_money`) — plus a real, deterministic eval that checks the
agent's own tool-call trajectory, not just its final answer.

## Concepts this exercise requires (taught in Lessons 02, 06, and 08)

- The agent loop itself (Lesson 02).
- Human-in-the-loop: pausing before a flagged tool and requiring
  approval (Lesson 06).
- A hard iteration cap, and a deterministic, trajectory-level eval
  (Lesson 08).

## Instructions

1. Open `starter/bank_agent.py`. It has `ACCOUNTS` (a small, hard-coded
   dict of account balances), and the loop's overall shape, with several
   `# TODO`s.
2. Implement two tools:
   - `check_balance(account: str) -> str` — safe, no confirmation needed.
   - `transfer_money(from_account: str, to_account: str, amount: float) -> str`
     — genuinely changes both accounts' balances. Flag this one in a
     `SENSITIVE_TOOLS` set, the same pattern Lesson 06's own
     human-in-the-loop example used.
3. Implement the human-in-the-loop gate: before `transfer_money` actually
   runs, call an `approve_fn(name, tool_input)` function (passed into
   `run_agent`) and only execute the transfer if it returns `True`. A
   denial should return a clear, recoverable `is_error` tool result, the
   same as Lesson 06's own example — never a raised exception.
4. Add a real guardrail: `transfer_money` must reject (return an error
   tool result, not execute) any transfer where `amount <= 0` or where
   `from_account` doesn't have enough balance — **enforced in the tool's
   own code**, never left to the system prompt or the model's own good
   judgment (Lesson 08's own "a guardrail has to live in code" point).
5. Write **two** deterministic evals, each a plain Python function with
   `assert` statements (no LLM judge, per Lesson 08):
   - `eval_denied_transfer_does_not_change_balances()` — scripts a fake
     conversation where a transfer is attempted and denied, then asserts
     both accounts' balances are unchanged afterward.
   - `eval_approved_transfer_moves_the_right_amount()` — scripts an
     approved transfer and asserts the exact right amount moved between
     the exact right two accounts.
6. Run both evals and confirm they pass. Then, deliberately break your
   own `transfer_money` implementation (e.g., comment out the
   insufficient-balance check) and confirm your evals **catch** the
   regression — this is the entire point of writing a real eval: it
   should fail loudly when the guardrail it's checking stops working.
   Put your `transfer_money` implementation back correctly before you're
   done.

## Acceptance criteria

- `transfer_money` is gated behind `approve_fn`, and a denial leaves both
  accounts' balances completely unchanged.
- `transfer_money` rejects a non-positive amount and an over-balance
  transfer, in its own code, regardless of what `approve_fn` says.
- Both evals pass against your correct implementation.
- You can describe, from having actually done it, what happened when you
  deliberately broke the balance check and reran your evals (a comment
  describing this is enough — you don't need to leave the broken code in).

## Hints

- **Level 1:** Re-read Lesson 06's own human-in-the-loop example and
  Lesson 08's own trajectory-eval example side by side — this exercise
  is those two patterns, combined, applied to a new domain.
- **Level 2:** `transfer_money`'s own balance/amount checks should happen
  **before** you even consider calling `approve_fn` — an invalid transfer
  should never reach a human for approval at all; it should be rejected
  outright.
- **Level 3:** For the "did the regression get caught" step, comment out
  just the `if ACCOUNTS[from_account] < amount:` check (or equivalent),
  rerun `eval_approved_transfer_moves_the_right_amount` with an amount
  larger than the account's balance, and watch it still succeed
  incorrectly — that's the guardrail's own absence, made visible by a
  failing (or wrongly-passing) eval.

## Running it

```bash
cd module-15-agents-and-modern-ai-workflows/exercises/05-guardrails-and-evals/starter
python bank_agent.py
```

**Expected output shape:** both evals print `PASS` with the values they
checked, after the script's own worked conversation examples run and
print their own tool-call traces.
