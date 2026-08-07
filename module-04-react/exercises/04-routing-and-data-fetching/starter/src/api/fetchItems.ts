import type { Item } from "../types";

// Complete -- same mocked-async-API pattern you already built by hand in
// Exercise 03 and saw again in project/questlog/src/api/fetchQuests.ts.

const SIMULATED_DELAY_MS = 700;
const DEFAULT_FAIL_RATE = 0.15;

const seedItems: Item[] = [
  { id: "i1", name: "Silverleaf Bundle", price: 5, description: "A common healing herb, sold in bundles of five." },
  { id: "i2", name: "Iron Shortsword", price: 40, description: "A reliable, if unremarkable, blade." },
  { id: "i3", name: "Traveler's Cloak", price: 25, description: "Keeps out the rain, mostly." },
  { id: "i4", name: "Sealed Letter", price: 0, description: "Not for sale -- a delivery quest item." },
];

export interface FetchItemsOptions {
  forceError?: boolean;
  failRate?: number;
}

export function fetchItems(options: FetchItemsOptions = {}): Promise<Item[]> {
  const { forceError = false, failRate = DEFAULT_FAIL_RATE } = options;

  return new Promise<Item[]>((resolve, reject) => {
    setTimeout(() => {
      const shouldFail = forceError || Math.random() < failRate;
      if (shouldFail) {
        reject(new Error("Could not reach the merchant's catalog. (Simulated failure.)"));
        return;
      }
      resolve(seedItems.map((item) => ({ ...item })));
    }, SIMULATED_DELAY_MS);
  });
}
