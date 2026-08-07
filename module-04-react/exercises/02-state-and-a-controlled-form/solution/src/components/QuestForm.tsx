import { useState, type FormEvent } from "react";
import type { Priority } from "../types";

interface QuestFormProps {
  onAddQuest: (title: string, priority: Priority) => void;
}

export function QuestForm({ onAddQuest }: QuestFormProps) {
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState<Priority>("medium");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedTitle = title.trim();
    if (trimmedTitle === "") {
      return;
    }

    onAddQuest(trimmedTitle, priority);
    setTitle("");
    // Deliberately NOT resetting `priority` -- if you're adding several
    // quests of the same priority in a row, resetting it every time would
    // be annoying. This is a small, real UX decision, not an oversight.
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <div className="field">
        <label htmlFor="title">Title</label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
      </div>

      <div className="field">
        <label htmlFor="priority">Priority</label>
        <select
          id="priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value as Priority)}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      <button type="submit" className="btn">
        Add Quest
      </button>
    </form>
  );
}
