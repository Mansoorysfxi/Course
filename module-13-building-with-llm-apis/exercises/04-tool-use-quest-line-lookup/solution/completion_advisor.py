# completion_advisor.py -- Exercise 04 reference solution.
# Learner: try the exercise yourself first -- see INSTRUCTIONS.md.

import anthropic

client = anthropic.Anthropic()

GET_COMPLETION_RATE_TOOL = {
    "name": "get_quest_line_completion_rate",
    "description": (
        "Returns the fraction of quests marked done in a given quest "
        "line, as a number between 0.0 and 1.0. Call this once per quest "
        "line you need to compare before making a recommendation."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "quest_line": {"type": "string", "description": "The exact quest line name."},
        },
        "required": ["quest_line"],
    },
}

FAKE_COMPLETION_RATES = {
    "Main Story": 0.8,
    "Side Quests": 0.25,
    "Village Errands": 0.5,
}


def get_quest_line_completion_rate(quest_line: str) -> float:
    return FAKE_COMPLETION_RATES.get(quest_line, 0.0)


messages = [
    {
        "role": "user",
        "content": (
            "I have three quest lines: Main Story, Side Quests, and "
            "Village Errands. Which one most needs my attention, and why?"
        ),
    }
]

MAX_ITERATIONS = 5
final_response = None

for iteration in range(MAX_ITERATIONS):
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=400,
        tools=[GET_COMPLETION_RATE_TOOL],
        messages=messages,
    )

    if response.stop_reason != "tool_use":
        final_response = response
        break

    messages.append({"role": "assistant", "content": response.content})

    # This turn may contain MORE THAN ONE tool_use block -- collect every
    # one before sending anything back, and send them all together in a
    # single user message.
    asked_this_turn = []
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            quest_line = block.input["quest_line"]
            asked_this_turn.append(quest_line)
            rate = get_quest_line_completion_rate(quest_line)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(rate),
                }
            )

    print(f"Iteration {iteration + 1}: model asked about {asked_this_turn}")
    messages.append({"role": "user", "content": tool_results})
else:
    print(f"Gave up after {MAX_ITERATIONS} iterations without a final answer.")

if final_response is not None:
    print("\n--- Final answer ---")
    print(final_response.content[0].text)
