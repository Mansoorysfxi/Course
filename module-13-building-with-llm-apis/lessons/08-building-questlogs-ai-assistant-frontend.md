# Lesson 08 — Building QuestLog's AI Assistant: The Frontend

Like Lesson 07, this lesson describes this module's own
`project/questlog/frontend/` code directly — every command and every
piece of output shown below was actually run while generating this
module.

## What you'll learn

- Why this feature's frontend uses `fetch()` with a `ReadableStream`,
  not the browser's native `EventSource`, to consume Server-Sent Events.
- How to parse a raw SSE byte stream into structured events in the
  browser, by hand, understanding exactly what's happening rather than
  trusting a library to do it invisibly.
- How to model a streaming AI feature's UI as a small, explicit state
  machine — idle, streaming, done, error — and why that mirrors the
  loading/error/success pattern Module 04 already taught for ordinary
  data fetching.
- How this feature's own test suite verifies that state machine without
  ever making a real network call.

## Why this matters

Lesson 07 built a real, tested, streaming backend endpoint — but a
backend endpoint nobody's UI ever calls isn't a feature yet. This lesson
is the other half: the part the player actually sees and interacts with.
It's also where Module 04's original "loading, error, success" framing
for data fetching gets a genuine fourth state worth understanding on its
own: **streaming** — a state that's neither "still loading with nothing
to show" nor "fully loaded," but something in between, worth its own
explicit UI.

## Prerequisites

- **Lesson 02 (streaming) and Lesson 07 (the backend this lesson calls)**
  — this lesson is the client half of exactly that server.
- **Module 04's data-fetching, loading/error-states lesson** — this
  lesson's state machine is a direct extension of that one, not a
  different pattern.
- **Module 07's `http.ts`/`Authorization` header pattern** — this
  lesson's new `aiApi.ts` reuses the same stored-JWT-and-Bearer-header
  approach, adapted for a streamed response.

## The concept, explained simply

Think of consuming this stream the way you'd think about a dialogue
system reading a stream of incoming network packets character by
character and deciding, packet by packet, whether it's received a
*complete* line yet or needs to keep buffering. Bytes arrive from the
network in arbitrary-sized chunks that have no obligation to line up with
anything meaningful — a chunk might contain half an event, three whole
events, or one whole event plus the start of the next one. The frontend's
job, exactly like that packet-buffering dialogue system, is to
accumulate bytes into a buffer, repeatedly check whether a *complete*
unit (one SSE event, ending in a blank line) has arrived yet, and only
then act on it — leaving any leftover partial data in the buffer for the
next chunk to complete.

## The details

### Why `fetch()`, not `EventSource`

The browser has a built-in API purpose-built for consuming Server-Sent
Events: `EventSource`. This feature doesn't use it, for a real, concrete
reason: **`EventSource` can only issue `GET` requests and cannot set
custom request headers at all.** This endpoint is a `POST` (Lesson 07's
own explanation of why), and every single `/api/quests` route — this new
one included — requires an `Authorization: Bearer <token>` header
(Module 07's whole auth system). `EventSource` structurally cannot do
either of those things. `fetch()`, with its own `ReadableStream`-typed
response body, has no such restriction — it's a plain HTTP request like
any other, whose *response* happens to be delivered incrementally rather
than all at once.

### `src/api/aiApi.ts` — reading raw bytes into structured events

```typescript
export async function* streamQuestBreakdown(questId: string): AsyncGenerator<BreakdownEvent> {
  const token = getStoredToken();

  const response = await fetch(`${API_BASE_URL}/api/quests/${questId}/suggest-breakdown`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  if (response.status === 503) {
    throw new Error("The AI assistant isn't configured on this server yet.");
  }
  if (!response.ok || response.body === null) {
    throw new Error(`The AI assistant request failed (status ${response.status}).`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let boundary = buffer.indexOf("\n\n");
    while (boundary !== -1) {
      const rawEvent = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);

      const eventLine = rawEvent.split("\n").find((line) => line.startsWith("event: "));
      const dataLine = rawEvent.split("\n").find((line) => line.startsWith("data: "));
      if (eventLine && dataLine) {
        yield {
          event: eventLine.slice("event: ".length) as BreakdownEvent["event"],
          data: JSON.parse(dataLine.slice("data: ".length)),
        };
      }

      boundary = buffer.indexOf("\n\n");
    }
  }
}
```

Piece by piece: `response.body.getReader()` gets a **reader** over the
response's raw byte stream — you pull chunks from it explicitly, one
`await reader.read()` at a time, rather than the whole body arriving as
one value the way a normal `await response.json()` call would. `TextDecoder`
turns each chunk's raw bytes into text; `{ stream: true }` tells it a
multi-byte character might be split across two chunks and to hold onto
any incomplete trailing bytes rather than corrupting them. The inner
`while (boundary !== -1)` loop is this lesson's own "buffer until you
have a complete unit" idea made real: it drains every *complete* event
(ending in a blank line, `"\n\n"`) currently sitting in `buffer`, and
whatever's left — a partial event that hasn't finished arriving yet —
stays in `buffer` for the next chunk to complete. `async function*`
(an async generator) is what lets the calling code write a plain `for
await (const event of streamQuestBreakdown(id))` loop instead of manually
managing this reader/buffer machinery itself — Lesson 02's async-generator
concept, applied here to consuming a stream from the browser side instead
of the SDK's own helper.

### `src/components/QuestBreakdownPanel.tsx` — the UI as an explicit state machine

```tsx
type BreakdownStatus = "idle" | "streaming" | "done" | "error";

export function QuestBreakdownPanel({ questId, onAcceptSuggestion }: QuestBreakdownPanelProps) {
  const [status, setStatus] = useState<BreakdownStatus>("idle");
  const [streamedText, setStreamedText] = useState("");
  const [checkingExisting, setCheckingExisting] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [errorMessage, setErrorMessage] = useState("");

  async function handleSuggestBreakdown() {
    setStatus("streaming");
    // ... reset every piece of state this run owns ...

    try {
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
  // ...
}
```

Four states, matching this lesson's own "concept" section directly:
`"idle"` (nothing happening yet — the button is available), `"streaming"`
(a request is in flight; the raw text and a "checking your other quests"
note are shown live, exactly this lesson's own "observable streaming"
principle from Lesson 02, not a bare spinner hiding what's happening),
`"done"` (the validated `result` event arrived — the raw text is
discarded and a clean list of accept/ignore suggestions is shown
instead), and `"error"` (either the stream itself reported an `error`
event, or `streamQuestBreakdown` threw — both land in the same `catch`
block and the same UI state, because from the player's point of view,
"the feature didn't work" is one state regardless of exactly where it
failed).

**Why the raw streamed text is shown, then thrown away.** This is the
frontend's own honest reconciliation of Lesson 07's streaming/structured-output
tension: the player sees real, live progress the instant Claude starts
generating (a genuinely responsive feel — the entire point of streaming,
Lesson 02), but the actual sub-quest list that becomes interactive
(the "Add as quest" buttons) only ever renders from the `result` event's
already-parsed, already-validated `sub_quests` array — never from
partially-accumulated JSON text, which (as Lesson 07 explained) isn't
safely parseable until it's complete anyway.

### Wiring it into `QuestDetailPage.tsx`

```tsx
const handleAcceptSuggestion = async (title: string) => {
  await addQuest({
    title,
    description: `A sub-quest of "${quest.title}", suggested by the AI assistant.`,
    priority: quest.priority,
    questLine: quest.questLine,
  });
};

// ... later, in the JSX ...
<QuestBreakdownPanel questId={quest.id} onAcceptSuggestion={handleAcceptSuggestion} />
```

`QuestBreakdownPanel` knows nothing about `QuestsContext`, `addQuest`, or
how a new quest actually gets created — it only calls whatever function
its `onAcceptSuggestion` prop was given, the exact same "the component
collects input, its parent decides what happens with it" separation
`QuestForm`'s own `onSubmit` prop already established back in Module 04.
Accepting a suggestion creates a real quest through the exact same
`addQuest` path (and therefore the exact same `POST /api/quests` call,
and the exact same Redis cache invalidation from Module 10) every other
"create a quest" action in this app already uses — nothing new was built
for that part at all.

### Testing this feature with no real network call

`src/components/QuestBreakdownPanel.test.tsx` mocks `streamQuestBreakdown`
itself — the exact module-boundary-mocking approach `QuestListPage.test.tsx`
already used for `useQuests` back in Module 08 — by replacing it with a
plain async generator that yields canned events:

```tsx
vi.mock("../api/aiApi", () => ({
  streamQuestBreakdown: vi.fn(),
}));

async function* eventsFrom(events: BreakdownEvent[]) {
  for (const event of events) {
    yield event;
  }
}

it("streams raw text, then shows the final suggestions once the result event arrives", async () => {
  vi.mocked(streamQuestBreakdown).mockReturnValue(
    eventsFrom([
      { event: "token", data: { text: "Checking..." } },
      { event: "tool_call", data: { tool: "check_existing_quest_titles" } },
      { event: "result", data: { sub_quests: ["Scout the lair", "Buy a sword"] } },
    ]),
  );

  render(<QuestBreakdownPanel questId="quest-1" onAcceptSuggestion={vi.fn()} />);
  await userEvent.setup().click(screen.getByRole("button", { name: "Suggest a Breakdown" }));

  await waitFor(() => expect(screen.getByText("Scout the lair")).toBeInTheDocument());
});
```

Because `streamQuestBreakdown` is a plain async generator function from
the component's point of view, faking it in a test needs nothing more
exotic than another plain async generator — no fetch-mocking library, no
fake `ReadableStream`, no simulated network timing at all. Five tests
cover: the full happy path (streaming text, then the final list); the
tool-call indicator appearing; an `error` event from the stream;
`streamQuestBreakdown` itself throwing (simulating the initial `fetch()`
failing outright); and accepting a suggestion correctly calling
`onAcceptSuggestion` and disabling its own button afterward.

**Actual output**, running the whole frontend suite (run for real from
`module-13-building-with-llm-apis/project/questlog/frontend/`):

```bash
npm ci
npx vitest run
```

```
 Test Files  5 passed (5)
      Tests  22 passed (22)
```

22 tests — the 17 already passing at the end of Module 11, plus this
lesson's 5 new ones. `npm run build` (TypeScript compilation plus the
Vite production build) also succeeds with zero type errors, and
`npm run lint` reports no new warnings from any file this module added or
changed.

**Try it yourself:** In `QuestBreakdownPanel.test.tsx`'s first test,
change the canned `result` event's `sub_quests` to an empty array (`[]`)
and rerun `npx vitest run`. Predict, before running it, whether the test
still passes — it shouldn't (the `getByText("Scout the lair")` assertion
has nothing left to find). Now look at `QuestBreakdownPanel.tsx`'s own
`"done"` branch: it renders an empty `<ul>` with no items and no
"no suggestions" message at all for this case. This is a real, honest
gap in this feature as shipped — decide for yourself whether it's worth
fixing, and if so, write the fix and a test for it.

## Common mistakes & gotchas

- **Trying to use `EventSource` for this feature.** It's the obvious
  first instinct for "consume Server-Sent Events," and it's wrong here
  for the concrete reason this lesson opened with — no custom headers, no
  `POST`. Recognizing *why* a seemingly purpose-built tool doesn't fit is
  as important as knowing the right one.
- **Assuming a single `reader.read()` chunk lines up with exactly one SSE
  event.** It doesn't, reliably — a chunk boundary is a networking detail
  with no relationship to your application's event boundaries. The
  buffer-and-drain-complete-events loop in `aiApi.ts` exists specifically
  because you cannot assume this.
- **Rendering the sub-quest list from partially-streamed text** instead
  of waiting for the `result` event. This would occasionally show a
  broken, truncated title mid-stream — exactly the failure mode Lesson
  07's own "streaming and structured output, reconciled honestly"
  section warned about, now on the client side.
- **Forgetting `onAcceptSuggestion` is the *only* thing `QuestBreakdownPanel`
  should know how to call**, and reaching into `QuestsContext` directly
  from inside the panel instead. That would duplicate logic `QuestDetailPage`
  already owns, and break the "components collect input, parents decide
  what happens" separation this whole codebase already follows.
- **Testing this feature by starting a real backend and making a real
  streamed request in a test.** Slow, flaky, and — per Lesson 07's own
  reasoning — completely unnecessary once the module boundary
  (`streamQuestBreakdown`) is mocked; this component's own rendering
  logic is what's actually under test here.

## How this connects

Lessons 07 and 08 together are this module's full answer to the master
plan's own curriculum line: "building an AI feature into the existing
full stack app... streamed to the React frontend." Every earlier lesson
in this module — the request shape, streaming, structured output, tool
use, error handling, and evaluation — is now sitting inside one real,
tested, working feature, in a codebase that started as a plain in-memory
CRUD API back in Module 05. Module 14 (RAG) is next in the course as a
whole, and it adds a genuinely new capability — "chat with your quest
notes" — to this exact same, still-growing codebase.

## Quick self-check

1. Why can't this feature use the browser's built-in `EventSource` API,
   specifically?
2. Walk through, in your own words, what happens to a chunk of bytes that
   arrives from `reader.read()` containing one and a half SSE events —
   where does the "half" go, and when does it get completed?
3. Name the four states `QuestBreakdownPanel`'s own state machine has,
   and what's shown to the player in each one.
4. Why does the raw, live-streaming text get discarded once the `result`
   event arrives, rather than being kept and just having the sub-quest
   list appended below it?
5. How does `QuestBreakdownPanel.test.tsx` fake a whole streaming network
   request without any fetch-mocking library or fake `ReadableStream` at
   all?
