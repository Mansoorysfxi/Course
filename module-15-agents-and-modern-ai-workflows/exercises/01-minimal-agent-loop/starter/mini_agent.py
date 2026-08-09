"""Exercise 01 -- Minimal Agent Loop.

Fill in the two TODOs below: the tool definitions (TOOLS) and the
dispatcher that actually runs one (run_tool). The loop itself
(run_agent) is already complete -- it's the exact same shape Lesson 02
built, so you can focus entirely on the tools this time.
"""

from types import SimpleNamespace

# TODO: define TOOLS -- a list with two tool definitions:
#   1. "convert_units": value (number), from_unit (string), to_unit (string)
#   2. "roll_dice": sides (integer), count (integer)
TOOLS = []


def run_tool(name: str, tool_input: dict) -> str:
    """TODO: implement both tools.

    - "convert_units": support "km" -> "miles" and "miles" -> "km"
      (1 km = 0.621371 miles). Return a readable string, e.g.
      "5.0 km is 3.11 miles".
    - "roll_dice": roll `count` dice with `sides` sides each, return a
      readable string of the results, e.g. "Rolled: [4, 1, 6]".
    """
    return f"Error: unknown tool '{name}'"


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
                result = run_tool(block.name, block.input)
                print(f"   tool result: {result}")
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": result}
                )
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
    fake = FakeClient(
        turns=[
            final(
                [tool_use_block("t1", "convert_units", {"value": 5, "from_unit": "km", "to_unit": "miles"})],
                stop_reason="tool_use",
            ),
            final([text_block("5 km is about 3.11 miles.")], stop_reason="end_turn"),
        ]
    )
    print("\nFinal answer:", run_agent(fake, "How many miles is 5 km?"))
