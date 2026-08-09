/**
 * The quest-notes domain model -- NEW in Module 14. See
 * lessons/09-building-questlogs-notes-feature-frontend.md for the full
 * walkthrough.
 */

/** The shape `GET`/`POST /api/quests/{id}/notes` return -- matches
 * backend/app/models.py's `QuestNote` Pydantic model field for field.
 * Deliberately has no `content` field, mirroring that model's own
 * docstring reasoning: the notes list only ever needs a title and a
 * count, never the full text, just to render itself. */
export interface QuestNote {
  id: string;
  title: string;
  createdAt: string;
  chunkCount: number;
}

/** The body this frontend sends to `POST /api/quests/{id}/notes`. */
export interface NewNoteInput {
  title: string;
  content: string;
}
