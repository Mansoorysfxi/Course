import { Link } from "react-router";
import { useQuests } from "../context/QuestsContext";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { ErrorBanner } from "../components/ErrorBanner";

interface QuestLineStats {
  total: number;
  done: number;
}

/** A new page (Exercise 05): one entry per quest line, showing how many
 * quests it has and how many are done. Reads `quests` from the same
 * `useQuests()` every other page already uses -- no changes to
 * QuestsContext were needed, since this feature only reads existing
 * data and derives something new from it locally. */
export function QuestLinesPage() {
  const { quests, loading, error, refetch } = useQuests();

  if (loading) {
    return <LoadingSpinner label="Loading quest lines..." />;
  }

  if (error) {
    return <ErrorBanner message={error} onRetry={refetch} />;
  }

  const statsByLine = new Map<string, QuestLineStats>();
  for (const quest of quests) {
    const current = statsByLine.get(quest.questLine) ?? { total: 0, done: 0 };
    current.total += 1;
    if (quest.done) {
      current.done += 1;
    }
    statsByLine.set(quest.questLine, current);
  }

  const sortedLines = Array.from(statsByLine.entries()).sort((a, b) =>
    a[0].localeCompare(b[0])
  );

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-slate-900">Quest Lines</h1>

      {sortedLines.length === 0 ? (
        <p className="rounded-lg border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
          No quest lines yet -- add a quest to see one appear here.
        </p>
      ) : (
        <ul className="flex flex-col gap-3">
          {sortedLines.map(([name, stats]) => (
            <li
              key={name}
              className="flex items-center justify-between rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
            >
              <span className="font-medium text-slate-900">{name}</span>
              <span className="text-sm text-slate-500">
                {stats.done} / {stats.total} done
              </span>
            </li>
          ))}
        </ul>
      )}

      <Link to="/" className="mt-6 inline-block text-indigo-600 hover:underline">
        Back to Quest Board
      </Link>
    </div>
  );
}
