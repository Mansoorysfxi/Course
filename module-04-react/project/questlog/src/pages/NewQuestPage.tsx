import { useNavigate } from "react-router";
import { useQuests } from "../context/QuestsContext";
import { QuestForm } from "../components/QuestForm";
import type { NewQuestInput } from "../types/quest";

/** The "add a quest" page. Delegates the actual form UI to QuestForm and
 * only supplies what's specific to *creating*: calling `addQuest` and
 * navigating back to the board afterward. */
export function NewQuestPage() {
  const { addQuest } = useQuests();
  const navigate = useNavigate();

  function handleSubmit(values: NewQuestInput) {
    addQuest(values);
    navigate("/");
  }

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="mb-6 text-2xl font-bold text-slate-900">New Quest</h1>
      <QuestForm submitLabel="Add Quest" onSubmit={handleSubmit} onCancel={() => navigate("/")} />
    </div>
  );
}
