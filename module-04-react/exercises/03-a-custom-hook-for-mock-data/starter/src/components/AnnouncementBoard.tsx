import { useAnnouncements } from "../hooks/useAnnouncements";

// TODO (Exercise 03, Step 2): AnnouncementBoard
// See lessons/07-data-fetching-loading-and-error-states.md.
//
// Call `useAnnouncements()` and render, using EARLY RETURNS (not one big
// nested conditional) for each of the three states, in this order:
//   1. If `loading` is true: render a <p>Loading announcements...</p>.
//   2. If `error` is non-null: render a <div className="error"> showing
//      the error message AND a <button className="btn"> that calls
//      `refetch` when clicked.
//   3. Otherwise: render a <ul> of the announcements, each as an <li
//      className="card"> showing its `message`.
export function AnnouncementBoard() {
  const result = useAnnouncements();

  return (
    <p className="muted">
      TODO: implement AnnouncementBoard using `result` (see the comments
      above). Currently loading={String(result.loading)}, error=
      {String(result.error)}.
    </p>
  );
}
