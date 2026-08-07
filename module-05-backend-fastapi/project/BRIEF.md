# Module 05 Capstone — The QuestLog API

## What this is

Per [`RUNNING_PROJECT.md`](../../RUNNING_PROJECT.md), this is where QuestLog
gets its first real backend. Module 04's finished `questlog` app — a React +
TypeScript SPA with all data held in local state, fetched through a mocked,
fake `fetchQuests()` — is copied forward into
[`project/questlog/frontend/`](./questlog/frontend/), and a brand-new
FastAPI backend is built alongside it in
[`project/questlog/backend/`](./questlog/backend/). The frontend's mocked
data layer is swapped for real HTTP calls to that backend — no database yet
(a plain in-memory Python `dict` stands in for one, deliberately, until
Module 06 adds PostgreSQL).

**The finished reference solution lives at
[`project/questlog/`](./questlog/)** — both `frontend/` and `backend/` were
actually built, installed, and run while writing this module (see each
folder's own README for exactly what was verified, and this module's root
`README.md` for whether they were confirmed running together with a real
browser round-trip).

## The API contract

The backend's `Quest` shape matches the frontend's exactly, field for field
(via Pydantic's `Field(alias=...)`, per Lesson 03's aliasing section):

```python
Priority = Literal["low", "medium", "high"]

class Quest(BaseModel):
    id: str
    title: str
    description: str
    priority: Priority
    done: bool
    quest_line: str   # JSON: "questLine"
    created_at: str   # JSON: "createdAt", ISO 8601
```

## Concepts this capstone uses

Every concept below has a dedicated lesson section — this project should not
require anything this module didn't already teach (Rule 1):

| Concept | Taught in |
|---|---|
| venv, installing FastAPI + Uvicorn, running with `uvicorn --reload`, running frontend+backend together | [Lesson 00](../lessons/00-setup.md) |
| `FastAPI()`, `@app.get(...)` and friends, decorators applied for real | [Lesson 01](../lessons/01-what-a-backend-does-and-your-first-routes.md) |
| Path parameters (`{quest_id}`), query parameters (`done`, `priority`, `quest_line` on the list route), route-matching order (`/stats` vs `/{quest_id}`) | [Lesson 02](../lessons/02-path-and-query-parameters.md) |
| Pydantic models, `Literal`, `Field`, `model_config`, `Field(alias=...)` for the camelCase contract | [Lesson 03](../lessons/03-request-bodies-and-pydantic-validation.md) |
| `get_quest_or_404` via `Depends()` and `Annotated` | [Lesson 04](../lessons/04-dependency-injection-and-depends.md) |
| `CORSMiddleware`, unblocking the frontend's cross-origin requests | [Lesson 05](../lessons/05-middleware.md) |
| `HTTPException`, `response_model`, deliberate status codes (`201`, `204`, `404`) | [Lesson 06](../lessons/06-error-handling-status-codes-and-responses.md) |
| Testing via Swagger UI (`/docs`) and understanding OpenAPI | [Lesson 07](../lessons/07-auto-docs-and-openapi.md) |
| The full multi-file `APIRouter` structure, in-memory store, CRUD-to-HTTP-method mapping | [Lesson 08](../lessons/08-building-the-questlog-api.md) |
| `fetch()`, async/await, loading/error state patterns (reused, not re-taught) | Module 03, Lesson 07; Module 04, Lessons 03/07 |

## What to build

1. Copy `module-04-react/project/questlog/` into
   `module-05-backend-fastapi/project/questlog/frontend/` (or verify it's
   already there, if you're reviewing the reference solution).
2. Build the backend at `project/questlog/backend/`, following
   [Lesson 08](../lessons/08-building-the-questlog-api.md) exactly:
   `app/models.py`, `app/store.py`, `app/dependencies.py`,
   `app/routers/quests.py`, `app/main.py` — full CRUD, seeded with starting
   quests, CORS enabled for `http://localhost:5173`.
3. Update the frontend:
   - Replace `src/api/fetchQuests.ts` with a new file making real `fetch()`
     calls to the backend for list/get/create/update/delete (this course's
     reference solution calls it `src/api/questsApi.ts`).
   - Update `src/context/QuestsContext.tsx`'s `addQuest`/`updateQuest`/
     `deleteQuest`/`toggleDone` to call the real API and become `async`,
     updating `quests` from the backend's actual response.
   - Update any page calling those functions (`NewQuestPage.tsx`,
     `QuestDetailPage.tsx`) to `await` them before navigating.
   - Add a `.env` with `VITE_API_BASE_URL=http://localhost:8000`.

## Acceptance criteria

- [ ] `cd backend && uvicorn app.main:app --reload` starts with no errors, and seeds five starting quests.
- [ ] Every route in `backend/README.md`'s table works correctly via `curl`: list, get-one (including a `404` for a fake ID), create (`201`), update (`200`, partial), delete (`204`), and `/stats`.
- [ ] `POST /api/quests` with an invalid body (missing field, bad `priority`) returns `422` with the exact error shape Lesson 03 taught.
- [ ] Visiting `/docs` shows every route, and "Try it out" works for each.
- [ ] `cd frontend && npm install && npm run build` completes with zero TypeScript errors.
- [ ] With both servers running (two terminals), visiting the frontend shows a loading state, then the real seeded quests — served by the backend, confirmed by stopping the backend and reloading the frontend (the error banner should now appear, with a message naming the backend, not a random simulated failure).
- [ ] Adding, editing, toggling done, and deleting a quest in the browser each produce a real request the backend's own terminal logs — confirm by watching Uvicorn's own request log while using the app.
- [ ] No component or page other than `QuestsContext.tsx` and the two pages listed above needed to change.

## What to submit

Point your AI session at your completed `project/questlog/` folder and say
*"check my module"* — graded per [GRADING_PROTOCOL.md](../../GRADING_PROTOCOL.md)
alongside a re-check of Exercises 01–05 as part of the full Module 05
module-end review.

## Why this project, specifically

This is the moment QuestLog stops being a self-contained illusion and
becomes a real client talking to a real server over real HTTP — every
concept from Lessons 00–08, applied to one coherent app instead of five
separate small examples. Getting the separation right here (routes that
only ever talk to `store.py`, never to a raw dict directly; a frontend that
only ever talks to `questsApi.ts`, never constructing a URL by hand
elsewhere) is exactly what makes Module 06's "swap the in-memory store for
PostgreSQL" instruction land on solid ground instead of requiring a
partial rewrite.
