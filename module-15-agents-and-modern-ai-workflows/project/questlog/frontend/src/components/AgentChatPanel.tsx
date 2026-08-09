import { useState } from "react";
import { streamAgentChat } from "../api/agentApi";
import type { AgentEvent, AgentMessage } from "../api/agentApi";

type TurnStatus = "idle" | "streaming" | "error";

interface ToolCallDisplay {
  tool: string;
  input: Record<string, unknown>;
}

interface SourceDisplay {
  noteId: string;
  noteTitle: string;
  excerpt: string;
}

interface UsageDisplay {
  iterations: number;
  toolCalls: number;
}

/** Human-readable labels for each tool the agent can call -- see
 * backend/app/agent.py's own `AGENT_TOOLS` for the underlying six tools.
 * Purely cosmetic: a player watching this panel sees "Creating a
 * quest..." instead of the raw tool name "create_quest" while the agent
 * is working. Falls back to the raw name for a tool this map doesn't
 * recognize, so a future new tool never renders as literally nothing. */
const TOOL_LABELS: Record<string, string> = {
  list_quests: "Looking at your quests...",
  create_quest: "Creating a quest...",
  update_quest: "Updating a quest...",
  complete_quest: "Marking a quest complete...",
  search_quest_notes: "Searching your notes...",
  suggest_quest_breakdown: "Thinking of a breakdown...",
};

/**
 * NEW in Module 15 -- QuestLog's autonomous agent, the course's final
 * capstone feature. See lessons/11-building-questlogs-agent-frontend-and-going-live.md
 * for the full, line-by-line walkthrough of every state transition below.
 *
 * A real chat panel: `messages` is the *entire* memory this feature has
 * (see backend/app/models.py's `AgentChatMessage` docstring for the full,
 * honest accounting) -- held in this one component's own React state,
 * never persisted anywhere, and gone the moment this page unmounts or the
 * browser tab closes. Every submit resends the whole transcript so far,
 * exactly the same "the API is stateless; the caller resends history"
 * shape Module 13's own `ConversationManager` example already taught.
 */
export function AgentChatPanel() {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState<TurnStatus>("idle");
  const [streamedText, setStreamedText] = useState("");
  const [activeTool, setActiveTool] = useState<ToolCallDisplay | null>(null);
  const [sources, setSources] = useState<SourceDisplay[]>([]);
  const [usage, setUsage] = useState<UsageDisplay | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const question = input.trim();
    if (!question || status === "streaming") {
      return;
    }

    const nextMessages: AgentMessage[] = [...messages, { role: "user", content: question }];
    setMessages(nextMessages);
    setInput("");
    setStatus("streaming");
    setStreamedText("");
    setActiveTool(null);
    setSources([]);
    setUsage(null);
    setErrorMessage("");

    try {
      for await (const event of streamAgentChat(nextMessages)) {
        applyEvent(event, nextMessages);
      }
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Something went wrong.");
      setStatus("error");
    }
  }

  function applyEvent(event: AgentEvent, historyBeforeThisTurn: AgentMessage[]) {
    if (event.event === "token" && event.data.text !== undefined) {
      setStreamedText((current) => current + event.data.text);
      // A new token means the model is writing text again, not waiting on
      // a tool -- clear any "Creating a quest..." status from an earlier
      // tool call in this same turn.
      setActiveTool(null);
    } else if (event.event === "tool_call" && event.data.tool) {
      setActiveTool({ tool: event.data.tool, input: event.data.input ?? {} });
    } else if (event.event === "sources" && event.data.sources) {
      setSources(
        event.data.sources.map((source) => ({
          noteId: source.note_id,
          noteTitle: source.note_title,
          excerpt: source.excerpt,
        })),
      );
    } else if (event.event === "usage" && event.data.iterations !== undefined) {
      setUsage({ iterations: event.data.iterations, toolCalls: event.data.tool_calls ?? 0 });
    } else if (event.event === "result" && event.data.answer !== undefined) {
      // The turn's own tool-calling scratch work is deliberately never
      // added to `messages` -- only the finished answer becomes part of
      // the visible transcript the next turn resends. See
      // backend/app/models.py's `AgentChatMessage` docstring for this
      // feature's own stated memory-scope trade-off.
      setMessages([...historyBeforeThisTurn, { role: "assistant", content: event.data.answer }]);
      setStreamedText("");
      setActiveTool(null);
      setStatus("idle");
    } else if (event.event === "error") {
      setErrorMessage(event.data.message ?? "Something went wrong.");
      setStatus("error");
    }
  }

  return (
    <div className="flex h-[70vh] flex-col rounded-lg border border-violet-200 bg-violet-50/40">
      <div className="border-b border-violet-200 px-4 py-3">
        <h1 className="text-sm font-semibold text-violet-900">QuestLog Assistant</h1>
        <p className="text-xs text-violet-700">
          Ask it to list, create, or update quests, look through a quest's notes, or suggest a
          breakdown. It can't delete a quest -- do that from the quest's own page.
        </p>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-3" role="log" aria-label="Conversation">
        {messages.length === 0 && status === "idle" && (
          <p className="text-sm text-slate-500">
            Try: "What quests do I have?" or "Break down my dragon quest."
          </p>
        )}
        <ul className="flex flex-col gap-3">
          {messages.map((message, index) => (
            <li
              key={index}
              className={`max-w-[85%] rounded-md px-3 py-2 text-sm whitespace-pre-wrap ${
                message.role === "user"
                  ? "ml-auto bg-violet-600 text-white"
                  : "bg-white text-slate-800"
              }`}
            >
              {message.content}
            </li>
          ))}
        </ul>

        {/* `sources` is deliberately shown whenever it's non-empty, not
         * only while `status === "streaming"` -- a player should still be
         * able to see which notes the *last* answer was grounded in after
         * it finishes, not just while it's arriving. It's cleared at the
         * start of the next submit (see `handleSubmit` above), so it
         * never lingers from a turn before the one it actually belongs
         * to. */}
        {sources.length > 0 && (
          <div className="mt-3 max-w-[85%] rounded-md bg-white p-2 text-xs text-slate-600">
            <p className="mb-1 font-semibold">Notes consulted:</p>
            <ul className="list-inside list-disc">
              {sources.map((source) => (
                <li key={source.noteId}>
                  "{source.noteTitle}": {source.excerpt}
                </li>
              ))}
            </ul>
          </div>
        )}

        {status === "streaming" && (
          <div role="status" aria-label="Agent is working" className="mt-3 max-w-[85%]">
            {activeTool && (
              <p className="mb-1 text-xs italic text-violet-700">
                {TOOL_LABELS[activeTool.tool] ?? `Using ${activeTool.tool}...`}
              </p>
            )}
            <p className="whitespace-pre-wrap rounded-md bg-white px-3 py-2 text-sm text-slate-700">
              {streamedText || "Thinking..."}
            </p>
          </div>
        )}

        {status === "error" && <p className="mt-3 text-sm text-rose-700">{errorMessage}</p>}
      </div>

      <div className="border-t border-violet-200 px-4 py-2">
        {usage && (
          <p className="mb-1 text-xs text-slate-400">
            {usage.iterations} turn{usage.iterations === 1 ? "" : "s"}, {usage.toolCalls} tool
            call{usage.toolCalls === 1 ? "" : "s"} this turn.
          </p>
        )}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask the assistant..."
            disabled={status === "streaming"}
            className="flex-1 rounded-md border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={status === "streaming" || input.trim() === ""}
            className="rounded-md bg-violet-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {status === "streaming" ? "Thinking..." : "Send"}
          </button>
        </form>
      </div>
    </div>
  );
}
