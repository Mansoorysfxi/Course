import { getStoredToken } from "./http";

/**
 * NEW in Module 13 -- the frontend half of the AI assistant feature. See
 * lessons/08-building-questlogs-ai-assistant-frontend.md for the full,
 * line-by-line walkthrough.
 *
 * Deliberately a **separate** file from src/api/http.ts's `request()`,
 * not a sixth function bolted onto questsApi.ts. `request()`'s entire job
 * is "make one JSON request, parse one JSON response" -- a *streamed*
 * response is a genuinely different shape of problem (an open connection
 * you read from repeatedly, not a single value you await once), so
 * reusing `request()` here would mean adding a `stream?: boolean` branch
 * to a function that's simple today precisely because it doesn't have
 * one. A native browser `EventSource` (the usual way to consume
 * Server-Sent Events) was **not** used here for a specific, real reason:
 * `EventSource` can only send GET requests and cannot set custom headers
 * at all, so it has no way to attach this app's `Authorization: Bearer
 * <token>` header -- and every /api/quests route, this new one included,
 * requires that header. `fetch()` with its own `ReadableStream` body has
 * no such limitation, which is exactly why this file exists instead of
 * using `EventSource`.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/** Mirrors the event shapes app/ai_assistant.py's `stream_quest_breakdown`
 * yields and app/routers/quests.py's `suggest_quest_breakdown` writes onto
 * the wire as SSE -- see this file's own module docstring, and the
 * backend files' docstrings, for what each event name means. */
export interface BreakdownEvent {
  event: "token" | "tool_call" | "result" | "error";
  data: {
    text?: string;
    tool?: string;
    sub_quests?: string[];
    message?: string;
  };
}

/**
 * An async generator -- `function*` with `async`, so callers write
 * `for await (const event of streamQuestBreakdown(id)) { ... }` (see
 * src/components/QuestBreakdownPanel.tsx) instead of manually managing a
 * reader and a buffer themselves. This function is the *only* place in
 * this frontend that knows the raw SSE wire format (two lines per event,
 * `event: <name>` then `data: <json>`, a blank line between events) --
 * exactly the same "one seam" discipline src/api/http.ts already applies
 * to plain JSON requests.
 */
export async function* streamQuestBreakdown(questId: string): AsyncGenerator<BreakdownEvent> {
  const token = getStoredToken();

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/quests/${questId}/suggest-breakdown`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
  } catch {
    throw new Error(
      "Could not reach the QuestLog API. Is the FastAPI backend running on " + `${API_BASE_URL}?`,
    );
  }

  if (response.status === 503) {
    throw new Error("The AI assistant isn't configured on this server yet.");
  }
  if (!response.ok || response.body === null) {
    throw new Error(`The AI assistant request failed (status ${response.status}).`);
  }

  // `response.body` is a `ReadableStream<Uint8Array>` -- raw bytes, not
  // text and not JSON. `TextDecoder` turns each chunk of bytes into a
  // string; `{ stream: true }` tells it a multi-byte character might be
  // split across two chunks, so it should hold onto any incomplete
  // trailing bytes and prepend them to the next chunk instead of
  // producing corrupted or replacement characters.
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });

    // A complete SSE event ends with a blank line ("\n\n"). A single
    // chunk from `reader.read()` might contain zero, one, or several
    // complete events, plus the start of one that isn't finished yet --
    // this loop drains every *complete* event currently in `buffer` and
    // leaves any trailing partial event there to be completed by a later
    // chunk.
    let boundary = buffer.indexOf("\n\n");
    while (boundary !== -1) {
      const rawEvent = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);

      const eventLine = rawEvent.split("\n").find((line) => line.startsWith("event: "));
      const dataLine = rawEvent.split("\n").find((line) => line.startsWith("data: "));
      if (eventLine && dataLine) {
        yield {
          event: eventLine.slice("event: ".length) as BreakdownEvent["event"],
          data: JSON.parse(dataLine.slice("data: ".length)),
        };
      }

      boundary = buffer.indexOf("\n\n");
    }
  }
}
