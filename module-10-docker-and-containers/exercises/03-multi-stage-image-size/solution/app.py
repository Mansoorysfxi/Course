import pandas as pd

quests = pd.DataFrame(
    {
        "title": ["Slay the Dragon", "Gather Herbs", "Deliver the Letter"],
        "priority": ["high", "low", "medium"],
    }
)
print(quests)
print(f"\nTotal quests: {len(quests)}")
