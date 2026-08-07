/*
 * Exercise 05 starter — TypeScript Conversion: Typing a Quest Roster.
 *
 * Every function below is currently typed with `any` — Lesson 09's
 * explicitly-flagged escape hatch. Replace every `any` with the correct
 * real type. See INSTRUCTIONS.md for exactly what's required.
 */

// TODO 1: define `interface Quest` here with the fields described in
// INSTRUCTIONS.md (name, difficulty as a 3-value string-literal union,
// rewardGold, completed, and an optional notes).


// TODO 2: replace `quest: any` with `quest: Quest`, and `: any` (the
// return type) with `: string`.
function formatQuest(quest: any): any {
  return `${quest.name} [${quest.difficulty}] — ${quest.rewardGold} gold`;
}

// TODO 3: replace both `any` parameter types and the `any` return type.
// `difficulty` should use the SAME union type as Quest["difficulty"], not
// a plain string.
function filterByDifficulty(quests: any, difficulty: any): any {
  return quests.filter((quest: any) => quest.difficulty === difficulty);
}

// TODO 4: replace `quests: any` and the `any` return type.
function totalRewards(quests: any): any {
  return quests.reduce((sum: number, quest: any) => sum + quest.rewardGold, 0);
}

// TODO 5: replace `quests: any`, `name: any`, and the return type
// (it should be `Quest | undefined` — Array.prototype.find already
// returns undefined when nothing matches; you're just describing that
// truthfully instead of hiding it behind `any`).
function findQuestByName(quests: any, name: any): any {
  return quests.find((quest: any) => quest.name === name);
}

// TODO 6: fill this in with at least four Quest objects. Include `notes`
// on at least one, and leave it out on at least one other.
const sampleQuests: any = [];

// --- Demo output — do not need to change this section, but it will only
// compile/run correctly once the TODOs above are done correctly. ---

console.log(formatQuest(sampleQuests[0]));
console.log("Hard quests:", filterByDifficulty(sampleQuests, "Hard").length);
console.log("Total rewards:", totalRewards(sampleQuests));

const found = findQuestByName(sampleQuests, "Slay the Dragon");
console.log("Found quest name:", found?.name ?? "No quest found");

const notFound = findQuestByName(sampleQuests, "This Quest Does Not Exist");
console.log("Not-found lookup:", notFound?.name ?? "No quest found");
