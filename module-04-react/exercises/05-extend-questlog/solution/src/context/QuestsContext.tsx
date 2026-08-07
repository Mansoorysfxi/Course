import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { fetchQuests } from "../api/fetchQuests";
import type { NewQuestInput, Quest, QuestUpdate } from "../types/quest";

interface QuestsContextValue {
  quests: Quest[];
  loading: boolean;
  error: string | null;
  /** Re-runs the simulated fetch from scratch (loading -> success/error). */
  refetch: () => void;
  addQuest: (input: NewQuestInput) => void;
  updateQuest: (id: string, changes: QuestUpdate) => void;
  deleteQuest: (id: string) => void;
  toggleDone: (id: string) => void;
  getQuest: (id: string) => Quest | undefined;
}

// `undefined` as the default means "no provider above me" -- see the
// explicit check inside useQuests() below, and lessons/06-context.md for
// why that check matters instead of just asserting the type away.
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
    // See lessons/03-useeffect-the-dependency-array-in-depth.md for exactly
    // why this `cancelled` flag exists: if the user triggers a second
    // refetch before the first one has settled, or this provider ever
    // unmounts mid-request, this flag stops the *stale* request's result
    // from overwriting state with old data after the fact.
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

  const addQuest = useCallback((input: NewQuestInput) => {
    const newQuest: Quest = {
      ...input,
      id: crypto.randomUUID(),
      done: false,
      createdAt: new Date().toISOString(),
    };
    setQuests((current) => [newQuest, ...current]);
  }, []);

  const updateQuest = useCallback((id: string, changes: QuestUpdate) => {
    setQuests((current) =>
      current.map((quest) => (quest.id === id ? { ...quest, ...changes } : quest))
    );
  }, []);

  const deleteQuest = useCallback((id: string) => {
    setQuests((current) => current.filter((quest) => quest.id !== id));
  }, []);

  const toggleDone = useCallback((id: string) => {
    setQuests((current) =>
      current.map((quest) => (quest.id === id ? { ...quest, done: !quest.done } : quest))
    );
  }, []);

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
 * lessons/06-context.md for why this wrapper (throwing a clear error if
 * there's no provider above the caller) is the standard pattern.
 */
export function useQuests(): QuestsContextValue {
  const context = useContext(QuestsContext);
  if (context === undefined) {
    throw new Error("useQuests() must be called from inside a <QuestsProvider>.");
  }
  return context;
}
