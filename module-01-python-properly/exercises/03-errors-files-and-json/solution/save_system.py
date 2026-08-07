"""
Exercise 03 reference solution — Error Handling, File I/O, and JSON.

Don't read this until you've made a genuine attempt at starter/save_system.py.
"""

import json


class QuestLogError(Exception):
    """Base class for all quest-log-related errors in this file."""
    pass


class QuestNotFoundError(QuestLogError):
    def __init__(self, quest_name):
        self.quest_name = quest_name
        super().__init__(f"No quest named '{quest_name}' exists.")


class CorruptSaveFileError(QuestLogError):
    def __init__(self, path, original_error):
        self.path = path
        self.original_error = original_error
        super().__init__(f"Save file at '{path}' is corrupted: {original_error}")


def load_quest_log(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise CorruptSaveFileError(path, e)


def save_quest_log(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def get_quest(quests, quest_name):
    if quest_name not in quests:
        raise QuestNotFoundError(quest_name)
    return quests[quest_name]


def mark_complete(quests, quest_name):
    quest = get_quest(quests, quest_name)
    quest["is_complete"] = True


if __name__ == "__main__":
    quests = {
        "slay_dragon": {"reward_gold": 500, "is_complete": False},
        "find_amulet": {"reward_gold": 200, "is_complete": False},
    }

    save_quest_log("demo_quests.json", quests)
    loaded = load_quest_log("demo_quests.json")
    print(loaded)

    mark_complete(loaded, "slay_dragon")
    print(loaded["slay_dragon"])

    try:
        mark_complete(loaded, "rescue_villager")
    except QuestNotFoundError as e:
        print(f"Could not complete quest: {e}")

    missing = load_quest_log("does_not_exist.json")
    print(missing)

    # Demonstrate the CorruptSaveFileError path too.
    with open("broken_demo.json", "w") as f:
        f.write("{not valid json")

    try:
        load_quest_log("broken_demo.json")
    except CorruptSaveFileError as e:
        print(f"Load failed as expected: {e}")
