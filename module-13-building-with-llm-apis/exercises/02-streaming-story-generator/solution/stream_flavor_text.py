# stream_flavor_text.py -- Exercise 02 reference solution.
# Learner: try the exercise yourself first -- see INSTRUCTIONS.md.

import sys

import anthropic

client = anthropic.Anthropic()

quest_line = sys.argv[1] if len(sys.argv) > 1 else "Side Quests"

with client.messages.stream(
    model="claude-haiku-4-5",
    max_tokens=200,
    messages=[
        {
            "role": "user",
            "content": (
                f"Write a 3-4 sentence, evocative, in-universe description of what "
                f'the "{quest_line}" quest line in an RPG is generally about.'
            ),
        }
    ],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    print()  # a real newline once streaming is done

    final_message = stream.get_final_message()

print(f"\nStop reason: {final_message.stop_reason}")
print(f"Output tokens: {final_message.usage.output_tokens}")

if final_message.stop_reason == "max_tokens":
    print(
        "\nWARNING: the response was cut off before it finished -- "
        "raise max_tokens and try again."
    )
