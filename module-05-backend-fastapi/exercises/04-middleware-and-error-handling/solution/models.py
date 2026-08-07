from pydantic import BaseModel


class VaultItem(BaseModel):
    id: str
    name: str
    locked: bool
    owner_note: str  # internal bookkeeping only -- must never leave this API


class VaultItemOut(BaseModel):
    """The external-facing shape -- deliberately excludes `owner_note`."""

    id: str
    name: str
    locked: bool
