# Exercise 03 — A Custom Hook for Mock Data

**Lessons:**
- [`lessons/03-useeffect-the-dependency-array-in-depth.md`](../../lessons/03-useeffect-the-dependency-array-in-depth.md) — dependency arrays, cleanup functions, the `cancelled`-flag pattern.
- [`lessons/04-useref-and-custom-hooks.md`](../../lessons/04-useref-and-custom-hooks.md) — what a custom hook is and the Rules of Hooks.
- [`lessons/07-data-fetching-loading-and-error-states.md`](../../lessons/07-data-fetching-loading-and-error-states.md) — the `{ data, loading, error, refetch }` shape, the "reload token," early-return UI.

Read all three before starting — this exercise combines them directly, on a smaller, standalone example before you see the real (very similar) code in the QuestLog capstone.

**Difficulty:** Guided/independent. The trickiest part (the hook's internal `useEffect`) is described in detailed comments, but no code is given for it — you're writing real, from-scratch async state management this time, not filling in single lines.

## Concepts this exercise uses

- `useEffect` with a dependency array controlling exactly when it re-runs.
- A cleanup function using a `cancelled` flag to prevent a stale response from overwriting newer state.
- A custom hook (`useAnnouncements`) that packages up loading/error/data state and a `refetch` function.
- Rendering loading/error/success as three separate early returns.

## What's already done for you

- `src/types.ts` — the `Announcement` type.
- `src/api/fetchAnnouncements.ts` — a complete, mocked async "backend": a Promise, a simulated delay, and a chance of failure (random, or forced via `{ forceError: true }`). Built the same way `project/questlog/src/api/fetchQuests.ts` is.
- `src/App.tsx` — complete, renders `<AnnouncementBoard />`.

## What to build

### Step 1 — `src/hooks/useAnnouncements.ts`

Follow the detailed TODO comments already in the file. In short: `announcements`/`loading`/`error`/`reloadToken` state, a `useEffect` that calls `fetchAnnouncements()` and updates that state correctly (with a `cancelled`-flag cleanup), and a `refetch` function that bumps `reloadToken` to deliberately re-trigger the effect. Return `{ announcements, loading, error, refetch }`.

### Step 2 — `src/components/AnnouncementBoard.tsx`

Call your hook, then render, as three separate early returns: a loading message, an error message with a working "Try again" button (calling `refetch`), or the real list.

## Acceptance criteria

- [ ] `npm run dev` shows "Loading announcements..." briefly, then either the real announcement list or (sometimes — it fails about 20% of the time on its own) the error state.
- [ ] Reloading the page (or, once error UI is showing, clicking "Try again" enough times) eventually shows the successful list — confirming your effect genuinely re-runs on `refetch`.
- [ ] Temporarily changing the hook's internal `fetchAnnouncements()` call to `fetchAnnouncements({ forceError: true })` reliably shows the error state every time (change it back afterward — this is just to prove your error path actually works, not a permanent change).
- [ ] No console errors about updating state on an unmounted component (a sign your cleanup/`cancelled` flag is missing or wrong).
- [ ] `npm run build` completes with zero TypeScript errors.

## What to submit

Point your AI session at your completed folder and say *"Review my solution for exercise 03."*

## Hints

**Level 1:** Lesson 07's own `useQuests`-shaped example (and `project/questlog/src/context/QuestsContext.tsx`, once you've finished, worth comparing against) is doing exactly this same job — same four pieces of state, same shape of effect, same `refetch` pattern, different data.

**Level 2:** The effect's skeleton:
```typescript
useEffect(() => {
  let cancelled = false;
  setLoading(true);
  setError(null);

  fetchAnnouncements()
    .then((data) => { if (!cancelled) setAnnouncements(data); })
    .catch((err) => { if (!cancelled) setError(/* ... */); })
    .finally(() => { if (!cancelled) setLoading(false); });

  return () => { cancelled = true; };
}, [reloadToken]);
```

**Level 3 (near-answer):** For the `.catch()`, TypeScript types a caught value as `unknown`, not `Error` — use `err instanceof Error ? err.message : "Something went wrong."` to safely get a string either way. If you're still stuck after this, ask your AI session for the full solution rather than guessing further.
