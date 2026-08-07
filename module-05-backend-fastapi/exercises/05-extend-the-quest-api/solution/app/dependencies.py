from fastapi import HTTPException, status

from app import store
from app.models import Quest


def get_quest_or_404(quest_id: str) -> Quest:
    quest = store.get_quest(quest_id)
    if quest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No quest with id '{quest_id}'")
    return quest


def require_quests_in_line(quest_line: str) -> list[Quest]:
    """New for exercise 05. Follows the exact get_quest_or_404 pattern
    (Lesson 04), just keyed by quest_line instead of quest_id, and
    returning a list instead of a single item."""
    quests = store.quests_in_line(quest_line)
    if not quests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No quests found in quest line '{quest_line}'",
        )
    return quests
