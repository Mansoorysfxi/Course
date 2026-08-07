import pytest
from quest_board import QuestBoard


@pytest.fixture
def empty_board() -> QuestBoard:
    return QuestBoard()


@pytest.fixture
def stocked_board(empty_board: QuestBoard) -> QuestBoard:
    """Depends on `empty_board` -- fixtures can take other fixtures as
    their own parameters, exactly like a test can (see
    lessons/02-pytest-fundamentals-and-fixtures.md's "Common mistakes"
    section). A fresh board, with three quests of different priorities,
    none done yet."""
    empty_board.add_quest("Slay the Dragon", "high")
    empty_board.add_quest("Gather Herbs", "low")
    empty_board.add_quest("Deliver the Letter", "medium")
    return empty_board
