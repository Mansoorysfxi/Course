from .models import Quest


def format_quest(quest: Quest) -> str:
    status = "Complete" if quest.is_complete else "In progress"
    return f"{quest.name} [{quest.difficulty}] — {quest.reward_gold} gold ({status})"


if __name__ == "__main__":
    demo_quest = Quest("Slay the Dragon", "Hard", 500)
    print(format_quest(demo_quest))
