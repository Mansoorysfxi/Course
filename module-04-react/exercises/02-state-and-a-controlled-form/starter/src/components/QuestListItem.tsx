import type { Quest } from "../types";

interface QuestListItemProps {
  quest: Quest;
  onToggleDone: (id: string) => void;
}

// This component is complete -- you don't need to change it. Notice it
// receives `onToggleDone` as a prop and just calls it; it doesn't know or
// care HOW toggling actually works, only that App.tsx handles it. This is
// the same "lift state up, pass the updater down as a prop" idea Lesson 05
// names explicitly, previewed here with a function you're about to write.
export function QuestListItem({ quest, onToggleDone }: QuestListItemProps) {
  return (
    <li className="card">
      <label style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <input
          type="checkbox"
          checked={quest.done}
          onChange={() => onToggleDone(quest.id)}
        />
        <span style={{ textDecoration: quest.done ? "line-through" : "none" }}>
          {quest.title}
        </span>
        <span className="badge">{quest.priority}</span>
      </label>
    </li>
  );
}
