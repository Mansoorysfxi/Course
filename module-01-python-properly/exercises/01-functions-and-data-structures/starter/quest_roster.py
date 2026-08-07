"""
Exercise 01 starter — Functions and Data Structures Warm-Up.

Fill in each function body below. Do not rename any function or change its
parameters. See INSTRUCTIONS.md in this exercise's folder for exactly what
each one must do and how it will be checked.
"""


def format_quest(name, difficulty, reward_gold=0):
    """
    Return a string in the exact form:
        "<name> [<difficulty>] — <reward_gold> gold"
    `reward_gold` should default to 0 if the caller doesn't supply it.
    """
    # TODO: implement this using an f-string.
    pass


def total_rewards(*rewards):
    """
    Accept any number of reward amounts as separate positional arguments
    (via *args) and return their sum. Calling this with zero arguments
    should return 0, not raise an error.
    """
    # TODO: implement this using *rewards and sum().
    pass


def describe_player(**stats):
    """
    Accept any number of keyword arguments describing a player (via
    **kwargs) and return a single string listing every key: value pair
    you were given. The exact formatting is up to you.
    """
    # TODO: implement this using **stats.
    pass


def filter_by_difficulty(quests, difficulty):
    """
    Given a list of quest dicts (each with at least "name" and
    "difficulty" keys) and a target difficulty string, return a NEW list
    containing only the quests whose "difficulty" matches. Use a plain
    for loop and if — do not use a comprehension (not taught yet at this
    point in the course) and do not mutate the input list.
    """
    # TODO: implement this with a for loop and if.
    pass


def unique_difficulties(quests):
    """
    Given the same shape of quest list, return a set of every distinct
    "difficulty" value present (duplicates collapse automatically).
    """
    # TODO: implement this, returning a set.
    pass


def build_reward_lookup(quests):
    """
    Given the same shape of quest list, return a dict mapping each
    quest's "name" to its "reward_gold", so looking up any quest's reward
    afterward is an O(1) dict lookup instead of an O(n) list scan.
    """
    # TODO: implement this, returning a dict.
    pass


# TODO: write a one-sentence comment here explaining why `completed_ids`
# is typed as a set rather than a list — think about how often
# `has_completed` might be called and what that means for performance.
def has_completed(completed_ids, quest_id):
    """
    Given a set of already-completed quest IDs and a specific quest_id,
    return True if quest_id is in the set, False otherwise.
    """
    # TODO: implement this using `in`.
    pass


if __name__ == "__main__":
    # Use this block to try your functions out as you write them.
    # Example (uncomment and adapt as you go):
    # print(format_quest("Slay the Dragon", "Hard"))
    # print(total_rewards(100, 250, 50))
    # print(describe_player(name="Aria", level=12))
    pass
