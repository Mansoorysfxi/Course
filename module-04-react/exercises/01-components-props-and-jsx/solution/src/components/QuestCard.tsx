import type { Priority } from "../App";
import { PriorityBadge } from "./PriorityBadge";

interface QuestCardProps {
  title: string;
  priority: Priority;
  questLine: string;
}

export function QuestCard({ title, priority, questLine }: QuestCardProps) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <PriorityBadge priority={priority} />
      <p className="muted">{questLine}</p>
    </div>
  );
}
