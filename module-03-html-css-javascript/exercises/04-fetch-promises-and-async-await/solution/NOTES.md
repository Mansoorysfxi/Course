# Notes on grading this yourself before asking for review

Open `index.html` in your browser with DevTools open (Console + Network
tabs) and a working internet connection.

- **Happy path:** pick "Tokyo," click "Get Weather." You should see
  "Loading..." appear immediately, then within roughly a second be replaced
  by a real reading like `26.1°C, 71% humidity`. The exact numbers will
  differ depending on when you run this — that's expected, it's live data.
- **Switch cities and click again** — confirm the old result is fully
  replaced, not appended below the previous one (check `resultEl.textContent`
  is being *set*, `=`, not concatenated with `+=`).
- **Click "Trigger a Deliberate Error."** You should see "Loading..." very
  briefly, then a real message like `Error: Weather service returned status
  400` — not a blank screen, not something stuck on "Loading...", and
  nothing that only shows up in the DevTools console with the page itself
  looking unchanged. Open the Network tab and confirm the actual request to
  `BROKEN_URL` really did come back with a 4xx status — this proves you're
  reacting to a real HTTP-level failure, not a hardcoded/faked error message.
- **Check `getCurrentTemperature` specifically throws, rather than returning
  `null`/`undefined` on failure.** The clean way to verify: temporarily call
  `getCurrentTemperature(999, 999)` (invalid coordinates) directly from the
  DevTools console and confirm you get a rejected Promise/thrown error
  printed, not a silently `undefined` result.
- **Grep your own file for `await` and confirm every single one is inside a
  function marked `async`.** This is a syntax-level requirement — if you
  got this wrong, `tsc`/the browser would have already told you with a
  syntax error, so this check is mostly about confirming you understand
  *why* that rule exists, not catching a live bug.
