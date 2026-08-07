import { useState, type FormEvent } from "react";
import { PRIORITIES, type NewQuestInput, type Priority } from "../types/quest";

interface QuestFormProps {
  /** Pre-filled values when editing an existing quest; omitted when
   * creating a new one. */
  initialValues?: NewQuestInput;
  submitLabel: string;
  onSubmit: (values: NewQuestInput) => void;
  onCancel?: () => void;
}

const emptyValues: NewQuestInput = {
  title: "",
  description: "",
  priority: "medium",
  questLine: "",
};

/**
 * A single, reusable, controlled form for both creating and editing a
 * quest. "Controlled" means every field's value lives in React state
 * (below) and is fed back into the input via its `value` prop -- the input
 * never holds its own hidden value the way an uncontrolled HTML input
 * would. See lessons/05-forms-controlled-components-and-lifting-state.md.
 *
 * This component knows nothing about QuestsContext, `addQuest`, or
 * `updateQuest` -- it only knows how to collect a `NewQuestInput` and hand
 * it to whoever rendered it, via the `onSubmit` prop. NewQuestPage and
 * QuestDetailPage decide what actually happens with that data. This is
 * the same "lift state up to the nearest shared owner" idea the lesson
 * teaches, just applied one level further: the form *itself* doesn't own
 * the result of submitting it.
 */
export function QuestForm({ initialValues, submitLabel, onSubmit, onCancel }: QuestFormProps) {
  const [values, setValues] = useState<NewQuestInput>(initialValues ?? emptyValues);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(values);
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div>
        <label htmlFor="title" className="mb-1 block text-sm font-medium text-slate-700">
          Title
        </label>
        <input
          id="title"
          type="text"
          required
          value={values.title}
          onChange={(e) => setValues({ ...values, title: e.target.value })}
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label htmlFor="description" className="mb-1 block text-sm font-medium text-slate-700">
          Description
        </label>
        <textarea
          id="description"
          required
          rows={3}
          value={values.description}
          onChange={(e) => setValues({ ...values, description: e.target.value })}
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label htmlFor="priority" className="mb-1 block text-sm font-medium text-slate-700">
            Priority
          </label>
          <select
            id="priority"
            value={values.priority}
            onChange={(e) => setValues({ ...values, priority: e.target.value as Priority })}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            {PRIORITIES.map((priority) => (
              <option key={priority} value={priority}>
                {priority.charAt(0).toUpperCase() + priority.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="questLine" className="mb-1 block text-sm font-medium text-slate-700">
            Quest line
          </label>
          <input
            id="questLine"
            type="text"
            required
            placeholder="e.g. Main Story, Village Errands"
            value={values.questLine}
            onChange={(e) => setValues({ ...values, questLine: e.target.value })}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>

      <div className="flex gap-2 pt-2">
        <button
          type="submit"
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
        >
          {submitLabel}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
