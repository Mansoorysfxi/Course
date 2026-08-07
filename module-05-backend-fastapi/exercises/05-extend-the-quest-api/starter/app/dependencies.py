"""get_quest_or_404 is already complete -- do not modify it. Add your own
new dependency (e.g. require_quests_in_line) below it, per INSTRUCTIONS.md
and lessons/04-dependency-injection-and-depends.md.
"""

from fastapi import HTTPException, status

from app import store
from app.models import Quest


def get_quest_or_404(quest_id: str) -> Quest:
    quest = store.get_quest(quest_id)
    if quest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No quest with id '{quest_id}'")
    return quest


# TODO: add a dependency here for exercise 05's complete-line feature --
# something like `require_quests_in_line(quest_line: str) -> list[Quest]`
# that raises a 404 if no quest currently has that exact quest line.
