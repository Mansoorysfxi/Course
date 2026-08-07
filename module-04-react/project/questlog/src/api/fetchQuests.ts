import type { Quest } from "../types/quest";

/**
 * A fake network delay, in milliseconds. QuestLog has no real backend yet
 * (Module 05 adds FastAPI) -- this constant stands in for "however long a
 * real HTTP round trip would actually take," so the loading state this
 * project builds is genuinely exercised instead of resolving so fast it's
 * never actually seen. See lessons/07-data-fetching-loading-and-error-states.md.
 */
const SIMULATED_DELAY_MS = 900;

/** How often a call with no explicit `forceError`/`failRate` fails on its
 * own, to make sure the error UI actually gets exercised sometimes without
 * anyone having to force it. Reload the app a handful of times and you
 * will eventually see it. */
const DEFAULT_FAIL_RATE = 0.15;

const seedQuests: Quest[] = [
  {
    id: "quest-001",
    title: "Slay the Dragon",
    description: "The dragon has been terrorizing the northern villages. Someone has to go.",
    priority: "high",
    done: false,
    questLine: "Main Story",
    createdAt: "2026-07-01T09:00:00.000Z",
  },
  {
    id: "quest-002",
    title: "Gather Healing Herbs",
    description: "The village healer needs five bundles of silverleaf from the eastern woods.",
    priority: "low",
    done: true,
    questLine: "Village Errands",
    createdAt: "2026-07-03T14:30:00.000Z",
  },
  {
    id: "quest-003",
    title: "Deliver the Sealed Letter",
    description: "A courier's letter must reach the capital before the harvest festival begins.",
    priority: "medium",
    done: false,
    questLine: "Village Errands",
    createdAt: "2026-07-05T08:15:00.000Z",
  },
  {
    id: "quest-004",
    title: "Clear the Old Mine",
    description: "Something has been digging new tunnels in the abandoned mine. Investigate.",
    priority: "high",
    done: false,
    questLine: "Side Quests",
    createdAt: "2026-07-06T11:45:00.000Z",
  },
  {
    id: "quest-005",
    title: "Repair the Bridge",
    description: "The stone bridge to the market town has a collapsed section.",
    priority: "medium",
    done: true,
    questLine: "Side Quests",
    createdAt: "2026-07-02T16:00:00.000Z",
  },
];

export interface FetchQuestsOptions {
  /** When true, always reject -- useful for deliberately testing error UI,
   * from a lesson example, an exercise, or a console call. */
  forceError?: boolean;
  /** The probability (0 to 1) of a random failure when `forceError` isn't
   * set. Defaults to `DEFAULT_FAIL_RATE`. Pass `0` to disable random
   * failures entirely while you're working on something else. */
  failRate?: number;
}

/**
 * A fake `fetchQuests` — this is deliberately built to look and feel like a
 * real network call (it returns a Promise, it takes a moment to settle, it
 * can fail) without actually requiring a server, per RUNNING_PROJECT.md:
 * "a fake `fetchQuests()` that returns a Promise with a setTimeout and can
 * be made to randomly/deliberately reject." Module 05 replaces this
 * function's insides with a real `fetch(...)` call to a FastAPI backend --
 * every component that calls `fetchQuests()` today will not need to change
 * at all, because the *shape* of what it returns (a Promise<Quest[]>) stays
 * identical. That's the whole point of isolating this in its own file.
 */
export function fetchQuests(options: FetchQuestsOptions = {}): Promise<Quest[]> {
  const { forceError = false, failRate = DEFAULT_FAIL_RATE } = options;

  return new Promise<Quest[]>((resolve, reject) => {
    setTimeout(() => {
      const shouldFail = forceError || Math.random() < failRate;
      if (shouldFail) {
        reject(
          new Error(
            "Could not reach the quest server. (This is a simulated failure -- QuestLog has no real backend yet. Try again.)"
          )
        );
        return;
      }
      // Return copies, not the original array/objects, so callers can
      // never accidentally mutate this module's own seed data by mutating
      // what they got back.
      resolve(seedQuests.map((quest) => ({ ...quest })));
    }, SIMULATED_DELAY_MS);
  });
}
