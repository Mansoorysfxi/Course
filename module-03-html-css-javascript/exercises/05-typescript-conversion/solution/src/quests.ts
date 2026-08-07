/*
 * Exercise 05 reference solution — TypeScript Conversion: Typing a Quest
 * Roster.
 *
 * Don't read this until you've made a genuine attempt at
 * starter/src/quests.ts.
 */

interface Quest {
  name: string;
  difficulty: "Easy" | "Medium" | "Hard";
  rewardGold: number;
  completed: boolean;
  notes?: string;
}

function formatQuest(quest: Quest): string {
  return `${quest.name} [${quest.difficulty}] — ${quest.rewardGold} gold`;
}

function filterByDifficulty(quests: Quest[], difficulty: Quest["difficulty"]): Quest[] {
  return quests.filter((quest) => quest.difficulty === difficulty);
}

function totalRewards(quests: Quest[]): number {
  return quests.reduce((sum, quest) => sum + quest.rewardGold, 0);
}

function findQuestByName(quests: Quest[], name: string): Quest | undefined {
  return quests.find((quest) => quest.name === name);
}

const sampleQuests: Quest[] = [
  {
    name: "Slay the Dragon",
    difficulty: "Hard",
    rewardGold: 500,
    completed: false,
    notes: "The dragon nests in the northern caves.",
  },
  {
    name: "Find the Lost Amulet",
    difficulty: "Medium",
    rewardGold: 200,
    completed: false,
  },
  {
    name: "Water the Elder's Plants",
    difficulty: "Easy",
    rewardGold: 5,
    completed: true,
  },
  {
    name: "Defeat the Bandit King",
    difficulty: "Hard",
    rewardGold: 450,
    completed: false,
    notes: "Bring backup — he travels with at least three guards.",
  },
];

// --- Demo output ---

console.log(formatQuest(sampleQuests[0]));
console.log("Hard quests:", filterByDifficulty(sampleQuests, "Hard").length);
console.log("Total rewards:", totalRewards(sampleQuests));

const found = findQuestByName(sampleQuests, "Slay the Dragon");
console.log("Found quest name:", found?.name ?? "No quest found");

const notFound = findQuestByName(sampleQuests, "This Quest Does Not Exist");
console.log("Not-found lookup:", notFound?.name ?? "No quest found");
