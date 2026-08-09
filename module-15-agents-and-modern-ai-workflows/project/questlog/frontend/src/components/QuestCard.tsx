import { Link } from "react-router";
import type { Quest } from "../types/quest";
import { PriorityBadge } from "./PriorityBadge";

interface QuestCardProps {
  quest: Quest;
  onToggleDone: (id: string) => void;
}

/**
 * One quest, rendered as a card. This is a "presentational" component: it
 * receives everything it needs as props and doesn't reach into
 * QuestsContext itself -- QuestListPage decides *what* to show, this
 * component decides *how* to show one. See
 * lessons/01-why-react-components-props-and-jsx.md for why this split is
 * worth keeping even in a small app.
 */
export function QuestCard({ quest, onToggleDone }: QuestCardProps) {
  return (
    <li className="flex items-start gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <input
        type="checkbox"
        checked={quest.done}
        onChange={() => onToggleDone(quest.id)}
        aria-label={`Mark "${quest.title}" as ${quest.done ? "not done" : "done"}`}
        className="mt-1 h-4 w-4 shrink-0 accent-indigo-600"
      />
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <Link
            to={`/quests/${quest.id}`}
            className={`font-medium hover:underline ${
              quest.done ? "text-slate-400 line-through" : "text-slate-900"
            }`}
          >
            {quest.title}
          </Link>
          <PriorityBadge priority={quest.priority} />
          <span className="text-xs text-slate-400">{quest.questLine}</span>
        </div>
        <p className="mt-1 line-clamp-2 text-sm text-slate-500">{quest.description}</p>
      </div>
    </li>
  );
}
