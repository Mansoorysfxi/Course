import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import {
  createQuest as apiCreateQuest,
  deleteQuest as apiDeleteQuest,
  fetchQuests,
  updateQuest as apiUpdateQuest,
} from "../api/questsApi";
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
    // result from overwriting state with old data after the fact. As of
    // Module 05, `fetchQuests()` is a real fetch() call to the FastAPI
    // backend (see src/api/questsApi.ts) instead of Module 04's mocked
    // Promise -- this effect's own logic needed no changes at all, exactly
    // as that module's BRIEF.md predicted, because the *shape* of what
    // fetchQuests() returns (a Promise<Quest[]> that can reject) is
    // identical either way.
    let cancelled = false;

    setLoading(true);
    setError(null);

    fetchQuests()
      .then((data) => {
        if (!cancelled) {
          setQuests(data);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Something went wrong.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [reloadToken]);

  const refetch = useCallback(() => {
    setReloadToken((token) => token + 1);
  }, []);

  /**
   * Every mutation below now makes a real HTTP request (Module 05) instead
   * of only updating local state (Module 04). Each one is `async` and
   * updates `quests` from the backend's actual response -- not from an
   * optimistic local guess -- so what's on screen always reflects what the
   * server actually has. Each one also catches its own errors and reports
   * them via this same `error` state QuestListPage already renders (via
   * ErrorBanner), so no calling component needed to change to handle a
   * network failure that Module 04's local-state version could never have
   * produced in the first place. This is the one deliberate, minimal
   * adaptation this module made to Module 04's frontend -- see
   * ../../README.md for the full explanation.
   */

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
    [quests, updateQuest]
  );

  const getQuest = useCallback(
    (id: string) => quests.find((quest) => quest.id === id),
    [quests]
  );

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
