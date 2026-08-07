import type { Announcement } from "../types";

// This file is complete -- you don't need to change it. It's deliberately
// built the same way project/questlog/src/api/fetchQuests.ts is: a
// Promise, a setTimeout standing in for a real network delay, and a
// chance of failure (random OR forced) so loading/error UI has something
// genuine to react to. See lessons/07-data-fetching-loading-and-error-states.md.

const SIMULATED_DELAY_MS = 800;
const DEFAULT_FAIL_RATE = 0.2;

const seedAnnouncements: Announcement[] = [
  { id: "a1", message: "The northern road is closed for repairs.", postedAt: "2026-07-01T09:00:00.000Z" },
  { id: "a2", message: "A new merchant has arrived in the village square.", postedAt: "2026-07-03T12:00:00.000Z" },
  { id: "a3", message: "The harvest festival begins next week.", postedAt: "2026-07-05T15:30:00.000Z" },
];

export interface FetchAnnouncementsOptions {
  forceError?: boolean;
  failRate?: number;
}

export function fetchAnnouncements(
  options: FetchAnnouncementsOptions = {}
): Promise<Announcement[]> {
  const { forceError = false, failRate = DEFAULT_FAIL_RATE } = options;

  return new Promise<Announcement[]>((resolve, reject) => {
    setTimeout(() => {
      const shouldFail = forceError || Math.random() < failRate;
      if (shouldFail) {
        reject(new Error("Could not reach the announcement board. (Simulated failure.)"));
        return;
      }
      resolve(seedAnnouncements.map((a) => ({ ...a })));
    }, SIMULATED_DELAY_MS);
  });
}
