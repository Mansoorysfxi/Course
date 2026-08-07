"""Already complete -- do not modify. See INSTRUCTIONS.md.

VaultItem is the FULL internal shape, including `_owner_note`, which must
never be sent to a client. Your job is to define your own, smaller
response model that excludes it -- see INSTRUCTIONS.md's hints.
"""

from pydantic import BaseModel


class VaultItem(BaseModel):
    id: str
    name: str
    locked: bool
    owner_note: str  # internal bookkeeping only -- must never leave this API
