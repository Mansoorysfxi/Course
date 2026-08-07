from datetime import date
from unittest.mock import patch

import quest_reminders
from quest_reminders import days_since_created, is_overdue, notify_if_overdue


# --- mocking the current date --------------------------------------------


def test_days_since_created_with_a_fixed_today():
    with patch("quest_reminders.date") as mock_date:
        mock_date.today.return_value = date(2026, 8, 10)
        assert days_since_created(date(2026, 8, 1)) == 9


def test_days_since_created_when_created_today():
    with patch("quest_reminders.date") as mock_date:
        mock_date.today.return_value = date(2026, 8, 10)
        assert days_since_created(date(2026, 8, 10)) == 0


def test_is_overdue_returns_false_at_exactly_the_deadline():
    """9 days have passed, deadline is 9 days -- NOT overdue yet (the
    docstring says "more than deadline_days," not "at least")."""
    with patch("quest_reminders.date") as mock_date:
        mock_date.today.return_value = date(2026, 8, 10)
        assert is_overdue(date(2026, 8, 1), deadline_days=9) is False


def test_is_overdue_returns_true_one_day_past_the_deadline():
    with patch("quest_reminders.date") as mock_date:
        mock_date.today.return_value = date(2026, 8, 10)
        assert is_overdue(date(2026, 8, 1), deadline_days=8) is True


# --- mocking the "external notification service" --------------------------


def test_notify_if_overdue_sends_a_reminder_when_overdue(monkeypatch):
    """Mocks `is_overdue` itself (already fully tested above, on its own)
    so this test can focus purely on notify_if_overdue's own branching
    logic, without needing to fuss with the real date again -- see
    lessons/03-parametrize-and-mocking.md's "mock the boundary, not the
    thing you're testing" rule, applied here to mean: don't re-test
    is_overdue's date math while testing notify_if_overdue's decision to
    call send_overdue_reminder or not."""
    monkeypatch.setattr(quest_reminders, "is_overdue", lambda created_on, deadline_days: True)

    with patch("quest_reminders.send_overdue_reminder") as mock_send:
        mock_send.return_value = True
        result = notify_if_overdue(
            "Slay the Dragon", "hero@example.com", date(2026, 1, 1), deadline_days=5
        )

    assert result is True
    mock_send.assert_called_once_with("Slay the Dragon", "hero@example.com")


def test_notify_if_overdue_does_not_send_when_not_overdue(monkeypatch):
    monkeypatch.setattr(quest_reminders, "is_overdue", lambda created_on, deadline_days: False)

    with patch("quest_reminders.send_overdue_reminder") as mock_send:
        result = notify_if_overdue(
            "Gather Herbs", "hero@example.com", date(2026, 1, 1), deadline_days=5
        )

    assert result is False
    mock_send.assert_not_called()
