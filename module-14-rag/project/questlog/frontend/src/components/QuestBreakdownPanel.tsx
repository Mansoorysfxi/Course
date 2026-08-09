import { useState } from "react";
import { streamQuestBreakdown } from "../api/aiApi";

interface QuestBreakdownPanelProps {
  questId: string;
  /** Called once per suggestion the player accepts. QuestDetailPage.tsx
   * passes a function that calls `addQuest` (QuestsContext) -- this
   * component knows nothing about QuestsContext itself, the same
   * "collect input, hand it to whoever rendered you" pattern
   * QuestForm.tsx already established for creating/editing a quest. */
  onAcceptSuggestion: (title: string) => void;
}

type BreakdownStatus = "idle" | "streaming" | "done" | "error";

/**
 * NEW in Module 13 -- QuestLog's first AI-powered UI. Renders a button
 * that starts a streamed request to `POST /api/quests/{id}/suggest-breakdown`
 * (src/api/aiApi.ts), shows Claude's raw output arriving token by token
 * while it's still generating, and then swaps to a clean list of
 * accept-or-ignore suggestions once the backend's `result` event confirms
 * the full response parsed and validated. See
 * lessons/08-building-questlogs-ai-assistant-frontend.md for the full
 * walkthrough of every state transition below, and
 * app/ai_assistant.py's own module docstring (backend) for exactly why
 * showing the raw stream, then switching to the parsed result, is the
 * honest way to reconcile streaming with structured output.
 */
export function QuestBreakdownPanel({ questId, onAcceptSuggestion }: QuestBreakdownPanelProps) {
  const [status, setStatus] = useState<BreakdownStatus>("idle");
  const [streamedText, setStreamedText] = useState("");
  const [checkingExisting, setCheckingExisting] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [addedTitles, setAddedTitles] = useState<Set<string>>(new Set());

  async function handleSuggestBreakdown() {
    setStatus("streaming");
    setStreamedText("");
    setCheckingExisting(false);
    setSuggestions([]);
    setErrorMessage("");
    setAddedTitles(new Set());

    try {
      // `for await...of` over an async generator -- each `event` here is
      // one `BreakdownEvent` src/api/aiApi.ts yielded, in the exact order
      // the backend produced it. This loop is the entire state machine:
      // every event type updates exactly the piece of state it owns, and
      // nothing here needs to know anything about Server-Sent Events,
      // `ReadableStream`s, or byte decoding -- that's all sealed inside
      // `streamQuestBreakdown` itself.
      for await (const event of streamQuestBreakdown(questId)) {
        if (event.event === "token" && event.data.text !== undefined) {
          setStreamedText((current) => current + event.data.text);
        } else if (event.event === "tool_call") {
          setCheckingExisting(true);
        } else if (event.event === "result" && event.data.sub_quests) {
          setSuggestions(event.data.sub_quests);
          setStatus("done");
        } else if (event.event === "error") {
          setErrorMessage(event.data.message ?? "Something went wrong.");
          setStatus("error");
        }
      }
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Something went wrong.");
      setStatus("error");
    }
  }

  function handleAccept(title: string) {
    onAcceptSuggestion(title);
    setAddedTitles((current) => new Set(current).add(title));
  }

  return (
    <div className="mt-6 rounded-lg border border-indigo-200 bg-indigo-50/40 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-indigo-900">AI Assistant</h2>
        <button
          type="button"
          onClick={handleSuggestBreakdown}
          disabled={status === "streaming"}
          className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {status === "streaming" ? "Thinking..." : "Suggest a Breakdown"}
        </button>
      </div>

      {status === "streaming" && (
        <div
          role="status"
          aria-label="Generating a quest breakdown"
          className="text-sm text-indigo-700"
        >
          {checkingExisting && (
            <p className="mb-2 italic">Checking your other quests for duplicates...</p>
          )}
          {/* The raw, still-arriving JSON text -- shown deliberately, not
           * hidden, so this is a genuinely *observable* streaming UI, not
           * just a spinner. See this component's own module docstring for
           * why the sub-quest list below only appears once the stream's
           * `result` event arrives, never parsed from this partial text. */}
          <pre className="max-h-32 overflow-y-auto whitespace-pre-wrap break-words rounded bg-white p-2 font-mono text-xs text-slate-500">
            {streamedText || "Generating..."}
          </pre>
        </div>
      )}

      {status === "error" && <p className="text-sm text-rose-700">{errorMessage}</p>}

      {status === "done" && (
        <ul className="flex flex-col gap-2">
          {suggestions.map((title) => (
            <li
              key={title}
              className="flex items-center justify-between gap-2 rounded-md bg-white px-3 py-2 text-sm"
            >
              <span>{title}</span>
              <button
                type="button"
                onClick={() => handleAccept(title)}
                disabled={addedTitles.has(title)}
                className="rounded-md border border-indigo-300 px-2 py-1 text-xs font-medium text-indigo-700 hover:bg-indigo-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {addedTitles.has(title) ? "Added" : "Add as quest"}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
