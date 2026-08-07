/** Shown whenever `error` in QuestsContext is non-null. Always paired with
 * a way to retry -- see lessons/07-data-fetching-loading-and-error-states.md
 * on never leaving a failed fetch as a dead end for the user. */
export function ErrorBanner({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="flex flex-col items-start gap-3 rounded-lg border border-rose-200 bg-rose-50 p-4 text-rose-800 sm:flex-row sm:items-center sm:justify-between">
      <p className="text-sm">
        <span className="font-semibold">Something went wrong:</span> {message}
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="shrink-0 rounded-md bg-rose-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-rose-700"
      >
        Try again
      </button>
    </div>
  );
}
