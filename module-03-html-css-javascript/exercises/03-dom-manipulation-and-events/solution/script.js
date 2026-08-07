/*
 * Exercise 03 reference solution — DOM Manipulation and Events.
 *
 * Don't read this until you've made a genuine attempt at
 * starter/script.js. There is more than one valid way to build the <li>
 * (e.g. exact wording of the buttons) — this is *a* correct solution, not
 * *the only* correct one.
 */

const form = document.querySelector("#quest-form");
const nameInput = document.querySelector("#quest-name");
const difficultySelect = document.querySelector("#quest-difficulty");
const questList = document.querySelector("#quest-list");

function createQuestItem(name, difficulty) {
  const item = document.createElement("li");

  const text = document.createElement("span");
  text.classList.add("quest-text");
  text.textContent = `${name} (${difficulty})`;

  const completeBtn = document.createElement("button");
  completeBtn.type = "button";
  completeBtn.textContent = "Complete";
  completeBtn.addEventListener("click", function () {
    item.classList.toggle("completed");
  });

  const deleteBtn = document.createElement("button");
  deleteBtn.type = "button";
  deleteBtn.textContent = "Delete";
  deleteBtn.addEventListener("click", function () {
    item.remove();
  });

  item.appendChild(text);
  item.appendChild(completeBtn);
  item.appendChild(deleteBtn);

  return item;
}

form.addEventListener("submit", function (event) {
  event.preventDefault();

  const name = nameInput.value;
  const difficulty = difficultySelect.value;

  const newItem = createQuestItem(name, difficulty);
  questList.appendChild(newItem);

  nameInput.value = "";
});
