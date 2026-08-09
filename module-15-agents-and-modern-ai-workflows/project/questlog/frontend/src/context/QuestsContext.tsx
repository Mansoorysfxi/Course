import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import {
  createQuest as apiCreateQuest,
  deleteQuest as apiDeleteQuest,
  fetchQuests,
  updateQuest as apiUpdateQuest,
} from "../api/questsApi";
import { UnauthorizedError } from "../api/http";
import { useAuth } from "./AuthContext";
import type { NewQuestInput, Quest, QuestUpdate } from "../types/quest";

interface QuestsContextValue {
  quests: Quest[];
  loading: boolean;
  error: string | null;
  /** Re-runs the fetch from scratch (loading -> success/error). */
  refetch: () => void;
  addQuest: (input: NewQuestInput) => Promise<void>;
  updateQuest: (id: string, changes: QuestUpdate) => Promise<void>;
  deleteQuest: (id: string) => Promise<void>;
  toggleDone: (id: string) => Promise<void>;
  getQuest: (id: string) => Quest | undefined;
}

// `undefined` as the default means "no provider above me" -- see the
// explicit check inside useQuests() below, and lessons/06-context.md
// (Module 04) for why that check matters instead of just asserting the
// type away.
const QuestsContext = createContext<QuestsContextValue | undefined>(undefined);

export function QuestsProvider({ children }: { children: ReactNode }) {
  // New in Module 07: every quest this app knows about belongs to
  // *someone*, so this provider needs to know who's currently logged in
  // before it can meaningfully fetch anything at all. `AuthProvider`
  // (src/context/AuthContext.tsx) must be an ancestor of this provider
  // in the component tree for this to work -- see src/main.tsx, where
  // `<AuthProvider>` wraps `<QuestsProvider>`, in that order.
  const { user } = useAuth();

  const [quests, setQuests] = useState<Quest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Incrementing this number is this component's way of saying "run the
  // fetch effect again" -- it's a dependency of the effect below purely so
  // that changing it re-triggers the effect. Its actual numeric value is
  // never read anywhere else.
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    // See lessons/03-useeffect-the-dependency-array-in-depth.md (Module 04)
    // for exactly why this `cancelled` flag exists: if the user triggers a
    // second refetch before the first one has settled, or this provider
    // ever unmounts mid-request, this flag stops the *stale* request's
    // result from overwriting state with old data after the fact.
    let cancelled = false;

    if (!user) {
      // Not logged in (yet, or anymore) -- there is nothing to fetch, and
      // fetching would just fail with a 401 anyway (every /api/quests
      // route is protected -- backend/app/routers/quests.py). Clear out
      // whatever the previous user's session had loaded, so logging out
      // and back in as someone else never briefly shows the wrong
      // person's quests.
      setQuests([]);
      setLoading(false);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    fetchQuests()
      .then((data) => {
        if (!cancelled) {
          setQuests(data);
        }
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        if (err instanceof UnauthorizedError) {
          // The token this request sent (if any) was rejected -- most
          // likely it expired mid-session. http.ts's request() already
          // cleared it from storage; a full page navigation to /login is
          // the simplest correct way to get AuthContext back into a
          // consistent "logged out" state too, rather than wiring a
          // second, separate cross-context notification mechanism for
          // what should be a rare edge case in a learning project. See
          // lessons/06-building-signup-login.md's honest note on this
          // simplification.
          window.location.href = "/login";
          return;
        }
        setError(err instanceof Error ? err.message : "Something went wrong.");
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [reloadToken, user]);

  const refetch = useCallback(() => {
    setReloadToken((token) => token + 1);
  }, []);

  const addQuest = useCallback(async (input: NewQuestInput) => {
    try {
      const created = await apiCreateQuest(input);
      setQuests((current) => [created, ...current]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create quest.");
    }
  }, []);

  const updateQuest = useCallback(async (id: string, changes: QuestUpdate) => {
    try {
      const updated = await apiUpdateQuest(id, changes);
      setQuests((current) => current.map((quest) => (quest.id === id ? updated : quest)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update quest.");
    }
  }, []);

  const deleteQuest = useCallback(async (id: string) => {
    try {
      await apiDeleteQuest(id);
      setQuests((current) => current.filter((quest) => quest.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete quest.");
    }
  }, []);

  const toggleDone = useCallback(
    async (id: string) => {
      const current = quests.find((quest) => quest.id === id);
      if (!current) return;
      await updateQuest(id, { done: !current.done });
    },
    [quests, updateQuest],
  );

  const getQuest = useCallback((id: string) => quests.find((quest) => quest.id === id), [quests]);

  const value: QuestsContextValue = {
    quests,
    loading,
    error,
    refetch,
    addQuest,
    updateQuest,
    deleteQuest,
    toggleDone,
    getQuest,
  };

  return <QuestsContext.Provider value={value}>{children}</QuestsContext.Provider>;
}

/**
 * The custom hook every component actually uses to reach the quests data,
 * instead of importing `QuestsContext` and calling `useContext` directly
 * everywhere. See lessons/04-useref-and-custom-hooks.md and
 * lessons/06-context.md (both Module 04) for why this wrapper (throwing a
 * clear error if there's no provider above the caller) is the standard
 * pattern.
 */
export function useQuests(): QuestsContextValue {
  const context = useContext(QuestsContext);
  if (context === undefined) {
    throw new Error("useQuests() must be called from inside a <QuestsProvider>.");
  }
  return context;
}
