import pytest
from quest_board import QuestBoard


# --- using the `empty_board` fixture --------------------------------------


def test_new_board_has_no_quests(empty_board: QuestBoard):
    assert empty_board.quests == []


def test_empty_board_is_all_done(empty_board: QuestBoard):
    """Vacuous truth -- see QuestBoard.all_done's own docstring."""
    assert empty_board.all_done() is True


def test_adding_a_quest_returns_it(empty_board: QuestBoard):
    quest = empty_board.add_quest("Slay the Dragon", "high")
    assert quest.title == "Slay the Dragon"
    assert quest.priority == "high"
    assert quest.done is False


def test_mark_done_on_missing_quest_raises_key_error(empty_board: QuestBoard):
    with pytest.raises(KeyError):
        empty_board.mark_done("No Such Quest")


# --- using the `stocked_board` fixture (which itself uses empty_board) ---


def test_stocked_board_has_three_quests(stocked_board: QuestBoard):
    assert len(stocked_board.quests) == 3


def test_stocked_board_is_not_all_done(stocked_board: QuestBoard):
    assert stocked_board.all_done() is False


def test_marking_every_quest_done_makes_all_done_true(stocked_board: QuestBoard):
    stocked_board.mark_done("Slay the Dragon")
    stocked_board.mark_done("Gather Herbs")
    stocked_board.mark_done("Deliver the Letter")
    assert stocked_board.all_done() is True


def test_marking_one_quest_done_does_not_affect_the_others(stocked_board: QuestBoard):
    stocked_board.mark_done("Slay the Dragon")

    dragon = next(q for q in stocked_board.quests if q.title == "Slay the Dragon")
    herbs = next(q for q in stocked_board.quests if q.title == "Gather Herbs")

    assert dragon.done is True
    assert herbs.done is False


# --- parametrize: the same check, run once per priority ------------------


@pytest.mark.parametrize(
    "priority, expected_count",
    [
        ("high", 1),
        ("medium", 1),
        ("low", 1),
    ],
)
def test_count_by_priority_on_stocked_board(
    stocked_board: QuestBoard, priority: str, expected_count: int
):
    assert stocked_board.count_by_priority(priority) == expected_count


def test_count_by_priority_on_empty_board_is_always_zero(empty_board: QuestBoard):
    assert empty_board.count_by_priority("high") == 0


@pytest.mark.parametrize("priority", ["low", "medium", "high"])
def test_adding_two_quests_of_the_same_priority_counts_both(
    empty_board: QuestBoard, priority: str
):
    empty_board.add_quest("Quest One", priority)
    empty_board.add_quest("Quest Two", priority)
    assert empty_board.count_by_priority(priority) == 2
