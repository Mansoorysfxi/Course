# Notes on grading this yourself before asking for review

Open `index.html` in your browser and open DevTools' Console tab (to catch
any errors) before testing.

- **Add a quest**, confirm the page does not reload (check the console isn't
  cleared/reset, which happens automatically on a real reload) and the new
  `<li>` appears with the exact name and difficulty you chose.
- **Confirm the form clears** — the quest-name field should be empty
  immediately after adding, ready for the next quest with no manual
  clearing needed.
- **Add three or four quests**, then click "Complete" on the second one —
  only that one should get struck through. Click it again — it should
  un-strike. This confirms `classList.toggle` (not `add`, which would only
  ever turn it on) is being used correctly.
- **Click "Delete" on a quest in the middle of the list** — confirm the
  correct one disappears and the others stay in their original order,
  untouched. Then check DevTools' Elements panel — the deleted `<li>` should
  be genuinely absent from the tree, not just hidden with CSS (search for
  its text in the Elements panel's search — it shouldn't be found at all).
- **Try submitting with an empty quest name.** The browser's own `required`
  validation (from the `<input>` in `index.html`, unchanged from the
  starter) should block submission — if it doesn't, check you didn't
  accidentally remove `required` while working, since this exercise's
  JavaScript doesn't duplicate that check itself.
- **Search your script for `innerHTML`.** There should be zero occurrences —
  every element here is built with `createElement`/`textContent`, per
  Lesson 06's security note about not using `innerHTML` on anything (even
  though nothing here is untrusted API data yet, the habit starts now).
- **A common near-miss worth checking specifically:** if clicking "Complete"
  or "Delete" on quest #2 accidentally affects quest #1 or #3 instead, the
  event listeners were probably attached somewhere that doesn't have a
  clear, distinct reference to *that specific* `<li>` — re-check that
  `createQuestItem` builds and returns one complete, self-contained `<li>`
  (with its own listeners closing over its own local `item` variable) per
  call, rather than trying to attach one shared listener to the whole list
  and figure out which button was clicked afterward.
