"""Quest overdue reminders -- depends on "the real current date" (which a
test cannot control without mocking) and a stand-in "external
notification service" (which a test should never actually trigger for
real). See lessons/03-parametrize-and-mocking.md before starting this
exercise -- both concepts this file needs are taught there.
"""

from datetime import date


def days_since_created(created_on: date) -> int:
    """How many days have passed since `created_on`, as of the real,
    current date."""
    return (date.today() - created_on).days


def is_overdue(created_on: date, deadline_days: int) -> bool:
    """A quest is overdue once more than `deadline_days` days have
    passed since it was created."""
    return days_since_created(created_on) > deadline_days


def send_overdue_reminder(quest_title: str, owner_email: str) -> bool:
    """Stands in for a real call to an external email/notification
    service. In a real app, this would be a slow, real network request
    -- exactly the kind of thing a test should never actually trigger,
    every time, hundreds of times a day. Always returns True here."""
    print(f"[would send email] To: {owner_email} -- Reminder: '{quest_title}' is overdue!")
    return True


def notify_if_overdue(
    quest_title: str, owner_email: str, created_on: date, deadline_days: int
) -> bool:
    """Sends a reminder (via send_overdue_reminder) if, and only if, the
    quest is currently overdue. Returns True if a reminder was actually
    sent, False otherwise."""
    if is_overdue(created_on, deadline_days):
        return send_overdue_reminder(quest_title, owner_email)
    return False
