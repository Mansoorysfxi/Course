# Reference Solution — A New Endpoint, End to End

Don't read this until you've made a genuine attempt.

## `app/models.py` addition

```python
class QuestLineSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    quest_count: int = Field(alias="questCount")
```

## `app/repository.py` addition

```python
async def list_quest_lines(session: AsyncSession) -> list[QuestLineSummary]:
    """Unlike quest_line_stats (a plain JOIN, which silently omits any
    quest line with zero quests), this uses a LEFT JOIN specifically so
    every quest line that exists is represented -- see Exercise 05 and
    lessons/04-joins-and-group-by.md."""
    stmt = (
        select(QuestLine.name, func.count(QuestRow.id).label("quest_count"))
        .select_from(QuestLine)
        .join(QuestRow, QuestRow.quest_line_id == QuestLine.id, isouter=True)
        .group_by(QuestLine.name)
        .order_by(QuestLine.name)
    )
    result = await session.execute(stmt)
    return [
        QuestLineSummary(name=row.name, quest_count=row.quest_count) for row in result
    ]
```

## `app/routers/quests.py` addition

```python
@router.get("/lines", response_model=list[QuestLineSummary])
async def list_quest_lines(session: DbSession):
    return await repository.list_quest_lines(session)
```

Registered as `/api/quests/lines` — placed alongside the existing
`/stats` route, **before** `/{quest_id}`, for the exact same route-ordering
reason Module 05 taught: `"lines"` would otherwise be swallowed by the
`{quest_id}` path parameter if it came first.

## Verification

```bash
# setup: a quest line with zero quests
psql -U questlog -d questlog -h localhost -c \
  "INSERT INTO quest_lines (id, name) VALUES ('ql-empty-test', 'Empty Line');"

curl http://127.0.0.1:8000/api/quests/lines
# [...,{"name":"Empty Line","questCount":0}]  <- appears here

curl http://127.0.0.1:8000/api/quests/stats
# [...]  <- "Empty Line" does NOT appear here, confirming the JOIN-vs-LEFT-JOIN difference

# cleanup
psql -U questlog -d questlog -h localhost -c \
  "DELETE FROM quest_lines WHERE id = 'ql-empty-test';"
```

## Notes on grading this yourself

- The core thing being tested is whether you actually understand *why*
  `isouter=True` (or `.outerjoin(...)`) was the one change needed, versus
  treating this as "copy `quest_line_stats` and rename it" without
  understanding the difference — the zero-quest verification step exists
  specifically to force that understanding to be demonstrated, not just
  claimed.
- If your route was placed *after* `/{quest_id}` in the file, test it —
  a request to `/api/quests/lines` would have been incorrectly matched by
  `/{quest_id}` (treating `"lines"` as a quest id) and returned a 404
  instead of your new endpoint's response.
