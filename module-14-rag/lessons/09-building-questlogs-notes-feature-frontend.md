# Lesson 09 — Building QuestLog's Notes Feature: Frontend

## What you'll learn

- The frontend shape of "chat with your quest notes": `src/types/note.ts`,
  `src/api/notesApi.ts`, and `src/components/QuestNotesPanel.tsx`.
- How this feature reuses Module 13's streaming pattern for a new SSE
  event shape, without inventing a second way to parse Server-Sent
  Events.
- How the UI shows citations, and every loading/streaming/error state a
  real feature needs.

## Why this matters

The backend (Lesson 08) is only half a feature until a player can
actually use it. This lesson closes the loop, exactly the way Module 13,
Lesson 08 did for the quest-breakdown assistant — same conventions,
extended to this module's own new event shape (`sources`, not
`tool_call`).

## Prerequisites

- **Module 13, Lesson 08** — `QuestBreakdownPanel.tsx` and `src/api/aiApi.ts`
  are this lesson's direct template; this lesson assumes you understand
  that streaming pattern already.
- **Lesson 08** — the backend routes and event shapes this frontend
  consumes.
- **Module 04's hooks lessons** — `useState`, `useEffect`, and the
  dependency-array discipline this component relies on.

## The concept, explained simply

This is the same "component collects input, streams a response, updates
its own state machine one event at a time" pattern Module 13 already
taught — applied to a new feature with one real addition: a `sources`
event that has to render *before* any answer text, so a player sees what
was retrieved before they see what Claude says about it.

## The details

### `src/types/note.ts`

```typescript
export interface QuestNote {
  id: string;
  title: string;
  createdAt: string;
  chunkCount: number;
}
export interface NewNoteInput {
  title: string;
  content: string;
}
```

Matches the backend's `QuestNote` Pydantic model field for field —
notice there is no `content` field here either, mirroring that model's
own docstring reasoning (Lesson 08): the notes list only ever needs a
title and a chunk count to render itself.

### `src/api/notesApi.ts`

Three plain JSON functions go through the shared `request()` helper
(`src/api/http.ts`), exactly like every function in `questsApi.ts`:

```typescript
export function createNote(questId: string, data: NewNoteInput): Promise<QuestNote> { ... }
export function listNotes(questId: string): Promise<QuestNote[]> { ... }
export function deleteNote(questId: string, noteId: string): Promise<void> { ... }
```

`streamAskQuestion`, the fourth function, is a streamed SSE response, so
it does **not** use `request()` — for the exact reason `src/api/aiApi.ts`'s
own module docstring already gave in Module 13: a native `EventSource`
can only send `GET` requests and cannot set custom headers, so it has no
way to attach this app's `Authorization: Bearer <token>` header, which
every protected route (this one included) requires. `streamAskQuestion`
reuses the exact same hand-rolled `fetch()` + `ReadableStream` reader +
buffer-until-blank-line parsing loop `streamQuestBreakdown` already
established — deliberately the same code shape, not a second, slightly
different way to read an SSE response.

The one new thing is the event shape itself:

```typescript
export interface AskEvent {
  event: "sources" | "token" | "result" | "error";
  data: {
    sources?: { note_id: string; note_title: string; chunk_index: number; excerpt: string }[];
    text?: string;
    answer?: string;
    message?: string;
  };
}
```

Notice `sources` keeps the backend's own snake_case field names
(`note_id`, not `noteId`) — the same choice `BreakdownEvent`'s
`sub_quests` already made in Module 13: these are raw SSE payloads, never
run through a Pydantic model with camelCase aliases on the backend
(`app/rag.py`'s own module docstring explains why — it's a plain,
hand-built dict, not an API response model), so there's no camelCase
contract to match here either.

### `QuestNotesPanel.tsx`: the state machine

Three pieces of state live in this one component, because they share one
thing: the notes list.

1. **The notes list itself** — loaded once on mount (and whenever
   `questId` changes) via `useEffect` + `listNotes`, with the standard
   loading/ready/error three-state pattern Module 04 already taught.
2. **The add-note form** — `createNote`, then append the result directly
   to local state, so a newly added note appears immediately without a
   second fetch.
3. **The ask-a-question flow** — the streaming state machine:

```typescript
for await (const event of streamAskQuestion(questId, question)) {
  if (event.event === "sources" && event.data.sources) {
    setSources(...)
  } else if (event.event === "token" && event.data.text !== undefined) {
    setStreamedAnswer((current) => current + event.data.text);
  } else if (event.event === "result") {
    setAskStatus("done");
  } else if (event.event === "error") {
    setAskError(event.data.message ?? "Something went wrong.");
    setAskStatus("error");
  }
}
```

Exactly the same `for await...of` shape `QuestBreakdownPanel` already
uses — every event updates exactly the one piece of state it owns, and
this component never needs to know anything about Server-Sent Events or
byte decoding itself; that's sealed inside `streamAskQuestion`.

### Rendering sources before the answer

The UI renders the sources list as soon as it arrives — *before* any
answer text exists yet, since the `sources` event always arrives first
(Lesson 06). This is a small but deliberate UI choice that mirrors the
backend's own citation design (Lesson 06's "citations you can trust")
: a player sees *what was found* immediately, and can already judge
whether it looks relevant, even before Claude's prose finishes
streaming in.

### Optimistic delete

`handleDeleteNote` removes a note from local state immediately, then
calls `deleteNote`, restoring the previous list only if the request
actually fails:

```typescript
const previous = notes;
setNotes((current) => current.filter((note) => note.id !== noteId));
try {
  await deleteNote(questId, noteId);
} catch (err) {
  setNotes(previous);
  setNotesError(...);
}
```

This is safe here specifically because deleting a note has no side
effect a player would need to see mid-flight (unlike, say, a payment) —
a failed delete simply restores the note, with an error message
explaining why.

## Common mistakes & gotchas

- **Reaching for `EventSource` for the ask-a-question stream.** It can't
  send the `Authorization` header this route requires — the same
  limitation Module 13 already hit, solved the same way (a hand-rolled
  `fetch()` + reader).
- **Mixing up `sources`' snake_case field names with the rest of this
  app's camelCase convention.** `note_id`/`note_title`/`chunk_index` are
  correct here — they're raw SSE payload fields, not a Pydantic-aliased
  REST response.
- **Rendering the answer text before checking `sources.length > 0`.**
  Since `sources` always arrives first in a successful response, there's
  rarely a real ordering bug here — but a test that only checks for
  answer text without also asserting `sources` arrived first would miss
  a real regression if that ordering ever broke.
- **Forgetting the `cancelled` flag in the notes-loading `useEffect`.**
  Without it, navigating away from a quest's detail page while its notes
  are still loading could call `setState` on an unmounted component —
  the exact same pattern Module 04's data-fetching lesson already taught
  for this reason.

## How this connects

This lesson completes QuestLog's "chat with your quest notes" feature,
end to end — from a player typing a note, through chunking, embedding,
storage, retrieval, and a cited, streamed answer, all the way back to
the screen. This module's own capstone project brief
(`project/BRIEF.md`) is this exact feature, built and verified by you.

## Quick self-check

1. Why does `streamAskQuestion` not use the shared `request()` helper the
   way `listNotes`/`createNote`/`deleteNote` do?
2. Why does `AskEvent`'s `sources` field use snake_case keys instead of
   this app's usual camelCase?
3. What does the UI do differently, in terms of rendering order, because
   `sources` always arrives before any answer text?
4. Why is optimistic deletion a reasonable choice for notes specifically,
   when it might not be for every kind of delete?
5. What would happen if the `cancelled` flag were removed from the
   notes-loading `useEffect`, and a player navigated away mid-load?
