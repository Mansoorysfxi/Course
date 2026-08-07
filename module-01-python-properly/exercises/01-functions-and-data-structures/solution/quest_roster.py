"""
Exercise 01 reference solution — Functions and Data Structures Warm-Up.

Don't read this until you've made a genuine attempt at starter/quest_roster.py
and either finished or are stuck after checking INSTRUCTIONS.md's hints.
There is more than one valid way to write several of these functions (e.g.
describe_player's exact formatting) — this is *a* correct solution, not
*the only* correct one.
"""


def format_quest(name, difficulty, reward_gold=0):
    return f"{name} [{difficulty}] — {reward_gold} gold"


def total_rewards(*rewards):
    return sum(rewards)


def describe_player(**stats):
    parts = [f"{key}: {value}" for key, value in stats.items()]
    return ", ".join(parts)


def filter_by_difficulty(quests, difficulty):
    matching = []
    for quest in quests:
        if quest["difficulty"] == difficulty:
            matching.append(quest)
    return matching


def unique_difficulties(quests):
    difficulties = set()
    for quest in quests:
        difficulties.add(quest["difficulty"])
    return difficulties


def build_reward_lookup(quests):
    lookup = {}
    for quest in quests:
        lookup[quest["name"]] = quest["reward_gold"]
    return lookup


# `completed_ids` is a set, not a list, because has_completed() is the kind
# of check that gets called once per quest, every time the roster is
# displayed — a set gives O(1) average-case membership checks regardless of
# how many quests have been completed, while a list would get slower as the
# player completes more and more quests over time.
def has_completed(completed_ids, quest_id):
    return quest_id in completed_ids


if __name__ == "__main__":
    print(format_quest("Slay the Dragon", "Hard"))
    print(format_quest("Water the Plants", "Trivial", 5))
    print(total_rewards())
    print(total_rewards(100, 250, 50))
    print(describe_player(name="Aria", level=12, hp=100))

    quests = [
        {"name": "Slay the Dragon", "difficulty": "Hard", "reward_gold": 500},
        {"name": "Find the Amulet", "difficulty": "Medium", "reward_gold": 200},
        {"name": "Water the Plants", "difficulty": "Trivial", "reward_gold": 5},
        {"name": "Defeat the Bandit King", "difficulty": "Hard", "reward_gold": 450},
    ]

    hard_quests = filter_by_difficulty(quests, "Hard")
    print([q["name"] for q in hard_quests])
    print(quests is not hard_quests)   # confirms a new list was returned

    print(unique_difficulties(quests))
    print(type(unique_difficulties(quests)))

    lookup = build_reward_lookup(quests)
    print(lookup["Slay the Dragon"])

    completed = {"q1", "q3"}
    print(has_completed(completed, "q1"))
    print(has_completed(completed, "q2"))
