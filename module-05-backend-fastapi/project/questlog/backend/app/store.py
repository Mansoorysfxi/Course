"""The in-memory "database". A plain Python dict, module-level, holding
every quest for as long as this server process runs -- deliberately
temporary; see lessons/08-building-the-questlog-api.md's "why in-memory"
section. Module 06 replaces this file's insides with real PostgreSQL
queries via SQLAlchemy; every route in routers/quests.py only ever calls
these functions, never touches `_quests` directly, which is exactly what
makes that future swap not require rewriting the routes themselves.
"""

import uuid
from datetime import datetime, timezone

from app.models import Quest, QuestCreate, QuestLineStats, QuestUpdate

_quests: dict[str, Quest] = {}


def seed() -> None:
    """Populates the store with the same starting quests Module 04's mocked
    fetchQuests() used, so the app behaves familiarly on first run."""
    starter = [
        QuestCreate(
            title="Slay the Dragon",
            description="The dragon has been terrorizing the northern villages. Someone has to go.",
            priority="high",
            quest_line="Main Story",
        ),
        QuestCreate(
            title="Gather Healing Herbs",
            description="The village healer needs five bundles of silverleaf from the eastern woods.",
            priority="low",
            quest_line="Village Errands",
        ),
        QuestCreate(
            title="Deliver the Sealed Letter",
            description="A courier's letter must reach the capital before the harvest festival begins.",
            priority="medium",
            quest_line="Village Errands",
        ),
        QuestCreate(
            title="Clear the Old Mine",
            description="Something has been digging new tunnels in the abandoned mine. Investigate.",
            priority="high",
            quest_line="Side Quests",
        ),
        QuestCreate(
            title="Repair the Bridge",
            description="The stone bridge to the market town has a collapsed section.",
            priority="medium",
            quest_line="Side Quests",
        ),
    ]
    for quest_create in starter:
        create_quest(quest_create)
    # The second seeded quest ("Gather Healing Herbs") and the fifth
    # ("Repair the Bridge") were already `done: true` in Module 04's own
    # mock data -- reproduce that here so the app looks identical on first
    # load.
    all_quests = list(_quests.values())
    update_quest(all_quests[1].id, QuestUpdate(done=True))
    update_quest(all_quests[4].id, QuestUpdate(done=True))


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
