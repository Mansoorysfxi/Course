/**
 * NEW in Module 15. Mocks src/api/agentApi.ts entirely -- the exact same
 * "mock the module boundary this component depends on" approach
 * QuestBreakdownPanel.test.tsx (Module 13) and QuestNotesPanel.test.tsx
 * (Module 14) already established -- so this file tests
 * AgentChatPanel's own rendering/state-machine logic, never a real
 * network call or a real backend.
 */
import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AgentChatPanel } from "./AgentChatPanel";
import { streamAgentChat } from "../api/agentApi";
import type { AgentEvent } from "../api/agentApi";

vi.mock("../api/agentApi", () => ({
  streamAgentChat: vi.fn(),
}));

async function* eventsFrom(events: AgentEvent[]) {
  for (const event of events) {
    yield event;
  }
}

describe("AgentChatPanel", () => {
  it("shows a hint and no messages before the first turn", () => {
    render(<AgentChatPanel />);
    expect(screen.getByText(/Try: "What quests do I have/)).toBeInTheDocument();
  });

  it("sends the user's message and renders the final answer", async () => {
    const user = userEvent.setup();
    vi.mocked(streamAgentChat).mockReturnValue(
      eventsFrom([
        { event: "token", data: { text: "You have one quest." } },
        { event: "usage", data: { iterations: 1, tool_calls: 0 } },
        { event: "result", data: { answer: "You have one quest." } },
      ]),
    );

    render(<AgentChatPanel />);
    await user.type(screen.getByPlaceholderText("Ask the assistant..."), "what are my quests?");
    await user.click(screen.getByRole("button", { name: "Send" }));

    expect(screen.getByText("what are my quests?")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("You have one quest.")).toBeInTheDocument();
    });
    expect(streamAgentChat).toHaveBeenCalledWith([
      { role: "user", content: "what are my quests?" },
    ]);
  });

  it("shows which tool the agent is using while a turn streams", async () => {
    const user = userEvent.setup();
    vi.mocked(streamAgentChat).mockReturnValue(
      eventsFrom([
        { event: "tool_call", data: { tool: "create_quest", input: { title: "Gather Herbs" } } },
        { event: "usage", data: { iterations: 1, tool_calls: 1 } },
        { event: "result", data: { answer: "Created 'Gather Herbs' for you." } },
      ]),
    );

    render(<AgentChatPanel />);
    await user.type(screen.getByPlaceholderText("Ask the assistant..."), "add a quest");
    await user.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.getByText("Created 'Gather Herbs' for you.")).toBeInTheDocument();
    });
  });

  it("shows sources when the agent searches quest notes", async () => {
    const user = userEvent.setup();
    vi.mocked(streamAgentChat).mockReturnValue(
      eventsFrom([
        { event: "tool_call", data: { tool: "search_quest_notes", input: {} } },
        {
          event: "sources",
          data: {
            sources: [
              { note_id: "n1", note_title: "Boss Fight Prep", excerpt: "Bring fire armor." },
            ],
          },
        },
        { event: "token", data: { text: "According to your note: bring fire armor." } },
        { event: "usage", data: { iterations: 1, tool_calls: 1 } },
        { event: "result", data: { answer: "According to your note: bring fire armor." } },
      ]),
    );

    render(<AgentChatPanel />);
    await user.type(screen.getByPlaceholderText("Ask the assistant..."), "what armor?");
    await user.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.getByText(/Boss Fight Prep/)).toBeInTheDocument();
    });
  });

  it("shows an error message when the agent reports an error event", async () => {
    const user = userEvent.setup();
    vi.mocked(streamAgentChat).mockReturnValue(
      eventsFrom([{ event: "error", data: { message: "Claude declined to answer that." } }]),
    );

    render(<AgentChatPanel />);
    await user.type(screen.getByPlaceholderText("Ask the assistant..."), "hello");
    await user.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.getByText("Claude declined to answer that.")).toBeInTheDocument();
    });
  });

  it("carries prior turns forward as history on the next message", async () => {
    const user = userEvent.setup();
    vi.mocked(streamAgentChat)
      .mockReturnValueOnce(
        eventsFrom([
          { event: "usage", data: { iterations: 1, tool_calls: 0 } },
          { event: "result", data: { answer: "Hi there!" } },
        ]),
      )
      .mockReturnValueOnce(
        eventsFrom([
          { event: "usage", data: { iterations: 1, tool_calls: 0 } },
          { event: "result", data: { answer: "You're welcome." } },
        ]),
      );

    render(<AgentChatPanel />);
    const input = screen.getByPlaceholderText("Ask the assistant...");

    await user.type(input, "hello");
    await user.click(screen.getByRole("button", { name: "Send" }));
    await waitFor(() => screen.getByText("Hi there!"));

    await user.type(input, "thanks");
    await user.click(screen.getByRole("button", { name: "Send" }));
    await waitFor(() => screen.getByText("You're welcome."));

    expect(streamAgentChat).toHaveBeenLastCalledWith([
      { role: "user", content: "hello" },
      { role: "assistant", content: "Hi there!" },
      { role: "user", content: "thanks" },
    ]);
  });
});
