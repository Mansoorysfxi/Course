import type { Priority } from "../App";

interface PriorityBadgeProps {
  priority: Priority;
}

export function PriorityBadge({ priority }: PriorityBadgeProps) {
  return <span className="badge">{priority}</span>;
}
