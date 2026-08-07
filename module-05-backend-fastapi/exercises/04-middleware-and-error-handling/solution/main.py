import time
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

import store
from dependencies import get_item_or_404
from models import VaultItem, VaultItemOut

app = FastAPI(title="Vault API (Exercise 04)")


@app.middleware("http")
async def add_response_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"
    return response


class VaultLockedError(Exception):
    def __init__(self, item_id: str):
        self.item_id = item_id


@app.exception_handler(VaultLockedError)
async def vault_locked_handler(request: Request, exc: VaultLockedError):
    return JSONResponse(
        status_code=409,
        content={"detail": f"Vault item '{exc.item_id}' is locked."},
    )


@app.get("/vault", response_model=list[VaultItemOut])
def list_vault_items():
    return store.list_items()


@app.post("/vault/{item_id}/reveal", response_model=VaultItemOut)
def reveal_item(item: Annotated[VaultItem, Depends(get_item_or_404)]):
    if item.locked:
        raise VaultLockedError(item.id)
    return item


@app.post("/vault/{item_id}/lock", response_model=VaultItemOut)
def lock_item(item: Annotated[VaultItem, Depends(get_item_or_404)]):
    return store.set_locked(item.id, True)


@app.post("/vault/{item_id}/unlock", response_model=VaultItemOut)
def unlock_item(item: Annotated[VaultItem, Depends(get_item_or_404)]):
    return store.set_locked(item.id, False)
