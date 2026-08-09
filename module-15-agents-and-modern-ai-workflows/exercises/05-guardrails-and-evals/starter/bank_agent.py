"""Exercise 05 -- Guardrails and Evals.

Combines Lesson 06 (human-in-the-loop) and Lesson 08 (guardrails +
deterministic evals) into one small agent.
"""

from types import SimpleNamespace

ACCOUNTS = {"checking": 500.0, "savings": 1200.0}

# TODO: mark transfer_money as sensitive here, per Lesson 06's own
# SENSITIVE_TOOLS pattern.
SENSITIVE_TOOLS: set[str] = set()

TOOLS = [
    {
        "name": "check_balance",
        "description": "Check the balance of one account.",
        "input_schema": {
            "type": "object",
            "properties": {"account": {"type": "string"}},
            "required": ["account"],
        },
    },
    {
        "name": "transfer_money",
        "description": "Transfer money from one account to another.",
        "input_schema": {
            "type": "object",
            "properties": {
                "from_account": {"type": "string"},
                "to_account": {"type": "string"},
                "amount": {"type": "number"},
            },
            "required": ["from_account", "to_account", "amount"],
        },
    },
]


def run_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """TODO: implement check_balance and transfer_money.

    transfer_money MUST reject (return an error, not execute) a
    non-positive amount or an insufficient balance -- enforced here, in
    code, regardless of what any human approval says.
    """
    return f"Error: unknown tool '{name}'", True


MAX_ITERATIONS = 5


def run_agent(client, user_message: str, approve_fn) -> tuple[str, list[str]]:
    """Returns (final_answer, tool_call_log) -- the log is what your
    evals below will assert against."""
    messages = [{"role": "user", "content": user_message}]
    tool_call_log = []
    for iteration in range(1, MAX_ITERATIONS + 1):
        response = client.messages.create(
            model="claude-haiku-4-5", max_tokens=512, tools=TOOLS, messages=messages
        )
        if response.stop_reason != "tool_use":
            return next(b.text for b in response.content if b.type == "text"), tool_call_log

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            tool_call_log.append(block.name)

            # TODO: if block.name is in SENSITIVE_TOOLS, call approve_fn
            # before running it, per Lesson 06's own pattern -- a denial
            # should produce an is_error tool result, not run the tool.

            content, is_error = run_tool(block.name, block.input)
            result = {"type": "tool_result", "tool_use_id": block.id, "content": content}
            if is_error:
                result["is_error"] = True
            tool_results.append(result)
        messages.append({"role": "user", "content": tool_results})

    return "Gave up after too many steps.", tool_call_log


# ---- Fake client helpers -- do not modify below this line ----
def text_block(text):
    return SimpleNamespace(type="text", text=text)


def tool_use_block(id_, name, input_):
    return SimpleNamespace(type="tool_use", id=id_, name=name, input=input_)


def final(content, stop_reason):
    return SimpleNamespace(content=content, stop_reason=stop_reason)


class FakeMessages:
    def __init__(self, turns):
        self._turns = iter(turns)

    def create(self, **kwargs):
        return next(self._turns)


class FakeClient:
    def __init__(self, turns):
        self.messages = FakeMessages(turns)


def eval_denied_transfer_does_not_change_balances():
    """TODO: script a fake conversation attempting a transfer, deny it
    via approve_fn, and assert both accounts' balances are unchanged."""
    raise NotImplementedError


def eval_approved_transfer_moves_the_right_amount():
    """TODO: script a fake conversation attempting a transfer, approve
    it, and assert the exact right amount moved between the exact right
    two accounts."""
    raise NotImplementedError


if __name__ == "__main__":
    eval_denied_transfer_does_not_change_balances()
    eval_approved_transfer_moves_the_right_amount()
