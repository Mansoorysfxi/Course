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

  // TODO (Exercise 02, Step 1): addQuest
  // See lessons/02-state-and-the-rendering-model.md.
  //
  // Given a title and a priority, add a brand-new Quest to `quests`.
  // Requirements:
  //   - Generate an `id` for the new quest. `crypto.randomUUID()` works
  //     fine (it's a built-in browser/Node function -- no import needed).
  //   - The new quest starts with `done: false`.
  //   - Do NOT mutate the existing `quests` array (no `.push()` on it) --
  //     create a brand NEW array (e.g. with the spread operator, `[...]`)
  //     and pass that new array to `setQuests`. The lesson explains
  //     exactly why this matters for React to notice the change.
  function addQuest(title: string, priority: Priority) {
    // Replace this with a real implementation.
    console.log("TODO: addQuest", title, priority);
  }

  // TODO (Exercise 02, Step 2): toggleDone
  // See lessons/02-state-and-the-rendering-model.md.
  //
  // Given a quest's id, flip that ONE quest's `done` value, leaving every
  // other quest in the array untouched.
  // Requirements:
  //   - Use `.map()` to produce a NEW array (same reasoning as addQuest
  //     above: don't mutate the existing quest objects or array).
  //   - Only the quest whose `id` matches should change; every other
  //     quest object should be the exact same reference it already was.
  function toggleDone(id: string) {
    // Replace this with a real implementation.
    console.log("TODO: toggleDone", id);
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
