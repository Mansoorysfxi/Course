import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router";
import { useQuests } from "../context/QuestsContext";
import { QuestForm } from "../components/QuestForm";
import { PriorityBadge } from "../components/PriorityBadge";
import type { NewQuestInput } from "../types/quest";

/** View, edit, complete, or delete a single quest. The `:id` in this
 * route's path (App.tsx) is read with `useParams` -- see
 * lessons/08-react-router.md. */
export function QuestDetailPage() {
  // `useParams` returns whatever the router matched for each `:name`
  // segment in the current route's path, always as strings (URLs are
  // text) -- there's no automatic conversion to a number, boolean, etc.
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { getQuest, updateQuest, deleteQuest, toggleDone } = useQuests();
  const [isEditing, setIsEditing] = useState(false);

  const quest = id ? getQuest(id) : undefined;

  if (!quest) {
    return (
      <div className="py-16 text-center">
        <h1 className="text-xl font-semibold text-slate-900">Quest not found</h1>
        <p className="mt-2 text-slate-500">It may have been deleted, or the link is wrong.</p>
        <Link to="/" className="mt-4 inline-block text-indigo-600 hover:underline">
          Back to the Quest Board
        </Link>
      </div>
    );
  }

  // These are `const` arrow functions, defined *after* the `if (!quest)`
  // guard above, rather than hoisted `function` declarations -- that's
  // deliberate, not just a style choice: TypeScript only keeps trusting
  // that `quest` is a real `Quest` (not `Quest | undefined`) inside a
  // closure when the closure is a `const` created after the narrowing
  // check in the code's actual top-to-bottom flow. A hoisted `function
  // handleUpdate() {}` here would make `tsc` complain that `quest` might
  // still be `undefined` inside it, even though by the time either of
  // these is ever actually called, the component would already have
  // returned early above if `quest` were missing.
  // Both async now (Module 05) -- updateQuest/deleteQuest make real PATCH/
  // DELETE requests (src/context/QuestsContext.tsx) instead of only
  // updating local state; awaiting each one means the UI only reflects
  // "saved"/"deleted" once the backend has actually confirmed it.
  const handleUpdate = async (values: NewQuestInput) => {
    await updateQuest(quest.id, values);
    setIsEditing(false);
  };

  const handleDelete = async () => {
    const confirmed = window.confirm(`Delete "${quest.title}"? This can't be undone.`);
    if (confirmed) {
      await deleteQuest(quest.id);
      navigate("/");
    }
  };

  if (isEditing) {
    return (
      <div className="mx-auto max-w-lg">
        <h1 className="mb-6 text-2xl font-bold text-slate-900">Edit Quest</h1>
        <QuestForm
          initialValues={{
            title: quest.title,
            description: quest.description,
            priority: quest.priority,
            questLine: quest.questLine,
          }}
          submitLabel="Save Changes"
          onSubmit={handleUpdate}
          onCancel={() => setIsEditing(false)}
        />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-lg">
      <div className="mb-4 flex items-start justify-between gap-4">
        <h1
          className={`text-2xl font-bold ${quest.done ? "text-slate-400 line-through" : "text-slate-900"}`}
        >
          {quest.title}
        </h1>
        <PriorityBadge priority={quest.priority} />
      </div>

      <p className="mb-1 text-xs font-medium uppercase tracking-wide text-slate-400">
        {quest.questLine}
      </p>
      <p className="mb-6 whitespace-pre-wrap text-slate-700">{quest.description}</p>

      <div className="mb-6 flex items-center gap-2">
        <input
          id="done"
          type="checkbox"
          checked={quest.done}
          onChange={() => toggleDone(quest.id)}
          className="h-4 w-4 accent-indigo-600"
        />
        <label htmlFor="done" className="text-sm text-slate-600">
          Mark as done
        </label>
      </div>

      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setIsEditing(true)}
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
        >
          Edit
        </button>
        <button
          type="button"
          onClick={handleDelete}
          className="rounded-md border border-rose-300 px-4 py-2 text-sm font-medium text-rose-700 hover:bg-rose-50"
        >
          Delete
        </button>
        <Link
          to="/"
          className="ml-auto rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Back
        </Link>
      </div>
    </div>
  );
}
