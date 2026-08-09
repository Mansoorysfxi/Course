# hello_questlog.py -- Exercise 01 reference solution.
# Learner: try the exercise yourself first -- see INSTRUCTIONS.md.

import anthropic

client = anthropic.Anthropic()

SYSTEM_PROMPT = (
    "You are QuestLog's onboarding assistant. Keep every answer to two "
    "sentences or fewer."
)

messages = [
    {
        "role": "user",
        "content": "I'm new to QuestLog. What's a quest line, and how is it different from a single quest?",
    }
]

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=150,
    system=SYSTEM_PROMPT,
    messages=messages,
)

print("--- First response ---")
print(response.content[0].text)
print(f"Stop reason: {response.stop_reason}")
print(f"Input tokens: {response.usage.input_tokens}")
print(f"Output tokens: {response.usage.output_tokens}")

# The assistant's own reply must be appended before the next call, or the
# follow-up question below has nothing to be "a follow-up" to.
messages.append({"role": "assistant", "content": response.content[0].text})
messages.append({"role": "user", "content": "Give me one example."})

second_response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=150,
    system=SYSTEM_PROMPT,
    messages=messages,
)

print("\n--- Second response (follow-up) ---")
print(second_response.content[0].text)
print(f"Stop reason: {second_response.stop_reason}")
print(f"Input tokens: {second_response.usage.input_tokens}")
print(f"Output tokens: {second_response.usage.output_tokens}")
