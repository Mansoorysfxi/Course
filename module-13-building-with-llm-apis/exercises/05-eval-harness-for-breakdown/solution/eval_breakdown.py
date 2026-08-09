# eval_breakdown.py -- Exercise 05 reference solution.
# Learner: try the exercise yourself first -- see INSTRUCTIONS.md.
#
# Default (mocked) mode needs NO API key at all:
#   python eval_breakdown.py
#
# Live mode makes real, small API calls (needs ANTHROPIC_API_KEY set):
#   python eval_breakdown.py --live

import json
import sys
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

SCHEMA = {
    "type": "object",
    "properties": {
        "sub_quests": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"title": {"type": "string"}},
                "required": ["title"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["sub_quests"],
    "additionalProperties": False,
}


class SubQuest(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class QuestBreakdown(BaseModel):
    sub_quests: list[SubQuest] = Field(min_length=2, max_length=4)


def generate_breakdown(
    quest_title: str, quest_description: str, existing_titles: list[str]
) -> list[str]:
    """A plain, non-streamed, no-tool-use version of QuestLog's real
    quest-breakdown feature (Lesson 07 uses the streamed, tool-using
    version for the real app) -- a legitimate, simpler alternative for a
    standalone evaluation script like this one, per this exercise's own
    instructions. Only imported/called in --live mode, so the mocked run
    never needs the `anthropic` package to actually make a network call."""
    import anthropic  # local import: never needed at all in mocked mode

    client = anthropic.Anthropic()
    existing_note = (
        f" The player already has these quests -- do not suggest a duplicate: "
        f"{', '.join(existing_titles)}."
        if existing_titles
        else ""
    )

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        system=(
            "Break the given quest into 2-4 short (under 12 words), "
            "actionable sub-quests." + existing_note
        ),
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[
            {
                "role": "user",
                "content": f"Quest title: {quest_title}\nQuest description: {quest_description}",
            }
        ],
    )

    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined to generate a breakdown for this quest.")

    parsed = json.loads(response.content[0].text)
    result = QuestBreakdown.model_validate(parsed)
    return [sub_quest.title for sub_quest in result.sub_quests]


@dataclass
class GoldenCase:
    name: str
    quest_title: str
    quest_description: str
    existing_titles: list[str] = field(default_factory=list)


GOLDEN_SET = [
    GoldenCase(
        name="ordinary_quest",
        quest_title="Repair the village well",
        quest_description="The well's pulley mechanism broke and the rope is fraying.",
        existing_titles=["Deliver the Sealed Letter"],
    ),
    GoldenCase(
        name="quest_with_existing_near_duplicate",
        quest_title="Defeat the dragon guarding the old mine",
        quest_description="The dragon has been terrorizing the northern villages.",
        existing_titles=["Scout the mine entrance"],
    ),
    GoldenCase(
        name="vague_one_word_quest",
        quest_title="Investigate",
        quest_description="Something strange is happening in the old cemetery at night.",
        existing_titles=[],
    ),
]

# Hand-written, canned "as if this came back from Claude" results for the
# default, no-API-key mode -- one deliberately good per case, one
# deliberately bad, matching Lesson 06's own demonstration pattern.
CANNED_RESULTS: dict[str, list[str]] = {
    "ordinary_quest": [
        "Find a replacement rope at the general store",
        "Ask the blacksmith to fix the pulley",
    ],
    # Deliberately bad: duplicates an existing title, so this exercise's
    # own harness catches a real, visible failure -- not just always
    # passing.
    "quest_with_existing_near_duplicate": [
        "Scout the mine entrance",
        "Gather fire-resistant gear",
    ],
    "vague_one_word_quest": [
        "Interview the cemetery caretaker",
        "Search the newest graves for disturbances",
        "Return after dark to observe firsthand",
    ],
}


def check_result(case: GoldenCase, sub_quests: list[str]) -> list[str]:
    """General-purpose checks -- no reference to any specific golden
    case's own data, per this exercise's own acceptance criteria."""
    problems: list[str] = []

    if not (2 <= len(sub_quests) <= 4):
        problems.append(f"expected 2-4 sub-quests, got {len(sub_quests)}")

    existing_lower = {title.strip().lower() for title in case.existing_titles}
    for title in sub_quests:
        stripped = title.strip()
        if not stripped:
            problems.append("a sub-quest title was empty")
            continue
        if len(stripped.split()) > 12:
            problems.append(f"title too long ({len(stripped.split())} words): {stripped!r}")
        if stripped.lower() == case.quest_title.strip().lower():
            problems.append(f"sub-quest restates the whole quest verbatim: {stripped!r}")
        if stripped.lower() in existing_lower:
            problems.append(f"sub-quest duplicates an existing quest title: {stripped!r}")

    return problems


def run(live_mode: bool) -> int:
    total_problems = 0

    for case in GOLDEN_SET:
        if live_mode:
            try:
                sub_quests = generate_breakdown(
                    case.quest_title, case.quest_description, case.existing_titles
                )
            except Exception as exc:  # noqa: BLE001 -- eval harness: report, never crash
                print(f"[SKIPPED] {case.name}: {exc}")
                continue
        else:
            sub_quests = CANNED_RESULTS[case.name]

        try:
            problems = check_result(case, sub_quests)
        except ValidationError as exc:
            problems = [str(exc)]

        status = "PASS" if not problems else "FAIL"
        print(f"[{status}] {case.name}")
        for problem in problems:
            print(f"    - {problem}")
        total_problems += len(problems)

    print()
    mode_label = "live" if live_mode else "mocked"
    print(f"{len(GOLDEN_SET)} cases run ({mode_label} mode), {total_problems} problem(s) found.")
    return total_problems


if __name__ == "__main__":
    live_mode = "--live" in sys.argv
    problems_found = run(live_mode)
    sys.exit(1 if problems_found else 0)
