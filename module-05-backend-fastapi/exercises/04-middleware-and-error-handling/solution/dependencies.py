from fastapi import HTTPException, status

import store
from models import VaultItem


def get_item_or_404(item_id: str) -> VaultItem:
    item = store.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No vault item with id '{item_id}'")
    return item
