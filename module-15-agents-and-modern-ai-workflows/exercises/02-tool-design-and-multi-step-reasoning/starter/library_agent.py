"""Exercise 02 -- Tool Design and Multi-Step Reasoning.

Starts with ONE deliberately bad, overloaded tool (manage_book). Your
job: replace it with two well-designed, narrow tools (find_book,
checkout_book), and script a conversation that chains them.
"""

from types import SimpleNamespace

BOOKS = {
    "b1": {"title": "Dune", "available": True},
    "b2": {"title": "Foundation", "available": False},
}

# ---- The bad design you're replacing. Delete this once your two new
# tools below fully replace it. ----
BAD_TOOLS = [
    {
        "name": "manage_book",
        "description": "Manages books.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string"},
                "title": {"type": "string"},
            },
            "required": ["action", "title"],
        },
    },
]

# TODO: replace BAD_TOOLS with TOOLS -- a list containing two
# well-designed tool definitions, find_book and checkout_book, per
# INSTRUCTIONS.md.
TOOLS = BAD_TOOLS


def run_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """TODO: implement find_book and checkout_book.

    Returns (content, is_error) -- the same shape this module's own
    QuestLog capstone uses for its own tool results (see app/agent.py).
    """
    return f"Error: unknown tool '{name}'", True


MAX_ITERATIONS = 5


def run_agent(client, user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    for iteration in range(1, MAX_ITERATIONS + 1):
        response = client.messages.create(
            model="claude-haiku-4-5", max_tokens=512, tools=TOOLS, messages=messages
        )
        print(f"-- iteration {iteration}: stop_reason={response.stop_reason}")

        if response.stop_reason != "tool_use":
            return next(b.text for b in response.content if b.type == "text")

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"   tool call: {block.name}({block.input})")
                content, is_error = run_tool(block.name, block.input)
                print(f"   tool result: {content} (is_error={is_error})")
                result = {"type": "tool_result", "tool_use_id": block.id, "content": content}
                if is_error:
                    result["is_error"] = True
                tool_results.append(result)
        messages.append({"role": "user", "content": tool_results})

    return "Gave up after too many steps."


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
    # TODO: script a fake conversation here where the user asks to check
    # out "Dune" by title only -- this should take two tool calls:
    # find_book("Dune") to get its book_id, then checkout_book(book_id).
    pass
