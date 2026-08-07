import { useCallback, useEffect, useState } from "react";
import { fetchItems } from "../api/fetchItems";
import type { Item } from "../types";

export interface UseItemsResult {
  items: Item[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

// Complete -- this is exactly the hook you built by hand in Exercise 03
// (there called useAnnouncements). It's given to you complete here so
// this exercise's NEW focus can be routing (Lesson 08), not re-proving
// you can write this hook a second time.
export function useItems(): UseItemsResult {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    setError(null);

    fetchItems()
      .then((data) => {
        if (!cancelled) setItems(data);
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Something went wrong.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [reloadToken]);

  const refetch = useCallback(() => setReloadToken((t) => t + 1), []);

  return { items, loading, error, refetch };
}
