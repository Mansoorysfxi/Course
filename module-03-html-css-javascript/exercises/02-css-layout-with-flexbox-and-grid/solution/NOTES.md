# Notes on grading this yourself before asking for review

Open `index.html` in your browser and check each item with DevTools open.

- **`box-sizing: border-box` must be the very first rule.** If you placed it
  after other rules that set explicit widths/padding on the same elements,
  it still works (it's not an ordering-sensitive property in practice, since
  nothing here overrides it with a conflicting `box-sizing` value) — but the
  convention of putting it first, before anything else, is worth keeping as
  a habit for every project from here on.
- **Toolbar check:** click into DevTools, select `.toolbar`, and confirm the
  Styles pane shows `display: flex` actually applied (not crossed out/
  overridden). The three links should visually spread across the full width
  of the header with equal gaps between them, and sit vertically centered
  even if you temporarily make the header taller.
- **Box model check:** select a `.quest-card` in DevTools' Elements panel and
  look at the box-model diagram in the Computed/Layout tab. If you set an
  explicit `width` on `.quest-card` anywhere, the diagram's outer number
  should match that value exactly — that's `border-box` confirmed working.
  (This solution doesn't set an explicit width on `.quest-card` — it's sized
  by the grid cell instead — so this check applies if you experimented with
  adding one yourself.)
- **Responsive check — this is the one people most often get subtly wrong.**
  Open DevTools' device toolbar (`Ctrl+Shift+M`) and drag the width slider
  across exactly 768px. Below it: header, sidebar, main content, and footer
  should all be stacked in one column, in that reading order. At or above
  it: header spans full width, sidebar and main content sit side by side
  below it, footer spans full width at the bottom. If nothing changes at
  768px at all, confirm your `@media (min-width: 768px)` block is actually
  present and not accidentally nested inside another rule's braces (a stray
  extra `}` above it is a common cause).
- **`quest-list` check:** slowly narrow and widen the browser (inside
  `.main-content`, not the whole page) and watch the number of quest cards
  per row change smoothly with no jump/overlap and no media query — that's
  `auto-fit`/`minmax` doing its job. If cards overlap or overflow, double
  check the `minmax(220px, 1fr)` syntax exactly — a missing comma or
  mismatched parenthesis fails silently rather than erroring visibly.
