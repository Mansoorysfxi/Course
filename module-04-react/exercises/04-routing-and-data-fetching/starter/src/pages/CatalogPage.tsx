// TODO (Exercise 04, Step 1): CatalogPage
// See lessons/07-data-fetching-loading-and-error-states.md and
// lessons/08-react-router.md.
//
// Build the catalog list page:
//   1. Call `useItems()` (from "../hooks/useItems").
//   2. Early-return a loading message while `loading` is true.
//   3. Early-return an error message + a "Try again" button (calling
//      `refetch`) if `error` is set.
//   4. Otherwise, render a list of items. Each item should be wrapped in
//      a <Link to={`/items/${item.id}`}> (from "react-router") showing
//      its name and price, so clicking it navigates to that item's own
//      page.
export function CatalogPage() {
  return <p className="muted">TODO: build CatalogPage (see the comments above).</p>;
}
