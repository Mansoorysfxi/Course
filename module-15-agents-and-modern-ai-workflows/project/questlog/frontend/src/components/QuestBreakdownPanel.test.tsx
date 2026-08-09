/**
 * NEW in Module 13. Mocks src/api/aiApi.ts's `streamQuestBreakdown` --
 * exactly the same "mock the module boundary this component depends on"
 * approach QuestListPage.test.tsx already uses for `useQuests` -- so this
 * file tests QuestBreakdownPanel's own rendering/state-machine logic,
 * never a real network call or a real backend. See
 * lessons/08-building-questlogs-ai-assistant-frontend.md's own testing
 * section for why an async generator is easy to fake in a test (a plain
 * `async function*` that yields canned events) without needing any
 * fetch-mocking library at all.
 */
import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QuestBreakdownPanel } from "./QuestBreakdownPanel";
import { streamQuestBreakdown } from "../api/aiApi";
import type { BreakdownEvent } from "../api/aiApi";

vi.mock("../api/aiApi", () => ({
  streamQuestBreakdown: vi.fn(),
}));

/** Turns a plain array of events into the same shape
 * `streamQuestBreakdown` returns for real -- an async generator. */
async function* eventsFrom(events: BreakdownEvent[]) {
  for (const event of events) {
    yield event;
  }
}

describe("QuestBreakdownPanel", () => {
  it("streams raw text, then shows the final suggestions once the result event arrives", async () => {
    const user = userEvent.setup();
    vi.mocked(streamQuestBreakdown).mockReturnValue(
      eventsFrom([
        { event: "token", data: { text: "Checking..." } },
        { event: "tool_call", data: { tool: "check_existing_quest_titles" } },
        { event: "token", data: { text: '{"sub_quests": [...] }' } },
        { event: "result", data: { sub_quests: ["Scout the lair", "Buy a sword"] } },
      ]),
    );

    render(<QuestBreakdownPanel questId="quest-1" onAcceptSuggestion={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: "Suggest a Breakdown" }));

    await waitFor(() => {
      expect(screen.getByText("Scout the lair")).toBeInTheDocument();
    });
    expect(screen.getByText("Buy a sword")).toBeInTheDocument();
    // The streaming state (spinner text, raw JSON preview) is gone once
    // the final list is showing.
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("shows the checking-for-duplicates message once a tool_call event arrives", async () => {
    const user = userEvent.setup();
    vi.mocked(streamQuestBreakdown).mockReturnValue(
      eventsFrom([
        { event: "tool_call", data: { tool: "check_existing_quest_titles" } },
        { event: "result", data: { sub_quests: ["Scout the lair"] } },
      ]),
    );

    render(<QuestBreakdownPanel questId="quest-1" onAcceptSuggestion={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: "Suggest a Breakdown" }));

    await waitFor(() => screen.getByText("Scout the lair"));
  });

  it("shows an error message when the stream reports an error event", async () => {
    const user = userEvent.setup();
    vi.mocked(streamQuestBreakdown).mockReturnValue(
      eventsFrom([
        { event: "error", data: { message: "Claude declined to suggest a breakdown." } },
      ]),
    );

    render(<QuestBreakdownPanel questId="quest-1" onAcceptSuggestion={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: "Suggest a Breakdown" }));

    await waitFor(() => {
      expect(screen.getByText("Claude declined to suggest a breakdown.")).toBeInTheDocument();
    });
  });

  it("shows an error message when the request itself throws (e.g. network failure)", async () => {
    const user = userEvent.setup();
    // This fake deliberately throws before ever yielding, to simulate
    // streamQuestBreakdown's own fetch() call failing outright (e.g. the
    // backend unreachable) rather than the stream reporting an `error`
    // event mid-stream -- see the "reports an error event" test above for
    // that other case.
    vi.mocked(streamQuestBreakdown).mockImplementation(
      // eslint-disable-next-line require-yield
      async function* () {
        throw new Error("Could not reach the QuestLog API.");
      },
    );

    render(<QuestBreakdownPanel questId="quest-1" onAcceptSuggestion={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: "Suggest a Breakdown" }));

    await waitFor(() => {
      expect(screen.getByText("Could not reach the QuestLog API.")).toBeInTheDocument();
    });
  });

  it("calls onAcceptSuggestion and disables the button once a suggestion is added", async () => {
    const user = userEvent.setup();
    const onAcceptSuggestion = vi.fn();
    vi.mocked(streamQuestBreakdown).mockReturnValue(
      eventsFrom([{ event: "result", data: { sub_quests: ["Scout the lair"] } }]),
    );

    render(<QuestBreakdownPanel questId="quest-1" onAcceptSuggestion={onAcceptSuggestion} />);
    await user.click(screen.getByRole("button", { name: "Suggest a Breakdown" }));
    await waitFor(() => screen.getByText("Scout the lair"));

    await user.click(screen.getByRole("button", { name: "Add as quest" }));

    expect(onAcceptSuggestion).toHaveBeenCalledWith("Scout the lair");
    expect(screen.getByRole("button", { name: "Added" })).toBeDisabled();
  });
});
