# hello_questlog.py -- Exercise 01 starter
#
# Fill in each TODO. See INSTRUCTIONS.md for the exact requirements, and
# Lesson 01 (lessons/01-calling-the-anthropic-api.md) for every piece of
# syntax you need -- this exercise doesn't require anything beyond what
# that lesson already showed you.

import anthropic

client = anthropic.Anthropic()

messages = []

# TODO 1: Append a user message asking the onboarding question from
# INSTRUCTIONS.md to `messages`.

# TODO 2: Call client.messages.create(...) with model="claude-haiku-4-5",
# max_tokens=150, the system prompt described in INSTRUCTIONS.md, and
# messages=messages.

# TODO 3: Print the response text, stop_reason, and usage (input_tokens
# and output_tokens).

# TODO 4: Append the assistant's reply to `messages` -- don't skip this,
# or the second request won't know what it's following up on.

# TODO 5: Append a second user message: "Give me one example."

# TODO 6: Call the API again with the now-longer `messages` list, and
# print the second response's text.
