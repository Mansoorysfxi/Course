/**
 * QuestCard is a small, "presentational" component (its own docstring in
 * QuestCard.tsx uses that exact word) -- it receives a `quest` and an
 * `onToggleDone` callback as props and renders purely from those, with no
 * context, no hooks of its own beyond what its props already give it.
 * This makes it the simplest possible test in this module -- see
 * lessons/07-frontend-testing-with-vitest-and-rtl.md's "start with the
 * simplest component" note -- and a good one to read first if the other
 * three test files in this module feel like too much at once.
 */
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { QuestCard } from "./QuestCard";
import type { Quest } from "../types/quest";

const quest: Quest = {
  id: "quest-1",
  title: "Slay the Dragon",
  description: "The dragon has been terrorizing the northern villages.",
  priority: "high",
  done: false,
  questLine: "Main Story",
  createdAt: "2026-01-01T00:00:00.000Z",
};

function renderQuestCard(overrides: Partial<Quest> = {}, onToggleDone = vi.fn()) {
  return render(
    // QuestCard renders a react-router <Link> internally -- it needs a
    // <MemoryRouter> ancestor for the same reason ProtectedRoute.test.tsx's
    // component does, even though this test never navigates anywhere.
    <MemoryRouter>
      <ul>
        <QuestCard quest={{ ...quest, ...overrides }} onToggleDone={onToggleDone} />
      </ul>
    </MemoryRouter>,
  );
}

describe("QuestCard", () => {
  it("renders the quest's title, priority, and quest line", () => {
    renderQuestCard();

    expect(screen.getByText("Slay the Dragon")).toBeInTheDocument();
    expect(screen.getByText("High")).toBeInTheDocument();
    expect(screen.getByText("Main Story")).toBeInTheDocument();
  });

  it("shows the checkbox as unchecked for a quest that isn't done", () => {
    renderQuestCard({ done: false });
    expect(screen.getByRole("checkbox")).not.toBeChecked();
  });

  it("shows the checkbox as checked for a quest that is done", () => {
    renderQuestCard({ done: true });
    expect(screen.getByRole("checkbox")).toBeChecked();
  });

  it("calls onToggleDone with the quest's id when the checkbox is clicked", async () => {
    const user = userEvent.setup();
    const handleToggle = vi.fn();
    renderQuestCard({}, handleToggle);

    await user.click(screen.getByRole("checkbox"));

    expect(handleToggle).toHaveBeenCalledTimes(1);
    expect(handleToggle).toHaveBeenCalledWith("quest-1");
  });
});
