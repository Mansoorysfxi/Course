# extract_quest.py -- Exercise 03 starter
#
# See INSTRUCTIONS.md for the full requirements, and Lesson 03
# (lessons/03-structured-outputs-with-pydantic.md) for every piece of
# syntax needed.

import json
from typing import Literal

import anthropic
from pydantic import BaseModel


# TODO 1: Define ExtractedQuest with fields: title (str), description
# (str), priority (Literal["low", "medium", "high"]), quest_line (str).
class ExtractedQuest(BaseModel):
    pass


# TODO 2: Define a raw JSON Schema dict matching ExtractedQuest's shape.
# Remember: every object needs "additionalProperties": False, and
# "priority" needs an "enum" of the three allowed values.
SCHEMA = {}

MESSY_INPUT = (
    "so basically there's this old lighthouse keeper on the coast who "
    "hasn't sent his weekly signal in like three weeks and people are "
    "getting worried, someone should probably go check on him, it's not "
    "urgent-urgent but it shouldn't wait forever either, this'd go under "
    "our coastal errands stuff"
)

client = anthropic.Anthropic()

# TODO 3: Call client.messages.create(...) with a system prompt
# instructing Claude to extract a structured quest, output_config set to
# SCHEMA, and MESSY_INPUT as the user message.

# TODO 4: json.loads() the response text, then
# ExtractedQuest.model_validate(...) it.

# TODO 5: Print every field, and a line confirming priority is one of
# the three allowed values.
