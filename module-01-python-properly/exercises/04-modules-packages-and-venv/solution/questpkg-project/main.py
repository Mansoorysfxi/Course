from questpkg import Quest
from questpkg.formatting import format_quest

if __name__ == "__main__":
    quests = [
        Quest("Slay the Dragon", "Hard", 500),
        Quest("Water the Plants", "Trivial", 5, is_complete=True),
    ]
    for quest in quests:
        print(format_quest(quest))
