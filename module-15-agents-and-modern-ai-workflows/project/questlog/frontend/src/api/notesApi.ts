import { getStoredToken, request } from "./http";
import type { NewNoteInput, QuestNote } from "../types/note";

/**
 * NEW in Module 14 -- the frontend half of "chat with your quest notes."
 * See lessons/09-building-questlogs-notes-feature-frontend.md for the full
 * walkthrough.
 *
 * `createNote`/`listNotes`/`deleteNote` are plain JSON requests, so they go
 * through the shared `request()` helper (src/api/http.ts) exactly like
 * every function in src/api/questsApi.ts. `streamAskQuestion` is a
 * streamed Server-Sent Events response, so it does NOT use `request()` --
 * see src/api/aiApi.ts's own module docstring for the full explanation of
 * why a streamed response needs its own hand-rolled `fetch()` +
 * `ReadableStream` reader (never a native `EventSource`, which can't send
 * the `Authorization` header every protected route in this app requires),
 * and this file's `streamAskQuestion` below reuses that exact same
 * parsing shape, deliberately, rather than inventing a second one.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function createNote(questId: string, data: NewNoteInput): Promise<QuestNote> {
  return request<QuestNote>(`/api/quests/${questId}/notes`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function listNotes(questId: string): Promise<QuestNote[]> {
  return request<QuestNote[]>(`/api/quests/${questId}/notes`);
}

export async function deleteNote(questId: string, noteId: string): Promise<void> {
  await request<void>(`/api/quests/${questId}/notes/${noteId}`, { method: "DELETE" });
}

/** Mirrors the raw event shapes backend/app/rag.py's `stream_note_answer`
 * yields and backend/app/routers/notes.py's `ask_question` writes onto
 * the wire as SSE -- deliberately kept in the backend's own snake_case
 * field names (`note_id`, not `noteId`), the same choice src/api/aiApi.ts's
 * `BreakdownEvent` already made for `sub_quests`: these are raw SSE
 * payloads, not a Pydantic-validated, alias-converted JSON body, so there
 * is no `camelCase` contract here to match in the first place. */
export interface AskEvent {
  event: "sources" | "token" | "result" | "error";
  data: {
    sources?: { note_id: string; note_title: string; chunk_index: number; excerpt: string }[];
    text?: string;
    answer?: string;
    message?: string;
  };
}

export async function* streamAskQuestion(
  questId: string,
  question: string,
): AsyncGenerator<AskEvent> {
  const token = getStoredToken();

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/quests/${questId}/notes/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ question }),
    });
  } catch {
    throw new Error(
      "Could not reach the QuestLog API. Is the FastAPI backend running on " + `${API_BASE_URL}?`,
    );
  }

  if (response.status === 503) {
    throw new Error("The notes assistant isn't configured on this server yet.");
  }
  if (!response.ok || response.body === null) {
    throw new Error(`The question request failed (status ${response.status}).`);
  }

  // See src/api/aiApi.ts's `streamQuestBreakdown` for a line-by-line
  // explanation of every piece of this loop -- the SSE-parsing logic
  // itself is identical on purpose (one seam for "how to read an SSE
  // response body," reused here rather than re-derived).
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });

    let boundary = buffer.indexOf("\n\n");
    while (boundary !== -1) {
      const rawEvent = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);

      const eventLine = rawEvent.split("\n").find((line) => line.startsWith("event: "));
      const dataLine = rawEvent.split("\n").find((line) => line.startsWith("data: "));
      if (eventLine && dataLine) {
        yield {
          event: eventLine.slice("event: ".length) as AskEvent["event"],
          data: JSON.parse(dataLine.slice("data: ".length)),
        };
      }

      boundary = buffer.indexOf("\n\n");
    }
  }
}
