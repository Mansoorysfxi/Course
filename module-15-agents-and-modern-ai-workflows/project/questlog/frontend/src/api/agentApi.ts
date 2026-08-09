import { getStoredToken } from "./http";

/**
 * NEW in Module 15 -- the frontend half of QuestLog's autonomous agent,
 * the course's final capstone feature. See
 * lessons/11-building-questlogs-agent-frontend-and-going-live.md for the
 * full walkthrough.
 *
 * Deliberately follows the exact same shape src/api/aiApi.ts (Module 13)
 * and src/api/notesApi.ts (Module 14) already established for a streamed
 * feature -- a hand-rolled `fetch()` + `ReadableStream` reader, never a
 * native `EventSource` (see aiApi.ts's own module docstring for why:
 * `EventSource` can't send the `Authorization` header this route
 * requires). This is the third time this exact SSE-parsing loop appears
 * in this frontend, unchanged in shape each time -- see lessons/11's own
 * "a fourth copy would be one too many" box for an honest discussion of
 * when repeating a pattern by hand stops paying for itself and a shared
 * helper would be the better call, and why this module still chooses not
 * to extract one, given this course's own scope.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/** One turn of the visible chat transcript -- the exact same shape
 * backend/app/models.py's `AgentChatMessage` describes, and the *entire*
 * memory this feature has (see that model's own docstring for the full,
 * honest accounting of what does and doesn't persist). */
export interface AgentMessage {
  role: "user" | "assistant";
  content: string;
}

/** Mirrors the event shapes backend/app/agent.py's `run_agent_turn`
 * yields and backend/app/routers/agent.py's `agent_chat` writes onto the
 * wire as SSE. Snake_case field names on purpose, the same choice
 * src/api/aiApi.ts's `BreakdownEvent` and src/api/notesApi.ts's
 * `AskEvent` already made -- these are raw SSE payloads, not a
 * Pydantic-validated, alias-converted JSON response body. */
export interface AgentEvent {
  event: "token" | "tool_call" | "sources" | "usage" | "result" | "error";
  data: {
    text?: string;
    tool?: string;
    input?: Record<string, unknown>;
    sources?: { note_id: string; note_title: string; excerpt: string }[];
    iterations?: number;
    tool_calls?: number;
    answer?: string;
    message?: string;
  };
}

export async function* streamAgentChat(messages: AgentMessage[]): AsyncGenerator<AgentEvent> {
  const token = getStoredToken();

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/agent/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ messages }),
    });
  } catch {
    throw new Error(
      "Could not reach the QuestLog API. Is the FastAPI backend running on " + `${API_BASE_URL}?`,
    );
  }

  if (response.status === 503) {
    throw new Error("The agent isn't configured on this server yet.");
  }
  if (!response.ok || response.body === null) {
    throw new Error(`The agent request failed (status ${response.status}).`);
  }

  // See src/api/aiApi.ts's `streamQuestBreakdown` for a line-by-line
  // explanation of every piece of this loop -- identical here on purpose.
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
          event: eventLine.slice("event: ".length) as AgentEvent["event"],
          data: JSON.parse(dataLine.slice("data: ".length)),
        };
      }

      boundary = buffer.indexOf("\n\n");
    }
  }
}
