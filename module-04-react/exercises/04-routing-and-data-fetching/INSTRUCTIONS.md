# Exercise 04 — Routing and Data Fetching

**Lessons:**
- [`lessons/08-react-router.md`](../../lessons/08-react-router.md) — `BrowserRouter`, `Routes`/`Route`, `Link`, `useParams`, index and catch-all routes.
- [`lessons/07-data-fetching-loading-and-error-states.md`](../../lessons/07-data-fetching-loading-and-error-states.md) — reused here, not re-taught; you already proved you can build this in Exercise 03.

**Difficulty:** Independent. Unlike Exercises 01–03, the starter's pages compile and run as-is (they just show placeholder text) — nothing forces you through the steps in order. Follow them anyway; the acceptance criteria check the real, working result.

## Concepts this exercise uses

- Declarative-mode React Router: `<BrowserRouter>` (already wired up for you in `main.tsx`), `<Routes>`, `<Route>`, index routes, a dynamic segment (`:id`), a catch-all (`*`).
- `<Link>` for navigation without a full page reload.
- `useParams()` to read a route parameter.
- Reusing a custom data-fetching hook (`useItems`, given complete — the same shape as Exercise 03's `useAnnouncements`) across two different pages.

## What's already done for you

- `src/types.ts`, `src/api/fetchItems.ts` — a mocked "merchant catalog" API, same pattern as Exercise 03.
- `src/hooks/useItems.ts` — **complete**. This is deliberately the same hook shape you already built by hand in Exercise 03, given to you here so this exercise's new material is routing, not re-proving the hook.
- `src/main.tsx` — **complete**: `react-router` is installed, and `<BrowserRouter>` already wraps `<App />`.
- `src/pages/CatalogPage.tsx`, `src/pages/ItemDetailPage.tsx`, `src/pages/NotFoundPage.tsx`, `src/App.tsx` — stubs with detailed TODO comments. Currently each just renders placeholder text.

## What to build

### Step 1 — `src/pages/CatalogPage.tsx`
Call `useItems()`. Handle loading/error the same way you did in Exercise 03. On success, render each item as a `<Link to={\`/items/${item.id}\`}>` showing its name and price.

### Step 2 — `src/pages/ItemDetailPage.tsx`
Read `:id` with `useParams<{ id: string }>()`. Call `useItems()`. Handle loading/error. Once loaded, `.find()` the item matching `id` — if none matches, show a clear "not found" message with a link back to `/`; otherwise show its full details and a link back to `/`.

### Step 3 — `src/pages/NotFoundPage.tsx`
A small page for any unmatched URL — a heading and a link back to `/`.

### Step 4 — `src/App.tsx`
Build the actual `<Routes>` tree: an index route to `CatalogPage`, `"items/:id"` to `ItemDetailPage`, and `"*"` to `NotFoundPage`.

## Acceptance criteria

- [ ] `npm run dev` shows the catalog list (after a brief loading state) at `/`.
- [ ] Clicking an item navigates to `/items/<its-id>` **without a full page reload** (check: the browser's loading spinner/favicon shouldn't flash) and shows that item's details.
- [ ] Manually editing the URL to a nonexistent item id (e.g. `/items/does-not-exist`) shows your "not found" message, not a blank page or a crash.
- [ ] Manually editing the URL to a completely unrelated path (e.g. `/nonsense`) shows your `NotFoundPage`.
- [ ] The browser's back button correctly returns from an item's detail page to the catalog.
- [ ] `npm run build` completes with zero TypeScript errors.

## What to submit

Point your AI session at your completed folder and say *"Review my solution for exercise 04."*

## Hints

**Level 1:** Re-read Lesson 08's real `App.tsx`/`Layout.tsx`/`QuestDetailPage.tsx` walkthrough — this exercise's route tree and detail page are the same shapes, without the nested `Layout`/`Outlet` (you don't need those here — a flat, non-nested route tree is enough).

**Level 2:** The route tree:
```tsx
<Routes>
  <Route index element={<CatalogPage />} />
  <Route path="items/:id" element={<ItemDetailPage />} />
  <Route path="*" element={<NotFoundPage />} />
</Routes>
```

**Level 3 (near-answer):** In `ItemDetailPage`, after `const { id } = useParams<{ id: string }>();` and getting `items` from `useItems()`, the lookup is `const item = items.find((i) => i.id === id);` — then check `if (!item) { /* not found UI */ }` before rendering the real details. If you're still stuck after this, ask your AI session for the full solution rather than guessing further.
