"""
Exercise 02 reference solution — Comprehensions, Generators, and a Real
Class Hierarchy.

Don't read this until you've made a genuine attempt at
starter/questline.py. There is more than one valid way to write several of
these (especially __repr__'s exact formatting) — this is *a* correct
solution, not *the only* correct one.
"""


class Quest:
    def __init__(self, name, difficulty, reward_gold, is_complete=False):
        self.name = name
        self.difficulty = difficulty
        self.reward_gold = reward_gold
        self.is_complete = is_complete

    def __repr__(self):
        return (
            f"Quest(name={self.name!r}, difficulty={self.difficulty!r}, "
            f"reward_gold={self.reward_gold}, is_complete={self.is_complete})"
        )

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.difficulty == other.difficulty
            and self.reward_gold == other.reward_gold
        )


class TimedQuest(Quest):
    def __init__(self, name, difficulty, reward_gold, time_limit_minutes, is_complete=False):
        super().__init__(name, difficulty, reward_gold, is_complete)
        self.time_limit_minutes = time_limit_minutes

    def __repr__(self):
        base = super().__repr__()
        # base ends in ")" — insert the extra field just before it.
        return base[:-1] + f", time_limit_minutes={self.time_limit_minutes})"


class QuestLine:
    def __init__(self, quests):
        self._quests = quests

    def __len__(self):
        return len(self._quests)

    def __iter__(self):
        return iter(self._quests)


def incomplete_quest_names(quest_line):
    return [q.name for q in quest_line if not q.is_complete]


def reward_lookup_over(quest_line, minimum_reward):
    return {q.name: q.reward_gold for q in quest_line if q.reward_gold >= minimum_reward}


def high_priority_quests(quest_line, minimum_reward):
    for quest in quest_line:
        if quest.reward_gold >= minimum_reward:
            yield quest


if __name__ == "__main__":
    line = QuestLine([
        Quest("Slay the Dragon", "Hard", 500),
        Quest("Water the Plants", "Trivial", 5, is_complete=True),
        TimedQuest("Defuse the Trap", "Medium", 300, time_limit_minutes=5),
    ])

    print(len(line))
    for q in line:
        print(q)

    print(Quest("A", "Hard", 100) == Quest("A", "Hard", 100, is_complete=True))
    print(Quest("A", "Hard", 100) == Quest("B", "Hard", 100))

    timed = TimedQuest("Defuse the Trap", "Medium", 300, time_limit_minutes=5)
    print(isinstance(timed, Quest))
    print(timed)

    print(incomplete_quest_names(line))
    print(reward_lookup_over(line, 100))

    gen = high_priority_quests(line, 100)
    print(type(gen))
    print(next(gen))
    print(next(gen))
