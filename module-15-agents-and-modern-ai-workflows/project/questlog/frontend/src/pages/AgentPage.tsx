import { AgentChatPanel } from "../components/AgentChatPanel";

/** NEW in Module 15 -- a thin page wrapper around `AgentChatPanel`,
 * exactly the same "page picks the layout slot, component owns the real
 * work" split every other page in this app already follows (compare
 * `QuestDetailPage`'s own use of `QuestNotesPanel`). Routed at `/agent`
 * (see `src/App.tsx`) -- a top-level page, not nested under one quest's
 * own URL, because this agent is a general assistant across every quest
 * the player has, not a per-quest feature. */
export function AgentPage() {
  return <AgentChatPanel />;
}
