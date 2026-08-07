import { useState, type FormEvent } from "react";
import type { Priority } from "../types";

interface QuestFormProps {
  onAddQuest: (title: string, priority: Priority) => void;
}

// TODO (Exercise 02, Step 3): QuestForm
// See lessons/05-forms-controlled-components-and-lifting-state.md.
//
// Build a CONTROLLED form with two fields:
//   1. A text <input> for the title, its value held in a `useState<string>`
//      right here in this component.
//   2. A <select> for priority ("low" | "medium" | "high"), its value
//      held in its own `useState<Priority>`.
//
// On submit:
//   - Call `event.preventDefault()` first (same API you already used on
//     a plain HTML form in Module 03, Lesson 06 -- same reason: stop the
//     browser's default full-page-reload form submission).
//   - If the title is empty (after trimming whitespace), do nothing --
//     don't call onAddQuest with a blank title.
//   - Call `onAddQuest(title, priority)` -- this is the "lifting state up"
//     part: THIS component doesn't decide what happens when a quest is
//     added, its parent (App.tsx) does, via this prop.
//   - Reset the title field back to an empty string after a successful
//     submit (leave the priority field as whatever it currently is).
//
// Reminder of what "controlled" means (from the lesson): the input's
// CURRENT value lives in this component's state, fed back in via the
// `value` prop, and every keystroke updates that state via `onChange`.

export function QuestForm({ onAddQuest }: QuestFormProps) {
  // Replace this stub with your real controlled form.
  return (
    <form className="card">
      <p className="muted">TODO: build this form. See the comments above.</p>
    </form>
  );
}
