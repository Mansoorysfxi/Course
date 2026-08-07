import pytest
from quest_utils import (
    count_completed,
    format_quest_title,
    is_valid_priority,
    priority_weight,
)


# --- is_valid_priority --------------------------------------------------


def test_is_valid_priority_accepts_high():
    assert is_valid_priority("high") is True


def test_is_valid_priority_accepts_medium():
    assert is_valid_priority("medium") is True


def test_is_valid_priority_accepts_low():
    assert is_valid_priority("low") is True


def test_is_valid_priority_rejects_unknown_value():
    assert is_valid_priority("urgent") is False


def test_is_valid_priority_is_case_sensitive():
    assert is_valid_priority("High") is False


# --- priority_weight -----------------------------------------------------


def test_priority_weight_orders_high_before_medium_before_low():
    assert priority_weight("high") < priority_weight("medium") < priority_weight("low")


# --- format_quest_title ---------------------------------------------------


def test_format_quest_title_capitalizes_first_letter():
    assert format_quest_title("slay the dragon") == "Slay the dragon"


def test_format_quest_title_strips_surrounding_whitespace():
    assert format_quest_title("  slay the dragon  ") == "Slay the dragon"


def test_format_quest_title_raises_on_empty_string():
    with pytest.raises(ValueError):
        format_quest_title("")


def test_format_quest_title_raises_on_whitespace_only():
    with pytest.raises(ValueError):
        format_quest_title("   ")


# --- count_completed -------------------------------------------------------


def test_count_completed_with_no_quests():
    assert count_completed([]) == 0


def test_count_completed_with_none_done():
    assert count_completed([False, False, False]) == 0


def test_count_completed_with_some_done():
    assert count_completed([True, False, True, False, True]) == 3


def test_count_completed_with_all_done():
    assert count_completed([True, True]) == 2
