"""Exercise 03 -- Memory and Planning.

run_agent below is complete and already takes a full `messages` list (not
just one new message) -- that's the right shape for what you're about to
build. Your job is the Conversation class, and two new tools.
"""

from types import SimpleNamespace

JOURNAL: list[str] = []

# TODO: add two tools here -- add_journal_entry(text) and plan(steps) --
# per INSTRUCTIONS.md.
TOOLS = []


def run_tool(name: str, tool_input: dict) -> str:
    """TODO: implement add_journal_entry and plan."""
    return f"Error: unknown tool '{name}'"


MAX_ITERATIONS = 5


def run_agent(client, messages: list[dict]) -> tuple[str, list[dict]]:
    """Runs the loop against the GIVEN messages list (already containing
    the full conversation so far, including the newest user turn), and
    returns (final_answer, updated_messages) -- the caller is responsible
    for keeping `updated_messages` around for the next call."""
    for iteration in range(1, MAX_ITERATIONS + 1):
        response = client.messages.create(
            model="claude-haiku-4-5", max_tokens=512, tools=TOOLS, messages=messages
        )
        print(f"-- iteration {iteration}: stop_reason={response.stop_reason}")

        if response.stop_reason != "tool_use":
            answer = next(b.text for b in response.content if b.type == "text")
            messages.append({"role": "assistant", "content": answer})
            return answer, messages

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"   tool call: {block.name}({block.input})")
                result = run_tool(block.name, block.input)
                print(f"   tool result: {result}")
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": result}
                )
        messages.append({"role": "user", "content": tool_results})

    return "Gave up after too many steps.", messages


# TODO: implement Conversation, per INSTRUCTIONS.md.
class Conversation:
    def __init__(self, client):
        pass

    def send(self, user_text: str) -> str:
        pass


# ---- A scripted fake client -- do not modify below this line ----
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


if __name__ == "__main__":
    # TODO: script a fake client with enough turns for TWO separate
    # conversation.send() calls, per INSTRUCTIONS.md's own Step 5.
    pass
