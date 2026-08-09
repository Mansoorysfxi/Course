# extract_quest.py -- Exercise 03 reference solution.
# Learner: try the exercise yourself first -- see INSTRUCTIONS.md.

import json
from typing import Literal

import anthropic
from pydantic import BaseModel


class ExtractedQuest(BaseModel):
    title: str
    description: str
    priority: Literal["low", "medium", "high"]
    quest_line: str


SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "priority": {"type": "string", "enum": ["low", "medium", "high"]},
        "quest_line": {"type": "string"},
    },
    "required": ["title", "description", "priority", "quest_line"],
    "additionalProperties": False,
}

MESSY_INPUT = (
    "so basically there's this old lighthouse keeper on the coast who "
    "hasn't sent his weekly signal in like three weeks and people are "
    "getting worried, someone should probably go check on him, it's not "
    "urgent-urgent but it shouldn't wait forever either, this'd go under "
    "our coastal errands stuff"
)

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=300,
    system=(
        "Extract a well-formed quest from the player's messy, informal "
        "description. Write a short, clear title and a one-sentence "
        "description in your own words. Judge the priority from the "
        "tone of the request. Infer a sensible quest_line name from any "
        "grouping the player mentions."
    ),
    output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
    messages=[{"role": "user", "content": MESSY_INPUT}],
)

text = response.content[0].text
print("--- Raw response text ---")
print(text)

data = json.loads(text)
quest = ExtractedQuest.model_validate(data)

print("\n--- Validated ExtractedQuest ---")
print(f"Title:       {quest.title}")
print(f"Description: {quest.description}")
print(f"Priority:    {quest.priority}")
print(f"Quest line:  {quest.quest_line}")
print(f"\npriority is one of low/medium/high: {quest.priority in ('low', 'medium', 'high')}")
