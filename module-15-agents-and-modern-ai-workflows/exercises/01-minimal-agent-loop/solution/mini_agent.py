"""Exercise 01 -- Minimal Agent Loop -- reference solution."""

import random
from types import SimpleNamespace

TOOLS = [
    {
        "name": "convert_units",
        "description": "Convert a numeric value between km and miles.",
        "input_schema": {
            "type": "object",
            "properties": {
                "value": {"type": "number"},
                "from_unit": {"type": "string", "enum": ["km", "miles"]},
                "to_unit": {"type": "string", "enum": ["km", "miles"]},
            },
            "required": ["value", "from_unit", "to_unit"],
        },
    },
    {
        "name": "roll_dice",
        "description": "Roll a number of dice with a given number of sides each.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sides": {"type": "integer"},
                "count": {"type": "integer"},
            },
            "required": ["sides", "count"],
        },
    },
]

KM_PER_MILE = 1 / 0.621371


def run_tool(name: str, tool_input: dict) -> str:
    if name == "convert_units":
        value = tool_input["value"]
        from_unit = tool_input["from_unit"]
        to_unit = tool_input["to_unit"]
        if from_unit == to_unit:
            return f"{value} {from_unit} is {value} {to_unit}."
        if from_unit == "km" and to_unit == "miles":
            converted = value * 0.621371
        elif from_unit == "miles" and to_unit == "km":
            converted = value * KM_PER_MILE
        else:
            return f"Error: unsupported conversion from '{from_unit}' to '{to_unit}'."
        return f"{value} {from_unit} is {converted:.2f} {to_unit}."

    if name == "roll_dice":
        sides = tool_input["sides"]
        count = tool_input["count"]
        # Answer to the exercise's own written question: count=0 sensibly
        # returns an empty roll, not an error -- there's nothing invalid
        # about asking for zero dice, so this returns a clear "no dice
        # rolled" message rather than raising.
        if count <= 0:
            return "Rolled: [] (no dice requested)"
        rolls = [random.randint(1, sides) for _ in range(count)]
        return f"Rolled: {rolls}"

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


# ---- A scripted fake client ----
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

    fake2 = FakeClient(
        turns=[
            final(
                [tool_use_block("t2", "roll_dice", {"sides": 20, "count": 2})],
                stop_reason="tool_use",
            ),
            final([text_block("You rolled two d20s.")], stop_reason="end_turn"),
        ]
    )
    print("\nFinal answer:", run_agent(fake2, "Roll two 20-sided dice."))

# Written answer (Step 5): count=0 sensibly returns an empty list of
# results, not an error -- "roll zero dice" is a valid, if unusual,
# request, and the implementation above returns "Rolled: [] (no dice
# requested)" rather than raising an exception for it.
