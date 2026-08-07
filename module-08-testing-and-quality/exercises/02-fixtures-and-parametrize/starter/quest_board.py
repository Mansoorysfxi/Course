"""An in-memory quest board -- no database, no HTTP. See
lessons/02-pytest-fundamentals-and-fixtures.md (fixtures) and
lessons/03-parametrize-and-mocking.md (parametrize) before starting this
exercise.
"""

from typing import Literal

Priority = Literal["low", "medium", "high"]


class Quest:
    def __init__(self, title: str, priority: Priority, done: bool = False) -> None:
        self.title = title
        self.priority = priority
        self.done = done


class QuestBoard:
    """Holds quests in memory, in the order they were added."""

    def __init__(self) -> None:
        self.quests: list[Quest] = []

    def add_quest(self, title: str, priority: Priority) -> Quest:
        quest = Quest(title=title, priority=priority)
        self.quests.append(quest)
        return quest

    def mark_done(self, title: str) -> None:
        """Marks the first quest with this exact title as done. Raises
        KeyError if no quest with that title exists."""
        for quest in self.quests:
            if quest.title == title:
                quest.done = True
                return
        raise KeyError(f"No quest titled {title!r} on this board.")

    def count_by_priority(self, priority: Priority) -> int:
        return sum(1 for quest in self.quests if quest.priority == priority)

    def all_done(self) -> bool:
        """True if every quest on the board is done. True (vacuously) for
        an empty board -- there is no quest that ISN'T done, because
        there are no quests at all."""
        return all(quest.done for quest in self.quests)
