import { useEffect, useState } from "react";
import { createNote, deleteNote, listNotes, streamAskQuestion } from "../api/notesApi";
import type { AskEvent } from "../api/notesApi";
import type { QuestNote } from "../types/note";

interface QuestNotesPanelProps {
  questId: string;
}

type NotesLoadStatus = "loading" | "ready" | "error";
type AskStatus = "idle" | "asking" | "done" | "error";

interface AskSource {
  noteId: string;
  noteTitle: string;
  chunkIndex: number;
  excerpt: string;
}

/**
 * NEW in Module 14 -- "chat with your quest notes," QuestLog's second real
 * AI feature. See lessons/09-building-questlogs-notes-feature-frontend.md
 * for the full walkthrough of every state transition below.
 *
 * Three pieces of UI live in this one component, each with its own loading/
 * error state, following the same conventions QuestBreakdownPanel (Module
 * 13) already established for a single streamed feature: (1) a list of
 * existing notes, loaded on mount; (2) a form to add a new note; (3) a
 * question box that streams a cited answer. Kept as one component rather
 * than three, because all three genuinely share one piece of state (the
 * notes list -- adding a note needs to appear in it immediately, and the
 * question box's whole point depends on that same list being non-empty).
 */
export function QuestNotesPanel({ questId }: QuestNotesPanelProps) {
  const [notes, setNotes] = useState<QuestNote[]>([]);
  const [notesStatus, setNotesStatus] = useState<NotesLoadStatus>("loading");
  const [notesError, setNotesError] = useState("");

  const [newTitle, setNewTitle] = useState("");
  const [newContent, setNewContent] = useState("");
  const [isSavingNote, setIsSavingNote] = useState(false);
  const [saveError, setSaveError] = useState("");

  const [question, setQuestion] = useState("");
  const [askStatus, setAskStatus] = useState<AskStatus>("idle");
  const [sources, setSources] = useState<AskSource[]>([]);
  const [streamedAnswer, setStreamedAnswer] = useState("");
  const [askError, setAskError] = useState("");

  // Loads this quest's notes once, when the component first mounts (or
  // `questId` changes -- e.g. navigating from one quest's detail page
  // straight to another's). See lessons/07-data-fetching-loading-and-error-states.md
  // (Module 04) for the "declare the dependency array honestly" habit this
  // effect follows -- `questId` is the only outside value this effect's
  // body actually reads.
  useEffect(() => {
    let cancelled = false;
    setNotesStatus("loading");
    listNotes(questId)
      .then((loaded) => {
        if (!cancelled) {
          setNotes(loaded);
          setNotesStatus("ready");
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setNotesError(err instanceof Error ? err.message : "Could not load notes.");
          setNotesStatus("error");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [questId]);

  async function handleAddNote(event: React.FormEvent) {
    event.preventDefault();
    setIsSavingNote(true);
    setSaveError("");
    try {
      const created = await createNote(questId, { title: newTitle, content: newContent });
      setNotes((current) => [...current, created]);
      setNewTitle("");
      setNewContent("");
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "Could not save this note.");
    } finally {
      setIsSavingNote(false);
    }
  }

  async function handleDeleteNote(noteId: string) {
    const previous = notes;
    // Optimistic removal -- see lessons/09's own "optimistic vs. confirmed
    // updates" box for why this is safe here specifically: a failed delete
    // just restores the note to the list below, and nothing about deleting
    // a note has any side effect a player would need to see mid-flight
    // (unlike, say, a payment).
    setNotes((current) => current.filter((note) => note.id !== noteId));
    try {
      await deleteNote(questId, noteId);
    } catch (err) {
      setNotes(previous);
      setNotesError(err instanceof Error ? err.message : "Could not delete this note.");
      setNotesStatus("error");
    }
  }

  async function handleAsk(event: React.FormEvent) {
    event.preventDefault();
    setAskStatus("asking");
    setSources([]);
    setStreamedAnswer("");
    setAskError("");

    try {
      for await (const evt of streamAskQuestion(questId, question)) {
        applyAskEvent(evt);
      }
    } catch (err) {
      setAskError(err instanceof Error ? err.message : "Something went wrong.");
      setAskStatus("error");
    }
  }

  function applyAskEvent(event: AskEvent) {
    if (event.event === "sources" && event.data.sources) {
      setSources(
        event.data.sources.map((source) => ({
          noteId: source.note_id,
          noteTitle: source.note_title,
          chunkIndex: source.chunk_index,
          excerpt: source.excerpt,
        })),
      );
    } else if (event.event === "token" && event.data.text !== undefined) {
      setStreamedAnswer((current) => current + event.data.text);
    } else if (event.event === "result") {
      setAskStatus("done");
    } else if (event.event === "error") {
      setAskError(event.data.message ?? "Something went wrong.");
      setAskStatus("error");
    }
  }

  return (
    <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50/40 p-4">
      <h2 className="mb-3 text-sm font-semibold text-emerald-900">Quest Notes</h2>

      {notesStatus === "loading" && <p className="text-sm text-slate-500">Loading notes...</p>}
      {notesStatus === "error" && <p className="text-sm text-rose-700">{notesError}</p>}

      {notesStatus === "ready" && (
        <>
          <ul className="mb-4 flex flex-col gap-2">
            {notes.length === 0 && (
              <li className="text-sm text-slate-500">No notes yet. Add one below.</li>
            )}
            {notes.map((note) => (
              <li
                key={note.id}
                className="flex items-center justify-between gap-2 rounded-md bg-white px-3 py-2 text-sm"
              >
                <span>
                  {note.title}{" "}
                  <span className="text-xs text-slate-400">
                    ({note.chunkCount} chunk{note.chunkCount === 1 ? "" : "s"})
                  </span>
                </span>
                <button
                  type="button"
                  onClick={() => handleDeleteNote(note.id)}
                  className="text-xs font-medium text-rose-700 hover:underline"
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>

          <form onSubmit={handleAddNote} className="mb-6 flex flex-col gap-2">
            <input
              value={newTitle}
              onChange={(event) => setNewTitle(event.target.value)}
              placeholder="Note title (e.g. Boss Fight Prep)"
              required
              className="rounded-md border border-slate-300 px-3 py-1.5 text-sm"
            />
            <textarea
              value={newContent}
              onChange={(event) => setNewContent(event.target.value)}
              placeholder="Paste or type your note here..."
              required
              rows={3}
              className="rounded-md border border-slate-300 px-3 py-1.5 text-sm"
            />
            {saveError && <p className="text-sm text-rose-700">{saveError}</p>}
            <button
              type="submit"
              disabled={isSavingNote}
              className="self-start rounded-md bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSavingNote ? "Saving..." : "Add Note"}
            </button>
          </form>

          <form onSubmit={handleAsk} className="flex flex-col gap-2">
            <label htmlFor="question" className="text-xs font-medium text-emerald-900">
              Ask a question about your notes
            </label>
            <div className="flex gap-2">
              <input
                id="question"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="What armor should I bring?"
                required
                className="flex-1 rounded-md border border-slate-300 px-3 py-1.5 text-sm"
              />
              <button
                type="submit"
                disabled={askStatus === "asking"}
                className="rounded-md bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {askStatus === "asking" ? "Thinking..." : "Ask"}
              </button>
            </div>

            {sources.length > 0 && (askStatus === "asking" || askStatus === "done") && (
              <div className="rounded-md bg-white p-2 text-xs text-slate-600">
                <p className="mb-1 font-semibold">Sources:</p>
                <ul className="list-inside list-disc">
                  {sources.map((source) => (
                    <li key={`${source.noteId}-${source.chunkIndex}`}>
                      "{source.noteTitle}": {source.excerpt}
                      {source.excerpt.length >= 150 ? "..." : ""}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {(askStatus === "asking" || askStatus === "done") && (
              <p
                role="status"
                aria-label="Notes assistant answer"
                className="whitespace-pre-wrap rounded-md bg-white p-2 text-sm text-slate-700"
              >
                {streamedAnswer || "Thinking..."}
              </p>
            )}

            {askStatus === "error" && <p className="text-sm text-rose-700">{askError}</p>}
          </form>
        </>
      )}
    </div>
  );
}
