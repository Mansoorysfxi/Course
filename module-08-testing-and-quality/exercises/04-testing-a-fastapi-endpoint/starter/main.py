"""The Guild Board API -- a tiny, standalone, in-memory FastAPI app (no
database at all, deliberately, so this exercise stays focused on
lessons/05-testing-fastapi-endpoints.md's actual subject: using
httpx.AsyncClient + ASGITransport, not database setup, which is
Lesson 06's separate topic). Announcements are ephemeral -- they reset
every time this app restarts, exactly like Module 05's own original
in-memory QuestLog API did, before Module 06 added Postgres.
"""

import uuid

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Guild Board API")


class AnnouncementCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: str = Field(min_length=1)


class Announcement(AnnouncementCreate):
    id: str


_announcements: dict[str, Announcement] = {}


@app.get("/announcements", response_model=list[Announcement])
def list_announcements():
    return list(_announcements.values())


@app.post(
    "/announcements", response_model=Announcement, status_code=status.HTTP_201_CREATED
)
def create_announcement(data: AnnouncementCreate):
    announcement = Announcement(id=str(uuid.uuid4()), **data.model_dump())
    _announcements[announcement.id] = announcement
    return announcement


@app.get("/announcements/{announcement_id}", response_model=Announcement)
def get_announcement(announcement_id: str):
    announcement = _announcements.get(announcement_id)
    if announcement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No announcement with id '{announcement_id}'",
        )
    return announcement


@app.delete("/announcements/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(announcement_id: str):
    if announcement_id not in _announcements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No announcement with id '{announcement_id}'",
        )
    del _announcements[announcement_id]
    return None
