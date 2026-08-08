import { request } from "./http";
import type { NewQuestInput, Quest, QuestUpdate } from "../types/quest";

/**
 * Every /api/quests call this frontend makes. Unchanged in *shape* since
 * Module 05 -- same five functions, same paths, same methods -- but now
 * built on the shared `request()` in src/api/http.ts (new in Module 07)
 * instead of a private copy of that same function living only in this
 * file. See http.ts's own module docstring for why it moved, and
 * lessons/06-building-signup-login.md for what `request()` now does that
 * it didn't in Module 06: attach this frontend's stored JWT, if any, to
 * every one of these calls automatically. Every route these functions
 * call is now **protected** on the backend (backend/app/routers/quests.py)
 * -- calling any of these without first logging in fails with a 401,
 * which `request()` turns into an `UnauthorizedError` (http.ts).
 */

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
