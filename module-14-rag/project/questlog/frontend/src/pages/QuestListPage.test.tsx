/**
 * Covers the three states lessons/07-data-fetching-loading-and-error-states.md
 * (Module 04) named and this module's own
 * lessons/07-frontend-testing-with-vitest-and-rtl.md revisits through a
 * testing lens: **loading**, **error**, and **success**. Like
 * ProtectedRoute.test.tsx, this file mocks the hook QuestListPage.tsx
 * depends on (`useQuests`, from ../context/QuestsContext) rather than
 * wiring up real providers and a real (or fake) network call -- this
 * page's own rendering logic is what's under test here, not
 * QuestsContext's fetching logic (which belongs in its own test file, not
 * shown in this module -- see Exercise 05 for practice writing exactly
 * that one).
 */
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { QuestListPage } from "./QuestListPage";
import { useQuests } from "../context/QuestsContext";
import type { Quest } from "../types/quest";

vi.mock("../context/QuestsContext", () => ({
  useQuests: vi.fn(),
}));

const sampleQuest: Quest = {
  id: "quest-1",
  title: "Slay the Dragon",
  description: "The dragon has been terrorizing the northern villages.",
  priority: "high",
  done: false,
  questLine: "Main Story",
  createdAt: "2026-01-01T00:00:00.000Z",
};

function renderQuestListPage() {
  return render(
    <MemoryRouter>
      <QuestListPage />
    </MemoryRouter>,
  );
}

describe("QuestListPage", () => {
  it("shows a loading indicator while quests are loading", () => {
    vi.mocked(useQuests).mockReturnValue({
      quests: [],
      loading: true,
      error: null,
      refetch: vi.fn(),
      addQuest: vi.fn(),
      updateQuest: vi.fn(),
      deleteQuest: vi.fn(),
      toggleDone: vi.fn(),
      getQuest: vi.fn(),
    });

    renderQuestListPage();

    expect(screen.getByRole("status")).toBeInTheDocument();
    expect(screen.queryByText("Quest Board")).not.toBeInTheDocument();
  });

  it("shows an error banner, with a retry button, when fetching failed", () => {
    const refetch = vi.fn();
    vi.mocked(useQuests).mockReturnValue({
      quests: [],
      loading: false,
      error: "Could not reach the QuestLog API.",
      refetch,
      addQuest: vi.fn(),
      updateQuest: vi.fn(),
      deleteQuest: vi.fn(),
      toggleDone: vi.fn(),
      getQuest: vi.fn(),
    });

    renderQuestListPage();

    expect(screen.getByText(/Could not reach the QuestLog API\./)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
  });

  it("renders every quest once loading succeeds", () => {
    vi.mocked(useQuests).mockReturnValue({
      quests: [sampleQuest],
      loading: false,
      error: null,
      refetch: vi.fn(),
      addQuest: vi.fn(),
      updateQuest: vi.fn(),
      deleteQuest: vi.fn(),
      toggleDone: vi.fn(),
      getQuest: vi.fn(),
    });

    renderQuestListPage();

    expect(screen.getByText("Quest Board")).toBeInTheDocument();
    expect(screen.getByText("Slay the Dragon")).toBeInTheDocument();
    expect(screen.getByText("1 of 1 quest shown")).toBeInTheDocument();
  });

  it("shows the empty-filters message once a filter excludes every quest", async () => {
    const user = userEvent.setup();
    vi.mocked(useQuests).mockReturnValue({
      quests: [sampleQuest],
      loading: false,
      error: null,
      refetch: vi.fn(),
      addQuest: vi.fn(),
      updateQuest: vi.fn(),
      deleteQuest: vi.fn(),
      toggleDone: vi.fn(),
      getQuest: vi.fn(),
    });

    renderQuestListPage();

    // Present before filtering: `quests` has one, "high"-priority quest.
    expect(screen.getByText("Slay the Dragon")).toBeInTheDocument();

    // `sampleQuest` is "high" priority -- selecting "Low" in the Priority
    // filter is a real user interaction (this component's own local
    // `priorityFilter` state, QuestListPage.tsx), not a mocked return
    // value, and it leaves zero visible quests even though `quests`
    // itself still has one. See lessons/07-frontend-testing-with-vitest-and-rtl.md's
    // "testing behavior, not implementation" section for why this test
    // drives the real `<select>` instead of reaching into component state.
    await user.selectOptions(screen.getByLabelText("Priority"), "Low");

    expect(screen.queryByText("Slay the Dragon")).not.toBeInTheDocument();
    expect(screen.getByText("No quests match these filters.")).toBeInTheDocument();
  });
});
