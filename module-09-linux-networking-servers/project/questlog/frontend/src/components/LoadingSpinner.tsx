/** A simple loading indicator, shown while `loading` is true in
 * QuestsContext. See lessons/07-data-fetching-loading-and-error-states.md
 * for why a dedicated, visible loading state (rather than a blank screen)
 * matters. */
export function LoadingSpinner({ label = "Loading quests..." }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-slate-500">
      <div
        className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-indigo-600"
        role="status"
        aria-label={label}
      />
      <p className="text-sm">{label}</p>
    </div>
  );
}
