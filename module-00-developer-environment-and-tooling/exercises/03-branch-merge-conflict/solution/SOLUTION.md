# Reference Solution — Branch, Conflict, and a Real Pull Request

Don't read this until you've made a genuine attempt.

```bash
cd ~/recipe-box

# (1) connect to GitHub if not already done — see Lesson 05
git remote add origin https://github.com/YOUR-USERNAME/recipe-box.git
git push -u origin main

# (2) waffles branch — no conflict expected
git switch -c add-waffles
cat > waffles.md << 'EOF'
# Waffles

## Ingredients
- 2 cups flour
- 2 eggs
- 1.5 cups milk
- 1/3 cup oil

## Steps
1. Whisk everything together.
2. Cook in a waffle iron until golden.
EOF
git add waffles.md
git commit -m "Add waffles recipe"

# (3) rename-pancakes-title branch
git switch main
git switch -c rename-pancakes-title
sed -i '1s/.*/# Fluffy Pancakes/' pancakes.md   # or edit the first line by hand in VS Code
git add pancakes.md
git commit -m "Rename pancakes title to Fluffy Pancakes"

# (4) also change the same line directly on main
git switch main
sed -i "1s/.*/# Grandma's Pancakes/" pancakes.md
git add pancakes.md
git commit -m "Rename pancakes title to Grandma's Pancakes"

# (5) merge add-waffles — clean, no conflict
git merge add-waffles
git log --oneline --graph

# (6) merge rename-pancakes-title — expect a conflict on line 1 of pancakes.md
git merge rename-pancakes-title
# --- CONFLICT ---
# Open pancakes.md, see:
#   <<<<<<< HEAD
#   # Grandma's Pancakes
#   =======
#   # Fluffy Pancakes
#   >>>>>>> rename-pancakes-title
# Resolve by picking/combining, e.g.:
#   # Grandma's Fluffy Pancakes
git add pancakes.md
git commit -m "Merge rename-pancakes-title, resolve pancakes title conflict"

# (7) push
git push

# (8) a real PR
git switch -c add-license-note
echo "" >> README.md
echo "This project has no formal license yet." >> README.md
git add README.md
git commit -m "Note that no license is set yet"
git push -u origin add-license-note
gh pr create --fill        # or use the GitHub website

# (9) merge the PR (on GitHub, via website or `gh pr merge`), then sync
git switch main
git pull
git branch -d add-waffles rename-pancakes-title add-license-note
```

**Expected `git log --oneline --graph` shape** (hashes/order will vary):
```
*   f7g8h9i Merge pull request #1 from YOUR-USERNAME/add-license-note
|\
| * e6f7g8h Note that no license is set yet
|/
*   d5e6f7g Merge rename-pancakes-title, resolve pancakes title conflict
|\
| * c4d5e6f Rename pancakes title to Fluffy Pancakes
* | b3c4d5e Rename pancakes title to Grandma's Pancakes
|/
*   a2b3c4d Merge add-waffles
... (earlier commits from Exercise 02)
```

## Notes on grading this yourself before asking for review

- The real test of this exercise is step 6: did you actually get a
  conflict, and did you resolve it cleanly with no leftover `<<<<<<<`
  markers anywhere in the final `pancakes.md`? Search the file for `<<<`
  before submitting.
- The PR must be merged **on GitHub**, not just merged locally and pushed —
  check the repo's "Pull requests" tab shows it as "Merged," with the merge
  commit itself showing "Merge pull request #N" in the log, which is
  GitHub's own generated message, distinct from your local merge commits'
  messages.
- If you skipped `git pull` after merging the PR on GitHub and just kept
  working, your local `main` would silently diverge from GitHub's `main` —
  worth deliberately checking `git log` locally vs. the GitHub website to
  confirm they match after step 9.
