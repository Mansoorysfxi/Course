import { useState } from "react";
import type { Priority, Quest } from "./types";
import { QuestForm } from "./components/QuestForm";
import { QuestListItem } from "./components/QuestListItem";

const initialQuests: Quest[] = [
  { id: "1", title: "Slay the Dragon", priority: "high", done: false },
  { id: "2", title: "Gather Healing Herbs", priority: "low", done: true },
];

function App() {
  const [quests, setQuests] = useState<Quest[]>(initialQuests);

  function addQuest(title: string, priority: Priority) {
    const newQuest: Quest = {
      id: crypto.randomUUID(),
      title,
      priority,
      done: false,
    };
    // A brand new array (spread), not a mutation of the old one -- this
    // is what lets React tell "old quests" and "new quests" apart by
    // reference, per lessons/02-state-and-the-rendering-model.md.
    setQuests([newQuest, ...quests]);
  }

  function toggleDone(id: string) {
    setQuests((current) =>
      current.map((quest) => (quest.id === id ? { ...quest, done: !quest.done } : quest))
    );
  }

  return (
    <div>
      <h1>QuestLog Lite</h1>
      <QuestForm onAddQuest={addQuest} />
      <ul style={{ listStyle: "none", padding: 0 }}>
        {quests.map((quest) => (
          <QuestListItem key={quest.id} quest={quest} onToggleDone={toggleDone} />
        ))}
      </ul>
    </div>
  );
}

export default App;
