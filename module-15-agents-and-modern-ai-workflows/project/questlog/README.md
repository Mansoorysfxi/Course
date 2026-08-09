# QuestLog — Module 13 (AI assistant: tool use + structured output + streaming)

Per `RUNNING_PROJECT.md`, this folder is Module 11's finished, deployed
`questlog/` copied forward. `backend/app/` and `frontend/src/` are
unchanged from Module 11 **except for this module's own new,
documented AI-assistant feature**: `POST
/api/quests/{quest_id}/suggest-breakdown`, and the `QuestBreakdownPanel`
UI that calls it. See
[`lessons/07-building-questlogs-ai-assistant-backend.md`](../../../module-13-building-with-llm-apis/lessons/07-building-questlogs-ai-assistant-backend.md)
and
[`lessons/08-building-questlogs-ai-assistant-frontend.md`](../../../module-13-building-with-llm-apis/lessons/08-building-questlogs-ai-assistant-frontend.md)
for the complete, line-by-line walkthrough, and
[`../BRIEF.md`](../BRIEF.md) for this module's capstone deliverables.

```
project/questlog/
├── backend/
│   ├── app/ai_assistant.py            — NEW: the whole feature's real logic
│   │                                       (tool use + structured output + streaming)
│   ├── app/config.py                    — NEW: anthropic_api_key, ai_model settings fields
│   ├── app/dependencies.py                — NEW: get_ai_client / AiClient
│   ├── app/routers/quests.py                — NEW: one route (suggest_quest_breakdown),
│   │                                             reusing get_quest_or_404 and list_quests
│   ├── tests/test_ai_assistant.py             — NEW: 7 tests, zero real API key required
│   ├── requirements.txt                         — NEW: anthropic==0.121.0
│   ├── .env.example                               — NEW: ANTHROPIC_API_KEY / AI_MODEL, both optional
│   └── ...                                            — everything else unchanged from Module 11
└── frontend/
    ├── src/api/aiApi.ts                    — NEW: SSE consumption via fetch() + ReadableStream
    ├── src/components/QuestBreakdownPanel.tsx  — NEW: the streaming UI (idle/streaming/done/error)
    ├── src/components/QuestBreakdownPanel.test.tsx — NEW: 5 tests, fully mocked
    ├── src/pages/QuestDetailPage.tsx          — NEW: renders QuestBreakdownPanel, one new handler
    └── ...                                        — everything else unchanged from Module 11
```

## The feature, in one paragraph

Given one of the player's own quests, `POST /api/quests/{quest_id}/suggest-breakdown`
streams back Claude's suggestion of 2-4 concrete sub-quests. Before
finalizing an answer, Claude can call a real tool
(`check_existing_quest_titles`) to see the player's other quest titles, so
it avoids suggesting a duplicate — a genuine tool-use round-trip, not a
scripted one. The final answer is constrained to a JSON Schema
(`output_config.format`) and validated again with Pydantic before this
backend ever trusts it. Every turn of the round-trip — including the
tool-use turn — is streamed to the frontend, so the player sees real
progress the instant Claude starts generating, not a spinner followed by
everything appearing at once.

## Running it

```bash
cd module-13-building-with-llm-apis/project/questlog/backend
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # paste into .env's SECRET_KEY
# Optional -- only needed to run the AI feature live:
#   ANTHROPIC_API_KEY=sk-ant-your-real-key-here
uvicorn app.main:app --reload
```

With no `ANTHROPIC_API_KEY` set, every other route works exactly as it
did in Module 11, and `POST /api/quests/{id}/suggest-breakdown` returns a
clean `503` explaining why, rather than a confusing failure:

```bash
curl -i -X POST http://localhost:8000/api/quests/<id>/suggest-breakdown \
  -H "Authorization: Bearer <your token>"
```
**Expected** (no key configured):
```
HTTP/1.1 503 Service Unavailable
...
{"detail":"The AI assistant isn't configured. Set ANTHROPIC_API_KEY and restart the server."}
```

With a real key set, the same request streams back Server-Sent Events —
see the two capstone lessons for the full event sequence and what each
one means.

## Running the test suites (both still pass, no real API key required)

```bash
cd backend && python -m pytest -q     # expect: 46 passed (39 from Module 11 + 7 new AI-assistant tests)
cd ../frontend && npx vitest run       # expect: Tests  22 passed (22) (17 from Module 11 + 5 new)
```

Both suites were run for real while writing this module, from a clean
install, with `ANTHROPIC_API_KEY` unset the entire time — see the two
capstone lessons for the exact commands and real output.

## What's still unchanged

Everything about how QuestLog stores, serves, authenticates, caches,
containerizes, and deploys quests is exactly what Module 11 left it as —
this module adds one real, self-contained feature on top, reusing the
existing auth-scoped quest lookup (`get_quest_or_404`) and the existing
quest-list query (`repository.list_quests`) rather than introducing any
new database access, auth logic, or deployment step.
