import type { NewQuestInput, Quest, QuestUpdate } from "../types/quest";

/**
 * Module 05 replaces this file's predecessor, `fetchQuests.ts` (a fake
 * Promise + setTimeout, per Module 04's BRIEF.md), with real `fetch()`
 * calls to the FastAPI backend built in this module -- see
 * lessons/08-building-the-questlog-api.md for the server-side routes this
 * file calls, and Module 03, Lesson 07 for the fetch()/Promise/async-await
 * mechanics this file relies on throughout.
 *
 * `import.meta.env.VITE_API_BASE_URL` is Vite's own convention for an
 * environment variable (Module 00's own term, extended here) that's safe
 * to expose to client-side code: any variable in a project's `.env` file
 * whose name starts with `VITE_` gets bundled into the built app and is
 * readable via `import.meta.env` -- everything else in `.env` stays
 * server/build-only and is never shipped to the browser. See `.env` in
 * this project's root for where this is actually set.
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/**
 * Turns a non-OK fetch Response into a thrown Error with a useful message,
 * pulled from the backend's own `{"detail": ...}` shape when possible
 * (Lesson 03's/Lesson 06's error shape) -- exactly the `response.ok` check
 * Module 03, Lesson 07 taught you never to skip, since fetch()'s own
 * Promise resolves even for a 404/500 response.
 */
async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body?.detail === "string") {
      return body.detail;
    }
    if (Array.isArray(body?.detail)) {
      // FastAPI's automatic 422 validation-error shape (Lesson 03) --
      // detail is a list of {type, loc, msg, input} objects.
      return body.detail.map((item: { msg?: string }) => item.msg).join("; ");
    }
  } catch {
    // Body wasn't JSON at all -- fall through to the generic message below.
  }
  return `Request failed with status ${response.status}.`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    // The fetch() call itself failed -- almost always the backend isn't
    // running, or CORS blocked it (see lessons/00-setup.md Step 6 and
    // lessons/05-middleware.md's CORS note).
    throw new Error(
      "Could not reach the QuestLog API. Is the FastAPI backend running on " +
        `${API_BASE_URL}? See backend/README.md.`
    );
  }

  if (!response.ok) {
    throw new Error(await parseErrorMessage(response));
  }

  if (response.status === 204) {
    // DELETE returns 204 No Content (Lesson 06) -- no body to parse at all.
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function fetchQuests(): Promise<Quest[]> {
  return request<Quest[]>("/api/quests");
}

export function fetchQuest(id: string): Promise<Quest> {
  return request<Quest>(`/api/quests/${id}`);
}

export function createQuest(input: NewQuestInput): Promise<Quest> {
  return request<Quest>("/api/quests", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateQuest(id: string, changes: QuestUpdate): Promise<Quest> {
  return request<Quest>(`/api/quests/${id}`, {
    method: "PATCH",
    body: JSON.stringify(changes),
  });
}

export function deleteQuest(id: string): Promise<void> {
  return request<void>(`/api/quests/${id}`, { method: "DELETE" });
}
