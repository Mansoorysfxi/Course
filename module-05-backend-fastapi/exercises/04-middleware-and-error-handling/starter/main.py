from fastapi import FastAPI

import store
from models import VaultItem

app = FastAPI(title="Vault API (Exercise 04)")

# TODO 1: add middleware here (@app.middleware("http")) that adds an
# X-Response-Time-Ms header to EVERY response. See lessons/05-middleware.md.


@app.get("/vault", response_model=list[VaultItem])
def list_vault_items():
    return store.list_items()


# TODO 2: define a smaller response model (e.g. VaultItemOut) that excludes
# `owner_note` entirely, for use as `response_model=` on the three routes
# below. See lessons/06-error-handling-status-codes-and-responses.md.

# TODO 3: define VaultLockedError (a plain Exception subclass carrying
# item_id) and register an @app.exception_handler(VaultLockedError) that
# returns a 409 with detail=f"Vault item '{item_id}' is locked."

# TODO 4: a get_item_or_404 dependency (models.py's VaultItem, store.get_item)
# -- follow lessons/04-dependency-injection-and-depends.md's pattern exactly.

# TODO 5: POST /vault/{item_id}/reveal
# Depends on get_item_or_404; raises VaultLockedError if item.locked;
# otherwise returns the item through your response_model.

# TODO 6: POST /vault/{item_id}/lock and POST /vault/{item_id}/unlock
# Depends on get_item_or_404; call store.set_locked(item.id, True/False);
# return the result through your response_model.
