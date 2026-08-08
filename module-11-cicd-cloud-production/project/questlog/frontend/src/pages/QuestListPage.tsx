import { useState } from "react";
import { useQuests } from "../context/QuestsContext";
import { QuestCard } from "../components/QuestCard";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { ErrorBanner } from "../components/ErrorBanner";
import { PRIORITIES, type Priority } from "../types/quest";

type DoneFilter = "all" | "done" | "not-done";
type SortField = "createdAt" | "priority" | "title";

const PRIORITY_WEIGHT: Record<Priority, number> = { high: 0, medium: 1, low: 2 };

/** The Quest Board -- the app's home page. Fetches (via QuestsContext),
 * filters, and sorts quests, and renders the loading/error/success states
 * for that data. See lessons/07-data-fetching-loading-and-error-states.md. */
export function QuestListPage() {
  const { quests, loading, error, refetch, toggleDone } = useQuests();

  // Filter/sort controls are local UI state -- they belong to this page
  // only, nothing else in the app needs them, so they do NOT belong in
  // QuestsContext. Contrast with `quests` itself, which several pages
  // need and therefore does live in context. This distinction --
  // "does more than one component need this?" -- is exactly what
  // lessons/05-forms-controlled-components-and-lifting-state.md and
  // lessons/06-context.md ask you to check before reaching for context.
  const [questLineFilter, setQuestLineFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState<Priority | "all">("all");
  const [doneFilter, setDoneFilter] = useState<DoneFilter>("all");
  const [sortField, setSortField] = useState<SortField>("createdAt");

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorBanner message={error} onRetry={refetch} />;
  }

  const questLines = Array.from(new Set(quests.map((quest) => quest.questLine))).sort();

  const visibleQuests = quests
    .filter((quest) => questLineFilter === "all" || quest.questLine === questLineFilter)
    .filter((quest) => priorityFilter === "all" || quest.priority === priorityFilter)
    .filter((quest) => {
      if (doneFilter === "all") return true;
      return doneFilter === "done" ? quest.done : !quest.done;
    })
    .sort((a, b) => {
      if (sortField === "title") return a.title.localeCompare(b.title);
      if (sortField === "priority")
        return PRIORITY_WEIGHT[a.priority] - PRIORITY_WEIGHT[b.priority];
      // "createdAt" -- newest first. ISO 8601 strings sort correctly as
      // plain strings, so no Date parsing is even needed here.
      return b.createdAt.localeCompare(a.createdAt);
    });

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Quest Board</h1>
        <p className="text-sm text-slate-500">
          {visibleQuests.length} of {quests.length} quest{quests.length === 1 ? "" : "s"} shown
        </p>
      </div>

      <div className="mb-6 flex flex-wrap gap-3 rounded-lg border border-slate-200 bg-white p-4">
        <label className="flex items-center gap-2 text-sm text-slate-600">
          Quest line
          <select
            value={questLineFilter}
            onChange={(e) => setQuestLineFilter(e.target.value)}
            className="rounded-md border border-slate-300 px-2 py-1 text-sm"
          >
            <option value="all">All</option>
            {questLines.map((line) => (
              <option key={line} value={line}>
                {line}
              </option>
            ))}
          </select>
        </label>

        <label className="flex items-center gap-2 text-sm text-slate-600">
          Priority
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value as Priority | "all")}
            className="rounded-md border border-slate-300 px-2 py-1 text-sm"
          >
            <option value="all">All</option>
            {PRIORITIES.map((priority) => (
              <option key={priority} value={priority}>
                {priority.charAt(0).toUpperCase() + priority.slice(1)}
              </option>
            ))}
          </select>
        </label>

        <label className="flex items-center gap-2 text-sm text-slate-600">
          Status
          <select
            value={doneFilter}
            onChange={(e) => setDoneFilter(e.target.value as DoneFilter)}
            className="rounded-md border border-slate-300 px-2 py-1 text-sm"
          >
            <option value="all">All</option>
            <option value="not-done">Not done</option>
            <option value="done">Done</option>
          </select>
        </label>

        <label className="ml-auto flex items-center gap-2 text-sm text-slate-600">
          Sort by
          <select
            value={sortField}
            onChange={(e) => setSortField(e.target.value as SortField)}
            className="rounded-md border border-slate-300 px-2 py-1 text-sm"
          >
            <option value="createdAt">Newest</option>
            <option value="priority">Priority</option>
            <option value="title">Title</option>
          </select>
        </label>
      </div>

      {visibleQuests.length === 0 ? (
        <p className="rounded-lg border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
          No quests match these filters.
        </p>
      ) : (
        <ul className="flex flex-col gap-3">
          {visibleQuests.map((quest) => (
            <QuestCard key={quest.id} quest={quest} onToggleDone={toggleDone} />
          ))}
        </ul>
      )}
    </div>
  );
}
