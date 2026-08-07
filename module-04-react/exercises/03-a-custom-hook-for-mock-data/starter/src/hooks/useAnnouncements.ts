import { useCallback, useEffect, useState } from "react";
import { fetchAnnouncements } from "../api/fetchAnnouncements";
import type { Announcement } from "../types";

export interface UseAnnouncementsResult {
  announcements: Announcement[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

// TODO (Exercise 03, Step 1): useAnnouncements
// See lessons/03-useeffect-the-dependency-array-in-depth.md,
// lessons/04-useref-and-custom-hooks.md, and
// lessons/07-data-fetching-loading-and-error-states.md.
//
// Build a custom hook that:
//   1. Holds three pieces of state: `announcements` (Announcement[],
//      starts as []), `loading` (boolean, starts true), `error`
//      (string | null, starts null).
//   2. Also holds a `reloadToken` number state (starts at 0) -- its
//      VALUE is never read anywhere except as a useEffect dependency;
//      incrementing it is how `refetch` deliberately re-runs the effect.
//   3. In a useEffect with `[reloadToken]` as its dependency array:
//      - set `loading` to true and `error` to null at the START (every
//        time the effect runs, including refetches)
//      - call `fetchAnnouncements()`
//      - on success: set `announcements` to the result
//      - on failure: set `error` to the caught error's `.message`
//      - either way: set `loading` to false
//      - use a `cancelled` flag (declared with `let` INSIDE the effect,
//        set to `true` in the effect's cleanup function) so a stale,
//        late-arriving response from a PREVIOUS effect run can never
//        overwrite state after a newer refetch has already started. This
//        is the exact pattern project/questlog/src/context/QuestsContext.tsx
//        uses for the real app -- go read it after finishing this if
//        you want to compare.
//   4. A `refetch` function (wrap it in `useCallback` with an empty
//      dependency array) that increments `reloadToken`.
//   5. Returns `{ announcements, loading, error, refetch }`.
export function useAnnouncements(): UseAnnouncementsResult {
  // Replace this stub with your real implementation.
  return {
    announcements: [],
    loading: false,
    error: "TODO: implement useAnnouncements (see the comments above)",
    refetch: () => {},
  };
}
