/**
 * NEW in Module 14. Mocks src/api/notesApi.ts entirely -- the exact same
 * "mock the module boundary this component depends on" approach
 * QuestBreakdownPanel.test.tsx (Module 13) already established -- so this
 * file tests QuestNotesPanel's own rendering/state-machine logic, never a
 * real network call or a real backend.
 */
import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QuestNotesPanel } from "./QuestNotesPanel";
import { createNote, deleteNote, listNotes, streamAskQuestion } from "../api/notesApi";
import type { AskEvent } from "../api/notesApi";

vi.mock("../api/notesApi", () => ({
  createNote: vi.fn(),
  listNotes: vi.fn(),
  deleteNote: vi.fn(),
  streamAskQuestion: vi.fn(),
}));

async function* eventsFrom(events: AskEvent[]) {
  for (const event of events) {
    yield event;
  }
}

describe("QuestNotesPanel", () => {
  it("loads and shows existing notes on mount", async () => {
    vi.mocked(listNotes).mockResolvedValue([
      { id: "n1", title: "Boss Fight Prep", createdAt: "2026-08-09T00:00:00Z", chunkCount: 2 },
    ]);

    render(<QuestNotesPanel questId="quest-1" />);

    await waitFor(() => {
      expect(screen.getByText(/Boss Fight Prep/)).toBeInTheDocument();
    });
    expect(screen.getByText(/2 chunks/)).toBeInTheDocument();
  });

  it("shows an error message if loading notes fails", async () => {
    vi.mocked(listNotes).mockRejectedValue(new Error("Could not reach the QuestLog API."));

    render(<QuestNotesPanel questId="quest-1" />);

    await waitFor(() => {
      expect(screen.getByText("Could not reach the QuestLog API.")).toBeInTheDocument();
    });
  });

  it("adds a note and shows it in the list", async () => {
    const user = userEvent.setup();
    vi.mocked(listNotes).mockResolvedValue([]);
    vi.mocked(createNote).mockResolvedValue({
      id: "n2",
      title: "New Note",
      createdAt: "2026-08-09T00:00:00Z",
      chunkCount: 1,
    });

    render(<QuestNotesPanel questId="quest-1" />);
    await waitFor(() => screen.getByText("No notes yet. Add one below."));

    await user.type(screen.getByPlaceholderText(/Note title/), "New Note");
    await user.type(screen.getByPlaceholderText(/Paste or type/), "Some content here.");
    await user.click(screen.getByRole("button", { name: "Add Note" }));

    await waitFor(() => {
      expect(screen.getByText(/New Note/)).toBeInTheDocument();
    });
    expect(createNote).toHaveBeenCalledWith("quest-1", {
      title: "New Note",
      content: "Some content here.",
    });
  });

  it("removes a note when delete is clicked", async () => {
    const user = userEvent.setup();
    vi.mocked(listNotes).mockResolvedValue([
      { id: "n1", title: "Boss Fight Prep", createdAt: "2026-08-09T00:00:00Z", chunkCount: 2 },
    ]);
    vi.mocked(deleteNote).mockResolvedValue(undefined);

    render(<QuestNotesPanel questId="quest-1" />);
    await waitFor(() => screen.getByText(/Boss Fight Prep/));

    await user.click(screen.getByRole("button", { name: "Delete" }));

    await waitFor(() => {
      expect(screen.getByText("No notes yet. Add one below.")).toBeInTheDocument();
    });
    expect(deleteNote).toHaveBeenCalledWith("quest-1", "n1");
  });

  it("streams sources then a final answer when a question is asked", async () => {
    const user = userEvent.setup();
    vi.mocked(listNotes).mockResolvedValue([
      { id: "n1", title: "Boss Fight Prep", createdAt: "2026-08-09T00:00:00Z", chunkCount: 1 },
    ]);
    vi.mocked(streamAskQuestion).mockReturnValue(
      eventsFrom([
        {
          event: "sources",
          data: {
            sources: [
              {
                note_id: "n1",
                note_title: "Boss Fight Prep",
                chunk_index: 0,
                excerpt: "Bring fire resistant armor.",
              },
            ],
          },
        },
        { event: "token", data: { text: "According to your note: bring fire armor." } },
        { event: "result", data: { answer: "According to your note: bring fire armor." } },
      ]),
    );

    render(<QuestNotesPanel questId="quest-1" />);
    await waitFor(() => screen.getByText(/Boss Fight Prep/));

    await user.type(screen.getByPlaceholderText(/What armor/), "What armor?");
    await user.click(screen.getByRole("button", { name: "Ask" }));

    await waitFor(() => {
      expect(screen.getByText(/bring fire armor/)).toBeInTheDocument();
    });
    expect(screen.getByText(/Bring fire resistant armor/)).toBeInTheDocument();
  });

  it("shows an error message when asking reports an error event", async () => {
    const user = userEvent.setup();
    vi.mocked(listNotes).mockResolvedValue([
      { id: "n1", title: "Boss Fight Prep", createdAt: "2026-08-09T00:00:00Z", chunkCount: 1 },
    ]);
    vi.mocked(streamAskQuestion).mockReturnValue(
      eventsFrom([
        {
          event: "error",
          data: { message: "This quest has no notes yet. Add one before asking a question." },
        },
      ]),
    );

    render(<QuestNotesPanel questId="quest-1" />);
    await waitFor(() => screen.getByText(/Boss Fight Prep/));

    await user.type(screen.getByPlaceholderText(/What armor/), "What armor?");
    await user.click(screen.getByRole("button", { name: "Ask" }));

    await waitFor(() => {
      expect(
        screen.getByText("This quest has no notes yet. Add one before asking a question."),
      ).toBeInTheDocument();
    });
  });
});
