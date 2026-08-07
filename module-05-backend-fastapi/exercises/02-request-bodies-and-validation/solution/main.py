from typing import Literal

from fastapi import FastAPI, status
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Adventurer Registry")


class AdventurerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    level: int = Field(ge=1, le=100)
    character_class: Literal["warrior", "mage", "rogue", "cleric"]

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name cannot be blank or only whitespace.")
        return value


@app.post("/adventurers", status_code=status.HTTP_201_CREATED)
def create_adventurer(adventurer: AdventurerCreate):
    return adventurer


@app.get("/adventurers/search")
def search_adventurers(min_level: int | None = None, character_class: str | None = None):
    # No real storage in this exercise -- Exercise 03 adds that. This route
    # exists purely to practice declaring genuinely optional query
    # parameters (Lesson 02) and returning a consistent, typed response.
    return []
