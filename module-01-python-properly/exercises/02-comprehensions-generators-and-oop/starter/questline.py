"""
Exercise 02 starter — Comprehensions, Generators, and a Real Class Hierarchy.

Fill in each TODO below, in order — later pieces depend on earlier ones.
See INSTRUCTIONS.md in this exercise's folder for exactly what each piece
must do and how it will be checked.
"""


class Quest:
    def __init__(self, name, difficulty, reward_gold, is_complete=False):
        # TODO: set self.name, self.difficulty, self.reward_gold, self.is_complete
        pass

    def __repr__(self):
        # TODO: return something like:
        # Quest(name='Slay the Dragon', difficulty='Hard', reward_gold=500, is_complete=False)
        pass

    def __eq__(self, other):
        # TODO: return True if name, difficulty, and reward_gold all match
        # (ignore is_complete in the comparison)
        pass


class TimedQuest(Quest):
    def __init__(self, name, difficulty, reward_gold, time_limit_minutes, is_complete=False):
        # TODO: call super().__init__(...) to set the shared attributes,
        # then set self.time_limit_minutes yourself.
        pass

    def __repr__(self):
        # TODO: call super().__repr__() and extend it to also show
        # time_limit_minutes.
        pass


class QuestLine:
    def __init__(self, quests):
        # TODO: store the given list of Quest/TimedQuest instances
        pass

    def __len__(self):
        # TODO: return the number of quests this QuestLine holds
        pass

    def __iter__(self):
        # TODO: return an iterator over the quests this QuestLine holds
        pass


def incomplete_quest_names(quest_line):
    """
    Return a list of names of every quest in quest_line where
    is_complete is False. Must be written as a single list comprehension.
    """
    # TODO: implement as one list comprehension.
    pass


def reward_lookup_over(quest_line, minimum_reward):
    """
    Return a dict mapping name -> reward_gold for every quest in
    quest_line whose reward_gold is >= minimum_reward. Must be written as
    a single dict comprehension.
    """
    # TODO: implement as one dict comprehension.
    pass


def high_priority_quests(quest_line, minimum_reward):
    """
    A generator function: lazily yield each quest in quest_line whose
    reward_gold is >= minimum_reward, one at a time. Must use `yield`,
    not build and return a list.
    """
    # TODO: implement using yield inside a loop.
    pass


if __name__ == "__main__":
    # Use this block to try your classes/functions out as you write them.
    line = QuestLine([
        Quest("Slay the Dragon", "Hard", 500),
        Quest("Water the Plants", "Trivial", 5, is_complete=True),
        TimedQuest("Defuse the Trap", "Medium", 300, time_limit_minutes=5),
    ])
    # print(len(line))
    # for q in line:
    #     print(q)
    # print(incomplete_quest_names(line))
    # print(reward_lookup_over(line, 100))
    # gen = high_priority_quests(line, 100)
    # print(type(gen))
    # print(next(gen))
