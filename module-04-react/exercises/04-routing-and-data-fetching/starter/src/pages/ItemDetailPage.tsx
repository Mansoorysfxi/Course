// TODO (Exercise 04, Step 2): ItemDetailPage
// See lessons/08-react-router.md (useParams, and handling a "not found"
// case) and lessons/07-data-fetching-loading-and-error-states.md.
//
// Build the single-item page:
//   1. Read the `:id` route param with `useParams<{ id: string }>()`
//      (from "react-router"). Remember: whatever this returns is a
//      STRING -- there's no automatic conversion.
//   2. Call `useItems()` -- yes, the same hook CatalogPage uses. It's
//      fine (and simple, for this exercise) for both pages to fetch the
//      full catalog independently and each find the one item they need.
//   3. Early-return a loading message while `loading` is true.
//   4. Early-return an error message + "Try again" button if `error` is
//      set.
//   5. Once `items` has loaded, use `.find()` to locate the item whose
//      `id` matches the route param. If none matches (a bad/old URL),
//      render a clear "Item not found" message with a
//      <Link to="/">Back to catalog</Link>.
//   6. Otherwise, render the found item's name, price, and description,
//      plus a <Link to="/">Back to catalog</Link>.
export function ItemDetailPage() {
  return <p className="muted">TODO: build ItemDetailPage (see the comments above).</p>;
}
