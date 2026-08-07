"""Already complete -- do not modify. See INSTRUCTIONS.md."""

from models import VaultItem

_items: dict[str, VaultItem] = {
    "item-001": VaultItem(id="item-001", name="Ancient Amulet", locked=True, owner_note="Insured, do not photograph."),
    "item-002": VaultItem(id="item-002", name="Silver Key", locked=False, owner_note="Spare cut in drawer 4."),
}


def list_items() -> list[VaultItem]:
    return list(_items.values())


def get_item(item_id: str) -> VaultItem | None:
    return _items.get(item_id)


def set_locked(item_id: str, locked: bool) -> VaultItem:
    existing = _items[item_id]
    updated = existing.model_copy(update={"locked": locked})
    _items[item_id] = updated
    return updated
