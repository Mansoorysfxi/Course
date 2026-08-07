import { QuestCard } from "./components/QuestCard";

export type Priority = "low" | "medium" | "high";

export interface QuestSummary {
  title: string;
  priority: Priority;
  questLine: string;
}

// This data is hardcoded on purpose -- this exercise is about components,
// props, and JSX only (Lesson 01). There is no useState here, and there
// doesn't need to be: nothing on this page ever changes after it first
// renders. State (Lesson 02) is coming in the next exercise.
const quests: QuestSummary[] = [
  { title: "Slay the Dragon", priority: "high", questLine: "Main Story" },
  { title: "Gather Healing Herbs", priority: "low", questLine: "Village Errands" },
  { title: "Repair the Bridge", priority: "medium", questLine: "Side Quests" },
];

function App() {
  return (
    <div>
      <h1>Quest Board (read-only)</h1>
      <p className="muted">
        This page is complete and will not compile until you build the two
        components it imports. See INSTRUCTIONS.md.
      </p>
      {quests.map((quest) => (
        <QuestCard
          key={quest.title}
          title={quest.title}
          priority={quest.priority}
          questLine={quest.questLine}
        />
      ))}
    </div>
  );
}

export default App;
