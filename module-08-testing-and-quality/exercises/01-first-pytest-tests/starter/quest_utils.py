"""Small, pure, dependency-free functions to practice testing on -- no
database, no HTTP, no fixtures needed at all. See
lessons/02-pytest-fundamentals-and-fixtures.md before starting this
exercise; every concept this file's tests need is taught there.
"""

from typing import Literal

Priority = Literal["low", "medium", "high"]
VALID_PRIORITIES: tuple[Priority, ...] = ("low", "medium", "high")


def is_valid_priority(value: str) -> bool:
    """Returns True if `value` is exactly one of the three allowed
    priorities, False otherwise. Case-sensitive on purpose -- "High" is
    not the same string as "high"."""
    return value in VALID_PRIORITIES


def priority_weight(priority: Priority) -> int:
    """Lower number = more urgent, matching the frontend's own
    PRIORITY_WEIGHT convention (frontend/src/pages/QuestListPage.tsx)."""
    weights: dict[Priority, int] = {"high": 0, "medium": 1, "low": 2}
    return weights[priority]


def format_quest_title(title: str) -> str:
    """Trims surrounding whitespace and capitalizes the first letter.
    Raises ValueError if, after trimming, nothing is left -- an empty
    quest title is never allowed."""
    trimmed = title.strip()
    if not trimmed:
        raise ValueError("Quest title cannot be empty.")
    return trimmed[0].upper() + trimmed[1:]


def count_completed(done_flags: list[bool]) -> int:
    """How many quests in this list are marked done."""
    return sum(1 for done in done_flags if done)
