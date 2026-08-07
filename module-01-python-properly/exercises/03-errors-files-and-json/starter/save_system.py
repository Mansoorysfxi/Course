"""
Exercise 03 starter — Error Handling, File I/O, and JSON.

Fill in each TODO below, in order. See INSTRUCTIONS.md in this exercise's
folder for exactly what each piece must do and how it will be checked.
"""

import json


# TODO: define QuestLogError(Exception) — the base class for this file's
# custom exceptions. It can be as simple as:
#     class QuestLogError(Exception):
#         pass


# TODO: define QuestNotFoundError(QuestLogError). __init__ should accept
# quest_name, store it as self.quest_name, and call
# super().__init__(f"No quest named '{quest_name}' exists.")


# TODO: define CorruptSaveFileError(QuestLogError). __init__ should accept
# path and original_error, store both, and call super().__init__(...)
# with a message like f"Save file at '{path}' is corrupted: {original_error}"


def load_quest_log(path):
    """
    Load and parse the JSON file at `path`.
    - Missing file (FileNotFoundError) -> return {} (normal, not an error).
    - Malformed JSON (json.JSONDecodeError) -> raise CorruptSaveFileError
      instead of letting the json module's own exception propagate.
    """
    # TODO: implement using try/except FileNotFoundError / json.JSONDecodeError.
    pass


def save_quest_log(path, data):
    """
    Write `data` (a dict) to `path` as JSON, using `with` and json.dump.
    """
    # TODO: implement.
    pass


def get_quest(quests, quest_name):
    """
    Return the inner dict for quest_name from the quests dict. Raise
    QuestNotFoundError(quest_name) if it doesn't exist — do not let a raw
    KeyError propagate.
    """
    # TODO: implement.
    pass


def mark_complete(quests, quest_name):
    """
    Use get_quest to fetch the quest (let QuestNotFoundError propagate if
    it's missing — do not catch it here), then set its "is_complete" key
    to True.
    """
    # TODO: implement.
    pass


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

    # TODO: wrap this call in try/except QuestNotFoundError and print a
    # friendly message instead of letting it crash.
    mark_complete(loaded, "rescue_villager")

    missing = load_quest_log("does_not_exist.json")
    print(missing)
