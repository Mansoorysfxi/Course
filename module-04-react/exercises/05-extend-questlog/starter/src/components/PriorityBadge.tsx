import type { Priority } from "../types/quest";

const STYLES: Record<Priority, string> = {
  low: "bg-slate-100 text-slate-700 ring-slate-300",
  medium: "bg-amber-100 text-amber-800 ring-amber-300",
  high: "bg-rose-100 text-rose-800 ring-rose-300",
};

const LABELS: Record<Priority, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
};

/** A small colored pill showing a quest's priority. A "prop" (see
 * lessons/01-why-react-components-props-and-jsx.md) is just a function
 * parameter by another name -- `priority` here is exactly that. */
export function PriorityBadge({ priority }: { priority: Priority }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${STYLES[priority]}`}
    >
      {LABELS[priority]}
    </span>
  );
}
