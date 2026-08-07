/**
 * The Quest domain model.
 *
 * QuestLog has no real backend yet (that arrives in Module 05) -- this
 * type is the single source of truth for what a "quest" looks like while
 * everything lives in React state. Every component, the mock API, and the
 * context in this project import this exact type rather than re-declaring
 * their own shape, so a change here is a change everywhere.
 */

/** The three allowed priority levels. A union of string literals -- see
 * lessons/01-why-react-components-props-and-jsx.md and Module 03, Lesson 09
 * for how this differs from a plain `string`. */
export type Priority = "low" | "medium" | "high";

export interface Quest {
  /** A unique identifier. Generated with `crypto.randomUUID()` when a quest
   * is created -- see src/context/QuestsContext.tsx. */
  id: string;
  title: string;
  description: string;
  priority: Priority;
  /** Whether this quest has been completed. */
  done: boolean;
  /** The quest line (a named group of related quests) this quest belongs
   * to, e.g. "Main Story" or "Village Errands". A plain string, not a
   * union -- unlike priority, the set of quest lines is open-ended and
   * user-defined. */
  questLine: string;
  /** An ISO 8601 timestamp string (e.g. "2026-08-06T10:15:00.000Z"),
   * produced by `new Date().toISOString()`. Stored as a string, not a
   * `Date` object, because a `Date` object can't survive being sent as
   * JSON -- a habit worth having now, before Module 05 adds a real API. */
  createdAt: string;
}

/** The fields a caller supplies when creating a new quest. `id`, `done`,
 * and `createdAt` are always assigned by the app itself (see `addQuest` in
 * QuestsContext.tsx), never typed in by the user -- so this type
 * deliberately excludes them. */
export type NewQuestInput = Omit<Quest, "id" | "done" | "createdAt">;

/** The fields a caller is allowed to change on an existing quest. `id` and
 * `createdAt` are permanent once a quest is created. */
export type QuestUpdate = Partial<Omit<Quest, "id" | "createdAt">>;

export const PRIORITIES: Priority[] = ["low", "medium", "high"];
