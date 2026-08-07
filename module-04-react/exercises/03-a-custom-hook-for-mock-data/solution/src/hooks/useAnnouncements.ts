import { useCallback, useEffect, useState } from "react";
import { fetchAnnouncements } from "../api/fetchAnnouncements";
import type { Announcement } from "../types";

export interface UseAnnouncementsResult {
  announcements: Announcement[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useAnnouncements(): UseAnnouncementsResult {
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    setError(null);

    fetchAnnouncements()
      .then((data) => {
        if (!cancelled) {
          setAnnouncements(data);
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

  return { announcements, loading, error, refetch };
}
