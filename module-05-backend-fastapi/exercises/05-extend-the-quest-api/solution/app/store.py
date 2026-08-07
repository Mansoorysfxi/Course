import uuid
from datetime import datetime, timezone

from app.models import Quest, QuestCreate, QuestLineStats, QuestUpdate

_quests: dict[str, Quest] = {}


def seed() -> None:
    starter = [
        QuestCreate(title="Slay the Dragon", description="The dragon has been terrorizing the northern villages.", priority="high", quest_line="Main Story"),
        QuestCreate(title="Gather Healing Herbs", description="Five bundles of silverleaf from the eastern woods.", priority="low", quest_line="Village Errands"),
        QuestCreate(title="Deliver the Sealed Letter", description="Must reach the capital before the festival.", priority="medium", quest_line="Village Errands"),
        QuestCreate(title="Clear the Old Mine", description="Something has been digging new tunnels.", priority="high", quest_line="Side Quests"),
    ]
    for quest_create in starter:
        create_quest(quest_create)


def list_quests() -> list[Quest]:
    return list(_quests.values())


def get_quest(quest_id: str) -> Quest | None:
    return _quests.get(quest_id)


def create_quest(data: QuestCreate) -> Quest:
    quest = Quest(
        id=str(uuid.uuid4()),
        done=False,
        created_at=datetime.now(timezone.utc).isoformat(),
        **data.model_dump(),
    )
    _quests[quest.id] = quest
    return quest


def update_quest(quest_id: str, changes: QuestUpdate) -> Quest | None:
    existing = _quests.get(quest_id)
    if existing is None:
        return None
    updated = existing.model_copy(update=changes.model_dump(exclude_unset=True))
    _quests[quest_id] = updated
    return updated


def delete_quest(quest_id: str) -> bool:
    return _quests.pop(quest_id, None) is not None


def quest_line_stats() -> list[QuestLineStats]:
    """New for exercise 05. One entry per distinct quest line with >=1 quest."""
    tally: dict[str, dict[str, int]] = {}
    for quest in _quests.values():
        entry = tally.setdefault(quest.quest_line, {"total": 0, "done": 0})
        entry["total"] += 1
        if quest.done:
            entry["done"] += 1
    return [
        QuestLineStats(quest_line=line, total=counts["total"], done=counts["done"])
        for line, counts in tally.items()
    ]


def quests_in_line(quest_line: str) -> list[Quest]:
    """New for exercise 05. Every quest currently in this exact quest line."""
    return [quest for quest in _quests.values() if quest.quest_line == quest_line]


def complete_line(quest_line: str) -> list[Quest]:
    """New for exercise 05. Marks every quest in this line done, returns them."""
    updated = []
    for quest in quests_in_line(quest_line):
        updated.append(update_quest(quest.id, QuestUpdate(done=True)))
    return updated
