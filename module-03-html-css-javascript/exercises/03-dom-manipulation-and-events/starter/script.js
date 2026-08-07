/*
 * Exercise 03 starter — DOM Manipulation and Events.
 *
 * Implement each TODO below. See INSTRUCTIONS.md for exactly what each
 * piece must do and how it will be checked. Do not use innerHTML anywhere
 * in this file — build elements with createElement/textContent only.
 */

const form = document.querySelector("#quest-form");
const nameInput = document.querySelector("#quest-name");
const difficultySelect = document.querySelector("#quest-difficulty");
const questList = document.querySelector("#quest-list");

// TODO 1: Build one <li> element for a quest, given its name and
// difficulty, and return it. It must contain:
//   - a <span class="quest-text"> showing something like
//     "Slay the Dragon (Hard)"
//   - a <button> with the text "Complete" that toggles the "completed"
//     class on this <li> when clicked
//   - a <button> with the text "Delete" that removes this <li> from the
//     page entirely when clicked
// Do not append it to the page yet — just build and return it. The event
// listeners for Complete/Delete should be attached here, since this is the
// one place that has direct access to this specific <li>.
function createQuestItem(name, difficulty) {
  // TODO: implement this.
}

// TODO 2: Attach a "submit" listener to `form` that:
//   - calls event.preventDefault()
//   - reads the current values of nameInput and difficultySelect
//   - calls createQuestItem(...) and appends the result to questList
//   - clears nameInput's value back to an empty string afterward
// (difficultySelect resetting itself is fine either way — not checked.)
